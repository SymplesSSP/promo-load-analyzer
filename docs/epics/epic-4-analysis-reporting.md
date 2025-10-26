# Epic 4: Results Analysis & Reporting

**Status:** Not Started
**Priority:** HIGH
**Estimated Effort:** 2-3 days
**Dependencies:** Epic 3

---

## Objectif

Analyser les résultats K6, calculer les scores A-F, estimer la capacité maximale serveur, et générer des recommandations actionnables pour les utilisateurs marketing.

## Scope

### Included
- Module `results_analyzer.py` pour scoring et recommandations
- Modèles Pydantic pour scores et rapport final
- Algorithme de calcul de grade
- Estimation capacité max users
- Génération recommandations prioritisées
- Orchestrateur `main.py` complet
- Export JSON final

### Excluded
- Interface Claude Code markdown (généré par Claude après)
- Dashboard temps réel (Phase 2)
- Alertes Slack (Phase 2)

---

## User Stories

### Story 4.1: Create Analysis Models
**As a** developer
**I want** models for scores and final report
**So that** output is structured

**Acceptance Criteria:**
- `src/models/analysis_report.py` created
- Models: PerformanceScore, Recommendation, AnalysisReport
- PerformanceScore includes: response_time_score, error_rate_score, global_score, grade, max_users_estimated
- Recommendation includes: priority, title, action, expected_gain, effort_estimate
- AnalysisReport aggregates all data

**Technical Tasks:**
- Create models
- Add validation
- Write serialization tests

**Estimated Effort:** 2-3 hours

---

### Story 4.2: Implement Response Time Scoring
**As a** system
**I want** to score response time on A-F scale
**So that** users understand performance

**Acceptance Criteria:**
- Algorithm per PRD:
  - A: p95 < 1000ms → score 100
  - B: p95 1000-2000ms → score 80
  - C: p95 2000-3000ms → score 60
  - D: p95 3000-5000ms → score 40
  - F: p95 > 5000ms → score 20
- Returns (score: int, grade: str)

**Technical Tasks:**
- Implement calculate_response_score()
- Add to constants.py: GRADE_THRESHOLDS
- Write parametrized tests for all grades

**Estimated Effort:** 2 hours

---

### Story 4.3: Implement Error Rate Scoring
**As a** system
**I want** to score error rate on A-F scale
**So that** reliability is measured

**Acceptance Criteria:**
- Algorithm per PRD:
  - A: < 0.1% → score 100
  - B: 0.1-1% → score 80
  - C: 1-5% → score 60
  - D: 5-10% → score 40
  - F: > 10% → score 20

**Technical Tasks:**
- Implement calculate_error_score()
- Write tests

**Estimated Effort:** 1 hour

---

### Story 4.4: Implement Global Score Calculation
**As a** system
**I want** a composite score
**So that** overall performance is clear

**Acceptance Criteria:**
- Formula: global_score = (response_score * 0.6) + (error_score * 0.4)
- Assigns final grade A-F based on composite score
- Returns PerformanceScore object

**Technical Tasks:**
- Implement calculate_global_score()
- Write tests

**Estimated Effort:** 1 hour

---

### Story 4.5: Implement Max Users Estimation (MVP)
**As a** system
**I want** to estimate max concurrent users
**So that** capacity planning is possible

**Acceptance Criteria:**
- MVP algorithm (conservative):
  - threshold_p95 = 2000ms
  - If actual_p95 < threshold: extrapolate capacity
  - Formula: `max_users = int(current_vus * (2000 / actual_p95) * 0.8)`
  - 20% safety margin applied
  - If actual_p95 > 2000: max_users = current_vus (already degraded)
- Confidence level: "low" | "medium" | "high"
- Document limitations in docstring

**Technical Tasks:**
- Implement estimate_max_users()
- Add formula to constants
- Write tests with various p95 values
- Document conservative nature

**Estimated Effort:** 2-3 hours

---

### Story 4.6: Implement Promo Impact Calculation
**As a** system
**I want** to calculate promo overhead
**So that** users understand cost

**Acceptance Criteria:**
- Sums impact from all detected promos
- Striked price: +5%
- Auto cart rule: +15% each
- Manual code input: +25%
- Returns percentage and description

**Technical Tasks:**
- Implement calculate_promo_impact()
- Use heuristics from PRD
- Write tests

**Estimated Effort:** 1 hour

---

### Story 4.7: Generate Recommendations
**As a** system
**I want** actionable recommendations
**So that** users know what to optimize

**Acceptance Criteria:**
- Rule-based recommendations:
  - If p95 > 2000ms → HIGH priority: "Optimize page performance"
  - If error_rate > 5% → HIGH: "Investigate errors"
  - If multiple auto cart rules → MEDIUM: "Merge promo codes"
  - If striked price alternative exists → LOW: "Consider striked price"
- Each recommendation includes: priority, action, gain estimate, effort
- Max 5 recommendations (top priorities)

**Technical Tasks:**
- Implement generate_recommendations()
- Define recommendation rules
- Prioritize correctly
- Write tests for each rule

**Estimated Effort:** 4-5 hours

---

### Story 4.8: Implement Results Analyzer
**As a** system
**I want** a complete analysis function
**So that** all metrics are calculated

**Acceptance Criteria:**
- `src/results_analyzer.py` created
- Function: analyze_results(k6_results, promo_data, config) -> AnalysisReport
- Calls all scoring functions
- Calls max users estimation
- Calls promo impact calculation
- Calls recommendation generation
- Returns complete AnalysisReport

**Technical Tasks:**
- Create results_analyzer.py
- Orchestrate all calculations
- Handle missing data gracefully
- Write integration tests

**Estimated Effort:** 3-4 hours

---

### Story 4.9: Implement Main Orchestrator
**As a** system
**I want** a complete pipeline in main.py
**So that** CLI execution works end-to-end

**Acceptance Criteria:**
- `src/main.py` created
- CLI with argparse: --url, --env, --intensity, --mode
- Pipeline execution:
  1. Parse arguments
  2. Detect page (page_detector)
  3. Scrape promos (promo_scraper)
  4. Build K6 config
  5. Generate K6 script (k6_generator)
  6. Execute K6 (k6_executor)
  7. Analyze results (results_analyzer)
  8. Write JSON to /tmp/analysis_{timestamp}.json
- Correlation ID for tracing
- Logging with loguru
- Error handling per error handling strategy
- Exit codes: 0 success, 1 validation, 2 detection, 3 k6, 4 analysis, 99 unknown

**Technical Tasks:**
- Create main.py
- Implement argparse
- Orchestrate all modules
- Add error handling
- Add logging
- Write JSON output
- Write end-to-end test

**Estimated Effort:** 6-8 hours

---

### Story 4.10: Add Logging & Correlation IDs
**As a** developer
**I want** comprehensive logging
**So that** debugging is easy

**Acceptance Criteria:**
- Loguru configured in src/utils/logger.py
- Daily rotation
- Correlation ID generated per execution
- All modules use logger.bind(correlation_id=...)
- Log levels: INFO for milestones, DEBUG for details, ERROR for failures
- No sensitive data logged (API keys, etc.)

**Technical Tasks:**
- Create src/utils/logger.py
- Configure loguru
- Add correlation ID to all modules
- Sanitize logs
- Write test verifying no secrets logged

**Estimated Effort:** 3-4 hours

---

## Definition of Done

- [ ] All scoring algorithms implemented correctly
- [ ] Max users estimation working
- [ ] Recommendations generated appropriately
- [ ] Main.py orchestrates full pipeline
- [ ] JSON output structured and valid
- [ ] Logging comprehensive with correlation IDs
- [ ] No sensitive data in logs
- [ ] Unit tests >= 80% coverage
- [ ] End-to-end test passes
- [ ] Code follows standards

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Max users estimate inaccurate | MEDIUM | Document conservative nature, improve in Phase 2 |
| Recommendations not actionable | MEDIUM | User testing, iterate on clarity |
| Pipeline failure mid-execution | LOW | Error handling at each step |

---

## Notes

- Keep recommendations simple and action-oriented
- Prioritize HIGH/MEDIUM/LOW clearly
- Document MVP limitations (conservative estimates)
- Test full pipeline on PREPROD
