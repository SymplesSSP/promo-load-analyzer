# 🏗️ Architecture

## Vue simplifiée

```
USER (Marketing)
  │
  │ "Teste promo: https://ipln.fr/..."
  ▼
┌──────────────────────────────────┐
│      CLAUDE CODE                 │
│  1. Parse demande                │
│  2. Détermine paramètres         │
│  3. Execute main.py              │
│  4. Lit JSON results             │
│  5. Génère rapport markdown      │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│  PYTHON ANALYZER (main.py)       │
│  ┌────────────────────────────┐  │
│  │ Page Detector              │  │
│  │ └─> Type + IDs produit     │  │
│  └────────────────────────────┘  │
│  ┌────────────────────────────┐  │
│  │ Promo Scraper (Playwright) │  │
│  │ └─> Prix barré / Codes auto│  │
│  └────────────────────────────┘  │
│  ┌────────────────────────────┐  │
│  │ API PrestaShop (opt.)      │  │
│  │ └─> Détails cart rules     │  │
│  └────────────────────────────┘  │
│  ┌────────────────────────────┐  │
│  │ K6 Generator               │  │
│  │ └─> Template dynamique     │  │
│  └────────────────────────────┘  │
│  ┌────────────────────────────┐  │
│  │ K6 Executor                │  │
│  │ └─> Test charge            │  │
│  └────────────────────────────┘  │
│  ┌────────────────────────────┐  │
│  │ Results Analyzer           │  │
│  │ └─> Score + Max users      │  │
│  └────────────────────────────┘  │
└──────────────┬───────────────────┘
               │
               ▼
    /tmp/analysis_XXXXX.json
               │
               ▼
┌──────────────────────────────────┐
│  CLAUDE CODE                     │
│  Génération rapport markdown     │
│  + Recommandations               │
└──────────────┬───────────────────┘
               │
               ▼
       Rapport final (markdown)
```

## Stack

```yaml
Orchestration:
  - Claude Code CLI
  - Python 3.11+

Scraping:
  - Playwright (DOM + interactions)
  - Regex (URL patterns)
  - requests (API PrestaShop)

Load Testing:
  - k6 v0.47+

Infrastructure:
  - PrestaShop 1.7.8.5
  - OVH Scale 3/5
  - Cloudflare CDN
  - Cache Smarty
```

---
