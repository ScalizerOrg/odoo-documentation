#!/usr/bin/env python3
"""
Build index from Odoo RST documentation and push to Supabase with vector embeddings.

Scans content/ directory for .rst files, generates embeddings via OpenAI,
and upserts everything into the Supabase doc_pages table.

Uses checksums to skip re-embedding unchanged pages (saves API costs).

Environment variables:
    SUPABASE_URL         - Supabase project URL
    SUPABASE_SERVICE_KEY - Supabase service role key
    OPENAI_API_KEY       - OpenAI API key for embeddings

Usage:
    python scripts/build_index.py --version 19.0 --content-dir content
    python scripts/build_index.py --version 19.0 --content-dir content --json-output index.json
    python scripts/build_index.py --version 19.0 --content-dir content --dry-run

Requirements:
    pip install openai requests
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import openai
import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

EXCLUDED_DIRS = {"locale", "extensions", "redirects", "static", "tests", "_static", "_templates"}
EXCLUDED_PATTERNS = {".pot", ".po", ".mo"}
RST_HEADING_CHARS = set("=-~^\"'`#*+:._")

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_BATCH_SIZE = 200  # OpenAI supports up to 2048 per batch
SUPABASE_BATCH_SIZE = 50    # Rows per upsert call
EMBEDDING_MAX_CHARS = 4000  # Max chars for embedding input text


# ---------------------------------------------------------------------------
# RST Parsing (unchanged from V1)
# ---------------------------------------------------------------------------

def extract_title(lines: list[str]) -> str:
    """Extract the first RST heading from file lines."""
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if (
                next_line
                and len(set(next_line)) == 1
                and next_line[0] in RST_HEADING_CHARS
                and len(next_line) >= len(stripped)
            ):
                if not (len(set(stripped)) == 1 and stripped[0] in RST_HEADING_CHARS):
                    return stripped
        if (
            len(set(stripped)) == 1
            and stripped[0] in RST_HEADING_CHARS
            and i + 2 < len(lines)
        ):
            title_line = lines[i + 1].strip()
            underline = lines[i + 2].strip()
            if (
                title_line
                and underline
                and len(set(underline)) == 1
                and underline[0] == stripped[0]
            ):
                return title_line
    return ""


def extract_keywords(text: str) -> list[str]:
    """Extract keywords from :menuselection: and :guilabel: directives."""
    keywords = set()
    for match in re.finditer(r":menuselection:`([^`]+)`", text):
        parts = match.group(1).split("-->")
        for part in parts:
            cleaned = part.strip()
            if cleaned:
                keywords.add(cleaned)
    for match in re.finditer(r":guilabel:`([^`]+)`", text):
        keywords.add(match.group(1).strip())
    return sorted(keywords)


def clean_text(text: str) -> str:
    """Remove RST directives, roles, and markup to produce plain text."""
    text = re.sub(r"\.\. [a-zA-Z0-9_-]+::.*", "", text)
    text = re.sub(r":[a-zA-Z0-9_-]+:`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"``([^`]+)``", r"\1", text)
    text = re.sub(r"\.\. (image|figure)::.*(\n[ \t]+.*)*", "", text)
    text = re.sub(r"^[=\-~^\"'`#+:._]{3,}$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\.\. toctree::.*?(\n\n|\Z)", "", text, flags=re.DOTALL)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def build_breadcrumb(rel_path: str) -> str:
    """Build a human-readable breadcrumb from the file path."""
    parts = Path(rel_path).with_suffix("").parts
    return " > ".join(p.replace("_", " ").replace("-", " ").title() for p in parts)


def parse_path_components(rel_path: str) -> dict:
    """Extract section, module, submodule from relative path."""
    parts = Path(rel_path).parts
    return {
        "section": parts[0] if len(parts) > 0 else "",
        "module": parts[1] if len(parts) > 1 else "",
        "submodule": parts[2] if len(parts) > 2 else "",
    }


def should_exclude(path: Path) -> bool:
    """Check if a path should be excluded from indexing."""
    for part in path.parts:
        if part in EXCLUDED_DIRS:
            return True
    return path.suffix in EXCLUDED_PATTERNS


# ---------------------------------------------------------------------------
# File Processing
# ---------------------------------------------------------------------------

def process_rst_file(file_path: Path, content_dir: Path) -> dict | None:
    """Process a single RST file and return its page data."""
    try:
        raw_text = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as e:
        print(f"  Warning: Could not read {file_path}: {e}", file=sys.stderr)
        return None

    lines = raw_text.split("\n")
    title = extract_title(lines)
    if not title:
        return None

    rel_path = file_path.relative_to(content_dir).as_posix()
    components = parse_path_components(rel_path)
    keywords = extract_keywords(raw_text)
    cleaned = clean_text(raw_text)
    preview = cleaned[:500] if cleaned else ""
    checksum = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()

    return {
        "path": rel_path,
        "title": title,
        "section": components["section"],
        "module": components["module"],
        "submodule": components["submodule"],
        "breadcrumb": build_breadcrumb(rel_path),
        "keywords": keywords,
        "preview": preview,
        "content": raw_text,
        "checksum": checksum,
        "embedding_text": f"{title}\n{' '.join(keywords)}\n{cleaned[:EMBEDDING_MAX_CHARS]}",
    }


def scan_content_dir(content_dir: Path, version: str) -> list[dict]:
    """Scan the content directory and return all page data."""
    pages = []
    rst_files = sorted(content_dir.rglob("*.rst"))
    print(f"Found {len(rst_files)} RST files in {content_dir}")

    for rst_file in rst_files:
        rel = rst_file.relative_to(content_dir)
        if should_exclude(rel):
            continue
        entry = process_rst_file(rst_file, content_dir)
        if entry:
            entry["version"] = version
            pages.append(entry)

    print(f"Parsed {len(pages)} valid pages")
    return pages


# ---------------------------------------------------------------------------
# Supabase Client
# ---------------------------------------------------------------------------

class SupabaseClient:
    """Minimal Supabase REST API client."""

    def __init__(self, url: str, service_key: str):
        self.base_url = url.rstrip("/")
        self.headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }

    def get_existing_checksums(self, version: str) -> dict[str, str]:
        """Fetch path→checksum map for existing pages."""
        resp = requests.get(
            f"{self.base_url}/rest/v1/doc_pages",
            headers={**self.headers, "Prefer": ""},
            params={
                "select": "path,checksum",
                "version": f"eq.{version}",
            },
        )
        resp.raise_for_status()
        return {row["path"]: row["checksum"] for row in resp.json()}

    def upsert_pages(self, pages: list[dict]) -> int:
        """Upsert pages in batches. Returns count of upserted rows."""
        count = 0
        for i in range(0, len(pages), SUPABASE_BATCH_SIZE):
            batch = pages[i : i + SUPABASE_BATCH_SIZE]
            resp = requests.post(
                f"{self.base_url}/rest/v1/doc_pages",
                headers={
                    **self.headers,
                    "Prefer": "resolution=merge-duplicates,return=minimal",
                },
                json=batch,
            )
            resp.raise_for_status()
            count += len(batch)
            print(f"  Upserted batch {i // SUPABASE_BATCH_SIZE + 1} ({len(batch)} rows)")
        return count

    def delete_removed_pages(self, version: str, valid_paths: set[str]) -> int:
        """Delete pages that no longer exist in the content directory."""
        existing = self.get_existing_checksums(version)
        to_delete = [p for p in existing if p not in valid_paths]
        if not to_delete:
            return 0

        for path in to_delete:
            resp = requests.delete(
                f"{self.base_url}/rest/v1/doc_pages",
                headers=self.headers,
                params={"path": f"eq.{path}", "version": f"eq.{version}"},
            )
            resp.raise_for_status()

        print(f"  Deleted {len(to_delete)} removed pages")
        return len(to_delete)


# ---------------------------------------------------------------------------
# OpenAI Embeddings
# ---------------------------------------------------------------------------

def generate_embeddings(texts: list[str], api_key: str) -> list[list[float]]:
    """Generate embeddings for a list of texts using OpenAI API."""
    client = openai.OpenAI(api_key=api_key)
    all_embeddings: list[list[float]] = [[] for _ in texts]

    for i in range(0, len(texts), EMBEDDING_BATCH_SIZE):
        batch = texts[i : i + EMBEDDING_BATCH_SIZE]
        print(f"  Generating embeddings batch {i // EMBEDDING_BATCH_SIZE + 1} ({len(batch)} texts)...")

        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch,
        )

        for j, item in enumerate(response.data):
            all_embeddings[i + j] = item.embedding

        # Respect rate limits
        if i + EMBEDDING_BATCH_SIZE < len(texts):
            time.sleep(0.5)

    return all_embeddings


# ---------------------------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------------------------

def run_pipeline(
    content_dir: Path,
    version: str,
    supabase_url: str,
    supabase_key: str,
    openai_key: str,
    json_output: str | None = None,
    dry_run: bool = False,
):
    """Full indexation pipeline: parse → diff → embed → upsert."""

    # 1. Parse all RST files
    pages = scan_content_dir(content_dir, version)
    if not pages:
        print("No pages found. Exiting.")
        return

    # 2. Optional JSON output (backup / debug)
    if json_output:
        json_data = {
            "version": version,
            "built_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "page_count": len(pages),
            "pages": [
                {k: v for k, v in p.items() if k not in ("content", "embedding_text")}
                for p in pages
            ],
        }
        with open(json_output, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        size_kb = os.path.getsize(json_output) / 1024
        print(f"JSON index written to {json_output} ({size_kb:.1f} KB)")

    if dry_run:
        print(f"Dry run: would process {len(pages)} pages. Exiting.")
        return

    # 3. Diff against Supabase to find changed pages
    sb = SupabaseClient(supabase_url, supabase_key)
    existing_checksums = sb.get_existing_checksums(version)
    print(f"Found {len(existing_checksums)} existing pages in Supabase")

    changed_pages = []
    unchanged_count = 0
    for page in pages:
        if existing_checksums.get(page["path"]) == page["checksum"]:
            unchanged_count += 1
        else:
            changed_pages.append(page)

    print(f"Changed/new: {len(changed_pages)}, unchanged: {unchanged_count}")

    if not changed_pages:
        # Still check for deletions
        deleted = sb.delete_removed_pages(version, {p["path"] for p in pages})
        print(f"No content changes. Deleted {deleted} removed pages. Done.")
        return

    # 4. Generate embeddings for changed pages
    print(f"Generating embeddings for {len(changed_pages)} pages...")
    embedding_texts = [p["embedding_text"] for p in changed_pages]
    embeddings = generate_embeddings(embedding_texts, openai_key)

    # 5. Prepare rows for upsert
    rows = []
    for page, embedding in zip(changed_pages, embeddings):
        rows.append({
            "path": page["path"],
            "title": page["title"],
            "section": page["section"],
            "module": page["module"],
            "submodule": page["submodule"],
            "breadcrumb": page["breadcrumb"],
            "keywords": page["keywords"],
            "preview": page["preview"],
            "content": page["content"],
            "embedding": embedding,
            "version": page["version"],
            "checksum": page["checksum"],
        })

    # 6. Upsert to Supabase
    print(f"Upserting {len(rows)} pages to Supabase...")
    upserted = sb.upsert_pages(rows)

    # 7. Delete removed pages
    deleted = sb.delete_removed_pages(version, {p["path"] for p in pages})

    print(f"\nDone! Upserted: {upserted}, Deleted: {deleted}, Unchanged: {unchanged_count}")
    print(f"Total pages in version {version}: {len(pages)}")


def main():
    parser = argparse.ArgumentParser(
        description="Index Odoo RST documentation into Supabase with vector embeddings"
    )
    parser.add_argument(
        "--version", default="19.0",
        help="Odoo version being indexed (default: 19.0)",
    )
    parser.add_argument(
        "--content-dir", default="content",
        help="Path to the content/ directory (default: content)",
    )
    parser.add_argument(
        "--json-output", default=None,
        help="Optional: also write a JSON index file (backup)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Parse files only, do not push to Supabase",
    )
    args = parser.parse_args()

    content_dir = Path(args.content_dir)
    if not content_dir.is_dir():
        print(f"Error: Content directory '{content_dir}' not found.", file=sys.stderr)
        sys.exit(1)

    # Environment variables
    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    openai_key = os.environ.get("OPENAI_API_KEY", "")

    if not args.dry_run:
        missing = []
        if not supabase_url:
            missing.append("SUPABASE_URL")
        if not supabase_key:
            missing.append("SUPABASE_SERVICE_KEY")
        if not openai_key:
            missing.append("OPENAI_API_KEY")
        if missing:
            print(f"Error: Missing environment variables: {', '.join(missing)}", file=sys.stderr)
            sys.exit(1)

    print(f"Indexing Odoo {args.version} documentation...")
    print(f"Content directory: {content_dir.resolve()}")

    run_pipeline(
        content_dir=content_dir,
        version=args.version,
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        openai_key=openai_key,
        json_output=args.json_output,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
