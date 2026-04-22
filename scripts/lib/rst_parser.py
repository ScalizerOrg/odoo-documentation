"""RST parsing utilities extracted from build_index.py."""

import hashlib
import re
from pathlib import Path

RST_HEADING_CHARS = set("=-~^\"'`#*+:._")
EXCLUDED_DIRS = {"locale", "extensions", "redirects", "static", "tests", "_static", "_templates"}
EXCLUDED_PATTERNS = {".pot", ".po", ".mo"}
EMBEDDING_MAX_CHARS = 12000


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
    """Extract keywords from RST directives, headings, bold text, and cross-references."""
    keywords = set()

    # :menuselection: directives (menu paths)
    for match in re.finditer(r":menuselection:`([^`]+)`", text):
        parts = match.group(1).split("-->")
        for part in parts:
            cleaned = part.strip()
            if cleaned:
                keywords.add(cleaned)

    # :guilabel: directives (field names, buttons)
    for match in re.finditer(r":guilabel:`([^`]+)`", text):
        keywords.add(match.group(1).strip())

    # :ref: cross-references (linked page labels)
    for match in re.finditer(r":ref:`(?:[^<`]*<)?([^>`]+)>?`", text):
        ref = match.group(1).strip().replace("_", " ").replace("-", " ")
        if len(ref) > 2:
            keywords.add(ref)

    # :doc: cross-references (linked doc paths)
    for match in re.finditer(r":doc:`(?:[^<`]*<)?([^>`]+)>?`", text):
        # Extract last meaningful part of path
        doc_path = match.group(1).strip()
        last_part = doc_path.rstrip("/").rsplit("/", 1)[-1]
        cleaned = last_part.replace("_", " ").replace("-", " ")
        if len(cleaned) > 2:
            keywords.add(cleaned)

    # RST H2/H3 headings (sub-section titles = key business terms)
    lines = text.split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        # Check if next line is an underline (H2/H3 use -, ~, ^)
        if i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if (
                next_line
                and len(next_line) >= 3
                and len(set(next_line)) == 1
                and next_line[0] in "-~^"
                and len(next_line) >= len(stripped) - 2
                and not (len(set(stripped)) == 1 and stripped[0] in RST_HEADING_CHARS)
            ):
                if len(stripped) > 2:
                    keywords.add(stripped)

    # Bold text (**term**) — often field names, important concepts
    for match in re.finditer(r"\*\*([^*]+)\*\*", text):
        term = match.group(1).strip()
        if 2 < len(term) < 60:
            keywords.add(term)

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


def split_rst_sections(text: str) -> list[dict]:
    """Split RST text into sections based on H2/H3 headings (-, ~, ^).

    Returns a list of dicts with 'title' and 'content' for each section.
    The first section (before any H2) gets title=None.
    """
    lines = text.split("\n")
    sections = []
    current_title = None
    current_lines = []

    i = 0
    while i < len(lines):
        stripped = lines[i].strip()

        # Detect heading: text line followed by underline with -, ~, or ^
        if (
            stripped
            and i + 1 < len(lines)
            and not (len(set(stripped)) == 1 and stripped[0] in RST_HEADING_CHARS)
        ):
            next_line = lines[i + 1].strip()
            if (
                next_line
                and len(next_line) >= 3
                and len(set(next_line)) == 1
                and next_line[0] in "-~^"
                and len(next_line) >= len(stripped) - 2
            ):
                # Save previous section
                if current_lines:
                    sections.append({
                        "title": current_title,
                        "content": "\n".join(current_lines),
                    })
                current_title = stripped
                current_lines = [lines[i], lines[i + 1]]
                i += 2
                continue

        current_lines.append(lines[i])
        i += 1

    # Save last section
    if current_lines:
        sections.append({
            "title": current_title,
            "content": "\n".join(current_lines),
        })

    return sections


CHUNK_THRESHOLD = 12000  # Only chunk pages longer than this (chars of cleaned text)


def process_rst_file(file_path: Path, content_dir: Path) -> list[dict]:
    """Process a single RST file and return page data (possibly with chunks).

    Returns a list: [parent_page] if short, or [parent_page, chunk1, chunk2, ...] if long.
    """
    try:
        raw_text = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as e:
        print(f"  Warning: Could not read {file_path}: {e}")
        return []

    lines = raw_text.split("\n")
    title = extract_title(lines)
    if not title:
        return []

    rel_path = file_path.relative_to(content_dir).as_posix()
    components = parse_path_components(rel_path)
    keywords = extract_keywords(raw_text)
    cleaned = clean_text(raw_text)
    preview = cleaned[:500] if cleaned else ""
    checksum = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()

    parent_page = {
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
        "parent_path": None,
        "chunk_index": None,
    }

    # Only chunk if content is longer than threshold
    if len(cleaned) <= CHUNK_THRESHOLD:
        return [parent_page]

    # Split into sections and create chunks
    sections = split_rst_sections(raw_text)
    # Need at least 2 titled sections to make chunking worthwhile
    titled_sections = [s for s in sections if s["title"]]
    if len(titled_sections) < 2:
        return [parent_page]

    # Mark parent as chunked (chunk_index=0)
    parent_page["chunk_index"] = 0
    result = [parent_page]

    chunk_idx = 1
    for section in sections:
        if not section["title"]:
            continue  # Skip intro section (already in parent)

        section_cleaned = clean_text(section["content"])
        if len(section_cleaned) < 100:
            continue  # Skip tiny sections

        section_keywords = extract_keywords(section["content"])
        section_preview = section_cleaned[:500]
        chunk_path = f"{rel_path}#chunk-{chunk_idx}"

        chunk_embedding = f"{title} — {section['title']}\n{' '.join(section_keywords)}\n{section_cleaned[:EMBEDDING_MAX_CHARS]}"
        chunk_checksum = hashlib.sha256(section["content"].encode("utf-8")).hexdigest()

        result.append({
            "path": chunk_path,
            "title": section["title"],
            "section": components["section"],
            "module": components["module"],
            "submodule": components["submodule"],
            "breadcrumb": f"{build_breadcrumb(rel_path)} > {section['title']}",
            "keywords": section_keywords,
            "preview": section_preview,
            "content": section["content"],
            "checksum": chunk_checksum,
            "embedding_text": chunk_embedding,
            "parent_path": rel_path,
            "chunk_index": chunk_idx,
        })
        chunk_idx += 1

    print(f"    Chunked {rel_path}: {len(result) - 1} chunks")
    return result


def scan_content_dir(content_dir: Path, version: str) -> list[dict]:
    """Scan the content directory and return all page data (including chunks)."""
    pages = []
    rst_files = sorted(content_dir.rglob("*.rst"))
    print(f"Found {len(rst_files)} RST files in {content_dir}")

    chunk_count = 0
    for rst_file in rst_files:
        rel = rst_file.relative_to(content_dir)
        if should_exclude(rel):
            continue
        entries = process_rst_file(rst_file, content_dir)
        for entry in entries:
            entry["version"] = version
            pages.append(entry)
            if entry.get("chunk_index") and entry["chunk_index"] > 0:
                chunk_count += 1

    parent_count = len(pages) - chunk_count
    print(f"Parsed {parent_count} pages + {chunk_count} chunks = {len(pages)} total entries")
    return pages
