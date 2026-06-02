from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class DatasetSummary:
    name: str
    path: Path
    row_count: int
    columns: list[str]
    numeric_columns: list[str]
    dimension_columns: list[str]
    start_date: str | None = None
    end_date: str | None = None


@dataclass
class ValidationIssue:
    dataset: str
    severity: str
    message: str


@dataclass
class SegmentPerformance:
    dimension: str
    segment: str
    dataset_type: str
    impressions: float
    clicks: float
    conversions: float
    spend: float
    revenue: float
    roas: float
    conversion_rate: float


@dataclass
class AnalysisResult:
    generated_at: str
    dataset_summaries: list[DatasetSummary]
    validation_issues: list[ValidationIssue]
    headline_metrics: dict[str, Any]
    flavor_performance: list[dict[str, Any]]
    segment_highlights: list[SegmentPerformance]
    hourly_highlights: list[dict[str, Any]]
    recommendations: list[str]
    source_files: list[str] = field(default_factory=list)

