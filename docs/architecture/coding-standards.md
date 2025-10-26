# Coding Standards

## Core Standards

- **Python 3.11+ required** (modern features: match/case, improved type hints)
- **Ruff** for linting + formatting (max line length: 100)
- **mypy** strict mode (all functions must have type hints)
- **pytest** for testing (≥80% coverage for core modules)

## Critical Rules (MANDATORY)

1. **NEVER hardcode URLs or credentials** - Use config/env
2. **ALWAYS validate PROD constraints before K6** - Safety critical
3. **ALWAYS use Pydantic models for data transfer** - Type safety
4. **NEVER suppress K6 threshold aborts as errors** - Exit 99 = expected
5. **ALWAYS close browser/resources in finally blocks**
6. **ALWAYS use correlation_id for traceability**
7. **NEVER log sensitive data** - Sanitize logs
8. **ALWAYS use pathlib.Path for files** - Cross-platform
9. **ALWAYS set timeouts for external operations** - Prevent hangs
10. **Use Loguru logger, never print()** - Except CLI output
11. **K6 templates must include safety thresholds** - REQUIRED
12. **Async functions use proper Playwright async API**

## Python 3.11+ Specifics

- Use Pydantic v2 validation
- Use match/case for cleaner conditionals
- Use native union types (`str | None` not `Union`)
- Type hints everywhere

---
