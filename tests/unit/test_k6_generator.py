"""Tests for K6 script generator."""

import tempfile
from pathlib import Path

import pytest

from src.k6_generator import K6ScriptGenerator
from src.models.k6_config import (
    Environment,
    Intensity,
    LoadTestConfig,
    TestMode,
)


class TestK6ScriptGenerator:
    """Tests for K6ScriptGenerator class."""

    @pytest.fixture
    def generator(self) -> K6ScriptGenerator:
        """Create generator instance."""
        return K6ScriptGenerator()

    @pytest.fixture
    def product_config(self) -> LoadTestConfig:
        """Create product page config."""
        return LoadTestConfig(
            url="https://preprod.ipln.fr/product-123.html",
            page_type="product",
            environment=Environment.PREPROD,
            intensity=Intensity.MEDIUM,
            mode=TestMode.FULL,
            id_product=123,
            id_product_attribute=456,
        )

    @pytest.fixture
    def homepage_config(self) -> LoadTestConfig:
        """Create homepage config."""
        return LoadTestConfig(
            url="https://preprod.ipln.fr/",
            page_type="homepage",
            environment=Environment.PREPROD,
            intensity=Intensity.LIGHT,
        )

    def test_init_default_templates_dir(self) -> None:
        """Test generator initialization with default templates directory."""
        generator = K6ScriptGenerator()
        assert generator.templates_dir.exists()
        assert generator.templates_dir.name == "templates"

    def test_init_custom_templates_dir(self, tmp_path: Path) -> None:
        """Test generator initialization with custom templates directory."""
        templates_dir = tmp_path / "custom_templates"
        templates_dir.mkdir()

        generator = K6ScriptGenerator(templates_dir)
        assert generator.templates_dir == templates_dir

    def test_init_nonexistent_templates_dir(self) -> None:
        """Test generator initialization with nonexistent directory fails."""
        with pytest.raises(FileNotFoundError, match="Templates directory not found"):
            K6ScriptGenerator("/nonexistent/path")

    def test_get_template_name(self, generator: K6ScriptGenerator) -> None:
        """Test template name generation."""
        assert generator._get_template_name("product") == "template_product.js"
        assert generator._get_template_name("homepage") == "template_homepage.js"
        assert generator._get_template_name("category") == "template_category.js"
        assert generator._get_template_name("landing") == "template_landing.js"

    def test_load_template_success(self, generator: K6ScriptGenerator) -> None:
        """Test loading existing template."""
        template = generator._load_template("product")
        assert template is not None

    def test_load_template_not_found(self, generator: K6ScriptGenerator) -> None:
        """Test loading nonexistent template fails."""
        with pytest.raises(FileNotFoundError, match="Template not found"):
            generator._load_template("nonexistent")  # type: ignore[arg-type]

    def test_validate_templates(self, generator: K6ScriptGenerator) -> None:
        """Test template validation."""
        results = generator.validate_templates()

        assert results["product"] is True
        assert results["homepage"] is True
        assert results["category"] is True
        assert results["landing"] is True

    def test_list_available_templates(self, generator: K6ScriptGenerator) -> None:
        """Test listing available templates."""
        templates = generator.list_available_templates()

        assert "template_product.js" in templates
        assert "template_homepage.js" in templates
        assert "template_category.js" in templates
        assert "template_landing.js" in templates
        assert len(templates) == 4

    def test_generate_product_page_script(
        self, generator: K6ScriptGenerator, product_config: LoadTestConfig
    ) -> None:
        """Test generating script for product page."""
        script = generator.generate(product_config)

        # Check basic structure
        assert "import http from 'k6/http';" in script
        assert "export const options" in script
        assert "export default function()" in script
        assert "export function setup()" in script
        assert "export function teardown(data)" in script

        # Check configuration injected
        assert product_config.url in script
        assert "preprod" in script
        assert "full" in script

        # Check product IDs injected
        assert "123" in script  # id_product
        assert "456" in script  # id_product_attribute

        # Check stages
        assert "stages: [" in script
        assert "duration:" in script
        assert "target:" in script

        # Check thresholds
        assert "thresholds: {" in script
        assert "http_req_failed" in script
        assert "http_req_duration" in script
        assert "checks" in script
        assert "abortOnFail" in script

    def test_generate_homepage_script(
        self, generator: K6ScriptGenerator, homepage_config: LoadTestConfig
    ) -> None:
        """Test generating script for homepage."""
        script = generator.generate(homepage_config)

        assert "import http from 'k6/http';" in script
        assert homepage_config.url in script
        assert "homepage" in script
        assert "preprod" in script

        # Homepage specific checks
        assert "homepage_load" in script

    def test_generate_category_script(self, generator: K6ScriptGenerator) -> None:
        """Test generating script for category page."""
        config = LoadTestConfig(
            url="https://preprod.ipln.fr/category/123",
            page_type="category",
            environment=Environment.PREPROD,
            intensity=Intensity.MEDIUM,
        )

        script = generator.generate(config)

        assert "import http from 'k6/http';" in script
        assert config.url in script
        assert "category" in script

    def test_generate_landing_script(self, generator: K6ScriptGenerator) -> None:
        """Test generating script for landing page."""
        config = LoadTestConfig(
            url="https://preprod.ipln.fr/promo/bf2025",
            page_type="landing",
            environment=Environment.PREPROD,
            intensity=Intensity.LIGHT,
        )

        script = generator.generate(config)

        assert "import http from 'k6/http';" in script
        assert config.url in script
        assert "landing" in script

    def test_generate_with_prod_thresholds(
        self, generator: K6ScriptGenerator
    ) -> None:
        """Test generating script with PROD environment thresholds."""
        config = LoadTestConfig(
            url="https://ipln.fr/",
            page_type="homepage",
            environment=Environment.PROD,
            intensity=Intensity.LIGHT,  # Only LIGHT allowed in PROD
        )

        script = generator.generate(config)

        # Check PROD-specific thresholds
        assert "rate<0.05" in script  # Stricter error rate for PROD
        assert "p(95)<3000" in script  # Stricter p95 for PROD
        assert "p(99)<5000" in script  # p99 threshold for PROD

    def test_generate_with_preprod_thresholds(
        self, generator: K6ScriptGenerator
    ) -> None:
        """Test generating script with PREPROD environment thresholds."""
        config = LoadTestConfig(
            url="https://preprod.ipln.fr/",
            page_type="homepage",
            environment=Environment.PREPROD,
            intensity=Intensity.HEAVY,
        )

        script = generator.generate(config)

        # Check PREPROD-specific thresholds
        assert "rate<0.10" in script  # Standard error rate for PREPROD
        assert "p(95)<5000" in script  # Standard p95 for PREPROD
        assert "p(99)<8000" in script  # p99 threshold for PREPROD

    def test_generate_stages_light_intensity(
        self, generator: K6ScriptGenerator
    ) -> None:
        """Test stage generation for LIGHT intensity."""
        config = LoadTestConfig(
            url="https://preprod.ipln.fr/",
            page_type="homepage",
            intensity=Intensity.LIGHT,
        )

        script = generator.generate(config)

        # Light intensity = 50 VUs, 2 minutes
        assert "target: 50" in script

    def test_generate_stages_medium_intensity(
        self, generator: K6ScriptGenerator
    ) -> None:
        """Test stage generation for MEDIUM intensity."""
        config = LoadTestConfig(
            url="https://preprod.ipln.fr/",
            page_type="homepage",
            intensity=Intensity.MEDIUM,
        )

        script = generator.generate(config)

        # Medium intensity = 200 VUs, 5 minutes
        assert "target: 200" in script

    def test_generate_stages_heavy_intensity(
        self, generator: K6ScriptGenerator
    ) -> None:
        """Test stage generation for HEAVY intensity."""
        config = LoadTestConfig(
            url="https://preprod.ipln.fr/",
            page_type="homepage",
            intensity=Intensity.HEAVY,
        )

        script = generator.generate(config)

        # Heavy intensity = 500 VUs, 10 minutes
        assert "target: 500" in script

    def test_generate_read_only_mode(self, generator: K6ScriptGenerator) -> None:
        """Test generating script in READ_ONLY mode."""
        config = LoadTestConfig(
            url="https://preprod.ipln.fr/product-123.html",
            page_type="product",
            mode=TestMode.READ_ONLY,
            id_product=123,
        )

        script = generator.generate(config)

        assert "read_only" in script
        # In read_only mode, no POST to cart
        # The template should not include add-to-cart logic

    def test_generate_full_mode(self, generator: K6ScriptGenerator) -> None:
        """Test generating script in FULL mode."""
        config = LoadTestConfig(
            url="https://preprod.ipln.fr/product-123.html",
            page_type="product",
            mode=TestMode.FULL,
            id_product=123,
        )

        script = generator.generate(config)

        assert "full" in script
        # In full mode, should include add-to-cart logic
        assert "add_to_cart" in script or "cart" in script.lower()

    def test_generate_to_file(
        self, generator: K6ScriptGenerator, product_config: LoadTestConfig
    ) -> None:
        """Test generating script to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_script.js"
            result_path = generator.generate_to_file(product_config, output_path)

            assert result_path == output_path
            assert output_path.exists()
            assert output_path.is_file()

            # Check content
            content = output_path.read_text(encoding="utf-8")
            assert "import http from 'k6/http';" in content
            assert product_config.url in content

    def test_generate_to_file_creates_parent_dir(
        self, generator: K6ScriptGenerator, product_config: LoadTestConfig
    ) -> None:
        """Test that generate_to_file creates parent directory if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "subdir" / "test_script.js"
            assert not output_path.parent.exists()

            result_path = generator.generate_to_file(product_config, output_path)

            assert result_path == output_path
            assert output_path.parent.exists()
            assert output_path.exists()

    def test_generate_with_all_threshold_types(
        self, generator: K6ScriptGenerator
    ) -> None:
        """Test that all threshold types are included in generated script."""
        config = LoadTestConfig(
            url="https://preprod.ipln.fr/",
            page_type="homepage",
        )

        script = generator.generate(config)

        # Check all threshold rules are present
        assert "http_req_failed" in script
        assert "http_req_duration" in script
        assert "checks" in script

        # Check abort conditions
        assert "abortOnFail: true" in script
        assert "abortOnFail: false" in script  # Alert-only threshold

        # Check delay
        assert "delayAbortEval" in script

    def test_generate_without_product_ids(self, generator: K6ScriptGenerator) -> None:
        """Test generating product script without product IDs in read-only mode."""
        config = LoadTestConfig(
            url="https://preprod.ipln.fr/product-123.html",
            page_type="product",
            mode=TestMode.READ_ONLY,
            # No id_product - OK for read-only
        )

        script = generator.generate(config)
        assert script is not None
        assert config.url in script


class TestK6GeneratorEdgeCases:
    """Test edge cases and error handling."""

    def test_generate_with_special_chars_in_url(self) -> None:
        """Test generating script with special characters in URL."""
        generator = K6ScriptGenerator()
        config = LoadTestConfig(
            url="https://preprod.ipln.fr/product-abc123?promo=BF2025&source=email",
            page_type="product",
            mode=TestMode.READ_ONLY,
        )

        script = generator.generate(config)
        assert config.url in script

    def test_list_templates_empty_directory(self, tmp_path: Path) -> None:
        """Test listing templates in empty directory."""
        templates_dir = tmp_path / "empty"
        templates_dir.mkdir()

        generator = K6ScriptGenerator(templates_dir)
        templates = generator.list_available_templates()

        assert templates == []

    def test_validate_templates_missing_template(self, tmp_path: Path) -> None:
        """Test validation with missing template."""
        templates_dir = tmp_path / "incomplete"
        templates_dir.mkdir()

        # Create only one template
        (templates_dir / "template_product.js").write_text("// test")

        generator = K6ScriptGenerator(templates_dir)
        results = generator.validate_templates()

        assert results["product"] is True
        assert results["homepage"] is False
        assert results["category"] is False
        assert results["landing"] is False
