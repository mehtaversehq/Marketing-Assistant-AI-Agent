from __future__ import annotations

from mktaiproject.analysis import MarketingAnalyzer
from mktaiproject.reporting import ArtifactStore, InsightNarrator
from mktaiproject.validation import MarketingDataLoader


class MarketingInsightsPipeline:
    """Run the full deterministic marketing analysis workflow."""

    def __init__(
        self,
        loader: MarketingDataLoader | None = None,
        analyzer: MarketingAnalyzer | None = None,
        narrator: InsightNarrator | None = None,
        store: ArtifactStore | None = None,
    ) -> None:
        self.loader = loader or MarketingDataLoader()
        self.analyzer = analyzer or MarketingAnalyzer()
        self.narrator = narrator or InsightNarrator()
        self.store = store or ArtifactStore()

    def run(self) -> dict[str, str]:
        """Load data, calculate metrics, generate summaries, and save artifacts."""
        datasets, summaries, issues = self.loader.load_all()
        analysis = self.analyzer.analyze(datasets, summaries, issues)
        summary = self.narrator.summarize(analysis)
        report = self._build_report(analysis, summary["narrative"])

        self.store.save_analysis(analysis)
        self.store.save_summary(summary)
        self.store.save_report(report)

        return {
            "analysis_path": str(self.store.analysis_path),
            "summary_path": str(self.store.summary_path),
            "report_path": str(self.store.report_path),
            "summary_status": summary["status"],
        }

    def _build_report(self, analysis, narrative: str) -> str:
        """Render the analysis output as a compact Markdown report."""
        dataset_lines = [
            f"- {summary.name}: {summary.row_count} rows, date range {summary.start_date or 'n/a'} to {summary.end_date or 'n/a'}"
            for summary in analysis.dataset_summaries
        ]
        issues = analysis.validation_issues or []
        validation_lines = ["- No validation issues detected."] if not issues else [
            f"- [{issue.severity}] {issue.dataset}: {issue.message}" for issue in issues
        ]
        recommendation_lines = [f"- {item}" for item in analysis.recommendations]

        return (
            "# Marketing Insights Report\n\n"
            "## Dataset Overview\n"
            + "\n".join(dataset_lines)
            + "\n\n## Validation Notes\n"
            + "\n".join(validation_lines)
            + "\n\n## Narrative\n"
            + narrative
            + "\n\n## Recommended Actions\n"
            + "\n".join(recommendation_lines)
            + "\n"
        )
