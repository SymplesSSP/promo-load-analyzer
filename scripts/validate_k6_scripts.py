#!/usr/bin/env python3
"""Validate generated K6 scripts with k6 syntax checker."""

import subprocess
import sys
import tempfile
from pathlib import Path

from src.k6_generator import K6ScriptGenerator
from src.models.k6_config import Environment, Intensity, LoadTestConfig, TestMode


def validate_script_with_k6(script_path: Path) -> tuple[bool, str]:
    """Validate a K6 script using k6 inspect.

    Args:
        script_path: Path to K6 script

    Returns:
        Tuple of (success, message)
    """
    try:
        result = subprocess.run(
            ["k6", "inspect", str(script_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            return True, "Script is valid"
        else:
            return False, f"K6 validation failed:\n{result.stderr}"

    except FileNotFoundError:
        return False, "K6 not found - install it to validate scripts"
    except subprocess.TimeoutExpired:
        return False, "K6 validation timed out"
    except Exception as e:
        return False, f"Validation error: {e}"


def main() -> int:
    """Validate all generated K6 scripts."""
    print("🔍 Validating K6 script generation...\n")

    generator = K6ScriptGenerator()

    # Test configurations
    test_configs = [
        LoadTestConfig(
            url="https://preprod.ipln.fr/product-123.html",
            page_type="product",
            mode=TestMode.FULL,
            id_product=123,
            intensity=Intensity.LIGHT,
        ),
        LoadTestConfig(
            url="https://preprod.ipln.fr/",
            page_type="homepage",
            intensity=Intensity.MEDIUM,
        ),
        LoadTestConfig(
            url="https://preprod.ipln.fr/category/123",
            page_type="category",
            intensity=Intensity.LIGHT,
        ),
        LoadTestConfig(
            url="https://preprod.ipln.fr/promo/bf2025",
            page_type="landing",
            intensity=Intensity.LIGHT,
        ),
        LoadTestConfig(
            url="https://ipln.fr/",
            page_type="homepage",
            environment=Environment.PROD,
            intensity=Intensity.LIGHT,
        ),
    ]

    all_valid = True

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        for i, config in enumerate(test_configs, 1):
            print(f"Test {i}/{len(test_configs)}: {config.page_type} page ({config.environment.value}, {config.intensity.value})")

            # Generate script
            try:
                script_path = tmp_path / f"test_{config.page_type}_{i}.js"
                generator.generate_to_file(config, script_path)
                print(f"  ✓ Script generated: {script_path.name}")
            except Exception as e:
                print(f"  ✗ Generation failed: {e}")
                all_valid = False
                continue

            # Validate with K6
            success, message = validate_script_with_k6(script_path)
            if success:
                print(f"  ✓ K6 validation passed")
            else:
                print(f"  ✗ K6 validation failed")
                print(f"    {message}")
                all_valid = False

            print()

    if all_valid:
        print("✅ All K6 scripts validated successfully!")
        return 0
    else:
        print("❌ Some scripts failed validation")
        return 1


if __name__ == "__main__":
    sys.exit(main())
