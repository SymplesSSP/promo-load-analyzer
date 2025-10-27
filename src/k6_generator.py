"""K6 load test script generator using Jinja2 templates."""

from pathlib import Path
from typing import Any, Literal

from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound

from src.models.k6_config import LoadTestConfig


class K6ScriptGenerator:
    """Generates K6 load test scripts from templates."""

    def __init__(self, templates_dir: str | Path | None = None) -> None:
        """Initialize the K6 script generator.

        Args:
            templates_dir: Path to templates directory. Defaults to ./templates
        """
        if templates_dir is None:
            # Default to templates/ directory at project root
            project_root = Path(__file__).parent.parent
            templates_dir = project_root / "templates"

        self.templates_dir = Path(templates_dir)
        if not self.templates_dir.exists():
            raise FileNotFoundError(
                f"Templates directory not found: {self.templates_dir}"
            )

        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

    def _get_template_name(
        self, page_type: Literal["product", "homepage", "category", "landing"]
    ) -> str:
        """Get template filename for a page type.

        Args:
            page_type: Type of page

        Returns:
            Template filename
        """
        return f"template_{page_type}.js"

    def _load_template(self, page_type: str) -> Template:
        """Load Jinja2 template for a page type.

        Args:
            page_type: Type of page

        Returns:
            Jinja2 Template object

        Raises:
            TemplateNotFound: If template file doesn't exist
        """
        template_name = self._get_template_name(page_type)  # type: ignore[arg-type]
        try:
            return self.env.get_template(template_name)
        except TemplateNotFound as exc:
            raise FileNotFoundError(
                f"Template not found: {self.templates_dir / template_name}"
            ) from exc

    def generate(self, config: LoadTestConfig) -> str:
        """Generate K6 script from configuration.

        Args:
            config: Load test configuration

        Returns:
            Generated K6 script as string

        Raises:
            FileNotFoundError: If template doesn't exist
            ValueError: If configuration is invalid
        """
        # Load template
        template = self._load_template(config.page_type)

        # Get stages and thresholds
        stages = config.get_stages()
        thresholds = config.get_threshold_config()

        # Prepare template context
        context: dict[str, Any] = {
            "url": config.url,
            "page_type": config.page_type,
            "environment": config.environment.value,
            "mode": config.mode.value,
            "stages": [
                {"duration": stage.duration, "target": stage.target}
                for stage in stages
            ],
            "thresholds": {
                "http_req_failed": [
                    {
                        "threshold": rule.threshold,
                        "abort_on_fail": rule.abort_on_fail,
                        "delay_abort_eval": rule.delay_abort_eval,
                    }
                    for rule in thresholds.http_req_failed
                ],
                "http_req_duration": [
                    {
                        "threshold": rule.threshold,
                        "abort_on_fail": rule.abort_on_fail,
                        "delay_abort_eval": rule.delay_abort_eval,
                    }
                    for rule in thresholds.http_req_duration
                ],
                "checks": [
                    {
                        "threshold": rule.threshold,
                        "abort_on_fail": rule.abort_on_fail,
                        "delay_abort_eval": rule.delay_abort_eval,
                    }
                    for rule in thresholds.checks
                ],
            },
        }

        # Add product-specific parameters if present
        if config.id_product is not None:
            context["id_product"] = config.id_product
        if config.id_product_attribute is not None:
            context["id_product_attribute"] = config.id_product_attribute

        # Render template
        script = template.render(**context)
        return script

    def generate_to_file(self, config: LoadTestConfig, output_path: str | Path) -> Path:
        """Generate K6 script and save to file.

        Args:
            config: Load test configuration
            output_path: Path to save generated script

        Returns:
            Path to generated script file

        Raises:
            FileNotFoundError: If template doesn't exist
            ValueError: If configuration is invalid
            OSError: If file cannot be written
        """
        script = self.generate(config)
        output_path = Path(output_path)

        # Create parent directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write script to file
        output_path.write_text(script, encoding="utf-8")

        return output_path

    def validate_templates(self) -> dict[str, bool]:
        """Validate that all required templates exist and can be loaded.

        Returns:
            Dictionary mapping page types to validation status (True if valid)
        """
        page_types: list[Literal["product", "homepage", "category", "landing"]] = [
            "product",
            "homepage",
            "category",
            "landing",
        ]

        results: dict[str, bool] = {}
        for page_type in page_types:
            try:
                self._load_template(page_type)
                results[page_type] = True
            except (FileNotFoundError, TemplateNotFound):
                results[page_type] = False

        return results

    def list_available_templates(self) -> list[str]:
        """List all available template files.

        Returns:
            List of template filenames
        """
        if not self.templates_dir.exists():
            return []

        return [
            f.name
            for f in self.templates_dir.glob("template_*.js")
            if f.is_file()
        ]
