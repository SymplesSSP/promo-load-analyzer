"""Analyze K6 test results and calculate performance scores."""

from loguru import logger

from src.models.k6_results import (
    K6ExecutionResult,
    PerformanceGrade,
    ScoreThresholds,
)


class ResultsAnalyzer:
    """Analyzes K6 test results and calculates performance grades."""

    def __init__(self, thresholds: ScoreThresholds | None = None) -> None:
        """Initialize results analyzer.

        Args:
            thresholds: Custom score thresholds (uses defaults if not provided)
        """
        self.thresholds = thresholds or ScoreThresholds()

    def analyze(self, result: K6ExecutionResult) -> K6ExecutionResult:
        """Analyze test results and add grades and estimates.

        Args:
            result: K6 execution result to analyze

        Returns:
            Updated result with analysis fields populated
        """
        if not result.success or result.metrics is None:
            logger.warning("Cannot analyze failed test result")
            return result

        metrics = result.metrics

        # Calculate response time grade
        rt_grade, rt_score = self.thresholds.calculate_response_time_grade(
            metrics.http_req_duration_p95
        )
        result.response_time_grade = PerformanceGrade(
            grade=rt_grade,
            score=rt_score,
            description=self._get_response_time_description(rt_grade),
        )

        # Calculate error rate grade
        err_grade, err_score = self.thresholds.calculate_error_rate_grade(
            metrics.http_req_failed_rate
        )
        result.error_rate_grade = PerformanceGrade(
            grade=err_grade,
            score=err_score,
            description=self._get_error_rate_description(err_grade),
        )

        # Calculate overall grade
        overall_grade, overall_score = self.thresholds.calculate_overall_grade(
            rt_score, err_score
        )
        result.overall_grade = PerformanceGrade(
            grade=overall_grade,
            score=overall_score,
            description=self._get_overall_description(overall_grade),
        )

        # Estimate max concurrent users
        result.max_users_estimate = self.estimate_max_users(
            current_vus=metrics.vus_max,
            current_p95=metrics.http_req_duration_p95,
        )

        logger.info(
            f"Analysis complete: {overall_grade} grade ({overall_score:.1f}), "
            f"max ~{result.max_users_estimate} users"
        )

        return result

    def estimate_max_users(self, current_vus: int, current_p95: float) -> int:
        """Estimate maximum concurrent users based on current metrics.

        Uses linear extrapolation with safety margin:
        max_users = current_vus * (target_p95 / current_p95) * safety_margin

        Args:
            current_vus: Virtual users in current test
            current_p95: Current p95 response time in milliseconds

        Returns:
            Estimated maximum concurrent users (conservative)
        """
        if current_vus <= 0 or current_p95 <= 0:
            logger.warning("Invalid metrics for max users estimation")
            return 0

        target_p95 = self.thresholds.max_users_threshold_ms

        # If already above target, we're at/past capacity
        if current_p95 >= target_p95:
            # Apply safety margin to current load
            max_users = int(current_vus * self.thresholds.max_users_safety_margin)
            logger.info(
                f"Current p95 ({current_p95:.0f}ms) >= target ({target_p95:.0f}ms), "
                f"at capacity: {max_users} users"
            )
            return max_users

        # Linear extrapolation with safety margin
        # max_users = current_vus * (target / current) * margin
        ratio = target_p95 / current_p95
        max_users_raw = current_vus * ratio
        max_users = int(max_users_raw * self.thresholds.max_users_safety_margin)

        logger.info(
            f"Max users estimate: {current_vus} VUs @ {current_p95:.0f}ms "
            f"→ ~{max_users} users @ {target_p95:.0f}ms (with {(1-self.thresholds.max_users_safety_margin)*100:.0f}% margin)"
        )

        return max_users

    def _get_response_time_description(self, grade: str) -> str:
        """Get description for response time grade.

        Args:
            grade: Performance grade (A-F)

        Returns:
            Human-readable description
        """
        descriptions = {
            "A": "Excellent - Very fast response times",
            "B": "Good - Acceptable response times for production",
            "C": "Acceptable - Response times are within limits",
            "D": "Slow - Response times need optimization",
            "F": "Critical - Response times are unacceptable",
        }
        return descriptions.get(grade, "Unknown")

    def _get_error_rate_description(self, grade: str) -> str:
        """Get description for error rate grade.

        Args:
            grade: Performance grade (A-F)

        Returns:
            Human-readable description
        """
        descriptions = {
            "A": "Excellent - Minimal errors",
            "B": "Good - Low error rate",
            "C": "Acceptable - Error rate within tolerances",
            "D": "Poor - High error rate needs investigation",
            "F": "Critical - Error rate is unacceptable",
        }
        return descriptions.get(grade, "Unknown")

    def _get_overall_description(self, grade: str) -> str:
        """Get description for overall grade.

        Args:
            grade: Performance grade (A-F)

        Returns:
            Human-readable description
        """
        descriptions = {
            "A": "Excellent - Ready for production with high confidence",
            "B": "Good - Suitable for production deployment",
            "C": "Acceptable - Can be deployed with monitoring",
            "D": "Poor - Optimization recommended before deployment",
            "F": "Critical - Not ready for production, requires fixes",
        }
        return descriptions.get(grade, "Unknown")

    def get_recommendations(self, result: K6ExecutionResult) -> list[str]:
        """Generate actionable recommendations based on test results.

        Args:
            result: Analyzed K6 execution result

        Returns:
            List of recommendations (prioritized: HIGH/MEDIUM/LOW)
        """
        if not result.success or result.metrics is None:
            return ["Cannot generate recommendations for failed test"]

        recommendations: list[str] = []
        metrics = result.metrics

        # Response time recommendations
        if result.response_time_grade and result.response_time_grade.grade in ["D", "F"]:
            recommendations.append(
                f"🔴 HIGH: Response time p95 is {metrics.http_req_duration_p95:.0f}ms. "
                "Optimize database queries, enable caching, or scale infrastructure."
            )
        elif result.response_time_grade and result.response_time_grade.grade == "C":
            recommendations.append(
                f"🟡 MEDIUM: Response time p95 is {metrics.http_req_duration_p95:.0f}ms. "
                "Consider caching strategies or CDN for static assets."
            )

        # Error rate recommendations
        if result.error_rate_grade and result.error_rate_grade.grade in ["D", "F"]:
            error_pct = metrics.http_req_failed_rate * 100
            recommendations.append(
                f"🔴 HIGH: Error rate is {error_pct:.2f}%. "
                f"Investigate {metrics.http_req_failed_count} failed requests. "
                "Check logs, database connections, and third-party API calls."
            )
        elif result.error_rate_grade and result.error_rate_grade.grade == "C":
            error_pct = metrics.http_req_failed_rate * 100
            recommendations.append(
                f"🟡 MEDIUM: Error rate is {error_pct:.2f}%. "
                "Monitor error logs and set up alerts for error rate spikes."
            )

        # Threshold failure recommendations
        if result.threshold_failed:
            recommendations.append(
                "🔴 HIGH: K6 safety thresholds were exceeded. "
                "Server is degrading under load. Reduce traffic or scale up."
            )

        # Capacity recommendations
        if result.max_users_estimate and metrics.vus_max > 0:
            margin = result.max_users_estimate - metrics.vus_max
            margin_pct = (margin / result.max_users_estimate) * 100

            if margin_pct < 20:
                recommendations.append(
                    f"🔴 HIGH: Capacity margin is only {margin_pct:.0f}% "
                    f"({margin} users). Scale infrastructure before Black Friday."
                )
            elif margin_pct < 50:
                recommendations.append(
                    f"🟡 MEDIUM: Capacity margin is {margin_pct:.0f}% ({margin} users). "
                    "Consider scaling if expecting traffic spikes."
                )

        # Check rate recommendations
        if metrics.checks_rate < 0.80:
            fail_pct = (1 - metrics.checks_rate) * 100
            recommendations.append(
                f"🟡 MEDIUM: {fail_pct:.1f}% of checks failed. "
                "Review check definitions or investigate intermittent failures."
            )

        # Success message if no issues
        if not recommendations:
            recommendations.append(
                "✅ No critical issues detected. System is performing well under load."
            )

        return recommendations
