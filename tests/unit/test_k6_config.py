"""Tests for K6 configuration models."""

import pytest
from pydantic import ValidationError

from src.models.k6_config import (
    Environment,
    Intensity,
    IntensityConfig,
    LoadTestConfig,
    Stage,
    TestMode,
    ThresholdConfig,
    ThresholdRule,
)


class TestStage:
    """Tests for Stage model."""

    def test_create_valid_stage(self) -> None:
        """Test creating a valid stage."""
        stage = Stage(duration="1m", target=200)
        assert stage.duration == "1m"
        assert stage.target == 200

    def test_stage_with_seconds(self) -> None:
        """Test stage with seconds duration."""
        stage = Stage(duration="30s", target=50)
        assert stage.duration == "30s"
        assert stage.target == 50

    def test_stage_with_hours(self) -> None:
        """Test stage with hours duration."""
        stage = Stage(duration="1h", target=100)
        assert stage.duration == "1h"
        assert stage.target == 100

    def test_stage_invalid_duration_format(self) -> None:
        """Test stage with invalid duration format."""
        with pytest.raises(ValidationError, match="Duration must end with"):
            Stage(duration="1x", target=100)

    def test_stage_invalid_duration_no_number(self) -> None:
        """Test stage with non-numeric duration."""
        with pytest.raises(ValidationError, match="Duration must end with"):
            Stage(duration="abc", target=100)

    def test_stage_target_too_low(self) -> None:
        """Test stage with target below minimum."""
        with pytest.raises(ValidationError):
            Stage(duration="1m", target=-1)

    def test_stage_target_too_high(self) -> None:
        """Test stage with target above maximum."""
        with pytest.raises(ValidationError):
            Stage(duration="1m", target=1001)


class TestThresholdRule:
    """Tests for ThresholdRule model."""

    def test_create_threshold_rule(self) -> None:
        """Test creating a threshold rule."""
        rule = ThresholdRule(
            threshold="rate<0.10",
            abort_on_fail=True,
            delay_abort_eval="10s",
        )
        assert rule.threshold == "rate<0.10"
        assert rule.abort_on_fail is True
        assert rule.delay_abort_eval == "10s"

    def test_threshold_rule_defaults(self) -> None:
        """Test threshold rule with defaults."""
        rule = ThresholdRule(threshold="p(95)<5000")
        assert rule.abort_on_fail is True  # Default
        assert rule.delay_abort_eval is None


class TestThresholdConfig:
    """Tests for ThresholdConfig model."""

    def test_create_empty_threshold_config(self) -> None:
        """Test creating empty threshold config."""
        config = ThresholdConfig()
        assert config.http_req_failed == []
        assert config.http_req_duration == []
        assert config.checks == []

    def test_threshold_config_for_prod(self) -> None:
        """Test creating threshold config for PROD environment."""
        config = ThresholdConfig.for_environment(Environment.PROD)

        # Check stricter PROD thresholds
        assert len(config.http_req_failed) == 1
        assert config.http_req_failed[0].threshold == "rate<0.05"
        assert config.http_req_failed[0].abort_on_fail is True

        assert len(config.http_req_duration) == 3
        assert config.http_req_duration[0].threshold == "p(95)<3000"
        assert config.http_req_duration[1].threshold == "p(99)<5000"
        assert config.http_req_duration[2].threshold == "p(95)<2000"
        assert config.http_req_duration[2].abort_on_fail is False  # Alert only

        assert len(config.checks) == 1
        assert config.checks[0].threshold == "rate>0.80"

    def test_threshold_config_for_preprod(self) -> None:
        """Test creating threshold config for PREPROD environment."""
        config = ThresholdConfig.for_environment(Environment.PREPROD)

        # Check standard PREPROD thresholds
        assert len(config.http_req_failed) == 1
        assert config.http_req_failed[0].threshold == "rate<0.10"

        assert len(config.http_req_duration) == 3
        assert config.http_req_duration[0].threshold == "p(95)<5000"
        assert config.http_req_duration[1].threshold == "p(99)<8000"
        assert config.http_req_duration[2].threshold == "p(95)<2000"
        assert config.http_req_duration[2].abort_on_fail is False


class TestIntensityConfig:
    """Tests for IntensityConfig model."""

    def test_create_intensity_config(self) -> None:
        """Test creating intensity config."""
        config = IntensityConfig(vus=200, duration_minutes=5)
        assert config.vus == 200
        assert config.duration_minutes == 5

    def test_intensity_for_light(self) -> None:
        """Test light intensity configuration."""
        config = IntensityConfig.for_intensity(Intensity.LIGHT, Environment.PREPROD)
        assert config.vus == 50
        assert config.duration_minutes == 2

    def test_intensity_for_medium(self) -> None:
        """Test medium intensity configuration."""
        config = IntensityConfig.for_intensity(Intensity.MEDIUM, Environment.PREPROD)
        assert config.vus == 200
        assert config.duration_minutes == 5

    def test_intensity_for_heavy(self) -> None:
        """Test heavy intensity configuration."""
        config = IntensityConfig.for_intensity(Intensity.HEAVY, Environment.PREPROD)
        assert config.vus == 500
        assert config.duration_minutes == 10

    def test_intensity_limited_in_prod(self) -> None:
        """Test that VUs are limited in PROD environment."""
        # Medium would normally be 200 VUs, but PROD limits to 50
        config = IntensityConfig.for_intensity(Intensity.MEDIUM, Environment.PROD)
        assert config.vus == 50
        assert config.duration_minutes == 5

        # Heavy would normally be 500 VUs, but PROD limits to 50
        config = IntensityConfig.for_intensity(Intensity.HEAVY, Environment.PROD)
        assert config.vus == 50
        assert config.duration_minutes == 10

    def test_to_stages(self) -> None:
        """Test converting intensity config to stages."""
        config = IntensityConfig(vus=200, duration_minutes=5)
        stages = config.to_stages()

        assert len(stages) == 3
        # Ramp up
        assert stages[0].duration == "1m"
        assert stages[0].target == 200
        # Sustain
        assert stages[1].duration == "3m"
        assert stages[1].target == 200
        # Ramp down
        assert stages[2].duration == "30s"
        assert stages[2].target == 0

    def test_to_stages_short_duration(self) -> None:
        """Test stages for short duration test."""
        config = IntensityConfig(vus=50, duration_minutes=2)
        stages = config.to_stages()

        assert len(stages) == 3
        # Ramp up is at least 1 minute
        assert stages[0].target == 50
        assert stages[2].target == 0


class TestLoadTestConfig:
    """Tests for LoadTestConfig model."""

    def test_create_basic_config(self) -> None:
        """Test creating basic load test config."""
        config = LoadTestConfig(
            url="https://preprod.ipln.fr/",
            page_type="homepage",
        )
        assert config.url == "https://preprod.ipln.fr/"
        assert config.page_type == "homepage"
        assert config.environment == Environment.PREPROD  # Default
        assert config.intensity == Intensity.MEDIUM  # Default
        assert config.mode == TestMode.READ_ONLY  # Default

    def test_create_product_config(self) -> None:
        """Test creating product page config."""
        config = LoadTestConfig(
            url="https://preprod.ipln.fr/product-123.html",
            page_type="product",
            mode=TestMode.FULL,
            id_product=123,
            id_product_attribute=456,
        )
        assert config.page_type == "product"
        assert config.mode == TestMode.FULL
        assert config.id_product == 123
        assert config.id_product_attribute == 456

    def test_product_full_mode_requires_id(self) -> None:
        """Test that product page in FULL mode requires id_product."""
        with pytest.raises(
            ValidationError, match="id_product is required for product pages in FULL mode"
        ):
            LoadTestConfig(
                url="https://preprod.ipln.fr/product.html",
                page_type="product",
                mode=TestMode.FULL,
                # Missing id_product
            )

    def test_product_read_only_without_id(self) -> None:
        """Test that product page in READ_ONLY mode doesn't require id_product."""
        config = LoadTestConfig(
            url="https://preprod.ipln.fr/product.html",
            page_type="product",
            mode=TestMode.READ_ONLY,
            # No id_product - OK for read-only
        )
        assert config.mode == TestMode.READ_ONLY
        assert config.id_product is None

    def test_prod_rejects_heavy_intensity(self) -> None:
        """Test that PROD environment rejects HEAVY intensity."""
        with pytest.raises(
            ValidationError, match="HEAVY intensity not allowed in PROD"
        ):
            LoadTestConfig(
                url="https://ipln.fr/",
                page_type="homepage",
                environment=Environment.PROD,
                intensity=Intensity.HEAVY,
            )

    def test_prod_allows_light_intensity(self) -> None:
        """Test that PROD environment allows LIGHT intensity."""
        config = LoadTestConfig(
            url="https://ipln.fr/",
            page_type="homepage",
            environment=Environment.PROD,
            intensity=Intensity.LIGHT,
        )
        assert config.environment == Environment.PROD
        assert config.intensity == Intensity.LIGHT

    def test_prod_allows_medium_intensity(self) -> None:
        """Test that PROD environment allows MEDIUM intensity (but VUs limited)."""
        config = LoadTestConfig(
            url="https://ipln.fr/",
            page_type="homepage",
            environment=Environment.PROD,
            intensity=Intensity.MEDIUM,
        )
        assert config.environment == Environment.PROD
        assert config.intensity == Intensity.MEDIUM

        # Check that VUs are limited to 50
        intensity_config = config.get_intensity_config()
        assert intensity_config.vus == 50

    def test_get_intensity_config(self) -> None:
        """Test getting intensity configuration."""
        config = LoadTestConfig(
            url="https://preprod.ipln.fr/",
            page_type="homepage",
            intensity=Intensity.MEDIUM,
        )
        intensity_config = config.get_intensity_config()
        assert intensity_config.vus == 200
        assert intensity_config.duration_minutes == 5

    def test_get_threshold_config(self) -> None:
        """Test getting threshold configuration."""
        config = LoadTestConfig(
            url="https://preprod.ipln.fr/",
            page_type="homepage",
            environment=Environment.PREPROD,
        )
        threshold_config = config.get_threshold_config()
        assert len(threshold_config.http_req_failed) == 1
        assert threshold_config.http_req_failed[0].threshold == "rate<0.10"

    def test_get_stages(self) -> None:
        """Test getting K6 stages."""
        config = LoadTestConfig(
            url="https://preprod.ipln.fr/",
            page_type="homepage",
            intensity=Intensity.LIGHT,
        )
        stages = config.get_stages()
        assert len(stages) == 3
        assert stages[0].target == 50
        assert stages[2].target == 0

    def test_all_page_types(self) -> None:
        """Test all supported page types."""
        page_types = ["product", "homepage", "category", "landing"]
        for page_type in page_types:
            config = LoadTestConfig(
                url=f"https://preprod.ipln.fr/{page_type}",
                page_type=page_type,  # type: ignore[arg-type]
            )
            assert config.page_type == page_type

    def test_invalid_page_type(self) -> None:
        """Test that invalid page type is rejected."""
        with pytest.raises(ValidationError):
            LoadTestConfig(
                url="https://preprod.ipln.fr/",
                page_type="invalid",  # type: ignore[arg-type]
            )

    def test_category_page_config(self) -> None:
        """Test creating category page config."""
        config = LoadTestConfig(
            url="https://preprod.ipln.fr/category/123",
            page_type="category",
            intensity=Intensity.MEDIUM,
        )
        assert config.page_type == "category"
        assert config.intensity == Intensity.MEDIUM

    def test_landing_page_config(self) -> None:
        """Test creating landing page config."""
        config = LoadTestConfig(
            url="https://preprod.ipln.fr/promo/bf2025",
            page_type="landing",
            intensity=Intensity.LIGHT,
        )
        assert config.page_type == "landing"
        assert config.intensity == Intensity.LIGHT


class TestEnums:
    """Tests for enum types."""

    def test_environment_enum(self) -> None:
        """Test Environment enum."""
        assert Environment.PROD.value == "prod"
        assert Environment.PREPROD.value == "preprod"

    def test_intensity_enum(self) -> None:
        """Test Intensity enum."""
        assert Intensity.LIGHT.value == "light"
        assert Intensity.MEDIUM.value == "medium"
        assert Intensity.HEAVY.value == "heavy"

    def test_test_mode_enum(self) -> None:
        """Test TestMode enum."""
        assert TestMode.READ_ONLY.value == "read_only"
        assert TestMode.FULL.value == "full"
