"""Data models for K6 test execution results."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class K6Metrics(BaseModel):
    """K6 test metrics extracted from JSON output."""

    # Response time metrics (milliseconds)
    http_req_duration_min: float = Field(..., ge=0, description="Minimum response time")
    http_req_duration_avg: float = Field(..., ge=0, description="Average response time")
    http_req_duration_p95: float = Field(..., ge=0, description="95th percentile response time")
    http_req_duration_p99: float = Field(..., ge=0, description="99th percentile response time")
    http_req_duration_max: float = Field(..., ge=0, description="Maximum response time")

    # Error metrics
    http_req_failed_rate: float = Field(..., ge=0, le=1, description="Request failure rate (0-1)")
    http_req_failed_count: int = Field(..., ge=0, description="Total failed requests")
    http_req_total_count: int = Field(..., ge=0, description="Total requests")

    # Check metrics
    checks_rate: float = Field(
        default=1.0, ge=0, le=1, description="Check pass rate (0-1)"
    )

    # Load metrics
    vus_max: int = Field(..., ge=0, description="Maximum virtual users")
    iterations: int = Field(..., ge=0, description="Total iterations completed")

    # Data transfer
    data_received_bytes: int = Field(
        default=0, ge=0, description="Total data received in bytes"
    )
    data_sent_bytes: int = Field(default=0, ge=0, description="Total data sent in bytes")

    @field_validator("http_req_failed_rate", "checks_rate")
    @classmethod
    def validate_rate(cls, v: float) -> float:
        """Ensure rates are between 0 and 1."""
        if v < 0 or v > 1:
            raise ValueError("Rate must be between 0 and 1")
        return v


class PerformanceGrade(BaseModel):
    """Performance grade with score and level."""

    grade: Literal["A", "B", "C", "D", "F"] = Field(..., description="Performance grade")
    score: float = Field(..., ge=0, le=100, description="Numeric score (0-100)")
    description: str = Field(..., description="Grade description")


class K6ExecutionResult(BaseModel):
    """Complete K6 test execution result with metrics and analysis."""

    # Test configuration
    url: str = Field(..., description="Target URL tested")
    page_type: Literal["product", "homepage", "category", "landing"] = Field(
        ..., description="Type of page tested"
    )
    environment: Literal["prod", "preprod"] = Field(
        ..., description="Environment tested"
    )
    intensity: Literal["light", "medium", "heavy"] = Field(
        ..., description="Test intensity"
    )

    # Execution metadata
    success: bool = Field(..., description="Whether test completed successfully")
    duration_seconds: float = Field(..., ge=0, description="Total test duration")
    threshold_failed: bool = Field(
        default=False, description="Whether any threshold was exceeded"
    )
    error_message: str | None = Field(
        default=None, description="Error message if test failed"
    )

    # Raw metrics
    metrics: K6Metrics | None = Field(
        default=None, description="Raw K6 metrics (if test succeeded)"
    )

    # Analysis results (computed by analyzer)
    response_time_grade: PerformanceGrade | None = Field(
        default=None, description="Response time grade"
    )
    error_rate_grade: PerformanceGrade | None = Field(
        default=None, description="Error rate grade"
    )
    overall_grade: PerformanceGrade | None = Field(
        default=None, description="Overall performance grade"
    )
    max_users_estimate: int | None = Field(
        default=None, ge=0, description="Estimated max concurrent users"
    )


class ScoreThresholds(BaseModel):
    """Thresholds for converting metrics to scores."""

    # Response time thresholds (p95, in milliseconds)
    response_time_excellent: float = Field(default=1000, description="A grade threshold")
    response_time_good: float = Field(default=2000, description="B grade threshold")
    response_time_acceptable: float = Field(default=3000, description="C grade threshold")
    response_time_slow: float = Field(default=5000, description="D grade threshold")

    # Error rate thresholds (as decimal, 0-1)
    error_rate_excellent: float = Field(default=0.001, description="A grade threshold")
    error_rate_good: float = Field(default=0.01, description="B grade threshold")
    error_rate_acceptable: float = Field(default=0.05, description="C grade threshold")
    error_rate_poor: float = Field(default=0.10, description="D grade threshold")

    # Max users estimation threshold (p95 response time, ms)
    max_users_threshold_ms: float = Field(
        default=2000, description="Target p95 for max users calculation"
    )
    max_users_safety_margin: float = Field(
        default=0.80, ge=0, le=1, description="Safety margin (0.80 = -20%)"
    )

    def calculate_response_time_grade(
        self, p95_ms: float
    ) -> tuple[Literal["A", "B", "C", "D", "F"], float]:
        """Calculate grade and score from p95 response time.

        Args:
            p95_ms: 95th percentile response time in milliseconds

        Returns:
            Tuple of (grade, score) where score is 0-100
        """
        if p95_ms < self.response_time_excellent:
            # A: 90-100
            score = 100 - (p95_ms / self.response_time_excellent) * 10
            return "A", max(90, min(100, score))
        elif p95_ms < self.response_time_good:
            # B: 80-89
            score = 90 - ((p95_ms - self.response_time_excellent) /
                         (self.response_time_good - self.response_time_excellent)) * 10
            return "B", max(80, min(89, score))
        elif p95_ms < self.response_time_acceptable:
            # C: 70-79
            score = 80 - ((p95_ms - self.response_time_good) /
                         (self.response_time_acceptable - self.response_time_good)) * 10
            return "C", max(70, min(79, score))
        elif p95_ms < self.response_time_slow:
            # D: 60-69
            score = 70 - ((p95_ms - self.response_time_acceptable) /
                         (self.response_time_slow - self.response_time_acceptable)) * 10
            return "D", max(60, min(69, score))
        else:
            # F: 0-59
            score = max(0, 60 - (p95_ms - self.response_time_slow) / 100)
            return "F", min(59, score)

    def calculate_error_rate_grade(
        self, error_rate: float
    ) -> tuple[Literal["A", "B", "C", "D", "F"], float]:
        """Calculate grade and score from error rate.

        Args:
            error_rate: Error rate as decimal (0-1)

        Returns:
            Tuple of (grade, score) where score is 0-100
        """
        if error_rate < self.error_rate_excellent:
            # A: 90-100
            score = 100 - (error_rate / self.error_rate_excellent) * 10
            return "A", max(90, min(100, score))
        elif error_rate < self.error_rate_good:
            # B: 80-89
            score = 90 - ((error_rate - self.error_rate_excellent) /
                         (self.error_rate_good - self.error_rate_excellent)) * 10
            return "B", max(80, min(89, score))
        elif error_rate < self.error_rate_acceptable:
            # C: 70-79
            score = 80 - ((error_rate - self.error_rate_good) /
                         (self.error_rate_acceptable - self.error_rate_good)) * 10
            return "C", max(70, min(79, score))
        elif error_rate < self.error_rate_poor:
            # D: 60-69
            score = 70 - ((error_rate - self.error_rate_acceptable) /
                         (self.error_rate_poor - self.error_rate_acceptable)) * 10
            return "D", max(60, min(69, score))
        else:
            # F: 0-59
            score = max(0, 60 - (error_rate - self.error_rate_poor) * 500)
            return "F", min(59, score)

    def calculate_overall_grade(
        self, response_time_score: float, error_rate_score: float
    ) -> tuple[Literal["A", "B", "C", "D", "F"], float]:
        """Calculate overall grade from component scores.

        Formula: 60% response time + 40% error rate

        Args:
            response_time_score: Score for response time (0-100)
            error_rate_score: Score for error rate (0-100)

        Returns:
            Tuple of (grade, overall_score)
        """
        overall_score = (response_time_score * 0.6) + (error_rate_score * 0.4)

        if overall_score >= 90:
            return "A", overall_score
        elif overall_score >= 80:
            return "B", overall_score
        elif overall_score >= 70:
            return "C", overall_score
        elif overall_score >= 60:
            return "D", overall_score
        else:
            return "F", overall_score
