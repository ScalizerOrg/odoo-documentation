# Odoo Documentation - Scalizer Fork (V2)

## Purpose
Fork of `odoo/documentation` used by Scalizer to provide Odoo documentation access via MCP Server (n8n → claude.ai), powered by Supabase vector search. **V2 supports 10 versions (V10→V19) + OCA modules.**

## Architecture
```
GitHub (main: scripts, 10.0-19.0: content)
        ↓
build_index.py → Supabase (pgvector + Voyage AI embeddings)
index_oca.py   → doc_pages table (native + OCA)
build_changelog.py → doc_changelog table
        ↓
Edge Functions: search-docs, check-native-or-oca
RPC: search_docs, get_page, list_modules, list_pages, get_changelog, check_native_or_oca
        ↓
n8n MCP Server (6 tools) → claude.ai
```

## Structure
- `content/` — RST documentation files (from upstream odoo/documentation, on version branches)
- `scripts/build_index.py` — Indexes native RST into Supabase with Voyage AI embeddings
- `scripts/index_oca.py` — Indexes OCA modules (shallow clones + manifest/README parsing)
- `scripts/build_changelog.py` — Builds inter-version changelog (added/removed/modified/renamed)
- `scripts/oca_repos.json` — Curated list of ~82 OCA repositories
- `scripts/lib/` — Shared modules (rst_parser, oca_parser, supabase_client, voyage_client)
- `scripts/requirements.txt` — Python dependencies (requests)
- `.github/workflows/build-index.yml` — CI: matrix build (native + OCA + changelog)
- `.github/workflows/sync-upstream.yml` — CI: weekly sync from odoo/documentation (10 branches)

## Key Decisions
- RST format kept as-is (Claude reads it natively, directives are useful)
- Hybrid search: pgvector semantic + PostgreSQL full-text (weighted 70/30)
- Embeddings: Voyage AI voyage-3 (1024 dimensions)
- Checksum-based diffing: only re-embeds changed pages (saves API costs)
- Multi-version: scripts on `main` branch, content on version branches (10.0-19.0)
- OCA: README + manifest description, curated ~82 repos, shallow clones
- Changelog: auto-generated between consecutive versions (path-based diffing)
- Unique constraint: (path, version, source) — supports same page across versions

## Environment Variables (for CI and local)
```
SUPABASE_URL=https://miymrcgruoooygmcsthl.supabase.co
SUPABASE_SERVICE_KEY=<service_role_key>
VOYAGE_API_KEY=<voyage_ai_key>
```

## Scripts
```bash
# Install deps
pip install -r scripts/requirements.txt

# Native indexation (single version)
python scripts/build_index.py --version 19.0 --content-dir content

# OCA indexation (single version)
python scripts/index_oca.py --version 17.0 --repos-file scripts/oca_repos.json

# Changelog (all version pairs)
python scripts/build_changelog.py --all-versions --source native

# Dry run (any script)
python scripts/build_index.py --version 19.0 --content-dir content --dry-run
```

## Supabase Project
- ID: `miymrcgruoooygmcsthl`
- Region: eu-west-3
- Tables: `doc_pages` (pgvector), `doc_changelog`, `oca_repos`
- Edge Functions: `search-docs` (v4), `check-native-or-oca` (v1)
- RPC Functions: `search_docs`, `get_page`, `list_modules`, `list_pages`, `get_changelog`, `check_native_or_oca`

## n8n MCP Server
- Workflow ID: `gQUFtW3wEoIwVXe3`
- MCP path: `/mcp/doc-odoo` (SSE, no auth on trigger)
- 6 tools: search_docs, get_page, list_modules, list_pages, get_changelog, check_native_or_oca
- All tools accept `version` parameter (REQUIRED in descriptions)
