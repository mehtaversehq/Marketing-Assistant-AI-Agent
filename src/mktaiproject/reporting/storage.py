from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from mktaiproject.models import AnalysisResult


class ArtifactStore:
    """Read and write generated pipeline artifacts under `outputs/`."""

    def __init__(self, project_root: Path | None = None) -> None:
        self.project_root = project_root or Path(__file__).resolve().parents[3]
        self.output_dir = self.project_root / "outputs"
        self.output_dir.mkdir(exist_ok=True)

    @property
    def analysis_path(self) -> Path:
        return self.output_dir / "analysis.json"

    @property
    def report_path(self) -> Path:
        return self.output_dir / "report.md"

    @property
    def summary_path(self) -> Path:
        return self.output_dir / "summary.json"

    def save_analysis(self, analysis: AnalysisResult) -> None:
        self.analysis_path.write_text(json.dumps(asdict(analysis), indent=2, default=str), encoding="utf-8")

    def save_summary(self, summary: dict[str, str]) -> None:
        self.summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    def save_report(self, report: str) -> None:
        self.report_path.write_text(report, encoding="utf-8")

    def load_analysis(self) -> dict:
        return json.loads(self.analysis_path.read_text(encoding="utf-8"))

    def load_summary(self) -> dict:
        return json.loads(self.summary_path.read_text(encoding="utf-8"))
