"""RST parsing utilities extracted from build_index.py."""

import hashlib
import re
from pathlib import Path

RST_HEADING_CHARS = set("=-~^\"'`#*+:._")
EXCLUDED_DIRS = {"locale", "extensions", "redirects", "static", "tests", "_static", "_templates"}
EXCLUDED_PATTERNS = {".pot", ".po", ".mo"}
EMBEDDING_MAX_CHARS = 4000


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


def process_rst_file(file_path: Path, content_dir: Path) -> dict | None:
    """Process a single RST file and return its page data."""
    try:
        raw_text = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as e:
        print(f"  Warning: Could not read {file_path}: {e}")
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
