"""OCA module parser: extracts docs from manifest + README files."""

import ast
import hashlib
import re
from pathlib import Path

from .rst_parser import clean_text, extract_keywords, EMBEDDING_MAX_CHARS

# Minimum chars of documentation to index a module (raised from 100 to filter noise)
MIN_DOC_CHARS = 250


def parse_manifest(manifest_path: Path) -> dict | None:
    """Parse __manifest__.py or __openerp__.py and return module metadata."""
    try:
        content = manifest_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None

    try:
        data = ast.literal_eval(content)
    except (ValueError, SyntaxError):
        return None

    if not isinstance(data, dict):
        return None

    return {
        "name": data.get("name", ""),
        "summary": data.get("summary", ""),
        "description": data.get("description", ""),
        "category": data.get("category", ""),
        "depends": data.get("depends", []),
        "version": data.get("version", ""),
        "installable": data.get("installable", True),
    }


def parse_oca_readme(module_dir: Path) -> str:
    """Parse OCA-style README fragments or fallback to README.rst."""
    readme_parts = []

    # OCA standard: readme/ directory with fragments
    readme_dir = module_dir / "readme"
    if readme_dir.is_dir():
        for fragment_name in ["DESCRIPTION.rst", "USAGE.rst", "CONFIGURE.rst"]:
            fragment_path = readme_dir / fragment_name
            if fragment_path.is_file():
                try:
                    text = fragment_path.read_text(encoding="utf-8")
                    if text.strip():
                        readme_parts.append(text.strip())
                except (UnicodeDecodeError, OSError):
                    continue

    # Fallback: root README.rst
    if not readme_parts:
        for readme_name in ["README.rst", "README.md", "readme.rst"]:
            readme_path = module_dir / readme_name
            if readme_path.is_file():
                try:
                    text = readme_path.read_text(encoding="utf-8")
                    if text.strip():
                        readme_parts.append(text.strip())
                        break
                except (UnicodeDecodeError, OSError):
                    continue

    return "\n\n".join(readme_parts)


def process_oca_module(
    module_dir: Path,
    repo_name: str,
    version: str,
) -> dict | None:
    """Process a single OCA module directory and return page data."""
    # Find manifest
    manifest_path = module_dir / "__manifest__.py"
    if not manifest_path.is_file():
        manifest_path = module_dir / "__openerp__.py"
        if not manifest_path.is_file():
            return None

    manifest = parse_manifest(manifest_path)
    if not manifest:
        return None

    # Skip non-installable modules
    if not manifest.get("installable", True):
        return None

    module_name = module_dir.name
    readme_text = parse_oca_readme(module_dir)
    cleaned_readme = clean_text(readme_text) if readme_text else ""

    # Build full documentation text
    doc_parts = []
    if manifest.get("name"):
        doc_parts.append(f"Module: {manifest['name']}")
    if manifest.get("summary"):
        doc_parts.append(f"Summary: {manifest['summary']}")
    if manifest.get("description"):
        doc_parts.append(manifest["description"])
    if cleaned_readme:
        doc_parts.append(cleaned_readme)

    full_doc = "\n\n".join(doc_parts)

    # Skip modules with too little documentation
    if len(full_doc) < MIN_DOC_CHARS:
        return None

    # Synthetic path for OCA modules
    path = f"oca/{repo_name}/{module_name}"

    # Content = manifest description + readme (raw)
    content_parts = []
    if manifest.get("description"):
        content_parts.append(manifest["description"])
    if readme_text:
        content_parts.append(readme_text)
    content = "\n\n".join(content_parts) if content_parts else full_doc

    checksum = hashlib.sha256(content.encode("utf-8")).hexdigest()

    # Embedding text: title + summary + cleaned readme
    embedding_parts = [manifest.get("name", module_name)]
    if manifest.get("summary"):
        embedding_parts.append(manifest["summary"])
    if cleaned_readme:
        embedding_parts.append(cleaned_readme[:EMBEDDING_MAX_CHARS])
    embedding_text = "\n".join(embedding_parts)

    # Build enriched keywords from manifest + README
    oca_keywords = set()

    # Module depends (common search terms)
    for dep in manifest.get("depends", []):
        if dep and dep not in ("base",):
            oca_keywords.add(dep.replace("_", " "))

    # Category (functional area)
    cat = manifest.get("category", "")
    if cat:
        oca_keywords.add(cat)
        # Also add sub-parts (e.g. "Accounting/Invoicing" -> "Accounting", "Invoicing")
        for part in cat.split("/"):
            part = part.strip()
            if part:
                oca_keywords.add(part)

    # Headings from README (business terms)
    if readme_text:
        readme_keywords = extract_keywords(readme_text)
        oca_keywords.update(readme_keywords)

    # Module technical name as keyword
    oca_keywords.add(module_name.replace("_", " "))

    return {
        "path": path,
        "title": manifest.get("name", module_name),
        "section": "oca",
        "module": repo_name,
        "submodule": module_name,
        "breadcrumb": f"OCA > {repo_name} > {module_name}",
        "keywords": sorted(oca_keywords),
        "preview": full_doc[:500],
        "content": content,
        "checksum": checksum,
        "embedding_text": embedding_text,
        "version": version,
        "source": "oca",
        "oca_repo": repo_name,
        "oca_module": module_name,
        "category": manifest.get("category", ""),
        "summary": manifest.get("summary", ""),
        "depends": manifest.get("depends", []),
    }
