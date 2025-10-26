# Epic 1: Project Setup & Infrastructure

**Status:** Not Started
**Priority:** CRITICAL
**Estimated Effort:** 1-2 days
**Dependencies:** None

---

## Objectif

Initialiser le projet Python, configurer l'environnement de développement, et mettre en place l'infrastructure de base pour permettre le développement.

## Scope

### Included
- Initialisation du repository Git
- Structure des dossiers du projet
- Configuration Python (venv, requirements.txt, pyproject.toml)
- Installation et vérification des dépendances externes (K6, Playwright)
- Scripts d'installation automatisés
- Configuration de base (.env.example, .gitignore)

### Excluded
- Code métier (dans Epic 2+)
- Tests unitaires (créés avec chaque module)
- Documentation utilisateur (Epic 4)

---

## User Stories

### Story 1.1: Initialize Git Repository
**As a** developer
**I want** a properly configured Git repository
**So that** code changes are tracked and collaboration is possible

**Acceptance Criteria:**
- Repository initialized with `git init`
- .gitignore configured (Python, .env, logs, tmp files)
- Initial commit with project structure
- README.md created with basic info

**Technical Tasks:**
- Create .gitignore from template
- Initialize git repo
- Create README.md with setup instructions
- Make initial commit

**Estimated Effort:** 30 minutes

---

### Story 1.2: Create Project Structure
**As a** developer
**I want** a clear folder structure
**So that** code is organized and easy to navigate

**Acceptance Criteria:**
- All directories created per architecture doc
- `src/`, `tests/`, `templates/`, `scripts/`, `docs/` exist
- `src/models/`, `src/utils/` subdirectories created
- Empty `__init__.py` files in Python packages

**Technical Tasks:**
- Create directory structure
- Add __init__.py files
- Verify structure matches architecture.md

**Estimated Effort:** 15 minutes

---

### Story 1.3: Setup Python Environment
**As a** developer
**I want** an isolated Python environment
**So that** dependencies don't conflict with system packages

**Acceptance Criteria:**
- Python 3.11+ verified
- Virtual environment created
- requirements.txt created with all dependencies
- requirements-dev.txt created with dev tools
- pyproject.toml configured for ruff and mypy

**Technical Tasks:**
- Check Python version >= 3.11
- Create venv: `python3.11 -m venv venv`
- Create requirements.txt
- Create requirements-dev.txt
- Create pyproject.toml with tool configs

**Estimated Effort:** 1 hour

---

### Story 1.4: Install Python Dependencies
**As a** developer
**I want** all Python packages installed
**So that** I can start coding

**Acceptance Criteria:**
- All packages from requirements.txt installed
- All dev packages from requirements-dev.txt installed
- Playwright browsers installed (`playwright install chromium`)
- No installation errors

**Technical Tasks:**
- `pip install -r requirements.txt`
- `pip install -r requirements-dev.txt`
- `playwright install chromium`
- Verify installations

**Estimated Effort:** 30 minutes

---

### Story 1.5: Install K6 Binary
**As a** developer
**I want** K6 installed and verified
**So that** load tests can be executed

**Acceptance Criteria:**
- K6 v0.47+ installed
- `k6 version` command works
- Installation script created for macOS and Linux

**Technical Tasks:**
- Install K6 (brew or apt)
- Verify installation
- Document installation steps
- Create check script

**Estimated Effort:** 30 minutes

---

### Story 1.6: Create Setup Scripts
**As a** developer
**I want** automated setup scripts
**So that** environment can be set up quickly

**Acceptance Criteria:**
- `scripts/setup_dev.sh` created
- Script checks Python version
- Script creates venv
- Script installs all dependencies
- Script verifies K6 installation
- Script is executable and tested

**Technical Tasks:**
- Create scripts/setup_dev.sh
- Add Python version check
- Add venv creation
- Add dependency installation
- Add K6 verification
- Make executable (chmod +x)
- Test script

**Estimated Effort:** 1-2 hours

---

### Story 1.7: Create Configuration Files
**As a** developer
**I want** configuration templates
**So that** the app can be configured without hardcoding

**Acceptance Criteria:**
- .env.example created with all variables
- .gitignore includes .env
- Config loading code in src/config.py

**Technical Tasks:**
- Create .env.example
- Document each variable
- Create src/config.py stub
- Add to .gitignore

**Estimated Effort:** 30 minutes

---

## Definition of Done

- [ ] Git repository initialized with initial commit
- [ ] Complete project structure created
- [ ] Python 3.11+ venv created and activated
- [ ] All dependencies installed (Python + K6 + Playwright)
- [ ] `scripts/setup_dev.sh` runs successfully
- [ ] `.env.example` created
- [ ] README.md has setup instructions
- [ ] Another developer can clone and setup in < 15 minutes

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Python version incompatibility | HIGH | Check version early, document requirement |
| K6 installation issues | MEDIUM | Provide manual steps for multiple OS |
| Playwright download failures | LOW | Document offline installation option |

---

## Notes

- This epic is **blocking** all other work
- Must be completed before Epic 2 can start
- Keep setup script simple and well-documented
- Test setup on clean machine if possible
