# Odoo Documentation - Scalizer Fork (V3)

## Purpose
Fork of `odoo/documentation` used by Scalizer to provide Odoo documentation access via MCP Server (n8n → claude.ai), powered by Supabase vector search. **V3: enhanced RAG quality — weighted FTS, 12K embeddings, chunking, enriched keywords.**

## Architecture
```
GitHub (main: scripts, 10.0-19.0: content)
        ↓
build_index.py → Supabase (pgvector + Voyage AI embeddings)
index_oca.py   → doc_pages table (native + OCA, with chunking)
build_changelog.py → doc_changelog table
        ↓
Edge Functions: search-docs (v5), check-native-or-oca (v2)
RPC: search_docs (v3), get_page (v2), list_modules, list_pages, get_changelog, check_native_or_oca
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
- `scripts/edge-functions/` — Edge Function source code (versioned in repo)
- `scripts/requirements.txt` — Python dependencies (requests)
- `SKILLS/doc-odoo/SKILL.md` — Skill definition for claude.ai (reformulation FR→EN, fallback, cross-ref)
- `.github/workflows/build-index.yml` — CI: matrix build (native + OCA + changelog)
- `.github/workflows/sync-upstream.yml` — CI: weekly sync from odoo/documentation (10 branches)

## Key Decisions
- RST format kept as-is (Claude reads it natively, directives are useful)
- Hybrid search: pgvector semantic + PostgreSQL full-text (weighted 70/30)
- **FTS: weighted tsvector** — title/keywords (A), summary/preview (B), full content (D)
- Embeddings: Voyage AI voyage-3 (1024 dimensions), **12K chars** (was 4K)
- **Chunking**: pages > 12K cleaned chars are split by RST sections, deduplicated in search
- **Keywords enriched**: RST headings, bold text, :ref:/:doc: cross-refs, OCA depends/category
- **Similarity threshold**: 0.25 minimum cosine similarity in search results
- **Title boost**: +0.1 score when query matches title (ILIKE)
- Checksum-based diffing: only re-embeds changed pages (saves API costs)
- Multi-version: scripts on `main` branch, content on version branches (10.0-19.0)
- OCA: README + manifest description, curated ~82 repos, shallow clones, MIN_DOC_CHARS=250
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
- Tables: `doc_pages` (pgvector + parent_path/chunk_index), `doc_changelog`, `oca_repos`
- Edge Functions: `search-docs` (v5), `check-native-or-oca` (v2)
- RPC Functions: `search_docs` (v3), `get_page` (v2), `list_modules`, `list_pages`, `get_changelog`, `check_native_or_oca`

## n8n MCP Server
- Workflow ID: `gQUFtW3wEoIwVXe3`
- MCP path: `/mcp/doc-odoo` (SSE, no auth on trigger)
- 6 tools: search_docs, get_page, list_modules, list_pages, get_changelog, check_native_or_oca
- All tools accept `version` parameter (REQUIRED in descriptions)

## V3 Changes Summary
1. **FTS Content-Aware**: weighted tsvector indexing full page content (A/B/D weights)
2. **Embedding 12K chars**: 3x more content embedded per page (was 4K)
3. **Keywords enriched**: headings, bold, cross-refs, OCA depends/category (~8-15 keywords/page vs 2-3)
4. **Chunking**: long pages (>12K chars) split into section-based chunks with deduplication
5. **Search quality**: similarity threshold 0.25, title boost +0.1, chunk deduplication
6. **Preview 500 chars**: edge functions return 500 chars (was 300)
7. **Skill file**: SKILLS/doc-odoo/SKILL.md with 30+ FR→EN reformulations and fallback patterns
8. **Edge functions in repo**: source code versioned in scripts/edge-functions/
9. **OCA quality**: MIN_DOC_CHARS raised to 250 (filters low-quality entries)
