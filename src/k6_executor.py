"""K6 load test executor and results parser."""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from loguru import logger

from src.models.k6_config import LoadTestConfig
from src.models.k6_results import K6ExecutionResult, K6Metrics


class K6ExecutionError(Exception):
    """Raised when K6 execution fails."""

    pass


class K6Executor:
    """Executes K6 load test scripts and parses results."""

    def __init__(
        self,
        k6_binary: str = "k6",
        timeout_seconds: int = 3600,
    ) -> None:
        """Initialize K6 executor.

        Args:
            k6_binary: Path to K6 binary (default: "k6" in PATH)
            timeout_seconds: Maximum execution time in seconds (default: 1 hour)
        """
        self.k6_binary = k6_binary
        self.timeout_seconds = timeout_seconds

    def execute_script(
        self,
        script_path: Path,
        config: LoadTestConfig,
    ) -> K6ExecutionResult:
        """Execute a K6 script and return results.

        Args:
            script_path: Path to K6 script file
            config: Load test configuration used to generate the script

        Returns:
            K6ExecutionResult with metrics and analysis

        Raises:
            K6ExecutionError: If K6 execution fails
            FileNotFoundError: If K6 binary or script not found
        """
        if not script_path.exists():
            raise FileNotFoundError(f"K6 script not found: {script_path}")

        # Create temporary file for JSON output
        with tempfile.NamedTemporaryFile(
            mode="w+", suffix=".json", delete=False
        ) as json_output:
            json_output_path = Path(json_output.name)

        try:
            # Run K6 with JSON output
            start_time = self._get_current_time()

            cmd = [
                self.k6_binary,
                "run",
                "--out",
                f"json={json_output_path}",
                str(script_path),
            ]

            logger.info(f"Executing K6: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,  # Don't raise on non-zero exit
            )

            end_time = self._get_current_time()
            duration_seconds = end_time - start_time

            # Check if K6 ran successfully
            if result.returncode != 0:
                # K6 returns non-zero if thresholds failed, but that's expected
                # Only fail if it's a real error (e.g., script syntax error)
                if "ERRO" in result.stderr or result.returncode >= 100:
                    error_msg = self._extract_error_message(result.stderr)
                    logger.error(f"K6 execution failed: {error_msg}")
                    return K6ExecutionResult(
                        url=config.url,
                        page_type=config.page_type,
                        environment=config.environment.value,
                        intensity=config.intensity.value,
                        success=False,
                        duration_seconds=duration_seconds,
                        threshold_failed=False,
                        error_message=error_msg,
                    )

            # Parse JSON output
            metrics = self._parse_k6_output(json_output_path)

            # Determine if thresholds failed
            threshold_failed = result.returncode != 0

            return K6ExecutionResult(
                url=config.url,
                page_type=config.page_type,
                environment=config.environment.value,
                intensity=config.intensity.value,
                success=True,
                duration_seconds=duration_seconds,
                threshold_failed=threshold_failed,
                metrics=metrics,
            )

        except subprocess.TimeoutExpired:
            logger.error(f"K6 execution timed out after {self.timeout_seconds}s")
            return K6ExecutionResult(
                url=config.url,
                page_type=config.page_type,
                environment=config.environment.value,
                intensity=config.intensity.value,
                success=False,
                duration_seconds=self.timeout_seconds,
                threshold_failed=False,
                error_message=f"Execution timed out after {self.timeout_seconds} seconds",
            )
        except FileNotFoundError as exc:
            logger.error(f"K6 binary not found: {self.k6_binary}")
            raise FileNotFoundError(
                f"K6 binary not found: {self.k6_binary}. Install K6: https://k6.io/docs/get-started/installation/"
            ) from exc
        finally:
            # Clean up temporary JSON file
            if json_output_path.exists():
                try:
                    json_output_path.unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete temp file: {e}")

    def _parse_k6_output(self, json_path: Path) -> K6Metrics:
        """Parse K6 JSON output to extract metrics.

        K6 outputs NDJSON (newline-delimited JSON) with "Point" entries
        containing metrics.

        Args:
            json_path: Path to K6 JSON output file

        Returns:
            K6Metrics with parsed values

        Raises:
            K6ExecutionError: If parsing fails
        """
        metrics_data: dict[str, Any] = {}

        try:
            with open(json_path, encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue

                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    # Only process "Point" entries (metric data points)
                    if entry.get("type") != "Point":
                        continue

                    metric_name = entry.get("metric")
                    data = entry.get("data", {})

                    # Extract values based on metric type
                    if metric_name == "http_req_duration":
                        metrics_data["http_req_duration_min"] = data.get("min", 0)
                        metrics_data["http_req_duration_avg"] = data.get("avg", 0)
                        metrics_data["http_req_duration_p95"] = data.get(
                            "p(95)", data.get("p95", 0)
                        )
                        metrics_data["http_req_duration_p99"] = data.get(
                            "p(99)", data.get("p99", 0)
                        )
                        metrics_data["http_req_duration_max"] = data.get("max", 0)
                    elif metric_name == "http_reqs":
                        metrics_data["http_req_total_count"] = int(
                            data.get("count", 0)
                        )
                    elif metric_name == "http_req_failed":
                        metrics_data["http_req_failed_rate"] = data.get("rate", 0)
                        metrics_data["http_req_failed_count"] = int(
                            data.get("count", 0)
                        )
                    elif metric_name == "checks":
                        metrics_data["checks_rate"] = data.get("rate", 1.0)
                    elif metric_name == "vus_max":
                        metrics_data["vus_max"] = int(data.get("value", 0))
                    elif metric_name == "iterations":
                        metrics_data["iterations"] = int(data.get("count", 0))
                    elif metric_name == "data_received":
                        metrics_data["data_received_bytes"] = int(data.get("count", 0))
                    elif metric_name == "data_sent":
                        metrics_data["data_sent_bytes"] = int(data.get("count", 0))

            # Validate we got required metrics
            required_fields = [
                "http_req_duration_min",
                "http_req_duration_avg",
                "http_req_duration_p95",
                "http_req_duration_p99",
                "http_req_duration_max",
                "http_req_failed_rate",
                "http_req_total_count",
            ]

            missing = [f for f in required_fields if f not in metrics_data]
            if missing:
                raise K6ExecutionError(
                    f"Failed to extract required metrics: {', '.join(missing)}"
                )

            # Set defaults for optional fields
            metrics_data.setdefault("http_req_failed_count", 0)
            metrics_data.setdefault("checks_rate", 1.0)
            metrics_data.setdefault("vus_max", 0)
            metrics_data.setdefault("iterations", 0)
            metrics_data.setdefault("data_received_bytes", 0)
            metrics_data.setdefault("data_sent_bytes", 0)

            return K6Metrics(**metrics_data)

        except Exception as exc:
            raise K6ExecutionError(f"Failed to parse K6 output: {exc}") from exc

    def _extract_error_message(self, stderr: str) -> str:
        """Extract meaningful error message from K6 stderr.

        Args:
            stderr: K6 stderr output

        Returns:
            Extracted error message
        """
        # Look for error patterns
        for line in stderr.split("\n"):
            line = line.strip()
            if "ERRO" in line or "Error" in line or "error" in line:
                # Remove ANSI color codes and timestamps
                line = line.split("ERRO")[-1].strip() if "ERRO" in line else line
                return line[:200]  # Limit length

        return "K6 execution failed (see logs for details)"

    def _get_current_time(self) -> float:
        """Get current time in seconds.

        Returns:
            Current timestamp
        """
        import time

        return time.time()

    def check_k6_available(self) -> bool:
        """Check if K6 is available in the system.

        Returns:
            True if K6 is available, False otherwise
        """
        try:
            result = subprocess.run(
                [self.k6_binary, "version"],
                capture_output=True,
                timeout=5,
                check=False,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
