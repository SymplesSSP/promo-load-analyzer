# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Recent Changes & Fixes (2025-10-27)

### Critical Bug Fixes Deployed
1. **K6 Metrics Parsing** - Added `--summary-export` flag to properly extract aggregated metrics
2. **K6 Staging Config** - Fixed 0-minute sustain phase for short duration tests (≤2 min)
3. **Promo Cart Detection** - Implemented active polling and multi-strategy clicking for reliable detection
4. **Page Type Detection** - Updated regex to support modern PrestaShop URLs without .html extension
5. **Percentage Parsing** - Fixed parsing of discount strings like "15%" and amounts like 399.996

### Current Status
- ✅ **229/229 unit tests passing** (100%)
- ✅ **Validated on production** (ipln.fr)
- ✅ **SONY GM-1 promo detected** correctly (300€ auto cart rule)
- ✅ **Grade A performance** (97.1/100) on full test with cart
- ✅ **README enhanced** with GitHub-standard styling and badges

## Project Overview

**Promo Load Analyzer** - Automated load testing tool for PrestaShop promotional campaigns, orchestrated by Claude Code via natural language interface.

**Target Platform:** PrestaShop 1.7.8.5 (ipln.fr)
**Primary Users:** Marketing team (non-technical) + Technical team
**Deadline:** < 2 weeks before Black Friday 2025

### Purpose
Marketing needs to understand the performance impact of promotional campaigns without technical knowledge. This tool:
1. Accepts URL in natural language from users
2. Auto-detects page type and active promotions
3. Runs adaptive K6 load tests
4. Returns simple A-F scores with actionable recommendations

### Business Context
- **Problem:** Risk of server crashes during Black Friday due to poorly optimized promotions
- **Solution:** Pre-test promotions to identify performance bottlenecks
- **ROI:** Prevent outages, optimize promos, identify max server capacity

## Project Architecture

### High-Level Flow
```
User (via Claude Code) → Python Analyzer (main.py) → K6 Load Tests → Results Analysis → Markdown Report
```

### Core Components (to be implemented)

1. **Page Detector** (`page_detector.py`)
   - Identifies page type: product, homepage, category, landing
   - Extracts metadata: product IDs, URLs, cart elements
   - Output: JSON with page classification

2. **Promo Scraper** (`promo_scraper.py`)
   - Uses Playwright to detect 3 promo types:
     - Striked prices (CSS `.regular-price`) - LOW impact ~5%
     - Auto cart rules (via `window.prestashop.cart.vouchers.added`) - MEDIUM impact ~15%
     - Manual codes (input `[name="discount_name"]`) - HIGH impact ~25%
   - Simulates add-to-cart to trigger auto-apply rules
   - Output: JSON with promo types and estimated server impact

3. **PrestaShop API** (`prestashop_api.py`) - OPTIONAL
   - Enriches cart rule data via PrestaShop webservice API
   - Endpoints: `/api/cart_rules`
   - Requires read-only API key from BO

4. **K6 Generator** (`k6_generator.py`)
   - Dynamically generates K6 scripts from templates
   - 4 templates: product, homepage, category, landing
   - Injects parameters: VUs, duration, URLs, product IDs, mode

5. **K6 Executor** (within `main.py`)
   - Runs: `k6 run --out json=/tmp/results.json script.js`
   - Collects metrics: p95, error rate, VUs, iterations

6. **Results Analyzer** (within `main.py`)
   - Parses K6 JSON output
   - Calculates composite score: 60% response time + 40% error rate
   - Assigns grade A-F based on web performance standards
   - Estimates max concurrent users (p95 threshold > 2000ms)

### Project Structure (to create)
```
promo-load-analyzer/
├── main.py                 # Entry point, orchestrates all components
├── page_detector.py        # Page type detection
├── promo_scraper.py        # Promotion scraping with Playwright
├── prestashop_api.py       # Optional API enrichment
├── k6_generator.py         # K6 script generator
├── results_analyzer.py     # Score calculation and reporting
├── requirements.txt        # Python dependencies
├── .env                    # Configuration (API keys, URLs)
├── templates/
│   ├── template_product.js     # Product page K6 template
│   ├── template_homepage.js    # Homepage K6 template
│   ├── template_category.js    # Category K6 template
│   └── template_landing.js     # Landing page K6 template
└── README.md
```

## Critical Constraints

### Production Testing Rules (STRICTLY ENFORCED)
- **Timing:** Tests only allowed 3h-6h AM (server time)
- **VUs:** Max 50 virtual users without Cloudflare whitelist
- **Mode:** `read_only` (GET only) by default in PROD
- **Protection:** Must validate time window before execution

### Environment Detection
- `ipln.fr` → PROD (strict limits apply)
- `preprod.ipln.fr` or other → PREPROD (no limits)

### Test Intensity Levels
| Intensity | VUs | Duration | Use Case |
|-----------|-----|----------|----------|
| light     | 50  | 2min     | Quick validation, PROD safe |
| medium    | 200 | 5min     | Realistic test (default) |
| heavy     | 500 | 10min    | Stress test (PREPROD only) |

### Cloudflare Rate Limiting
- Default: 50-100 VUs/IP before rate limiting
- Solution: Whitelist IP in Cloudflare or use PREPROD

## K6 Safety Mechanisms

**CRITICAL:** K6 has NO automatic circuit breaker. All protections must be configured explicitly via `thresholds` with `abortOnFail: true`.

### Mandatory Thresholds (all K6 scripts)

```javascript
thresholds: {
    // Protection 1: Error rate
    'http_req_failed': [{
        threshold: 'rate<0.10',      // Max 10% errors
        abortOnFail: true,           // Stop test immediately
        delayAbortEval: '10s'        // After 10s stabilization
    }],

    // Protection 2: Server degradation
    'http_req_duration': [{
        threshold: 'p(95)<5000',     // p95 < 5s
        abortOnFail: true
    }],

    // Protection 3: Health checks
    'checks': [{
        threshold: 'rate>0.80',      // Min 80% checks pass
        abortOnFail: true,
        delayAbortEval: '10s'
    }],

    // Alert only (no abort)
    'http_req_duration': [{
        threshold: 'p(95)<2000',     // p95 < 2s
        abortOnFail: false           // Continue but flag
    }]
}
```

### PROD vs PREPROD Thresholds
- **PROD:** Stricter (rate<0.05, p95<3000ms)
- **PREPROD:** Standard (rate<0.10, p95<5000ms)

### Emergency Stop Procedures
1. **Graceful:** Ctrl+C (5-30s, exports metrics)
2. **Immediate:** Double Ctrl+C (instant kill)
3. **Remote:** K6 REST API if running in server mode
4. **Automatic:** Thresholds trigger abort if exceeded

## Scoring System

### Response Time Grades (p95)
- A (Excellent): < 1000ms
- B (Good): 1000-2000ms
- C (Acceptable): 2000-3000ms
- D (Slow): 3000-5000ms
- F (Critical): > 5000ms

### Error Rate Grades
- A: < 0.1%
- B: 0.1-1%
- C: 1-5%
- D: 5-10%
- F: > 10%

### Global Score Calculation
```python
score = (score_response * 0.6) + (score_error * 0.4)
```

### Max Users Detection (MVP)
- Conservative estimation via linear extrapolation
- Threshold: p95 > 2000ms with -20% safety margin
- Phase 2: More precise detection via curve analysis

## Development Commands

### Setup
```bash
# Install Python dependencies
pip install playwright requests python-dotenv

# Install K6
brew install k6          # macOS
# or: apt install k6     # Linux

# Install Playwright browsers
playwright install chromium
```

### Run Analysis (CLI)
```bash
python main.py \
  --url "https://ipln.fr/promo/bf2025" \
  --env prod \
  --intensity medium \
  --mode read_only
```

### Run via Claude Code (Natural Language)
```
"Test this Black Friday promo: https://ipln.fr/promo/bf2025"
"Quick test, medium load"
```

### Configuration (.env)
```bash
PRESTASHOP_API_KEY=xxx                    # Optional
PRESTASHOP_BASE_URL=https://ipln.fr
MAX_USERS_DEFAULT=200
K6_OUTPUT_DIR=/tmp/k6_results
```

## Output Format

The tool generates a **markdown report** with:
- **Executive summary:** Score A-F, max capacity, warnings
- **Detailed scores:** Performance, error rate, promo impact
- **Server capacity:** Max concurrent users estimation
- **Detected promotions:** Types, complexity, server overhead
- **Actionable recommendations:** Prioritized (HIGH/MEDIUM/LOW) with effort estimates
- **Black Friday plan:** Timeline with specific tasks
- **Glossary:** Non-technical explanations for marketing

See PRD lines 846-980 for full example report.

## Implementation Phases

### Phase 1 - MVP (< 2 weeks, CURRENT)
- Page detection (product/homepage/landing)
- Promo scraping (3 types)
- Dynamic K6 generation with safety thresholds
- Automated scoring
- Claude Code integration
- Validation tests

### Phase 2 - Post Black Friday
- Real-time dashboard (InfluxDB + Grafana)
- Dashboard emergency stop button
- Category support with filters
- Automatic peak detection
- Slack alerts
- Historical comparison

### Phase 3 - 2026
- ML capacity prediction
- Automatic optimizations
- Multi-region testing
- CI/CD integration

## Key Implementation Notes

### Page Type Detection Strategy
Use regex patterns on URLs:
- Product: `/\d+-[\w-]+\.html`
- Homepage: `^https?://[^/]+/?$`
- Category: `/[\w-]+/\d+`
- Landing: Fallback (DOM analysis)

### Promo Detection Strategy
1. **Striked Price:** Look for `.regular-price` CSS selector
2. **Auto Cart Rules:**
   - Playwright: navigate to page
   - **Wait 1s for page stabilization** (critical for success)
   - Simulate add-to-cart with **3-level fallback**: normal click → force click → JavaScript click
   - Wait for cart modal `#blockcart-modal` (optional, non-blocking)
   - **Poll cart state** every 500ms for max 15s (instead of fixed 5s timeout)
   - Extract `window.prestashop.cart.vouchers.added` from page context
   - Handles both dict `{"id": {voucher}}` and array formats
   - Parses percentage strings like "15%" and numeric values
3. **Manual Codes:** Detect input `[name="discount_name"]`

**Critical fixes (2025-10-27):**
- Added 1s stabilization delay before clicking add-to-cart (prevents click failures)
- Implemented active polling instead of fixed timeout (handles variable AJAX response times)
- Added multiple click strategies to handle overlays and disabled buttons
- Improved amount parsing to handle both "15%" strings and numeric 399.996 values

### K6 Template Variables (inject dynamically)
- `{target_users}`: 50/200/500
- `{duration}`: 2min/5min/10min
- `{url}`: Target URL
- `{id_product}`, `{id_attr}`: Product identifiers
- `{mode}`: read_only vs full (with POST add-to-cart)

### Limitations to Communicate
1. Only detects immediately visible/applicable promos
2. Cannot test complex conditions (e.g., cart > 1000€)
3. Max users = conservative estimate in MVP
4. Cloudflare rate limiting without IP whitelist
5. PROD tests limited to 3h-6h window

## Known Issues & Troubleshooting

### Issue: "Cart not updated after add-to-cart click"
**Symptoms:** Auto cart rules not detected, warning in logs
**Root Cause:** AJAX response takes longer than expected, page not fully stabilized
**Solution:**
- Tool now waits 1s for page stabilization before clicking
- Implements active polling (500ms × 30 attempts = 15s max)
- Uses 3-level click fallback (normal → force → JavaScript)

### Issue: "No striked price found" when promotion is visible
**Symptoms:** Promo badge visible (e.g., "-300€") but not detected
**Root Cause:** Badge promos use different HTML structure than striked prices
**Current Status:** Badge promos require cart rules detection (add-to-cart simulation)
**Workaround:** Use `--mode full` to trigger cart rules detection

### Issue: Playwright "Target page closed" error
**Symptoms:** Immediate crash on macOS Sequoia
**Root Cause:** Outdated Playwright version (< 1.55)
**Solution:** Update to Playwright 1.55+ and reinstall browsers
```bash
pip install playwright==1.55.0
playwright install chromium
```

### Issue: K6 returns 0 iterations despite success
**Symptoms:** Test completes but metrics show 0 requests/iterations
**Root Cause:** K6 `--out json` only outputs Points, not aggregated metrics
**Solution:** Tool now uses `--summary-export` flag for proper metrics parsing

## Technology Stack

- **Orchestration:** Claude Code CLI, Python 3.11+
- **Web Scraping:** Playwright (headless Chromium), regex
- **API:** requests (optional PrestaShop API)
- **Load Testing:** k6 v0.47+
- **Target Platform:** PrestaShop 1.7.8.5
- **Infrastructure:** OVH Scale 3/5, Cloudflare CDN + WAF, Smarty cache

## References

See PRD-Promo-Load-Analyzer-v2.md (full specification document) for:
- Detailed technical specifications
- Complete workflow diagrams
- Business requirements
- Risk analysis
- Support information
