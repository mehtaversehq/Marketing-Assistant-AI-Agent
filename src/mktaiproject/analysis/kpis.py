from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
from typing import Any, Iterable

from mktaiproject.models import AnalysisResult, DatasetSummary, SegmentPerformance, ValidationIssue

SEGMENT_DIMENSIONS = [
    "placement",
    "device",
    "geography",
    "age_band",
    "gender",
    "audience_type",
    "hour_of_day",
]


class MarketingAnalyzer:
    """Calculate deterministic KPI comparisons from validated campaign data."""

    def analyze(
        self,
        datasets: dict[str, list[dict[str, object]]],
        dataset_summaries: list[DatasetSummary],
        validation_issues: list[ValidationIssue],
    ) -> AnalysisResult:
        """Build the complete analysis object used by reports and chat."""
        active_campaign = self._require_dataset(
            datasets,
            "active_campaign_performance_month.csv",
            "active_campaign_performance.csv",
        )
        historical_campaign = self._require_dataset(
            datasets,
            "historical_campaign_performance_month.csv",
            "historical_campaign_performance.csv",
        )
        active_hourly = self._require_dataset(
            datasets,
            "active_hourly_breakdown_month.csv",
            "active_hourly_breakdown.csv",
        )
        historical_hourly = self._require_dataset(
            datasets,
            "historical_hourly_breakdown_month.csv",
            "historical_hourly_breakdown.csv",
        )

        headline_metrics = self._headline_metrics(active_campaign, historical_campaign)
        flavor_performance = self._flavor_performance(active_campaign, historical_campaign)
        segment_highlights = self._segment_highlights(active_hourly, historical_hourly)
        hourly_highlights = self._hourly_highlights(active_hourly, historical_hourly)
        recommendations = self._recommendations(headline_metrics, flavor_performance, segment_highlights)

        return AnalysisResult(
            generated_at=datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
            dataset_summaries=dataset_summaries,
            validation_issues=validation_issues,
            headline_metrics=headline_metrics,
            flavor_performance=flavor_performance,
            segment_highlights=segment_highlights,
            hourly_highlights=hourly_highlights,
            recommendations=recommendations,
            source_files=[summary.name for summary in dataset_summaries],
        )

    def _headline_metrics(
        self,
        active_rows: list[dict[str, object]],
        historical_rows: list[dict[str, object]],
    ) -> dict[str, Any]:
        active = self._totals(active_rows)
        historical = self._totals(historical_rows)
        return {
            "active": active,
            "historical": historical,
            "delta": {
                key: round(active.get(key, 0.0) - historical.get(key, 0.0), 4)
                for key in ("spend", "revenue", "conversions", "roas")
            },
        }

    def _totals(self, rows: Iterable[dict[str, object]]) -> dict[str, float]:
        spend = sum(self._num(row.get("spend")) for row in rows)
        revenue = sum(self._num(row.get("revenue")) for row in rows)
        conversions = sum(self._num(row.get("conversions")) for row in rows)
        clicks = sum(self._num(row.get("clicks")) for row in rows)
        impressions = sum(self._num(row.get("impressions")) for row in rows)
        return {
            "spend": round(spend, 2),
            "revenue": round(revenue, 2),
            "conversions": round(conversions, 2),
            "clicks": round(clicks, 2),
            "impressions": round(impressions, 2),
            "roas": round(revenue / spend, 4) if spend else 0.0,
            "conversion_rate": round(conversions / clicks, 4) if clicks else 0.0,
        }

    def _flavor_performance(
        self,
        active_rows: list[dict[str, object]],
        historical_rows: list[dict[str, object]],
    ) -> list[dict[str, Any]]:
        merged: dict[str, dict[str, Any]] = {}
        for dataset_name, rows in (("active", active_rows), ("historical", historical_rows)):
            for row in rows:
                flavor = str(row.get("product_flavor"))
                bucket = merged.setdefault(flavor, {"product_flavor": flavor})
                bucket[dataset_name] = {
                    "spend": round(self._num(row.get("spend")), 2),
                    "revenue": round(self._num(row.get("revenue")), 2),
                    "conversions": round(self._num(row.get("conversions")), 2),
                    "roas": round(self._num(row.get("roas")), 4),
                    "conversion_rate": round(self._num(row.get("conversion_rate")), 4),
                }

        results: list[dict[str, Any]] = []
        for flavor, payload in merged.items():
            active = payload.get("active", {})
            historical = payload.get("historical", {})
            results.append(
                {
                    "product_flavor": flavor,
                    "active": active,
                    "historical": historical,
                    "delta_roas": round(active.get("roas", 0.0) - historical.get("roas", 0.0), 4),
                    "delta_conversions": round(
                        active.get("conversions", 0.0) - historical.get("conversions", 0.0), 4
                    ),
                }
            )

        return sorted(results, key=lambda item: item.get("active", {}).get("roas", 0.0), reverse=True)

    def _segment_highlights(
        self,
        active_rows: list[dict[str, object]],
        historical_rows: list[dict[str, object]],
    ) -> list[SegmentPerformance]:
        highlights: list[SegmentPerformance] = []
        for dimension in SEGMENT_DIMENSIONS:
            highlights.extend(self._top_and_bottom_segments(active_rows, dimension, "active"))
            highlights.extend(self._top_and_bottom_segments(historical_rows, dimension, "historical"))
        return highlights

    def _top_and_bottom_segments(
        self,
        rows: list[dict[str, object]],
        dimension: str,
        dataset_type: str,
    ) -> list[SegmentPerformance]:
        grouped: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        for row in rows:
            segment = str(row.get(dimension))
            bucket = grouped[segment]
            for metric in ("impressions", "clicks", "conversions", "spend", "revenue"):
                bucket[metric] += self._num(row.get(metric))

        performances: list[SegmentPerformance] = []
        for segment, metrics in grouped.items():
            spend = metrics["spend"]
            clicks = metrics["clicks"]
            performances.append(
                SegmentPerformance(
                    dimension=dimension,
                    segment=segment,
                    dataset_type=dataset_type,
                    impressions=round(metrics["impressions"], 2),
                    clicks=round(clicks, 2),
                    conversions=round(metrics["conversions"], 2),
                    spend=round(spend, 2),
                    revenue=round(metrics["revenue"], 2),
                    roas=round(metrics["revenue"] / spend, 4) if spend else 0.0,
                    conversion_rate=round(metrics["conversions"] / clicks, 4) if clicks else 0.0,
                )
            )

        performances = [item for item in performances if item.spend > 0]
        if not performances:
            return []

        performances.sort(key=lambda item: (item.roas, item.conversion_rate), reverse=True)
        top = performances[0]
        bottom = performances[-1]
        return [top] if top.segment == bottom.segment else [top, bottom]

    def _hourly_highlights(
        self,
        active_rows: list[dict[str, object]],
        historical_rows: list[dict[str, object]],
    ) -> list[dict[str, Any]]:
        highlights = []
        for dataset_type, rows in (("active", active_rows), ("historical", historical_rows)):
            grouped: dict[int, dict[str, float]] = defaultdict(lambda: defaultdict(float))
            for row in rows:
                hour = int(self._num(row.get("hour_of_day")))
                bucket = grouped[hour]
                for metric in ("spend", "revenue", "conversions", "clicks"):
                    bucket[metric] += self._num(row.get(metric))

            hour_rows = []
            for hour, metrics in grouped.items():
                spend = metrics["spend"]
                clicks = metrics["clicks"]
                hour_rows.append(
                    {
                        "dataset_type": dataset_type,
                        "hour_of_day": hour,
                        "spend": round(spend, 2),
                        "revenue": round(metrics["revenue"], 2),
                        "conversions": round(metrics["conversions"], 2),
                        "roas": round(metrics["revenue"] / spend, 4) if spend else 0.0,
                        "conversion_rate": round(metrics["conversions"] / clicks, 4) if clicks else 0.0,
                    }
                )
            hour_rows.sort(key=lambda item: item["roas"], reverse=True)
            if hour_rows:
                highlights.append({"dataset_type": dataset_type, "best_hour": hour_rows[0], "worst_hour": hour_rows[-1]})
        return highlights

    def _recommendations(
        self,
        headline_metrics: dict[str, Any],
        flavor_performance: list[dict[str, Any]],
        segment_highlights: list[SegmentPerformance],
    ) -> list[str]:
        recommendations: list[str] = []
        delta_roas = headline_metrics["delta"]["roas"]
        if delta_roas > 0:
            recommendations.append("Active campaign ROAS is ahead of the historical baseline; scale only the best-performing segments.")
        else:
            recommendations.append("Active campaign ROAS trails the historical baseline; tighten spend against weak segments before scaling.")

        if flavor_performance:
            best_flavor = flavor_performance[0]
            worst_flavor = flavor_performance[-1]
            recommendations.append(
                f"Prioritize {best_flavor['product_flavor']} creative testing and review why {worst_flavor['product_flavor']} lags on ROAS."
            )

        active_segments = [segment for segment in segment_highlights if segment.dataset_type == "active"]
        if active_segments:
            weakest = min(active_segments, key=lambda item: item.roas)
            strongest = max(active_segments, key=lambda item: item.roas)
            recommendations.append(
                f"Shift budget away from {weakest.dimension}={weakest.segment} and toward {strongest.dimension}={strongest.segment} if volume holds."
            )

        return recommendations

    def _num(self, value: object) -> float:
        return float(value) if isinstance(value, (int, float)) else 0.0

    def _require_dataset(
        self,
        datasets: dict[str, list[dict[str, object]]],
        *candidate_names: str,
    ) -> list[dict[str, object]]:
        for name in candidate_names:
            if name in datasets:
                return datasets[name]

        available = ", ".join(sorted(datasets)) or "none"
        expected = " or ".join(candidate_names)
        raise ValueError(
            f"Missing required dataset: expected {expected}. Available datasets: {available}."
        )
