# Data Models

See detailed Pydantic models in `src/models/`:

- **PageDetectionResult:** Page metadata (type, IDs, elements detected)
- **PromotionData:** Detected promotions with complexity and impact estimates
- **StrikedPriceData:** Striked price details
- **AutoCartRule:** Auto-applied promotional code
- **K6TestConfig:** Configuration for K6 script generation
- **K6Results:** Parsed K6 execution results
- **PerformanceScore:** Calculated scores and grades
- **AnalysisReport:** Final complete report (JSON output)
- **Recommendation:** Actionable recommendation with priority

All models use Pydantic for automatic validation and serialization.

---
