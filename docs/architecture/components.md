# Components

## main.py (Orchestrator)
- CLI entry point and pipeline orchestration
- Validates PROD constraints (time window, VUs)
- Executes sequential pipeline
- Handles exceptions and generates exit codes
- Writes final JSON output

## page_detector.py
- Detects page type via regex patterns or DOM analysis
- Extracts product IDs and metadata
- Uses requests + BeautifulSoup for lightweight parsing

## promo_scraper.py
- Scrapes promotions using Playwright headless browser
- Detects striked prices, auto cart rules, manual code inputs
- Simulates add-to-cart to trigger auto-apply rules
- Calculates complexity (LOW/MEDIUM/HIGH) and server impact

## prestashop_api.py (Optional)
- Enriches cart rule data via PrestaShop Webservice API
- HTTP Basic Auth with API key
- Graceful degradation if API unavailable
- Retry logic with exponential backoff

## k6_generator.py
- Generates K6 JavaScript scripts from Jinja2 templates
- Selects appropriate template based on page type
- Injects test parameters (VUs, duration, thresholds)
- Applies environment-specific thresholds (PROD strict, PREPROD standard)

## k6_executor.py
- Executes K6 binary via subprocess
- Parses NDJSON output
- Detects threshold aborts (exit code 99 = expected, not error)
- Handles K6 not installed gracefully

## results_analyzer.py
- Calculates performance scores (response time + error rate)
- Assigns A-F grades based on web performance standards
- Estimates max concurrent users capacity
- Generates prioritized recommendations

---
