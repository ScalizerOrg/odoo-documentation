#!/usr/bin/env python3
"""
Build changelog between consecutive Odoo documentation versions.

Compares pages by path across version pairs and detects:
- added: path in version N+1 but not N
- removed: path in version N but not N+1
- modified: path in both, different checksum
- renamed: among removed+added, title similarity > 0.8

Environment variables:
    SUPABASE_URL         - Supabase project URL
    SUPABASE_SERVICE_KEY - Supabase service role key

Usage:
    python scripts/build_changelog.py --from-version 18.0 --to-version 19.0
    python scripts/build_changelog.py --all-versions
    python scripts/build_changelog.py --all-versions --source native
    python scripts/build_changelog.py --all-versions --dry-run
"""

import argparse
import os
import sys
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.supabase_client import SupabaseClient

# Ordered list of Odoo versions
ALL_VERSIONS = ["10.0", "11.0", "12.0", "13.0", "14.0", "15.0", "16.0", "17.0", "18.0", "19.0"]

# Thresholds
RENAME_TITLE_THRESHOLD = 0.8  # Levenshtein ratio for detecting renames
COSMETIC_CHANGE_THRESHOLD = 0.98  # SequenceMatcher ratio to ignore cosmetic changes


def build_changelog_pair(
    sb: SupabaseClient,
    version_from: str,
    version_to: str,
    source: str = "native",
    dry_run: bool = False,
) -> dict:
    """Build changelog between two consecutive versions."""
    print(f"\n--- Changelog {version_from} -> {version_to} ({source}) ---")

    # Fetch pages for both versions
    pages_from = sb.get_pages_summary(version_from, source)
    pages_to = sb.get_pages_summary(version_to, source)

    if not pages_from and not pages_to:
        print("  Both versions empty, skipping")
        return {"added": 0, "removed": 0, "modified": 0, "renamed": 0}

    from_map = {p["path"]: p for p in pages_from}
    to_map = {p["path"]: p for p in pages_to}

    from_paths = set(from_map.keys())
    to_paths = set(to_map.keys())

    # Classify changes
    added_paths = to_paths - from_paths
    removed_paths = from_paths - to_paths
    common_paths = from_paths & to_paths

    # Detect modified (different checksum)
    modified_paths = set()
    for path in common_paths:
        if from_map[path]["checksum"] != to_map[path]["checksum"]:
            modified_paths.add(path)

    # Detect renames among removed+added pairs (by title similarity)
    renamed = []
    remaining_removed = set(removed_paths)
    remaining_added = set(added_paths)

    if remaining_removed and remaining_added:
        for r_path in list(remaining_removed):
            r_title = from_map[r_path].get("title", "")
            if not r_title:
                continue
            best_match = None
            best_ratio = 0.0
            for a_path in remaining_added:
                a_title = to_map[a_path].get("title", "")
                if not a_title:
                    continue
                ratio = SequenceMatcher(None, r_title.lower(), a_title.lower()).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = a_path
            if best_match and best_ratio >= RENAME_TITLE_THRESHOLD:
                renamed.append((r_path, best_match, best_ratio))
                remaining_removed.discard(r_path)
                remaining_added.discard(best_match)

    # Build changelog entries
    entries = []

    for path in sorted(remaining_added):
        entries.append({
            "path": path,
            "source": source,
            "version_from": version_from,
            "version_to": version_to,
            "change_type": "added",
            "change_summary": f"New page: {to_map[path].get('title', path)}",
            "diff_stats": {},
        })

    for path in sorted(remaining_removed):
        entries.append({
            "path": path,
            "source": source,
            "version_from": version_from,
            "version_to": version_to,
            "change_type": "removed",
            "change_summary": f"Removed page: {from_map[path].get('title', path)}",
            "diff_stats": {},
        })

    for path in sorted(modified_paths):
        entries.append({
            "path": path,
            "source": source,
            "version_from": version_from,
            "version_to": version_to,
            "change_type": "modified",
            "change_summary": f"Modified: {to_map[path].get('title', path)}",
            "diff_stats": {},
        })

    for old_path, new_path, ratio in renamed:
        entries.append({
            "path": new_path,
            "source": source,
            "version_from": version_from,
            "version_to": version_to,
            "change_type": "renamed",
            "change_summary": f"Renamed from {old_path} (similarity: {ratio:.2f})",
            "diff_stats": {"old_path": old_path, "similarity": round(ratio, 3)},
        })

    stats = {
        "added": len(remaining_added),
        "removed": len(remaining_removed),
        "modified": len(modified_paths),
        "renamed": len(renamed),
    }
    print(f"  Added: {stats['added']}, Removed: {stats['removed']}, "
          f"Modified: {stats['modified']}, Renamed: {stats['renamed']}")

    if dry_run:
        print(f"  Dry run: would upsert {len(entries)} changelog entries")
        return stats

    if entries:
        # Clear existing changelog for this pair then insert
        sb.clear_changelog(version_from, version_to)
        upserted = sb.upsert_changelog(entries)
        print(f"  Upserted {upserted} changelog entries")

    return stats


def run_pipeline(
    version_pairs: list[tuple[str, str]],
    source: str,
    supabase_url: str,
    supabase_key: str,
    dry_run: bool = False,
):
    """Build changelog for all version pairs."""
    sb = SupabaseClient(supabase_url, supabase_key)

    total_stats = {"added": 0, "removed": 0, "modified": 0, "renamed": 0}
    for v_from, v_to in version_pairs:
        stats = build_changelog_pair(sb, v_from, v_to, source, dry_run)
        for k in total_stats:
            total_stats[k] += stats[k]

    print(f"\n{'='*60}")
    print(f"Total changelog: Added={total_stats['added']}, Removed={total_stats['removed']}, "
          f"Modified={total_stats['modified']}, Renamed={total_stats['renamed']}")


def main():
    parser = argparse.ArgumentParser(
        description="Build changelog between Odoo documentation versions"
    )
    parser.add_argument(
        "--from-version", default=None,
        help="Source version (e.g. 18.0)",
    )
    parser.add_argument(
        "--to-version", default=None,
        help="Target version (e.g. 19.0)",
    )
    parser.add_argument(
        "--all-versions", action="store_true",
        help="Build changelog for all consecutive version pairs",
    )
    parser.add_argument(
        "--source", default="native", choices=["native", "oca"],
        help="Source type (default: native)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Compare only, do not push to Supabase",
    )
    args = parser.parse_args()

    if args.all_versions:
        version_pairs = list(zip(ALL_VERSIONS[:-1], ALL_VERSIONS[1:]))
    elif args.from_version and args.to_version:
        version_pairs = [(args.from_version, args.to_version)]
    else:
        print("Error: specify --all-versions or both --from-version and --to-version", file=sys.stderr)
        sys.exit(1)

    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", "")

    if not args.dry_run:
        missing = []
        if not supabase_url:
            missing.append("SUPABASE_URL")
        if not supabase_key:
            missing.append("SUPABASE_SERVICE_KEY")
        if missing:
            print(f"Error: Missing environment variables: {', '.join(missing)}", file=sys.stderr)
            sys.exit(1)

    print(f"Building changelog for {len(version_pairs)} version pair(s) ({args.source})...")

    run_pipeline(
        version_pairs=version_pairs,
        source=args.source,
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
