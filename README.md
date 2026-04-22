# Odoo Documentation - Scalizer Fork

Fork of [odoo/documentation](https://github.com/odoo/documentation) used by Scalizer to provide Odoo documentation access via MCP Server (n8n → claude.ai).

## Branch structure

| Branch | Content |
|--------|---------|
| `main` | Scripts, CI/CD workflows, configuration |
| `10.0` - `19.0` | RST documentation (synced from upstream) |

## Features (V2)

- **Multi-version**: 10 Odoo versions (10.0 → 19.0)
- **OCA modules**: ~82 curated OCA repos indexed
- **Changelog**: Auto-generated diffs between consecutive versions
- **Native vs OCA**: Check if a feature is native Odoo or community
- **Hybrid search**: pgvector semantic (70%) + PostgreSQL full-text (30%)
- **MCP Server**: 6 tools accessible from claude.ai via n8n

## Quick start

```bash
pip install -r scripts/requirements.txt

# Index native docs (requires SUPABASE_URL, SUPABASE_SERVICE_KEY, VOYAGE_API_KEY)
python scripts/build_index.py --version 19.0 --content-dir content

# Index OCA modules
python scripts/index_oca.py --version 17.0

# Build changelog
python scripts/build_changelog.py --all-versions
```

See [CLAUDE.md](CLAUDE.md) for full architecture documentation.
