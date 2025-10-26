# Error Handling Strategy

## Exception Hierarchy

```
PromoAnalyzerException (base)
├── ValidationError (user input, PROD constraints)
├── DetectionError (page/promo detection failures)
├── ScrapingError (Playwright/network issues)
├── K6ExecutionError (K6 binary, script execution)
├── APIError (PrestaShop API failures)
└── AnalysisError (results parsing, scoring)
```

## Logging Standards

- **Library:** Loguru 0.7.2
- **Format:** Timestamp | Level | Module:Function:Line | Message
- **Correlation ID:** Generated per execution for full traceability
- **Levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Restrictions:** NEVER log API keys, auth tokens, PII, sensitive data

## Error Handling Patterns

**External API Errors:**
- Retry policy: Max 2 retries, exponential backoff (1s, 2s)
- Timeout: 15s total per request
- Graceful degradation on failure (continue without enrichment)

**Playwright Scraping:**
- Retry: Max 2 retries on timeout/network errors
- Timeout: 30s page load, 60s total per page
- Partial results on failure

**K6 Execution:**
- Exit code 99 = threshold abort (expected, not error)
- Timeout: 10min max
- Detect K6 not installed with clear error message

## Critical Rules

1. NEVER log sensitive data (API keys, credentials, PII)
2. ALWAYS validate PROD constraints before K6 execution
3. ALWAYS close resources in finally blocks
4. ALWAYS wrap K6 subprocess with timeout
5. NEVER suppress exceptions silently

---
