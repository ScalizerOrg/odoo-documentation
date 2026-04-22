# Odoo Documentation - Scalizer Fork

## Purpose
Fork of `odoo/documentation` used by Scalizer to provide Odoo documentation access via MCP Server (n8n → claude.ai), powered by Supabase vector search.

## Architecture
```
GitHub (19.0 branch)  →  build_index.py  →  Supabase (pgvector + embeddings)
                                                    ↓
                                           Edge Function search-docs
                                           RPC: get_page, list_modules, list_pages
                                                    ↓
                                              n8n MCP Server → claude.ai
```

## Structure
- `content/` — RST documentation files (from upstream odoo/documentation)
- `scripts/build_index.py` — Indexes RST into Supabase with OpenAI embeddings
- `scripts/requirements.txt` — Python dependencies (openai, requests)
- `.github/workflows/build-index.yml` — CI: builds index on push/schedule
- `.github/workflows/sync-upstream.yml` — CI: weekly sync from odoo/documentation

## Key Decisions
- RST format kept as-is (Claude reads it natively, directives are useful)
- Hybrid search: pgvector semantic + PostgreSQL full-text (weighted 70/30)
- Embeddings: OpenAI text-embedding-3-small (1536 dimensions)
- Checksum-based diffing: only re-embeds changed pages (saves API costs)
- Excluded from index: images, locale/, extensions/, redirects/, static/, tests/

## Environment Variables (for CI and local)
```
SUPABASE_URL=https://miymrcgruoooygmcsthl.supabase.co
SUPABASE_SERVICE_KEY=<service_role_key>
OPENAI_API_KEY=<openai_key>
```

## Scripts
```bash
# Install deps
pip install -r scripts/requirements.txt

# Dry run (parse only, no Supabase/OpenAI calls)
python scripts/build_index.py --version 19.0 --content-dir content --dry-run

# Full indexation
python scripts/build_index.py --version 19.0 --content-dir content

# With JSON backup
python scripts/build_index.py --version 19.0 --content-dir content --json-output index-19.0.json
```

## Supabase Project
- ID: `miymrcgruoooygmcsthl`
- Region: eu-west-3
- Table: `doc_pages` (with pgvector embeddings)
- Edge Function: `search-docs` (hybrid search with query embedding)
- RPC Functions: `get_page`, `list_modules`, `list_pages`
