"""Main orchestrator for Promo Load Analyzer."""

import tempfile
from pathlib import Path

from loguru import logger

from src.k6_executor import K6Executor
from src.k6_generator import K6ScriptGenerator
from src.models.k6_config import Environment, Intensity, LoadTestConfig, TestMode
from src.models.k6_results import K6ExecutionResult
from src.page_detector import detect_page_type_from_url
from src.promo_scraper import (
    detect_manual_code_input,
    scrape_auto_cart_rules,
    scrape_striked_price,
)
from src.report_generator import ReportGenerator
from src.results_analyzer import ResultsAnalyzer


class PromoLoadAnalyzer:
    """Main orchestrator for the Promo Load Analyzer tool.

    Coordinates all components to perform end-to-end load testing:
    1. Detect page type from URL
    2. Scrape promotions
    3. Generate K6 script
    4. Execute load test
    5. Analyze results
    6. Generate report
    """

    def __init__(
        self,
        environment: Environment = Environment.PREPROD,
        intensity: Intensity = Intensity.MEDIUM,
        mode: TestMode = TestMode.READ_ONLY,
        k6_binary: str = "k6",
        timeout_seconds: int = 3600,
        enable_influxdb: bool = False,
    ) -> None:
        """Initialize the analyzer.

        Args:
            environment: Target environment (PROD or PREPROD)
            intensity: Test intensity (LIGHT, MEDIUM, HEAVY)
            mode: Test mode (READ_ONLY or FULL)
            k6_binary: Path to K6 binary
            timeout_seconds: Maximum test execution time
            enable_influxdb: Enable real-time Grafana dashboard (requires Docker)
        """
        self.environment = environment
        self.intensity = intensity
        self.mode = mode
        self.enable_influxdb = enable_influxdb

        # Initialize components
        self.k6_generator = K6ScriptGenerator()
        self.k6_executor = K6Executor(
            k6_binary=k6_binary,
            timeout_seconds=timeout_seconds,
            enable_influxdb=enable_influxdb,
        )
        self.results_analyzer = ResultsAnalyzer()
        self.report_generator = ReportGenerator()

        logger.info(
            f"PromoLoadAnalyzer initialized: {environment.value}, "
            f"{intensity.value}, {mode.value}"
        )

        if enable_influxdb:
            logger.info("📊 Real-time dashboard enabled")

    async def analyze(
        self,
        url: str,
        output_path: Path | None = None,
    ) -> tuple[K6ExecutionResult, str]:
        """Run complete analysis pipeline.

        Args:
            url: Target URL to analyze
            output_path: Optional path to save report (if None, uses temp file)

        Returns:
            Tuple of (execution_result, report_path)

        Raises:
            ValueError: If URL is invalid or page detection fails
            FileNotFoundError: If K6 is not installed
        """
        logger.info(f"Starting analysis for: {url}")

        # Step 1: Detect page type
        logger.info("Step 1/6: Detecting page type...")
        page_detection = detect_page_type_from_url(url)

        if page_detection.page_type == "unknown":
            raise ValueError(
                f"Could not detect page type for URL: {url}. "
                "Please check the URL is a valid PrestaShop page."
            )

        logger.info(
            f"Detected: {page_detection.page_type} "
            f"(confidence: {page_detection.confidence:.1%})"
        )

        # Step 2: Scrape promotions
        logger.info("Step 2/6: Scraping promotions...")
        promotions: dict[str, any] | None = None  # type: ignore[valid-type]

        try:
            striked_price = await scrape_striked_price(url)
            auto_cart_rules = await scrape_auto_cart_rules(url)
            has_manual_code = await detect_manual_code_input(url)

            # Note: PromotionData will be used for display in report only
            # We'll pass raw data to avoid validation issues
            promo_data = {
                "striked_price": striked_price,
                "auto_cart_rules": auto_cart_rules or [],
                "has_manual_code_input": has_manual_code,
            }

            # Calculate metrics for logging
            has_promos = striked_price or auto_cart_rules or has_manual_code
            if has_promos:
                logger.info("Promotions detected on page")
            else:
                logger.info("No promotions detected")

            promotions = promo_data
        except Exception as e:
            logger.warning(f"Failed to scrape promotions: {e}")
            promotions = {
                "striked_price": None,
                "auto_cart_rules": [],
                "has_manual_code_input": False,
            }

        # Step 3: Generate K6 script
        logger.info("Step 3/6: Generating K6 script...")

        # Map page types from PageDetectionResult to LoadTestConfig
        # "catalog" → "homepage", others pass through
        page_type_mapping = {
            "product": "product",
            "category": "category",
            "catalog": "homepage",
        }
        k6_page_type = page_type_mapping.get(
            page_detection.page_type, "landing"
        )  # Default to landing for any other type

        config = LoadTestConfig(
            url=url,
            page_type=k6_page_type,  # type: ignore[arg-type]
            environment=self.environment,
            intensity=self.intensity,
            mode=self.mode,
            id_product=page_detection.product_id,  # Map product_id to id_product
            id_product_attribute=None,  # Not extracted by page detector
        )

        # Generate script to temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".js", delete=False
        ) as script_file:
            script_path = Path(script_file.name)

        try:
            self.k6_generator.generate_to_file(config, script_path)
            logger.info(f"K6 script generated: {script_path}")

            # Step 4: Execute K6 test
            logger.info("Step 4/6: Executing K6 load test...")
            logger.info("This may take several minutes depending on intensity...")

            result = self.k6_executor.execute_script(script_path, config)

            if result.success:
                logger.info(
                    f"Test completed successfully in {result.duration_seconds:.1f}s"
                )
            else:
                logger.error(f"Test failed: {result.error_message}")

            # Step 5: Analyze results
            logger.info("Step 5/6: Analyzing results...")
            result = self.results_analyzer.analyze(result)

            if result.overall_grade:
                logger.info(
                    f"Overall grade: {result.overall_grade.grade} "
                    f"({result.overall_grade.score:.1f}/100)"
                )

            # Step 6: Generate report
            logger.info("Step 6/6: Generating report...")
            report = self.report_generator.generate_report(result, promotions)

            # Save report
            if output_path is None:
                output_path = Path(
                    tempfile.gettempdir()
                ) / f"promo_load_report_{int(result.duration_seconds)}.md"

            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report, encoding="utf-8")

            logger.info(f"Report saved: {output_path}")
            logger.success("Analysis complete!")

            return result, str(output_path)

        finally:
            # Clean up temporary script file
            if script_path.exists():
                try:
                    script_path.unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete temporary script: {e}")

    def check_dependencies(self) -> dict[str, bool]:
        """Check if all required dependencies are available.

        Returns:
            Dictionary mapping dependency names to availability status
        """
        dependencies = {}

        # Check K6
        dependencies["k6"] = self.k6_executor.check_k6_available()

        # Check templates
        template_validation = self.k6_generator.validate_templates()
        dependencies["templates"] = all(template_validation.values())

        return dependencies
