# Tech Stack

## Cloud Infrastructure

- **Provider:** No cloud provider (Local execution)
- **Key Services:** N/A - Standalone CLI tool
- **Deployment Regions:** Local developer machine / CI runner

## Technology Stack Table

| Category | Technology | Version | Purpose | Rationale |
|----------|-----------|---------|---------|-----------|
| **Language** | Python | 3.11+ | Primary development language | Excellent libraries, team expertise, async support, type hints |
| **Runtime** | CPython | 3.11.6 | Python interpreter | Standard, stable, wide compatibility |
| **CLI Framework** | argparse | stdlib | Command-line parsing | Built-in, zero dependencies, sufficient for simple CLI |
| **Web Scraping** | Playwright | 1.40.0 | Browser automation & DOM scraping | Headless browser, JavaScript execution, PrestaShop interaction support |
| **HTTP Client** | requests | 2.31.0 | PrestaShop API calls (optional) | Simple, reliable, widely used |
| **Template Engine** | Jinja2 | 3.1.2 | K6 script generation | Powerful templating, clean syntax, Python standard |
| **Load Testing** | K6 | 0.47+ | Load test execution | Best-in-class, scriptable, threshold support, JSON output |
| **Config Management** | python-dotenv | 1.0.0 | Environment variables | Simple .env file support for API keys |
| **Package Manager** | pip | latest | Dependency management | Python standard, simple requirements.txt |
| **Virtual Env** | venv | stdlib | Isolated dependencies | Built-in, no extra tools needed |
| **Type Checking** | mypy | 1.7.0 | Static type validation | Catches errors early, improves code quality |
| **Linter** | ruff | 0.1.6 | Code linting & formatting | Fast, modern, replaces flake8+black+isort |
| **Testing Framework** | pytest | 7.4.3 | Unit & integration tests | Industry standard, powerful fixtures, parametrization |
| **Test Coverage** | pytest-cov | 4.1.0 | Coverage reporting | Integrates with pytest, clear reports |
| **JSON Validation** | pydantic | 2.5.0 | Data validation & serialization | Type-safe JSON parsing, excellent errors |
| **Logging** | loguru | 0.7.2 | Structured logging | Better than stdlib logging, automatic rotation, colorized |
| **Version Control** | Git | 2.40+ | Source control | Industry standard |
| **CI/CD** | GitHub Actions | N/A (future) | Automated testing (Phase 2) | Free for public repos, YAML config |

---
