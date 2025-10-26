# Epic 3: K6 Generation & Execution

**Status:** Not Started
**Priority:** HIGH
**Estimated Effort:** 3-4 days
**Dependencies:** Epic 2

---

## Objectif

Générer dynamiquement des scripts K6 avec protections de sécurité et exécuter les tests de charge en collectant les métriques.

## Scope

### Included
- 4 templates K6 Jinja2 (product, homepage, category, landing)
- Module `k6_generator.py` pour génération dynamique
- Module `k6_executor.py` pour exécution
- Modèles Pydantic pour config K6 et résultats
- Thresholds de sécurité PROD vs PREPROD
- Parsing JSON NDJSON de K6

### Excluded
- Analyse des résultats (Epic 4)
- Validation PROD (Epic 5)
- Dashboard temps réel (Phase 2)

---

## User Stories

### Story 3.1: Create K6 Config Model
**As a** developer
**I want** a validated K6 configuration model
**So that** invalid configs are caught early

**Acceptance Criteria:**
- `src/models/k6_config.py` created with `K6TestConfig`
- Fields: target_url, environment, intensity, test_mode, max_vus, duration_seconds
- Validation: environment in [prod, preprod], intensity in [light, medium, heavy]
- Model includes page_metadata and promo_data

**Technical Tasks:**
- Create K6TestConfig Pydantic model
- Add field validators
- Write model tests

**Estimated Effort:** 1-2 hours

---

### Story 3.2: Create K6 Results Model
**As a** developer
**I want** a model for K6 results
**So that** parsing is type-safe

**Acceptance Criteria:**
- `src/models/k6_results.py` created with `K6Results`
- Fields: http_req_duration_p95, http_req_failed_rate, vus_max, iterations_total, test_aborted, abort_reason
- Can deserialize from K6 JSON format

**Technical Tasks:**
- Create K6Results model
- Add parsing helpers
- Write tests with sample K6 JSON

**Estimated Effort:** 1-2 hours

---

### Story 3.3: Create Base K6 Template
**As a** developer
**I want** a base K6 template with safety thresholds
**So that** all tests have PROD protection

**Acceptance Criteria:**
- `templates/base.js.j2` created
- Includes mandatory thresholds (http_req_failed, http_req_duration, checks)
- Variables: {{error_rate_threshold}}, {{p95_threshold}}, {{p99_threshold}}
- PROD thresholds: rate<0.05, p95<3000ms
- PREPROD thresholds: rate<0.10, p95<5000ms
- All thresholds have abortOnFail: true

**Technical Tasks:**
- Create base template
- Document threshold rationale
- Test template renders correctly

**Estimated Effort:** 2-3 hours

---

### Story 3.4: Create Product Page Template
**As a** system
**I want** a K6 template for product pages
**So that** product tests simulate real user behavior

**Acceptance Criteria:**
- `templates/template_product.js.j2` created
- Extends base template
- GET product page
- POST add-to-cart (if mode=full)
- Checks: page loads, status 200, no 5xx errors
- Variables: {{url}}, {{id_product}}, {{id_attr}}, {{mode}}

**Technical Tasks:**
- Create template
- Add realistic think time (sleep 1-3s)
- Add checks
- Test with sample data

**Estimated Effort:** 2-3 hours

---

### Story 3.5: Create Other Templates
**As a** system
**I want** templates for homepage, category, landing
**So that** all page types are testable

**Acceptance Criteria:**
- `template_homepage.js.j2`: GET homepage + assets
- `template_category.js.j2`: GET listing + pagination
- `template_landing.js.j2`: GET page + CTA
- All extend base template
- All have appropriate checks

**Technical Tasks:**
- Create 3 templates
- Add page-specific checks
- Test rendering

**Estimated Effort:** 3-4 hours

---

### Story 3.6: Implement K6 Generator
**As a** system
**I want** dynamic K6 script generation
**So that** tests adapt to page type and environment

**Acceptance Criteria:**
- `src/k6_generator.py` created
- Function: generate_k6_script(config: K6TestConfig) -> Path
- Selects correct template based on page_type
- Injects all variables (VUs, duration, thresholds, URLs)
- Applies PROD vs PREPROD threshold values
- Outputs to /tmp/k6_script_{timestamp}.js
- Returns script path

**Technical Tasks:**
- Create k6_generator.py
- Implement template selection logic
- Implement Jinja2 rendering
- Add threshold calculation
- Write unit tests (mock templates)

**Estimated Effort:** 4-5 hours

---

### Story 3.7: Implement K6 Executor
**As a** system
**I want** to execute K6 and collect results
**So that** load tests run automatically

**Acceptance Criteria:**
- `src/k6_executor.py` created
- Function: execute_k6_test(script_path: Path) -> K6Results
- Checks K6 installed (`which k6`)
- Runs: `k6 run --out json={output} {script}`
- Timeout: 10 minutes max
- Detects exit code 99 (threshold abort) as expected
- Parses NDJSON output
- Returns K6Results object

**Technical Tasks:**
- Create k6_executor.py
- Implement subprocess execution
- Add K6 binary check
- Implement NDJSON parser
- Handle exit codes correctly
- Write integration tests (requires K6)

**Estimated Effort:** 5-6 hours

---

### Story 3.8: Handle K6 Not Installed
**As a** user
**I want** clear error if K6 not installed
**So that** I know what to do

**Acceptance Criteria:**
- Detects K6 missing before test
- Error message: "K6 binary not found. Install with: brew install k6"
- Raises K6ExecutionError
- Logged clearly

**Technical Tasks:**
- Add check in k6_executor
- Provide OS-specific install instructions
- Write test with K6 not in PATH

**Estimated Effort:** 1 hour

---

### Story 3.9: Parse K6 JSON Output
**As a** system
**I want** to parse K6 NDJSON results
**So that** metrics are extracted

**Acceptance Criteria:**
- Parses line-by-line NDJSON
- Extracts p95, p99, avg from http_req_duration
- Extracts error rate from http_req_failed
- Extracts VUs, iterations, data received
- Detects test_aborted flag
- Handles malformed JSON gracefully

**Technical Tasks:**
- Implement parse_k6_results()
- Handle partial results (if aborted)
- Write tests with sample K6 output

**Estimated Effort:** 3-4 hours

---

### Story 3.10: Integration Testing
**As a** developer
**I want** to test K6 execution end-to-end
**So that** the pipeline works

**Acceptance Criteria:**
- Test generates script from config
- Test executes real K6 binary
- Test parses results successfully
- Test validates threshold abort behavior
- Tests marked @pytest.mark.integration @pytest.mark.requires_k6

**Technical Tasks:**
- Create integration test
- Use httpbin.org as safe target
- Test threshold abort scenario
- Document test requirements

**Estimated Effort:** 2-3 hours

---

## Definition of Done

- [ ] All 4 K6 templates created with safety thresholds
- [ ] K6 generator produces valid scripts
- [ ] K6 executor runs tests and collects metrics
- [ ] Exit code 99 handled as expected (not error)
- [ ] K6 not installed error is clear
- [ ] JSON parsing works with real K6 output
- [ ] Unit tests >= 80% coverage
- [ ] Integration tests pass with real K6
- [ ] Code follows standards (ruff + mypy pass)

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| K6 changes JSON format | MEDIUM | Pin K6 version 0.47+ |
| Threshold abort false positives | MEDIUM | Test thresholds on PREPROD first |
| K6 hangs indefinitely | HIGH | Subprocess timeout enforced |
| Template rendering errors | LOW | Unit test all templates |

---

## Notes

- **CRITICAL:** All templates MUST include safety thresholds
- Test threshold abort behavior thoroughly
- Keep K6 scripts simple and readable
- Document threshold rationale in comments
