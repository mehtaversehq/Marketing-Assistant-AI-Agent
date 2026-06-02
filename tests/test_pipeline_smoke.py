import json
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from mktaiproject.analysis import MarketingAnalyzer
from mktaiproject.chat import MarketingChatbot
from mktaiproject.llm import OllamaResponse
from mktaiproject.pipeline import MarketingInsightsPipeline
from mktaiproject.reporting import ArtifactStore, InsightNarrator
from mktaiproject.validation import MarketingDataLoader


class StubClient:
    def generate(self, prompt: str, system: str | None = None, temperature: float = 0.1) -> OllamaResponse:
        return OllamaResponse(ok=True, content="Executive Summary\nStubbed narrative.", error=None)


class PipelineSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.project_root = PROJECT_ROOT

    def test_loader_finds_expected_datasets(self) -> None:
        loader = MarketingDataLoader(project_root=self.project_root)
        dataset_names = [path.name for path in loader.dataset_paths()]
        self.assertEqual(
            dataset_names,
            [
                "active_campaign_performance_month.csv",
                "active_hourly_breakdown_month.csv",
                "historical_campaign_performance_month.csv",
                "historical_hourly_breakdown_month.csv",
            ],
        )

    def test_analysis_produces_expected_sections(self) -> None:
        loader = MarketingDataLoader(project_root=self.project_root)
        datasets, summaries, issues = loader.load_all()
        analysis = MarketingAnalyzer().analyze(datasets, summaries, issues)

        self.assertIn("active", analysis.headline_metrics)
        self.assertIn("historical", analysis.headline_metrics)
        self.assertGreater(len(analysis.flavor_performance), 0)
        self.assertGreater(len(analysis.segment_highlights), 0)
        self.assertGreater(len(analysis.recommendations), 0)

    def test_pipeline_writes_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            store = ArtifactStore(project_root=root)
            loader = MarketingDataLoader(project_root=self.project_root)
            pipeline = MarketingInsightsPipeline(
                loader=loader,
                analyzer=MarketingAnalyzer(),
                narrator=InsightNarrator(client=StubClient()),
                store=store,
            )

            result = pipeline.run()

            self.assertEqual(result["summary_status"], "generated")
            self.assertTrue(store.analysis_path.exists())
            self.assertTrue(store.summary_path.exists())
            self.assertTrue(store.report_path.exists())

            summary = json.loads(store.summary_path.read_text(encoding="utf-8"))
            self.assertIn("Stubbed narrative", summary["narrative"])

    def test_chat_uses_latest_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            store = ArtifactStore(project_root=root)
            store.save_analysis(
                analysis=MarketingAnalyzer().analyze(*MarketingDataLoader(project_root=self.project_root).load_all())
            )
            store.save_summary({"status": "generated", "narrative": "Executive Summary\nGrounded stub summary."})

            bot = MarketingChatbot(store=store, client=StubClient())
            answer = bot.answer("Which flavor is performing best?")

            self.assertIn("Stubbed narrative", answer)

    def test_chat_handles_missing_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            store = ArtifactStore(project_root=root)

            answer = MarketingChatbot(store=store, client=StubClient()).answer("Which flavor is performing best?")

            self.assertIn("Run `PYTHONPATH=src python3 -m mktaiproject.main run` first", answer)

    def test_chat_fallback_answers_common_metric_questions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            store = ArtifactStore(project_root=root)
            store.save_analysis(
                analysis=MarketingAnalyzer().analyze(*MarketingDataLoader(project_root=self.project_root).load_all())
            )
            store.save_summary({"status": "fallback", "narrative": "Fallback summary."})

            class OfflineClient:
                def generate(self, prompt: str, system: str | None = None, temperature: float = 0.1) -> OllamaResponse:
                    return OllamaResponse(ok=False, content="", error="Ollama connection refused")

            answer = MarketingChatbot(store=store, client=OfflineClient()).answer("Which flavor is performing best?")

            self.assertIn("Strawberry is performing best", answer)
            self.assertIn("active ROAS of 0.28", answer)


if __name__ == "__main__":
    unittest.main()
