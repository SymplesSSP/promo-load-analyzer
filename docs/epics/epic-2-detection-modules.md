# Epic 2: Detection Modules (Page & Promo)

**Status:** Not Started
**Priority:** HIGH
**Estimated Effort:** 3-4 days
**Dependencies:** Epic 1

---

## Objectif

Implémenter les modules de détection de type de page et de scraping de promotions pour extraire automatiquement les informations nécessaires à l'analyse.

## Scope

### Included
- Module `page_detector.py` avec détection par regex et DOM
- Module `promo_scraper.py` avec Playwright
- Module `prestashop_api.py` (optionnel)
- Modèles Pydantic pour les données détectées
- Tests unitaires et d'intégration
- Constants pour patterns et seuils

### Excluded
- Génération K6 (Epic 3)
- Scoring et analyse (Epic 4)
- Interface Claude Code (Epic 4)

---

## User Stories

### Story 2.1: Create Data Models
**As a** developer
**I want** Pydantic models for page detection and promotions
**So that** data is validated automatically

**Acceptance Criteria:**
- `src/models/page_detection.py` created with `PageDetectionResult`
- `src/models/promotion.py` created with `PromotionData`, `StrikedPriceData`, `AutoCartRule`
- All fields have proper types and validation
- Models can serialize to/from JSON

**Technical Tasks:**
- Create PageDetectionResult model
- Create PromotionData and related models
- Add field validators
- Write model tests

**Estimated Effort:** 2-3 hours

---

### Story 2.2: Implement Page Detector (Regex)
**As a** system
**I want** to detect page type from URL patterns
**So that** I know which scraping strategy to use

**Acceptance Criteria:**
- Detects product pages: `/\d+-[\w-]+\.html`
- Detects homepage: `^https?://[^/]+/?$`
- Detects category: `/[\w-]+/\d+`
- Falls back to "landing" for unknown
- Extracts product IDs from URLs
- Returns PageDetectionResult

**Technical Tasks:**
- Create src/page_detector.py
- Implement regex patterns in constants.py
- Implement detect_page() function
- Handle edge cases (malformed URLs)
- Write unit tests (10+ test cases)

**Estimated Effort:** 3-4 hours

---

### Story 2.3: Implement Page Detector (DOM Fallback)
**As a** system
**I want** DOM-based detection for ambiguous URLs
**So that** all page types are correctly identified

**Acceptance Criteria:**
- Uses requests + BeautifulSoup for lightweight parsing
- Detects add-to-cart buttons
- Detects promo code inputs
- Timeout: 10 seconds
- Returns PageDetectionResult with detection_method="dom_analysis"

**Technical Tasks:**
- Add BeautifulSoup dependency
- Implement DOM analysis
- Handle HTTP errors gracefully
- Write integration tests (requires network)

**Estimated Effort:** 3-4 hours

---

### Story 2.4: Implement Promo Scraper (Striked Price)
**As a** system
**I want** to detect striked price promotions
**So that** I can estimate server impact

**Acceptance Criteria:**
- Detects `.regular-price` CSS selector
- Extracts regular and current prices
- Calculates discount percentage
- Sets complexity="LOW", impact=0.05
- Returns StrikedPriceData

**Technical Tasks:**
- Setup Playwright async
- Implement striked price detection
- Parse price strings to floats
- Handle multiple currencies
- Write tests with mock pages

**Estimated Effort:** 2-3 hours

---

### Story 2.5: Implement Promo Scraper (Auto Cart Rules)
**As a** system
**I want** to detect auto-applied cart rules
**So that** I can measure their performance impact

**Acceptance Criteria:**
- Simulates add-to-cart action
- Extracts `window.prestashop.cart.vouchers.added`
- Parses rule IDs, names, amounts
- Sets complexity="MEDIUM", impact=0.15 per rule
- Handles no vouchers case
- Timeout: 30 seconds

**Technical Tasks:**
- Implement add-to-cart simulation
- Extract JavaScript variables from page context
- Parse voucher data structure
- Handle Playwright timeouts
- Write integration tests with real PREPROD page

**Estimated Effort:** 4-5 hours

---

### Story 2.6: Implement Promo Scraper (Manual Code Input)
**As a** system
**I want** to detect manual promo code inputs
**So that** I know if manual codes are possible

**Acceptance Criteria:**
- Detects `input[name="discount_name"]`
- Sets has_manual_code_input = True
- Sets complexity="HIGH", impact=0.25 if present

**Technical Tasks:**
- Implement input detection
- Update PromotionData model
- Write tests

**Estimated Effort:** 1 hour

---

### Story 2.7: Implement Complexity Calculation
**As a** system
**I want** automatic complexity scoring
**So that** users understand promo difficulty

**Acceptance Criteria:**
- LOW: striked price only
- MEDIUM: 1 auto cart rule OR manual code
- HIGH: 2+ auto cart rules OR manual + auto
- Algorithm documented in code

**Technical Tasks:**
- Implement calculate_complexity()
- Implement estimate_server_impact()
- Write test cases for all scenarios

**Estimated Effort:** 2 hours

---

### Story 2.8: Implement PrestaShop API (Optional)
**As a** system
**I want** to enrich cart rule data from API
**So that** analysis is more accurate

**Acceptance Criteria:**
- Checks if API key configured
- Gracefully skips if not configured
- Calls GET /api/cart_rules/{id}
- Parses XML response
- Retry 2x with exponential backoff
- Timeout: 15 seconds total
- Enriches AutoCartRule objects

**Technical Tasks:**
- Create src/prestashop_api.py
- Implement API calls with requests
- Parse XML responses
- Implement retry logic
- Write tests with mocked API

**Estimated Effort:** 3-4 hours

---

### Story 2.9: Integration Testing
**As a** developer
**I want** integration tests with real PREPROD
**So that** scraping works in production

**Acceptance Criteria:**
- Tests run against preprod.ipln.fr
- Skip if network unavailable
- Test all page types
- Test all promo types
- Tests marked as @pytest.mark.integration

**Technical Tasks:**
- Create tests/integration/test_page_detector.py
- Create tests/integration/test_promo_scraper.py
- Document PREPROD test URLs
- Run and validate tests

**Estimated Effort:** 2-3 hours

---

## Definition of Done

- [ ] All data models created and validated
- [ ] Page detection works for all 4 types
- [ ] Promo scraping detects all 3 types
- [ ] Complexity calculation accurate
- [ ] PrestaShop API optional and working
- [ ] Unit tests >= 80% coverage
- [ ] Integration tests pass on PREPROD
- [ ] Code follows coding standards (ruff + mypy pass)
- [ ] Documentation in docstrings

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Playwright crashes | MEDIUM | Retry logic + finally blocks |
| PrestaShop DOM changes | HIGH | Flexible selectors + tests |
| Cloudflare blocks scraping | LOW | Use PREPROD for tests |
| API unavailable | LOW | Graceful degradation implemented |

---

## Notes

- Focus on PREPROD testing to avoid PROD impact
- Keep scraping fast (< 30s total per page)
- Document limitations (only visible promos detected)
