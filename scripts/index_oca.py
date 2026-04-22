#!/usr/bin/env python3
"""
Index OCA modules into Supabase with vector embeddings.

For each repo in oca_repos.json, shallow-clones the target branch from GitHub,
parses __manifest__.py + README fragments, generates embeddings, and upserts.

Environment variables:
    SUPABASE_URL         - Supabase project URL
    SUPABASE_SERVICE_KEY - Supabase service role key
    VOYAGE_API_KEY       - Voyage AI API key for embeddings

Usage:
    python scripts/index_oca.py --version 17.0
    python scripts/index_oca.py --version 17.0 --repos-file scripts/oca_repos.json
    python scripts/index_oca.py --version 17.0 --dry-run
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.oca_parser import process_oca_module
from lib.supabase_client import SupabaseClient
from lib.voyage_client import generate_embeddings


def branch_exists_remote(repo_name: str, branch: str) -> bool:
    """Check if a branch exists on the OCA GitHub repo using git ls-remote."""
    url = f"https://github.com/OCA/{repo_name}.git"
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--heads", url, branch],
            capture_output=True, text=True, timeout=30,
        )
        return branch in result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def clone_repo(repo_name: str, branch: str, dest: Path) -> bool:
    """Shallow clone an OCA repo at a specific branch."""
    url = f"https://github.com/OCA/{repo_name}.git"
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", branch, url, str(dest)],
            capture_output=True, text=True, timeout=120,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"  Warning: Could not clone {repo_name}@{branch}: {e}")
        return False


def find_modules(repo_dir: Path) -> list[Path]:
    """Find all module directories (containing __manifest__.py or __openerp__.py)."""
    modules = []
    for item in sorted(repo_dir.iterdir()):
        if not item.is_dir() or item.name.startswith("."):
            continue
        if (item / "__manifest__.py").is_file() or (item / "__openerp__.py").is_file():
            modules.append(item)
    return modules


def run_pipeline(
    repos_file: Path,
    version: str,
    supabase_url: str,
    supabase_key: str,
    voyage_key: str,
    dry_run: bool = False,
):
    """Index all OCA modules for a given version."""

    with open(repos_file, "r", encoding="utf-8") as f:
        repos_config = json.load(f)

    repos = [r for r in repos_config["repos"] if r.get("active", True)]
    print(f"Processing {len(repos)} active OCA repos for version {version}")

    all_pages = []
    skipped_repos = []

    for repo_info in repos:
        repo_name = repo_info["repo"]
        print(f"\n--- {repo_name} ---")

        # Check if branch exists
        if not branch_exists_remote(repo_name, version):
            print(f"  Branch {version} not found, skipping")
            skipped_repos.append(repo_name)
            continue

        # Clone to temp dir
        with tempfile.TemporaryDirectory() as tmpdir:
            clone_dir = Path(tmpdir) / repo_name
            if not clone_repo(repo_name, version, clone_dir):
                skipped_repos.append(repo_name)
                continue

            # Find and process modules
            modules = find_modules(clone_dir)
            print(f"  Found {len(modules)} modules")

            for module_dir in modules:
                page = process_oca_module(module_dir, repo_name, version)
                if page:
                    all_pages.append(page)
                    print(f"    + {module_dir.name}: {page['title']}")

    print(f"\n{'='*60}")
    print(f"Total modules indexed: {len(all_pages)}")
    print(f"Repos skipped (no branch {version}): {len(skipped_repos)}")

    if dry_run:
        print(f"Dry run: would process {len(all_pages)} OCA modules. Exiting.")
        return

    if not all_pages:
        print("No OCA modules to index. Exiting.")
        return

    # Diff against Supabase
    sb = SupabaseClient(supabase_url, supabase_key)
    existing_checksums = sb.get_existing_checksums(version, "oca")
    print(f"Found {len(existing_checksums)} existing OCA pages in Supabase")

    changed_pages = []
    unchanged_count = 0
    for page in all_pages:
        if existing_checksums.get(page["path"]) == page["checksum"]:
            unchanged_count += 1
        else:
            changed_pages.append(page)

    print(f"Changed/new: {len(changed_pages)}, unchanged: {unchanged_count}")

    if not changed_pages:
        deleted = sb.delete_removed_pages(version, {p["path"] for p in all_pages}, "oca")
        print(f"No content changes. Deleted {deleted} removed pages. Done.")
        return

    # Generate embeddings
    print(f"Generating embeddings for {len(changed_pages)} OCA modules...")
    embedding_texts = [p["embedding_text"] for p in changed_pages]
    embeddings = generate_embeddings(embedding_texts, voyage_key)

    # Prepare rows
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
            "oca_repo": page["oca_repo"],
            "oca_module": page["oca_module"],
            "category": page["category"],
            "summary": page["summary"],
            "depends": page["depends"],
        })

    # Upsert
    print(f"Upserting {len(rows)} OCA pages to Supabase...")
    upserted = sb.upsert_pages(rows)

    # Clean up removed
    deleted = sb.delete_removed_pages(version, {p["path"] for p in all_pages}, "oca")

    # Update oca_repos registry
    now = datetime.now(timezone.utc).isoformat()
    registry_entries = []
    indexed_repos = {p["oca_repo"] for p in all_pages}
    for repo_info in repos:
        if repo_info["repo"] in indexed_repos:
            entry = {
                "repo_name": repo_info["repo"],
                "category": repo_info.get("category", ""),
                "description": repo_info.get("description", ""),
                "last_indexed_at": now,
                "is_active": True,
            }
            # Update versions_available would need a read-modify-write, skip for now
            registry_entries.append(entry)

    if registry_entries:
        sb.upsert_oca_repos(registry_entries)
        print(f"Updated {len(registry_entries)} OCA repos in registry")

    print(f"\nDone! Upserted: {upserted}, Deleted: {deleted}, Unchanged: {unchanged_count}")


def main():
    parser = argparse.ArgumentParser(
        description="Index OCA modules into Supabase with vector embeddings"
    )
    parser.add_argument(
        "--version", required=True,
        help="Odoo version to index (e.g. 17.0)",
    )
    parser.add_argument(
        "--repos-file", default=None,
        help="Path to oca_repos.json (default: scripts/oca_repos.json)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Clone and parse only, do not push to Supabase",
    )
    args = parser.parse_args()

    repos_file = Path(args.repos_file) if args.repos_file else Path(__file__).parent / "oca_repos.json"
    if not repos_file.is_file():
        print(f"Error: Repos file '{repos_file}' not found.", file=sys.stderr)
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

    run_pipeline(
        repos_file=repos_file,
        version=args.version,
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        voyage_key=voyage_key,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
