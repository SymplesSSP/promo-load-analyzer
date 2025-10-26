"""Configuration management for Promo Load Analyzer.

This module loads configuration from environment variables and .env files,
providing type-safe access to all configuration parameters.
"""

import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings


# Load .env file if it exists
load_dotenv()


class Config(BaseSettings):
    """Application configuration loaded from environment variables."""

    # PrestaShop API Configuration
    prestashop_api_url: str | None = Field(
        default=None, description="PrestaShop API base URL"
    )
    prestashop_api_key: str | None = Field(
        default=None, description="PrestaShop API key"
    )

    # Environment Configuration
    default_environment: Literal["PREPROD", "PROD"] = Field(
        default="PREPROD", description="Default execution environment"
    )

    # PROD Safety Constraints
    prod_time_window_start: str = Field(
        default="03:00", description="PROD test start time (HH:MM)"
    )
    prod_time_window_end: str = Field(
        default="06:00", description="PROD test end time (HH:MM)"
    )
    prod_max_vus: int = Field(
        default=50, description="Maximum VUs for PROD", ge=1, le=100
    )
    prod_max_duration_minutes: int = Field(
        default=30, description="Maximum test duration for PROD (minutes)", ge=1
    )

    # K6 Configuration
    k6_binary_path: str = Field(default="k6", description="Path to K6 binary")
    default_vus: int = Field(
        default=10, description="Default virtual users for PREPROD", ge=1
    )
    default_duration: str = Field(
        default="5m", description="Default test duration"
    )
    default_ramp_up_time: str = Field(
        default="30s", description="Default ramp-up time"
    )

    # Logging Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging level"
    )
    log_file_path: Path = Field(
        default=Path("logs/promo_analyzer.log"),
        description="Log file path",
    )
    log_rotation: str = Field(
        default="10 MB", description="Log rotation size"
    )
    log_retention: str = Field(
        default="7 days", description="Log retention period"
    )

    # Output Configuration
    output_dir: Path = Field(
        default=Path("output"), description="Output directory"
    )
    k6_scripts_dir: Path = Field(
        default=Path("k6_scripts"), description="K6 scripts directory"
    )
    k6_results_dir: Path = Field(
        default=Path("k6_results"), description="K6 results directory"
    )
    output_format: Literal["JSON", "HTML", "BOTH"] = Field(
        default="BOTH", description="Output format"
    )

    # Playwright Configuration
    browser_type: Literal["chromium", "firefox", "webkit"] = Field(
        default="chromium", description="Browser type"
    )
    headless: bool = Field(
        default=True, description="Run browser in headless mode"
    )
    page_timeout: int = Field(
        default=30000, description="Page load timeout (ms)", ge=1000
    )
    network_timeout: int = Field(
        default=15000, description="Network timeout (ms)", ge=1000
    )

    # Performance Thresholds
    threshold_p95_excellent: int = Field(
        default=500, description="P95 threshold for excellent (ms)"
    )
    threshold_p95_good: int = Field(
        default=1000, description="P95 threshold for good (ms)"
    )
    threshold_p95_acceptable: int = Field(
        default=2000, description="P95 threshold for acceptable (ms)"
    )
    threshold_p95_poor: int = Field(
        default=5000, description="P95 threshold for poor (ms)"
    )

    threshold_error_rate_excellent: float = Field(
        default=0.1, description="Error rate threshold for excellent (%)"
    )
    threshold_error_rate_good: float = Field(
        default=1.0, description="Error rate threshold for good (%)"
    )
    threshold_error_rate_acceptable: float = Field(
        default=5.0, description="Error rate threshold for acceptable (%)"
    )
    threshold_error_rate_poor: float = Field(
        default=10.0, description="Error rate threshold for poor (%)"
    )

    # Development/Debug Settings
    debug_mode: bool = Field(
        default=False, description="Enable debug mode"
    )
    preserve_k6_scripts: bool = Field(
        default=False, description="Preserve K6 scripts after execution"
    )
    enable_http_logging: bool = Field(
        default=False, description="Enable HTTP request/response logging"
    )

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global configuration instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance.

    Returns:
        Config: The application configuration
    """
    return config


def reload_config() -> Config:
    """Reload configuration from environment.

    Useful for testing or when environment variables change.

    Returns:
        Config: The reloaded configuration
    """
    global config
    load_dotenv(override=True)
    config = Config()
    return config
