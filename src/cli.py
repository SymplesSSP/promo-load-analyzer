"""Command-line interface for Promo Load Analyzer."""

import argparse
import asyncio
import sys
from pathlib import Path

from loguru import logger

from src.main import PromoLoadAnalyzer
from src.models.k6_config import Environment, Intensity, TestMode


def setup_logging(verbose: bool = False) -> None:
    """Configure logging output.

    Args:
        verbose: Enable verbose logging
    """
    logger.remove()  # Remove default handler

    log_format = (
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<level>{message}</level>"
    )

    if verbose:
        logger.add(sys.stderr, format=log_format, level="DEBUG")
    else:
        logger.add(sys.stderr, format=log_format, level="INFO")


def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser.

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog="promo-load-analyzer",
        description="Automated load testing tool for PrestaShop promotional campaigns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test a product page in preprod (default: medium intensity, read-only)
  python -m src.cli https://preprod.ipln.fr/product-123.html

  # Test in production with light intensity (safe)
  python -m src.cli https://ipln.fr/promo/bf2025 --env prod --intensity light

  # Full test with add-to-cart (requires product ID)
  python -m src.cli https://preprod.ipln.fr/product-123.html --mode full

  # Save report to specific location
  python -m src.cli https://preprod.ipln.fr/ --output ./reports/homepage.md

  # Check dependencies
  python -m src.cli --check-deps

For more information: https://github.com/your-repo/promo-load-analyzer
        """,
    )

    # Required arguments
    parser.add_argument(
        "url",
        nargs="?",
        help="Target URL to test (PrestaShop page)",
    )

    # Test configuration
    parser.add_argument(
        "--env",
        "--environment",
        type=str,
        choices=["prod", "preprod"],
        default="preprod",
        help="Target environment (default: preprod)",
    )

    parser.add_argument(
        "--intensity",
        type=str,
        choices=["light", "medium", "heavy"],
        default="medium",
        help=(
            "Test intensity: "
            "light (50 VUs, 2min), "
            "medium (200 VUs, 5min), "
            "heavy (500 VUs, 10min). "
            "Note: PROD limited to 50 VUs. "
            "(default: medium)"
        ),
    )

    parser.add_argument(
        "--mode",
        type=str,
        choices=["read_only", "full"],
        default="read_only",
        help=(
            "Test mode: "
            "read_only (GET only), "
            "full (GET + POST add-to-cart). "
            "(default: read_only)"
        ),
    )

    # Output options
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output path for markdown report (default: temp file)",
    )

    # K6 configuration
    parser.add_argument(
        "--k6-binary",
        type=str,
        default="k6",
        help="Path to K6 binary (default: k6 in PATH)",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=3600,
        help="Maximum test duration in seconds (default: 3600 = 1 hour)",
    )

    # Monitoring options
    parser.add_argument(
        "--enable-dashboard",
        action="store_true",
        help="Enable real-time Grafana dashboard (requires Docker running)",
    )

    # Utility options
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Check if all dependencies are available and exit",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Promo Load Analyzer v1.0.0",
    )

    return parser


async def run_analysis(args: argparse.Namespace) -> int:
    """Run the analysis with provided arguments.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 = success, 1 = error)
    """
    # Validate URL
    if not args.url:
        logger.error("URL is required")
        return 1

    # Parse enum values
    try:
        environment = Environment(args.env)
        intensity = Intensity(args.intensity)
        mode = TestMode(args.mode)
    except ValueError as e:
        logger.error(f"Invalid argument: {e}")
        return 1

    # Validate PROD constraints
    if environment == Environment.PROD:
        if intensity == Intensity.HEAVY:
            logger.error(
                "HEAVY intensity is not allowed in PROD environment. "
                "Use LIGHT or MEDIUM instead."
            )
            return 1

        if mode == TestMode.FULL:
            logger.warning(
                "FULL mode in PROD should only be used during allowed hours (3h-6h AM). "
                "Proceeding anyway..."
            )

    # Create analyzer
    analyzer = PromoLoadAnalyzer(
        environment=environment,
        intensity=intensity,
        mode=mode,
        k6_binary=args.k6_binary,
        timeout_seconds=args.timeout,
        enable_influxdb=args.enable_dashboard,
    )

    # Check dependencies
    logger.info("Checking dependencies...")
    deps = analyzer.check_dependencies()

    if not deps.get("k6"):
        logger.error(
            "K6 is not installed or not in PATH. "
            "Install it from: https://k6.io/docs/get-started/installation/"
        )
        return 1

    if not deps.get("templates"):
        logger.error("K6 templates are missing or invalid")
        return 1

    logger.success("All dependencies available")

    # Parse output path
    output_path = Path(args.output) if args.output else None

    # Run analysis
    try:
        result, report_path = await analyzer.analyze(args.url, output_path)

        # Print summary
        print("\n" + "=" * 60)
        print("  ANALYSIS COMPLETE")
        print("=" * 60)

        if result.overall_grade:
            print(f"  Overall Grade: {result.overall_grade.grade}")
            print(f"  Score: {result.overall_grade.score:.1f}/100")

        if result.max_users_estimate:
            print(f"  Max Users: ~{result.max_users_estimate}")

        print(f"\n  📄 Full report: {report_path}")
        print("=" * 60 + "\n")

        return 0 if result.success else 1

    except Exception as e:
        logger.exception(f"Analysis failed: {e}")
        return 1


def check_dependencies() -> int:
    """Check and report on all dependencies.

    Returns:
        Exit code (0 = all OK, 1 = missing dependencies)
    """
    logger.info("Checking dependencies...")

    analyzer = PromoLoadAnalyzer()
    deps = analyzer.check_dependencies()

    all_ok = True

    for dep_name, available in deps.items():
        status = "✅" if available else "❌"
        print(f"{status} {dep_name}: {'available' if available else 'MISSING'}")

        if not available:
            all_ok = False

            if dep_name == "k6":
                print(
                    "   Install K6: https://k6.io/docs/get-started/installation/"
                )
            elif dep_name == "templates":
                print("   K6 templates are missing from templates/ directory")

    if all_ok:
        logger.success("All dependencies are available")
        return 0
    else:
        logger.error("Some dependencies are missing")
        return 1


def main() -> int:
    """Main CLI entry point.

    Returns:
        Exit code
    """
    parser = create_parser()
    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    # Handle special commands
    if args.check_deps:
        return check_dependencies()

    # Validate URL is provided
    if not args.url:
        parser.print_help()
        print("\nError: URL is required (or use --check-deps)")
        return 1

    # Run analysis
    try:
        return asyncio.run(run_analysis(args))
    except KeyboardInterrupt:
        logger.warning("\nAnalysis interrupted by user")
        return 130  # Standard exit code for SIGINT


if __name__ == "__main__":
    sys.exit(main())
