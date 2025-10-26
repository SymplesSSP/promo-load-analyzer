# 🚀 Déploiement

## Prérequis

```bash
# Python 3.11+
pip install playwright requests

# K6
brew install k6  # macOS
# ou apt install k6

# Playwright browsers
playwright install chromium
```

## Structure

```
promo-load-analyzer/
├── main.py                 # Entry point Claude Code
├── page_detector.py        # Détection type page
├── promo_scraper.py        # Scraping promotions
├── prestashop_api.py       # API PrestaShop (opt.)
├── k6_generator.py         # Générateur scripts
├── requirements.txt        # Dépendances
├── templates/
│   ├── template_product.js
│   ├── template_homepage.js
│   ├── template_category.js
│   └── template_landing.js
└── .env
    └── PRESTASHOP_API_KEY  # Optionnel
```

## Configuration

```bash
# .env
PRESTASHOP_API_KEY=xxx              # Optionnel
PRESTASHOP_BASE_URL=https://ipln.fr
MAX_USERS_DEFAULT=200
K6_OUTPUT_DIR=/tmp/k6_results
```

## Activation API PrestaShop (optionnel)

```
BO → Paramètres avancés → Webservice
├─> Activer webservice
├─> Créer clé API
│   ├─> Nom: "Load Testing"
│   ├─> Permissions: cart_rules (GET)
│   └─> Générer
└─> Copier clé dans .env
```

---
