"""Tests for K6 results models and scoring logic."""

import pytest
from pydantic import ValidationError

from src.models.k6_results import (
    K6ExecutionResult,
    K6Metrics,
    PerformanceGrade,
    ScoreThresholds,
)


class TestK6Metrics:
    """Tests for K6Metrics model."""

    def test_create_valid_metrics(self) -> None:
        """Test creating valid K6 metrics."""
        metrics = K6Metrics(
            http_req_duration_min=100.0,
            http_req_duration_avg=500.0,
            http_req_duration_p95=1200.0,
            http_req_duration_p99=1500.0,
            http_req_duration_max=2000.0,
            http_req_failed_rate=0.01,
            http_req_failed_count=10,
            http_req_total_count=1000,
            vus_max=50,
            iterations=950,
        )
        assert metrics.http_req_duration_p95 == 1200.0
        assert metrics.http_req_failed_rate == 0.01
        assert metrics.vus_max == 50

    def test_metrics_with_defaults(self) -> None:
        """Test metrics with default values."""
        metrics = K6Metrics(
            http_req_duration_min=100.0,
            http_req_duration_avg=500.0,
            http_req_duration_p95=1200.0,
            http_req_duration_p99=1500.0,
            http_req_duration_max=2000.0,
            http_req_failed_rate=0.0,
            http_req_failed_count=0,
            http_req_total_count=1000,
            vus_max=50,
            iterations=1000,
        )
        assert metrics.checks_rate == 1.0  # Default
        assert metrics.data_received_bytes == 0  # Default
        assert metrics.data_sent_bytes == 0  # Default

    def test_negative_duration_rejected(self) -> None:
        """Test that negative durations are rejected."""
        with pytest.raises(ValidationError):
            K6Metrics(
                http_req_duration_min=-100.0,  # Invalid
                http_req_duration_avg=500.0,
                http_req_duration_p95=1200.0,
                http_req_duration_p99=1500.0,
                http_req_duration_max=2000.0,
                http_req_failed_rate=0.01,
                http_req_failed_count=10,
                http_req_total_count=1000,
                vus_max=50,
                iterations=950,
            )

    def test_invalid_error_rate_rejected(self) -> None:
        """Test that error rate > 1 is rejected."""
        with pytest.raises(ValidationError):
            K6Metrics(
                http_req_duration_min=100.0,
                http_req_duration_avg=500.0,
                http_req_duration_p95=1200.0,
                http_req_duration_p99=1500.0,
                http_req_duration_max=2000.0,
                http_req_failed_rate=1.5,  # Invalid
                http_req_failed_count=10,
                http_req_total_count=1000,
                vus_max=50,
                iterations=950,
            )


class TestPerformanceGrade:
    """Tests for PerformanceGrade model."""

    def test_create_performance_grade(self) -> None:
        """Test creating a performance grade."""
        grade = PerformanceGrade(
            grade="A",
            score=95.0,
            description="Excellent performance",
        )
        assert grade.grade == "A"
        assert grade.score == 95.0
        assert grade.description == "Excellent performance"

    def test_invalid_grade_rejected(self) -> None:
        """Test that invalid grades are rejected."""
        with pytest.raises(ValidationError):
            PerformanceGrade(
                grade="Z",  # type: ignore[arg-type]  # Invalid
                score=95.0,
                description="Test",
            )

    def test_score_out_of_range_rejected(self) -> None:
        """Test that scores outside 0-100 are rejected."""
        with pytest.raises(ValidationError):
            PerformanceGrade(
                grade="A",
                score=101.0,  # Invalid
                description="Test",
            )


class TestScoreThresholds:
    """Tests for ScoreThresholds scoring logic."""

    @pytest.fixture
    def thresholds(self) -> ScoreThresholds:
        """Create default thresholds."""
        return ScoreThresholds()

    def test_response_time_grade_a(self, thresholds: ScoreThresholds) -> None:
        """Test A grade for excellent response time."""
        grade, score = thresholds.calculate_response_time_grade(500)  # < 1000ms
        assert grade == "A"
        assert 90 <= score <= 100

    def test_response_time_grade_b(self, thresholds: ScoreThresholds) -> None:
        """Test B grade for good response time."""
        grade, score = thresholds.calculate_response_time_grade(1500)  # 1000-2000ms
        assert grade == "B"
        assert 80 <= score < 90

    def test_response_time_grade_c(self, thresholds: ScoreThresholds) -> None:
        """Test C grade for acceptable response time."""
        grade, score = thresholds.calculate_response_time_grade(2500)  # 2000-3000ms
        assert grade == "C"
        assert 70 <= score < 80

    def test_response_time_grade_d(self, thresholds: ScoreThresholds) -> None:
        """Test D grade for slow response time."""
        grade, score = thresholds.calculate_response_time_grade(4000)  # 3000-5000ms
        assert grade == "D"
        assert 60 <= score < 70

    def test_response_time_grade_f(self, thresholds: ScoreThresholds) -> None:
        """Test F grade for critical response time."""
        grade, score = thresholds.calculate_response_time_grade(6000)  # > 5000ms
        assert grade == "F"
        assert 0 <= score < 60

    def test_error_rate_grade_a(self, thresholds: ScoreThresholds) -> None:
        """Test A grade for minimal errors."""
        grade, score = thresholds.calculate_error_rate_grade(0.0005)  # < 0.001
        assert grade == "A"
        assert 90 <= score <= 100

    def test_error_rate_grade_b(self, thresholds: ScoreThresholds) -> None:
        """Test B grade for low errors."""
        grade, score = thresholds.calculate_error_rate_grade(0.005)  # 0.001-0.01
        assert grade == "B"
        assert 80 <= score < 90

    def test_error_rate_grade_c(self, thresholds: ScoreThresholds) -> None:
        """Test C grade for acceptable errors."""
        grade, score = thresholds.calculate_error_rate_grade(0.03)  # 0.01-0.05
        assert grade == "C"
        assert 70 <= score < 80

    def test_error_rate_grade_d(self, thresholds: ScoreThresholds) -> None:
        """Test D grade for high errors."""
        grade, score = thresholds.calculate_error_rate_grade(0.07)  # 0.05-0.10
        assert grade == "D"
        assert 60 <= score < 70

    def test_error_rate_grade_f(self, thresholds: ScoreThresholds) -> None:
        """Test F grade for critical errors."""
        grade, score = thresholds.calculate_error_rate_grade(0.15)  # > 0.10
        assert grade == "F"
        assert 0 <= score < 60

    def test_overall_grade_calculation(self, thresholds: ScoreThresholds) -> None:
        """Test overall grade calculation with 60/40 weighting."""
        # A grade response (95) + A grade errors (95) = 95 overall (A)
        grade, score = thresholds.calculate_overall_grade(95.0, 95.0)
        assert grade == "A"
        assert score == 95.0

        # B grade response (85) + A grade errors (95) = 89 overall (B)
        grade, score = thresholds.calculate_overall_grade(85.0, 95.0)
        assert grade == "B"
        assert abs(score - 89.0) < 0.1  # 85*0.6 + 95*0.4 = 89

        # D grade response (65) + C grade errors (75) = 69 overall (D)
        grade, score = thresholds.calculate_overall_grade(65.0, 75.0)
        assert grade == "D"
        assert abs(score - 69.0) < 0.1  # 65*0.6 + 75*0.4 = 69

    def test_overall_grade_response_time_weighted_more(
        self, thresholds: ScoreThresholds
    ) -> None:
        """Test that response time has more weight (60%)."""
        # Good response time (85), poor errors (65)
        grade, score = thresholds.calculate_overall_grade(85.0, 65.0)
        expected = 85 * 0.6 + 65 * 0.4  # = 77
        assert abs(score - expected) < 0.1
        assert grade == "C"

        # Poor response time (65), good errors (85)
        grade, score = thresholds.calculate_overall_grade(65.0, 85.0)
        expected = 65 * 0.6 + 85 * 0.4  # = 73
        assert abs(score - expected) < 0.1
        assert grade == "C"


class TestK6ExecutionResult:
    """Tests for K6ExecutionResult model."""

    def test_create_successful_result(self) -> None:
        """Test creating successful execution result."""
        metrics = K6Metrics(
            http_req_duration_min=100.0,
            http_req_duration_avg=500.0,
            http_req_duration_p95=1200.0,
            http_req_duration_p99=1500.0,
            http_req_duration_max=2000.0,
            http_req_failed_rate=0.01,
            http_req_failed_count=10,
            http_req_total_count=1000,
            vus_max=50,
            iterations=950,
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

        assert result.success is True
        assert result.metrics is not None
        assert result.metrics.vus_max == 50
        assert result.threshold_failed is False

    def test_create_failed_result(self) -> None:
        """Test creating failed execution result."""
        result = K6ExecutionResult(
            url="https://preprod.ipln.fr/",
            page_type="homepage",
            environment="preprod",
            intensity="medium",
            success=False,
            duration_seconds=10.0,
            error_message="Script syntax error",
        )

        assert result.success is False
        assert result.metrics is None
        assert result.error_message == "Script syntax error"

    def test_result_with_analysis(self) -> None:
        """Test result with analysis fields populated."""
        metrics = K6Metrics(
            http_req_duration_min=100.0,
            http_req_duration_avg=500.0,
            http_req_duration_p95=1200.0,
            http_req_duration_p99=1500.0,
            http_req_duration_max=2000.0,
            http_req_failed_rate=0.01,
            http_req_failed_count=10,
            http_req_total_count=1000,
            vus_max=50,
            iterations=950,
        )

        result = K6ExecutionResult(
            url="https://preprod.ipln.fr/",
            page_type="homepage",
            environment="preprod",
            intensity="medium",
            success=True,
            duration_seconds=300.0,
            metrics=metrics,
            response_time_grade=PerformanceGrade(
                grade="B", score=85.0, description="Good"
            ),
            error_rate_grade=PerformanceGrade(
                grade="B", score=85.0, description="Good"
            ),
            overall_grade=PerformanceGrade(
                grade="B", score=85.0, description="Good"
            ),
            max_users_estimate=520,
        )

        assert result.overall_grade is not None
        assert result.overall_grade.grade == "B"
        assert result.max_users_estimate == 520
