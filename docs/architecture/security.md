# Security

## Input Validation

- **Library:** Pydantic 2.5.0 (automatic validation)
- **Location:** At API boundary (main.py + model constructors)
- **Rules:** All external inputs validated, whitelist approach, fail-fast

## Authentication & Authorization

- **User Auth:** None (local CLI tool)
- **API Auth:** HTTP Basic Auth with API key from `.env`
- **API keys:** Never hardcoded, stored in `.env` (gitignored)

## Secrets Management

- **Development:** `.env` file (gitignored)
- **Production:** `.env` file (manually configured per user)
- **Requirements:**
  - NEVER hardcode secrets
  - Access via Config.get_api_key()
  - No secrets in logs, errors, or JSON outputs

## HTTPS Enforcement

- All HTTP requests use HTTPS only
- SSL certificate verification enabled (`verify=True`)
- Reject HTTP URLs in validation

## Logging Restrictions

**NEVER log:**
- API keys, auth tokens
- Full API responses (may contain sensitive business data)
- Complete K6 results (may contain response bodies)
- Environment variables

**Safe to log:**
- URLs (sanitized, no query params)
- HTTP status codes
- Aggregated metrics
- Execution flow
- Error types (not sensitive details)

## Dependency Security

- **Tool:** pip-audit (manual scans)
- **Policy:** Review advisories monthly, update quarterly
- **Approval:** New dependencies require CVE check and maintenance verification

## Threat Model

**Critical mitigations:**
- PROD overload prevention: Time window + VU limits + K6 thresholds
- API key leaks: Sanitize logs, gitignore .env
- MITM attacks: HTTPS only + certificate verification

---
