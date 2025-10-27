"""Tests for results analyzer."""

import pytest

from src.models.k6_results import (
    K6ExecutionResult,
    K6Metrics,
    ScoreThresholds,
)
from src.results_analyzer import ResultsAnalyzer


class TestResultsAnalyzer:
    """Tests for ResultsAnalyzer class."""

    @pytest.fixture
    def analyzer(self) -> ResultsAnalyzer:
        """Create analyzer with default thresholds."""
        return ResultsAnalyzer()

    @pytest.fixture
    def successful_result(self) -> K6ExecutionResult:
        """Create successful test result."""
        metrics = K6Metrics(
            http_req_duration_min=100.0,
            http_req_duration_avg=500.0,
            http_req_duration_p95=1200.0,
            http_req_duration_p99=1500.0,
            http_req_duration_max=2000.0,
            http_req_failed_rate=0.005,
            http_req_failed_count=5,
            http_req_total_count=1000,
            vus_max=200,
            iterations=995,
        )

        return K6ExecutionResult(
            url="https://preprod.ipln.fr/",
            page_type="homepage",
            environment="preprod",
            intensity="medium",
            success=True,
            duration_seconds=300.0,
            metrics=metrics,
        )

    def test_analyze_successful_result(
        self, analyzer: ResultsAnalyzer, successful_result: K6ExecutionResult
    ) -> None:
        """Test analyzing successful result."""
        result = analyzer.analyze(successful_result)

        assert result.response_time_grade is not None
        assert result.error_rate_grade is not None
        assert result.overall_grade is not None
        assert result.max_users_estimate is not None

        # p95 = 1200ms should be B grade (1000-2000ms)
        assert result.response_time_grade.grade == "B"

        # error rate = 0.005 should be B grade (0.001-0.01)
        assert result.error_rate_grade.grade == "B"

        # Overall should be B
        assert result.overall_grade.grade == "B"

    def test_analyze_failed_result(self, analyzer: ResultsAnalyzer) -> None:
        """Test analyzing failed result returns unchanged."""
        failed_result = K6ExecutionResult(
            url="https://preprod.ipln.fr/",
            page_type="homepage",
            environment="preprod",
            intensity="medium",
            success=False,
            duration_seconds=10.0,
            error_message="Test failed",
        )

        result = analyzer.analyze(failed_result)

        # Should not add analysis to failed result
        assert result.response_time_grade is None
        assert result.error_rate_grade is None
        assert result.overall_grade is None
        assert result.max_users_estimate is None

    def test_analyze_excellent_performance(self, analyzer: ResultsAnalyzer) -> None:
        """Test analyzing excellent performance."""
        metrics = K6Metrics(
            http_req_duration_min=50.0,
            http_req_duration_avg=300.0,
            http_req_duration_p95=800.0,  # < 1000ms = A grade
            http_req_duration_p99=1000.0,
            http_req_duration_max=1200.0,
            http_req_failed_rate=0.0005,  # < 0.001 = A grade
            http_req_failed_count=1,
            http_req_total_count=2000,
            vus_max=100,
            iterations=1999,
        )

        result = K6ExecutionResult(
            url="https://preprod.ipln.fr/",
            page_type="homepage",
            environment="preprod",
            intensity="medium",
            success=True,
            duration_seconds=300.0,
            metrics=metrics,
        )

        result = analyzer.analyze(result)

        assert result.response_time_grade is not None
        assert result.response_time_grade.grade == "A"
        assert result.error_rate_grade is not None
        assert result.error_rate_grade.grade == "A"
        assert result.overall_grade is not None
        assert result.overall_grade.grade == "A"

    def test_analyze_poor_performance(self, analyzer: ResultsAnalyzer) -> None:
        """Test analyzing poor performance."""
        metrics = K6Metrics(
            http_req_duration_min=500.0,
            http_req_duration_avg=3000.0,
            http_req_duration_p95=6000.0,  # > 5000ms = F grade
            http_req_duration_p99=8000.0,
            http_req_duration_max=10000.0,
            http_req_failed_rate=0.15,  # > 0.10 = F grade
            http_req_failed_count=300,
            http_req_total_count=2000,
            vus_max=50,
            iterations=1700,
        )

        result = K6ExecutionResult(
            url="https://preprod.ipln.fr/",
            page_type="homepage",
            environment="preprod",
            intensity="light",
            success=True,
            duration_seconds=120.0,
            metrics=metrics,
        )

        result = analyzer.analyze(result)

        assert result.response_time_grade is not None
        assert result.response_time_grade.grade == "F"
        assert result.error_rate_grade is not None
        assert result.error_rate_grade.grade == "F"
        assert result.overall_grade is not None
        assert result.overall_grade.grade == "F"

    def test_estimate_max_users_below_threshold(
        self, analyzer: ResultsAnalyzer
    ) -> None:
        """Test max users estimation when below threshold."""
        # Test with 200 VUs @ 1000ms p95
        # Should estimate ~400 users @ 2000ms (with 20% margin = 320)
        max_users = analyzer.estimate_max_users(
            current_vus=200,
            current_p95=1000.0,
        )

        # 200 * (2000/1000) * 0.80 = 320
        assert max_users == 320

    def test_estimate_max_users_at_threshold(self, analyzer: ResultsAnalyzer) -> None:
        """Test max users estimation when at threshold."""
        # Test with 200 VUs @ 2000ms p95 (at target)
        # Should return current load with margin
        max_users = analyzer.estimate_max_users(
            current_vus=200,
            current_p95=2000.0,
        )

        # 200 * 0.80 = 160
        assert max_users == 160

    def test_estimate_max_users_above_threshold(
        self, analyzer: ResultsAnalyzer
    ) -> None:
        """Test max users estimation when above threshold."""
        # Test with 100 VUs @ 3000ms p95 (above target)
        # Should return current load with margin (at capacity)
        max_users = analyzer.estimate_max_users(
            current_vus=100,
            current_p95=3000.0,
        )

        # 100 * 0.80 = 80
        assert max_users == 80

    def test_estimate_max_users_invalid_metrics(
        self, analyzer: ResultsAnalyzer
    ) -> None:
        """Test max users estimation with invalid metrics."""
        # Zero VUs
        max_users = analyzer.estimate_max_users(
            current_vus=0,
            current_p95=1000.0,
        )
        assert max_users == 0

        # Zero p95
        max_users = analyzer.estimate_max_users(
            current_vus=100,
            current_p95=0.0,
        )
        assert max_users == 0

    def test_get_recommendations_excellent_performance(
        self, analyzer: ResultsAnalyzer
    ) -> None:
        """Test recommendations for excellent performance."""
        metrics = K6Metrics(
            http_req_duration_min=50.0,
            http_req_duration_avg=300.0,
            http_req_duration_p95=800.0,
            http_req_duration_p99=1000.0,
            http_req_duration_max=1200.0,
            http_req_failed_rate=0.0005,
            http_req_failed_count=1,
            http_req_total_count=2000,
            vus_max=100,
            iterations=1999,
        )

        result = K6ExecutionResult(
            url="https://preprod.ipln.fr/",
            page_type="homepage",
            environment="preprod",
            intensity="medium",
            success=True,
            duration_seconds=300.0,
            metrics=metrics,
        )

        result = analyzer.analyze(result)
        recommendations = analyzer.get_recommendations(result)

        # Should have success message
        assert len(recommendations) > 0
        assert any("No critical issues" in rec for rec in recommendations)

    def test_get_recommendations_slow_response(
        self, analyzer: ResultsAnalyzer
    ) -> None:
        """Test recommendations for slow response time."""
        metrics = K6Metrics(
            http_req_duration_min=500.0,
            http_req_duration_avg=3000.0,
            http_req_duration_p95=6000.0,  # F grade
            http_req_duration_p99=8000.0,
            http_req_duration_max=10000.0,
            http_req_failed_rate=0.001,  # Good
            http_req_failed_count=2,
            http_req_total_count=2000,
            vus_max=50,
            iterations=1998,
        )

        result = K6ExecutionResult(
            url="https://preprod.ipln.fr/",
            page_type="homepage",
            environment="preprod",
            intensity="light",
            success=True,
            duration_seconds=120.0,
            metrics=metrics,
        )

        result = analyzer.analyze(result)
        recommendations = analyzer.get_recommendations(result)

        # Should have HIGH priority recommendation for response time
        assert any("HIGH" in rec and "Response time" in rec for rec in recommendations)

    def test_get_recommendations_high_errors(
        self, analyzer: ResultsAnalyzer
    ) -> None:
        """Test recommendations for high error rate."""
        metrics = K6Metrics(
            http_req_duration_min=100.0,
            http_req_duration_avg=500.0,
            http_req_duration_p95=1000.0,  # Good
            http_req_duration_p99=1200.0,
            http_req_duration_max=1500.0,
            http_req_failed_rate=0.15,  # F grade
            http_req_failed_count=300,
            http_req_total_count=2000,
            vus_max=50,
            iterations=1700,
        )

        result = K6ExecutionResult(
            url="https://preprod.ipln.fr/",
            page_type="homepage",
            environment="preprod",
            intensity="light",
            success=True,
            duration_seconds=120.0,
            metrics=metrics,
        )

        result = analyzer.analyze(result)
        recommendations = analyzer.get_recommendations(result)

        # Should have HIGH priority recommendation for error rate
        assert any("HIGH" in rec and "Error rate" in rec for rec in recommendations)

    def test_get_recommendations_threshold_failed(
        self, analyzer: ResultsAnalyzer
    ) -> None:
        """Test recommendations when thresholds failed."""
        metrics = K6Metrics(
            http_req_duration_min=100.0,
            http_req_duration_avg=2000.0,
            http_req_duration_p95=4000.0,
            http_req_duration_p99=5000.0,
            http_req_duration_max=6000.0,
            http_req_failed_rate=0.05,
            http_req_failed_count=100,
            http_req_total_count=2000,
            vus_max=200,
            iterations=1900,
        )

        result = K6ExecutionResult(
            url="https://preprod.ipln.fr/",
            page_type="homepage",
            environment="preprod",
            intensity="medium",
            success=True,
            duration_seconds=300.0,
            threshold_failed=True,  # Threshold failed
            metrics=metrics,
        )

        result = analyzer.analyze(result)
        recommendations = analyzer.get_recommendations(result)

        # Should have HIGH priority recommendation for threshold failure
        assert any(
            "HIGH" in rec and "threshold" in rec.lower() for rec in recommendations
        )

    def test_get_recommendations_low_capacity_margin(
        self, analyzer: ResultsAnalyzer
    ) -> None:
        """Test recommendations for low capacity margin."""
        metrics = K6Metrics(
            http_req_duration_min=100.0,
            http_req_duration_avg=1000.0,
            http_req_duration_p95=1900.0,  # Just below 2000ms
            http_req_duration_p99=2100.0,
            http_req_duration_max=2500.0,
            http_req_failed_rate=0.005,
            http_req_failed_count=10,
            http_req_total_count=2000,
            vus_max=190,  # High load, low margin
            iterations=1990,
        )

        result = K6ExecutionResult(
            url="https://preprod.ipln.fr/",
            page_type="homepage",
            environment="preprod",
            intensity="medium",
            success=True,
            duration_seconds=300.0,
            metrics=metrics,
        )

        result = analyzer.analyze(result)
        recommendations = analyzer.get_recommendations(result)

        # Should have recommendation about capacity margin
        assert any("margin" in rec.lower() for rec in recommendations)

    def test_custom_thresholds(self) -> None:
        """Test analyzer with custom thresholds."""
        custom_thresholds = ScoreThresholds(
            response_time_excellent=500,  # Stricter
            response_time_good=1000,
            max_users_threshold_ms=1500,
            max_users_safety_margin=0.90,  # Less conservative
        )

        analyzer = ResultsAnalyzer(thresholds=custom_thresholds)

        metrics = K6Metrics(
            http_req_duration_min=50.0,
            http_req_duration_avg=300.0,
            http_req_duration_p95=700.0,  # Would be B with default, A with custom
            http_req_duration_p99=900.0,
            http_req_duration_max=1000.0,
            http_req_failed_rate=0.001,
            http_req_failed_count=2,
            http_req_total_count=2000,
            vus_max=100,
            iterations=1998,
        )

        result = K6ExecutionResult(
            url="https://preprod.ipln.fr/",
            page_type="homepage",
            environment="preprod",
            intensity="medium",
            success=True,
            duration_seconds=300.0,
            metrics=metrics,
        )

        result = analyzer.analyze(result)

        # With stricter threshold (500ms), 700ms should be B grade
        assert result.response_time_grade is not None
        assert result.response_time_grade.grade == "B"
