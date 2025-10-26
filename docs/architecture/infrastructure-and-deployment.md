# Infrastructure and Deployment

## Deployment Strategy

**Manual local installation** - No cloud deployment required.

**Installation process:**
1. Clone repository
2. Run `./scripts/setup_dev.sh` (creates venv, installs deps, checks k6)
3. Configure `.env` (optional for API)
4. Verify: `python src/main.py --help`

**k6 installation:**
- macOS: `brew install k6`
- Linux: See k6.io installation instructions

## Environments

- **Development:** Local machine, PREPROD URLs only
- **Testing:** Local machine, integration tests against PREPROD
- **Production Use:** Local machine, testing against PROD (with time/VU restrictions)

## Rollback Strategy

- **Method:** Git revert commit
- **RTO:** Immediate (revert + re-run)
- No deployment rollback needed (local tool)

## Monitoring

- **Logging:** Loguru with daily rotation, correlation IDs for tracing
- **Metrics:** Embedded in JSON output (execution times, success rates)
- **Phase 2:** Slack notifications, structured logging export

---
