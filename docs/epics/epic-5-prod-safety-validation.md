# Epic 5: PROD Safety & Validation

**Status:** Not Started
**Priority:** CRITICAL
**Estimated Effort:** 1-2 days
**Dependencies:** Epic 4

---

## Objectif

Implémenter et valider toutes les protections nécessaires pour tester en PRODUCTION sans risque de crash ou surcharge du site.

## Scope

### Included
- Validation fenêtre horaire PROD (3h-6h)
- Validation limites VUs PROD (max 50)
- Validation mode read_only PROD
- Détection environnement automatique
- Tests de validation PROD (sans toucher vraiment PROD)
- Documentation checklist pré-test
- Script de vérification

### Excluded
- IP whitelist Cloudflare (configuration manuelle)
- Monitoring temps réel (Phase 2)
- Dashboard d'urgence (Phase 2)

---

## User Stories

### Story 5.1: Implement Environment Detection
**As a** system
**I want** automatic environment detection
**So that** PROD constraints are enforced

**Acceptance Criteria:**
- Detects "ipln.fr" (not preprod) → environment = "prod"
- Detects "preprod.ipln.fr" or other → environment = "preprod"
- Logs detection clearly
- Auto-sets environment if not provided by user

**Technical Tasks:**
- Add detect_environment(url: str) -> str
- Add to main.py argument parsing
- Write tests

**Estimated Effort:** 1 hour

---

### Story 5.2: Implement Time Window Validation
**As a** system
**I want** to enforce 3h-6h window for PROD
**So that** tests only run during low traffic

**Acceptance Criteria:**
- Function: validate_time_window(environment: str) -> None
- If env=="prod" and hour not in [3, 4, 5]: raise ValidationError
- Error message: "PROD tests only allowed 3h-6h AM. Current time: {time}"
- Timezone: Server timezone (document in code)
- Called before K6 execution

**Technical Tasks:**
- Create src/utils/validators.py
- Implement validate_time_window()
- Add timezone handling
- Write tests with mocked datetime

**Estimated Effort:** 2-3 hours

---

### Story 5.3: Implement VU Limit Validation
**As a** system
**I want** to enforce max 50 VUs in PROD
**So that** Cloudflare doesn't rate limit

**Acceptance Criteria:**
- Function: validate_prod_constraints(config: K6TestConfig) -> None
- If env=="prod" and max_vus > 50: raise ValidationError
- Error message: "PROD tests limited to 50 VUs (Cloudflare rate limiting). Use --intensity light or test on PREPROD"
- Called before K6 generation

**Technical Tasks:**
- Add to validators.py
- Implement validate_prod_constraints()
- Write tests

**Estimated Effort:** 1 hour

---

### Story 5.4: Enforce Read-Only Mode in PROD
**As a** system
**I want** to force read_only mode in PROD
**So that** no write operations occur

**Acceptance Criteria:**
- If env=="prod" and mode!="read_only": auto-force mode="read_only"
- Log WARNING: "PROD tests forced to read_only mode for safety"
- No POST requests in PROD K6 scripts

**Technical Tasks:**
- Add check in main.py
- Modify K6 template selection logic
- Write tests

**Estimated Effort:** 1 hour

---

### Story 5.5: Implement All Validations in Main
**As a** system
**I want** all PROD validations called before execution
**So that** unsafe tests are blocked

**Acceptance Criteria:**
- main.py calls validate_prod_constraints() after config built
- Validation occurs BEFORE any K6 generation or execution
- Failed validation raises ValidationError with clear message
- Returns exit code 1

**Technical Tasks:**
- Integrate validators into main.py
- Add early return on validation failure
- Write end-to-end test

**Estimated Effort:** 2 hours

---

### Story 5.6: Create Pre-Test Checklist
**As a** user
**I want** a pre-test checklist
**So that** I know PROD tests are safe

**Acceptance Criteria:**
- Checklist in README.md or docs/
- Items:
  - [ ] Time is 3h-6h AM
  - [ ] VUs = 50 or less
  - [ ] Mode = read_only
  - [ ] Thresholds PROD configured
  - [ ] Dashboard/logs monitoring ready
  - [ ] Team member on standby
  - [ ] Recent backup exists

**Technical Tasks:**
- Create checklist document
- Link from README

**Estimated Effort:** 30 minutes

---

### Story 5.7: Create Safety Verification Script
**As a** user
**I want** a script to verify safety config
**So that** I'm confident before testing

**Acceptance Criteria:**
- `scripts/verify_prod_safety.sh` created
- Checks current hour in 3-6 range
- Checks config file for PROD settings
- Prompts user to confirm
- Exit if unsafe

**Technical Tasks:**
- Create verification script
- Make executable
- Test script

**Estimated Effort:** 1-2 hours

---

### Story 5.8: Test PROD Validation Logic
**As a** developer
**I want** comprehensive tests for PROD safety
**So that** protections work

**Acceptance Criteria:**
- Test time window validation (in/out of range)
- Test VU limit enforcement
- Test mode forcing
- Test environment detection
- All tests pass
- Coverage >= 100% for validators

**Technical Tasks:**
- Write unit tests for all validators
- Mock datetime for time tests
- Test error messages are clear
- Test integration in main.py

**Estimated Effort:** 3-4 hours

---

### Story 5.9: Dry-Run Mode
**As a** user
**I want** a dry-run mode
**So that** I can test without actually running K6

**Acceptance Criteria:**
- CLI flag: `--dry-run`
- Executes full pipeline except K6 execution
- Generates K6 script but doesn't run it
- Shows what would happen
- Logs: "DRY RUN: Would execute K6 with config: ..."

**Technical Tasks:**
- Add --dry-run flag
- Skip K6 execution if dry-run
- Add logging
- Write test

**Estimated Effort:** 2 hours

---

### Story 5.10: Validation Testing (Simulated PROD)
**As a** developer
**I want** to test PROD validation without touching PROD
**So that** safety is verified

**Acceptance Criteria:**
- Test attempts PROD config outside 3-6h → fails
- Test attempts 200 VUs in PROD → fails
- Test attempts mode=full in PROD → forced to read_only
- All validation errors have clear messages
- Tests use mocked time and don't touch real PROD

**Technical Tasks:**
- Create comprehensive validation tests
- Mock datetime for time tests
- Verify error messages user-friendly
- Run and document tests

**Estimated Effort:** 2-3 hours

---

## Definition of Done

- [ ] Environment auto-detection working
- [ ] Time window validation enforced (3h-6h)
- [ ] VU limits enforced (max 50 PROD)
- [ ] Read-only mode forced in PROD
- [ ] All validations integrated in main.py
- [ ] Pre-test checklist created
- [ ] Safety verification script created
- [ ] Dry-run mode working
- [ ] Validation tests 100% coverage
- [ ] Documentation clear
- [ ] No way to bypass PROD protections

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Validation bypassed accidentally | CRITICAL | Multiple check points, tests verify |
| Wrong timezone for time check | HIGH | Document timezone, test across timezones |
| User forces unsafe config | MEDIUM | Validation can't be disabled, no --force flag |

---

## Notes

- **THIS IS THE MOST CRITICAL EPIC** - PROD safety non-negotiable
- Test exhaustively with mocked time
- Document all protections clearly
- No backdoors or bypass mechanisms
- When in doubt, fail safe (block execution)
