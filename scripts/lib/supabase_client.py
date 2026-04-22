"""Supabase REST API client extracted from build_index.py."""

import requests

SUPABASE_BATCH_SIZE = 50


class SupabaseClient:
    """Minimal Supabase REST API client for doc_pages operations."""

    def __init__(self, url: str, service_key: str):
        self.base_url = url.rstrip("/")
        self.headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }

    def get_existing_checksums(self, version: str, source: str = "native") -> dict[str, str]:
        """Fetch path->checksum map for existing pages."""
        resp = requests.get(
            f"{self.base_url}/rest/v1/doc_pages",
            headers={**self.headers, "Prefer": ""},
            params={
                "select": "path,checksum",
                "version": f"eq.{version}",
                "source": f"eq.{source}",
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
                f"{self.base_url}/rest/v1/doc_pages?on_conflict=path,version,source",
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

    def delete_removed_pages(self, version: str, valid_paths: set[str], source: str = "native") -> int:
        """Delete pages that no longer exist in the content directory."""
        existing = self.get_existing_checksums(version, source)
        to_delete = [p for p in existing if p not in valid_paths]
        if not to_delete:
            return 0

        for path in to_delete:
            resp = requests.delete(
                f"{self.base_url}/rest/v1/doc_pages",
                headers=self.headers,
                params={
                    "path": f"eq.{path}",
                    "version": f"eq.{version}",
                    "source": f"eq.{source}",
                },
            )
            resp.raise_for_status()

        print(f"  Deleted {len(to_delete)} removed pages")
        return len(to_delete)

    def get_pages_summary(self, version: str, source: str = "native") -> list[dict]:
        """Fetch path, checksum, title for a version (used by changelog)."""
        all_rows = []
        offset = 0
        limit = 1000
        while True:
            resp = requests.get(
                f"{self.base_url}/rest/v1/doc_pages",
                headers={**self.headers, "Prefer": ""},
                params={
                    "select": "path,checksum,title",
                    "version": f"eq.{version}",
                    "source": f"eq.{source}",
                    "limit": str(limit),
                    "offset": str(offset),
                },
            )
            resp.raise_for_status()
            rows = resp.json()
            all_rows.extend(rows)
            if len(rows) < limit:
                break
            offset += limit
        return all_rows

    def upsert_changelog(self, entries: list[dict]) -> int:
        """Upsert changelog entries in batches."""
        count = 0
        for i in range(0, len(entries), SUPABASE_BATCH_SIZE):
            batch = entries[i : i + SUPABASE_BATCH_SIZE]
            resp = requests.post(
                f"{self.base_url}/rest/v1/doc_changelog?on_conflict=path,source,version_from,version_to",
                headers={
                    **self.headers,
                    "Prefer": "resolution=merge-duplicates,return=minimal",
                },
                json=batch,
            )
            resp.raise_for_status()
            count += len(batch)
        return count

    def clear_changelog(self, version_from: str, version_to: str) -> None:
        """Delete existing changelog for a version pair before rebuilding."""
        resp = requests.delete(
            f"{self.base_url}/rest/v1/doc_changelog",
            headers=self.headers,
            params={
                "version_from": f"eq.{version_from}",
                "version_to": f"eq.{version_to}",
            },
        )
        resp.raise_for_status()

    def upsert_oca_repos(self, repos: list[dict]) -> int:
        """Upsert OCA repo registry entries."""
        count = 0
        for i in range(0, len(repos), SUPABASE_BATCH_SIZE):
            batch = repos[i : i + SUPABASE_BATCH_SIZE]
            resp = requests.post(
                f"{self.base_url}/rest/v1/oca_repos?on_conflict=repo_name",
                headers={
                    **self.headers,
                    "Prefer": "resolution=merge-duplicates,return=minimal",
                },
                json=batch,
            )
            resp.raise_for_status()
            count += len(batch)
        return count
