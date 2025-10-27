"""Data models for K6 load test configuration."""

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class Environment(str, Enum):
    """Deployment environment."""

    PROD = "prod"
    PREPROD = "preprod"


class Intensity(str, Enum):
    """Test intensity level."""

    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"


class TestMode(str, Enum):
    """Test execution mode."""

    READ_ONLY = "read_only"  # GET requests only
    FULL = "full"  # GET + POST (add to cart)


class Stage(BaseModel):
    """K6 load test stage configuration."""

    duration: str = Field(..., description="Stage duration (e.g., '1m', '30s')")
    target: int = Field(..., ge=0, le=1000, description="Target VUs for this stage")

    @field_validator("duration")
    @classmethod
    def validate_duration(cls, v: str) -> str:
        """Validate duration format."""
        if not v or not any(v.endswith(unit) for unit in ["s", "m", "h"]):
            raise ValueError("Duration must end with 's', 'm', or 'h'")
        try:
            int(v[:-1])
        except ValueError as exc:
            raise ValueError("Duration must start with a number") from exc
        return v


class ThresholdRule(BaseModel):
    """K6 threshold rule configuration."""

    threshold: str = Field(..., description="Threshold expression (e.g., 'rate<0.10')")
    abort_on_fail: bool = Field(
        default=True, description="Abort test immediately if threshold fails"
    )
    delay_abort_eval: str | None = Field(
        default=None,
        description="Delay before evaluating abort condition (e.g., '10s')",
    )


class ThresholdConfig(BaseModel):
    """K6 thresholds configuration."""

    http_req_failed: list[ThresholdRule] = Field(
        default_factory=list, description="HTTP request failure thresholds"
    )
    http_req_duration: list[ThresholdRule] = Field(
        default_factory=list, description="HTTP request duration thresholds"
    )
    checks: list[ThresholdRule] = Field(
        default_factory=list, description="Check pass rate thresholds"
    )

    @classmethod
    def for_environment(cls, env: Environment) -> "ThresholdConfig":
        """Create threshold configuration for a specific environment.

        Args:
            env: Target environment (PROD or PREPROD)

        Returns:
            ThresholdConfig with appropriate safety thresholds
        """
        if env == Environment.PROD:
            # Strict thresholds for production
            return cls(
                http_req_failed=[
                    ThresholdRule(
                        threshold="rate<0.05",  # Max 5% errors
                        abort_on_fail=True,
                        delay_abort_eval="10s",
                    )
                ],
                http_req_duration=[
                    ThresholdRule(
                        threshold="p(95)<3000",  # p95 < 3s
                        abort_on_fail=True,
                    ),
                    ThresholdRule(
                        threshold="p(99)<5000",  # p99 < 5s
                        abort_on_fail=True,
                    ),
                    ThresholdRule(
                        threshold="p(95)<2000",  # Alert only
                        abort_on_fail=False,
                    ),
                ],
                checks=[
                    ThresholdRule(
                        threshold="rate>0.80",  # Min 80% checks pass
                        abort_on_fail=True,
                        delay_abort_eval="10s",
                    )
                ],
            )
        else:
            # Standard thresholds for preprod
            return cls(
                http_req_failed=[
                    ThresholdRule(
                        threshold="rate<0.10",  # Max 10% errors
                        abort_on_fail=True,
                        delay_abort_eval="10s",
                    )
                ],
                http_req_duration=[
                    ThresholdRule(
                        threshold="p(95)<5000",  # p95 < 5s
                        abort_on_fail=True,
                    ),
                    ThresholdRule(
                        threshold="p(99)<8000",  # p99 < 8s
                        abort_on_fail=True,
                    ),
                    ThresholdRule(
                        threshold="p(95)<2000",  # Alert only
                        abort_on_fail=False,
                    ),
                ],
                checks=[
                    ThresholdRule(
                        threshold="rate>0.80",  # Min 80% checks pass
                        abort_on_fail=True,
                        delay_abort_eval="10s",
                    )
                ],
            )


class IntensityConfig(BaseModel):
    """Configuration for test intensity levels."""

    vus: int = Field(..., ge=1, le=1000, description="Number of virtual users")
    duration_minutes: int = Field(
        ..., ge=1, le=60, description="Total test duration in minutes"
    )

    @classmethod
    def for_intensity(
        cls, intensity: Intensity, env: Environment
    ) -> "IntensityConfig":
        """Get configuration for a specific intensity level.

        Args:
            intensity: Test intensity level
            env: Target environment (affects max VUs for PROD)

        Returns:
            IntensityConfig with appropriate VUs and duration
        """
        configs = {
            Intensity.LIGHT: cls(vus=50, duration_minutes=2),
            Intensity.MEDIUM: cls(vus=200, duration_minutes=5),
            Intensity.HEAVY: cls(vus=500, duration_minutes=10),
        }

        config = configs[intensity]

        # Limit VUs for production environment
        if env == Environment.PROD and config.vus > 50:
            config = cls(vus=50, duration_minutes=config.duration_minutes)

        return config

    def to_stages(self) -> list[Stage]:
        """Convert intensity config to K6 stages.

        Returns:
            List of Stage objects for ramp-up, sustain, ramp-down
        """
        ramp_up = max(1, self.duration_minutes // 5)  # 20% of time for ramp-up
        sustain = self.duration_minutes - ramp_up - 1  # Majority sustains load

        return [
            Stage(duration=f"{ramp_up}m", target=self.vus),
            Stage(duration=f"{sustain}m", target=self.vus),
            Stage(duration="30s", target=0),  # Quick ramp-down
        ]


class LoadTestConfig(BaseModel):
    """Complete K6 load test configuration."""

    url: str = Field(..., description="Target URL to test")
    page_type: Literal["product", "homepage", "category", "landing"] = Field(
        ..., description="Type of page being tested"
    )
    environment: Environment = Field(
        default=Environment.PREPROD, description="Target environment"
    )
    intensity: Intensity = Field(
        default=Intensity.MEDIUM, description="Test intensity level"
    )
    mode: TestMode = Field(
        default=TestMode.READ_ONLY, description="Test execution mode"
    )

    # Optional product-specific parameters
    id_product: int | None = Field(
        default=None, ge=1, description="Product ID (for product pages)"
    )
    id_product_attribute: int | None = Field(
        default=None, ge=1, description="Product attribute ID (for product variations)"
    )

    @model_validator(mode="after")
    def validate_product_page(self) -> "LoadTestConfig":
        """Validate that product pages have required IDs."""
        if self.page_type == "product" and self.mode == TestMode.FULL:
            if self.id_product is None:
                raise ValueError(
                    "id_product is required for product pages in FULL mode"
                )
        return self

    @model_validator(mode="after")
    def validate_prod_constraints(self) -> "LoadTestConfig":
        """Validate production environment constraints."""
        if self.environment == Environment.PROD:
            # Production constraints
            if self.intensity == Intensity.HEAVY:
                raise ValueError("HEAVY intensity not allowed in PROD environment")

            if self.mode == TestMode.FULL:
                # Full mode (with POST) should only be used during allowed hours
                # This will be validated at runtime by the executor
                pass

        return self

    def get_intensity_config(self) -> IntensityConfig:
        """Get intensity configuration for this load test."""
        return IntensityConfig.for_intensity(self.intensity, self.environment)

    def get_threshold_config(self) -> ThresholdConfig:
        """Get threshold configuration for this load test."""
        return ThresholdConfig.for_environment(self.environment)

    def get_stages(self) -> list[Stage]:
        """Get K6 stages for this load test."""
        return self.get_intensity_config().to_stages()
