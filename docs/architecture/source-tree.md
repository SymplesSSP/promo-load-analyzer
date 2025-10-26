# Source Tree

```
promo-load-analyzer/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
│
├── src/
│   ├── main.py
│   ├── models/
│   │   ├── page_detection.py
│   │   ├── promotion.py
│   │   ├── k6_config.py
│   │   ├── k6_results.py
│   │   └── analysis_report.py
│   ├── page_detector.py
│   ├── promo_scraper.py
│   ├── prestashop_api.py
│   ├── k6_generator.py
│   ├── k6_executor.py
│   ├── results_analyzer.py
│   ├── config.py
│   ├── constants.py
│   └── utils/
│       ├── logger.py
│       ├── validators.py
│       └── file_utils.py
│
├── templates/
│   ├── base.js.j2
│   ├── template_product.js.j2
│   ├── template_homepage.js.j2
│   ├── template_category.js.j2
│   └── template_landing.js.j2
│
├── tests/
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── scripts/
│   ├── check_dependencies.sh
│   ├── setup_dev.sh
│   └── run_tests.sh
│
└── docs/
    ├── prd.md
    ├── architecture.md
    ├── prd/
    ├── architecture/
    ├── epics/
    ├── stories/
    └── qa/
```

---
