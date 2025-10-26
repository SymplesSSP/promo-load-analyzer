# Test Strategy

## Testing Philosophy

- **Approach:** TDD encouraged but not mandatory for MVP
- **Coverage Goals:** ≥80% for core modules, ≥70% overall
- **Test Pyramid:** 70% unit, 25% integration, 5% E2E

## Test Types

**Unit Tests:**
- Framework: pytest
- Location: `tests/unit/`
- Mock all external dependencies
- Fast execution (< 1s total)

**Integration Tests:**
- Location: `tests/integration/`
- Real dependencies (k6 binary, Playwright, PREPROD network)
- Skip if dependencies missing

**E2E Tests:**
- Full pipeline execution
- PREPROD only
- Expensive, run on-demand

## Test Organization

- Test files: `test_<module>.py`
- Test functions: `test_<function>_<scenario>`
- Fixtures in `tests/conftest.py`
- AAA pattern (Arrange, Act, Assert)

---
