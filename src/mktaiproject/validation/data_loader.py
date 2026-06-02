from __future__ import annotations

import csv
from pathlib import Path

from mktaiproject.models import DatasetSummary, ValidationIssue

NUMERIC_FIELDS = {
    "impressions",
    "reach",
    "frequency",
    "clicks",
    "link_clicks",
    "landing_page_views",
    "sessions",
    "bounce_rate",
    "avg_session_duration",
    "add_to_cart",
    "initiate_checkout",
    "checkout_completion",
    "purchases",
    "conversions",
    "conversion_rate",
    "spend",
    "cost_per_click",
    "cost_per_conversion",
    "revenue",
    "roas",
    "qualified_leads",
    "lead_score_avg",
    "repeat_customer_purchases",
    "row_budget_allocated",
    "budget_remaining",
    "hour_of_day",
}

DATE_FIELDS = {"date", "campaign_start_date", "campaign_end_date", "timestamp_hour"}


class MarketingDataLoader:
    """Load campaign CSV files and perform lightweight validation.

    The loader keeps parsing and validation deterministic so generated metrics
    do not depend on an LLM. It looks for sample campaign data under
    `data/campaign_csvs/` by default.
    """

    def __init__(self, project_root: Path | None = None) -> None:
        self.project_root = project_root or Path(__file__).resolve().parents[3]
        self.data_dir = self._resolve_data_dir()

    def _resolve_data_dir(self) -> Path:
        return self.project_root / "data" / "campaign_csvs"

    def dataset_paths(self) -> list[Path]:
        """Return campaign CSV files in stable filename order."""
        return sorted(self.data_dir.glob("*.csv"))

    def load_all(self) -> tuple[dict[str, list[dict[str, object]]], list[DatasetSummary], list[ValidationIssue]]:
        """Load every campaign CSV and return rows, summaries, and validation notes."""
        datasets: dict[str, list[dict[str, object]]] = {}
        summaries: list[DatasetSummary] = []
        issues: list[ValidationIssue] = []

        for path in self.dataset_paths():
            rows = self._read_csv(path)
            datasets[path.name] = rows
            summaries.append(self._build_summary(path, rows))
            issues.extend(self._validate_dataset(path.name, rows))

        return datasets, summaries, issues

    def _read_csv(self, path: Path) -> list[dict[str, object]]:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            return [self._coerce_row(row) for row in reader]

    def _coerce_row(self, row: dict[str, str]) -> dict[str, object]:
        converted: dict[str, object] = {}
        for key, value in row.items():
            if value is None:
                converted[key] = None
                continue

            text = value.strip()
            if text == "":
                converted[key] = None
            elif key in NUMERIC_FIELDS:
                converted[key] = float(text)
            else:
                converted[key] = text
        return converted

    def _build_summary(self, path: Path, rows: list[dict[str, object]]) -> DatasetSummary:
        columns = list(rows[0].keys()) if rows else []
        numeric_columns = [name for name in columns if name in NUMERIC_FIELDS]
        dimension_columns = [name for name in columns if name not in NUMERIC_FIELDS and name not in DATE_FIELDS]

        date_values: list[str] = []
        for row in rows:
            for field in ("date", "campaign_start_date", "timestamp_hour"):
                value = row.get(field)
                if isinstance(value, str):
                    date_values.append(value[:10])

        return DatasetSummary(
            name=path.name,
            path=path,
            row_count=len(rows),
            columns=columns,
            numeric_columns=numeric_columns,
            dimension_columns=dimension_columns,
            start_date=min(date_values) if date_values else None,
            end_date=max(date_values) if date_values else None,
        )

    def _validate_dataset(self, dataset_name: str, rows: list[dict[str, object]]) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        if not rows:
            issues.append(ValidationIssue(dataset=dataset_name, severity="error", message="Dataset is empty."))
            return issues

        seen_ids: set[object] = set()
        id_field = "row_id" if "row_id" in rows[0] else "breakdown_row_id"
        for row in rows:
            row_id = row.get(id_field)
            if row_id in seen_ids:
                issues.append(
                    ValidationIssue(
                        dataset=dataset_name,
                        severity="warning",
                        message=f"Duplicate identifier detected: {row_id}",
                    )
                )
            seen_ids.add(row_id)

        for field in ("dataset_type", "campaign_id", "campaign_name"):
            missing = sum(1 for row in rows if not row.get(field))
            if missing:
                issues.append(
                    ValidationIssue(
                        dataset=dataset_name,
                        severity="error",
                        message=f"Missing values in required field `{field}`: {missing}",
                    )
                )

        for field in ("spend", "revenue", "conversions", "clicks"):
            if field in rows[0]:
                negative_count = sum(1 for row in rows if isinstance(row.get(field), float) and row[field] < 0)
                if negative_count:
                    issues.append(
                        ValidationIssue(
                            dataset=dataset_name,
                            severity="error",
                            message=f"Negative values in `{field}`: {negative_count}",
                        )
                    )

        return issues
