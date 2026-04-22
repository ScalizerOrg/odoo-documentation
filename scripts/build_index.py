#!/usr/bin/env python3
"""
Build index from Odoo RST documentation and push to Supabase with vector embeddings.

V2: Supports --source flag and multi-version indexing via shared lib/.

Scans content/ directory for .rst files, generates embeddings via Voyage AI,
and upserts everything into the Supabase doc_pages table.

Uses checksums to skip re-embedding unchanged pages (saves API costs).

Environment variables:
    SUPABASE_URL         - Supabase project URL
    SUPABASE_SERVICE_KEY - Supabase service role key
    VOYAGE_API_KEY       - Voyage AI API key for embeddings

Usage:
    python scripts/build_index.py --version 19.0 --content-dir content
    python scripts/build_index.py --version 19.0 --content-dir content --source native
    python scripts/build_index.py --version 19.0 --content-dir content --json-output index.json
    python scripts/build_index.py --version 19.0 --content-dir content --dry-run

Requirements:
    pip install requests
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Allow running from repo root or scripts/
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.rst_parser import scan_content_dir
from lib.supabase_client import SupabaseClient
from lib.voyage_client import generate_embeddings


def run_pipeline(
    content_dir: Path,
    version: str,
    source: str,
    supabase_url: str,
    supabase_key: str,
    voyage_key: str,
    json_output: str | None = None,
    dry_run: bool = False,
):
    """Full indexation pipeline: parse -> diff -> embed -> upsert."""

    # 1. Parse all RST files
    pages = scan_content_dir(content_dir, version)
    if not pages:
        print("No pages found. Exiting.")
        return

    # Tag all pages with source
    for page in pages:
        page["source"] = source

    # 2. Optional JSON output (backup / debug)
    if json_output:
        json_data = {
            "version": version,
            "source": source,
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
    existing_checksums = sb.get_existing_checksums(version, source)
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
        deleted = sb.delete_removed_pages(version, {p["path"] for p in pages}, source)
        print(f"No content changes. Deleted {deleted} removed pages. Done.")
        return

    # 4. Generate embeddings for changed pages
    print(f"Generating embeddings for {len(changed_pages)} pages...")
    embedding_texts = [p["embedding_text"] for p in changed_pages]
    embeddings = generate_embeddings(embedding_texts, voyage_key)

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
            "source": page["source"],
            "parent_path": page.get("parent_path"),
            "chunk_index": page.get("chunk_index"),
        })

    # 6. Upsert to Supabase
    print(f"Upserting {len(rows)} pages to Supabase...")
    upserted = sb.upsert_pages(rows)

    # 7. Delete removed pages
    deleted = sb.delete_removed_pages(version, {p["path"] for p in pages}, source)

    print(f"\nDone! Upserted: {upserted}, Deleted: {deleted}, Unchanged: {unchanged_count}")
    print(f"Total pages in version {version} ({source}): {len(pages)}")


def main():
    parser = argparse.ArgumentParser(
        description="Index Odoo RST documentation into Supabase with vector embeddings"
    )
    parser.add_argument(
        "--version", default="19.0",
        help="Odoo version being indexed (default: 19.0)",
    )
    parser.add_argument(
        "--source", default="native", choices=["native"],
        help="Source type (default: native). Use index_oca.py for OCA.",
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

    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    voyage_key = os.environ.get("VOYAGE_API_KEY", "")

    if not args.dry_run:
        missing = []
        if not supabase_url:
            missing.append("SUPABASE_URL")
        if not supabase_key:
            missing.append("SUPABASE_SERVICE_KEY")
        if not voyage_key:
            missing.append("VOYAGE_API_KEY")
        if missing:
            print(f"Error: Missing environment variables: {', '.join(missing)}", file=sys.stderr)
            sys.exit(1)

    print(f"Indexing Odoo {args.version} documentation ({args.source})...")
    print(f"Content directory: {content_dir.resolve()}")

    run_pipeline(
        content_dir=content_dir,
        version=args.version,
        source=args.source,
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        voyage_key=voyage_key,
        json_output=args.json_output,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
