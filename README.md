# Odoo Documentation — Scalizer Fork

Fork de [`odoo/documentation`](https://github.com/odoo/documentation) maintenu par [Scalizer](https://www.scalizer.fr) pour alimenter un **MCP Server** rendant la documentation Odoo accessible depuis claude.ai.

## Architecture

```
GitHub (ce repo)          Supabase                   n8n MCP Server       claude.ai
┌─────────────────┐      ┌──────────────────────┐   ┌──────────────┐    ┌─────────┐
│ 19.0 (RST docs) │─────→│ doc_pages + pgvector  │──→│ search_docs  │───→│         │
│                 │      │ Edge Fn: search-docs  │   │ get_page     │    │ Claude  │
│ GitHub Actions  │      │ RPC: get_page         │   │ list_modules │    │         │
│ (build + sync)  │      │ RPC: list_modules     │   │ list_pages   │    │         │
└─────────────────┘      │ RPC: list_pages       │   └──────────────┘    └─────────┘
                         └──────────────────────┘
```

## Fonctionnement

1. **Indexation** : `scripts/build_index.py` parcourt `content/`, génère des embeddings via OpenAI (`text-embedding-3-small`), et stocke tout dans Supabase (métadonnées + contenu RST + vecteurs)
2. **Recherche hybride** : L'Edge Function `search-docs` combine similarité vectorielle (70%) et full-text PostgreSQL (30%) pour des résultats pertinents
3. **Sync upstream** : GitHub Action hebdomadaire pour rester synchronisé avec `odoo/documentation`
4. **MCP Server** : Workflow n8n exposant 4 outils via le protocole MCP :
   - `search_docs` — Recherche hybride sémantique + full-text
   - `get_page` — Récupère le contenu RST complet d'une page
   - `list_modules` — Liste l'arbre des modules
   - `list_pages` — Liste les pages d'un module

## Développement local

```bash
# Pré-requis : Python 3.10+
pip install -r scripts/requirements.txt

# Variables d'environnement requises
export SUPABASE_URL="https://miymrcgruoooygmcsthl.supabase.co"
export SUPABASE_SERVICE_KEY="..."
export OPENAI_API_KEY="..."

# Dry run (vérifie le parsing sans appels API)
python scripts/build_index.py --version 19.0 --content-dir content --dry-run

# Indexation complète
python scripts/build_index.py --version 19.0 --content-dir content

# Avec export JSON en backup
python scripts/build_index.py --version 19.0 --content-dir content --json-output index-19.0.json
```

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| Documentation source | RST (reStructuredText) |
| Stockage & recherche | Supabase (PostgreSQL + pgvector) |
| Embeddings | OpenAI text-embedding-3-small (1536 dim) |
| Recherche hybride | 70% similarité cosinus + 30% ts_rank full-text |
| MCP Server | n8n workflow |
| CI/CD | GitHub Actions |

## V2 (roadmap)

- Multi-version : branches 16.0, 17.0, 18.0
- Recherche FR-aware : tokenisation française
- Analytics des requêtes
- Changelog : diff entre versions pour un module donné

## Licence

La documentation Odoo est sous [Creative Commons Attribution-NonCommercial-ShareAlike 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/).
