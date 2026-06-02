from __future__ import annotations

import json
import re
from pathlib import Path

from mktaiproject.llm import OllamaClient
from mktaiproject.reporting import ArtifactStore


class MarketingChatbot:
    """Answer questions using generated analysis artifacts.

    The chatbot tries Ollama first for natural-language answers. When Ollama is
    offline, it answers common metric questions deterministically from
    `outputs/analysis.json`.
    """

    def __init__(self, store: ArtifactStore | None = None, client: OllamaClient | None = None) -> None:
        self.store = store or ArtifactStore()
        self.client = client or OllamaClient()
        self.project_root = Path(__file__).resolve().parents[3]

    def answer(self, question: str) -> str:
        """Answer a user question against the latest generated artifacts."""
        try:
            analysis = self.store.load_analysis()
            summary = self.store.load_summary()
        except FileNotFoundError:
            return (
                "No analysis artifacts are available yet. "
                "Run `PYTHONPATH=src python3 -m mktaiproject.main run` first, then ask again."
            )
        retrieval_context = self._retrieve_context(question, analysis, summary)
        prompt = (
            "Answer the user's question using only the grounded context below.\n"
            "If the answer is uncertain or not directly supported, say that clearly.\n"
            "Prefer exact values from the analysis context when available.\n\n"
            f"Question: {question}\n\n"
            f"Context:\n{retrieval_context}"
        )
        system = "You are a careful marketing insights assistant. Do not invent data."
        response = self.client.generate(prompt=prompt, system=system, temperature=0.1)
        if response.ok and response.content:
            return response.content
        return self._fallback_answer(question, analysis, summary, retrieval_context, response.error or "Ollama unavailable.")

    def _retrieve_context(self, question: str, analysis: dict, summary: dict) -> str:
        chunks = [
            f"Summary narrative:\n{summary.get('narrative', '')}",
            f"Headline metrics:\n{json.dumps(analysis.get('headline_metrics', {}), indent=2)}",
            f"Flavor performance:\n{json.dumps(analysis.get('flavor_performance', []), indent=2)}",
            f"Hourly highlights:\n{json.dumps(analysis.get('hourly_highlights', []), indent=2)}",
            "Recommendations:\n" + "\n".join(f"- {item}" for item in analysis.get("recommendations", [])),
        ]

        segment_match = self._find_dimension(question)
        if segment_match:
            segments = [
                {
                    "dimension": item["dimension"],
                    "segment": item["segment"],
                    "dataset_type": item["dataset_type"],
                    "roas": item["roas"],
                    "conversion_rate": item["conversion_rate"],
                    "spend": item["spend"],
                }
                for item in analysis.get("segment_highlights", [])
                if item["dimension"] == segment_match
            ]
            chunks.append(f"Segment highlights for {segment_match}:\n{json.dumps(segments, indent=2)}")

        catalog_path = self.project_root / "knowledge" / "marketing_data_catalog.md"
        if catalog_path.exists():
            chunks.append(f"Data catalog:\n{catalog_path.read_text(encoding='utf-8')}")

        return "\n\n".join(chunks)

    def _fallback_answer(self, question: str, analysis: dict, summary: dict, context: str, error: str) -> str:
        deterministic_answer = self._deterministic_answer(question, analysis, summary)
        if deterministic_answer:
            return f"{deterministic_answer}\n\nNote: Ollama is unavailable, so this answer used deterministic metrics only. {error}"

        first_block = context.split("\n\n", 1)[0]
        return (
            f"Ollama is unavailable, so I used the available deterministic context. {error}\n\n"
            f"{first_block}"
        )

    def _deterministic_answer(self, question: str, analysis: dict, summary: dict) -> str | None:
        """Answer common metric questions without an LLM."""
        lowered = question.lower()
        flavors = analysis.get("flavor_performance", [])
        active_metrics = analysis.get("headline_metrics", {}).get("active", {})
        historical_metrics = analysis.get("headline_metrics", {}).get("historical", {})
        recommendations = analysis.get("recommendations", [])

        if "summary" in lowered or "performance" in lowered and "campaign" in lowered:
            return (
                "Active campaign performance: "
                f"spend ${active_metrics.get('spend', 0):,.2f}, "
                f"revenue ${active_metrics.get('revenue', 0):,.2f}, "
                f"conversions {active_metrics.get('conversions', 0):,.0f}, "
                f"ROAS {active_metrics.get('roas', 0):.4f}. "
                "Historical baseline: "
                f"spend ${historical_metrics.get('spend', 0):,.2f}, "
                f"revenue ${historical_metrics.get('revenue', 0):,.2f}, "
                f"conversions {historical_metrics.get('conversions', 0):,.0f}, "
                f"ROAS {historical_metrics.get('roas', 0):.4f}."
            )

        if any(phrase in lowered for phrase in ("focus", "recommend", "what should i do", "action")):
            if recommendations:
                return "Recommended focus:\n" + "\n".join(f"- {item}" for item in recommendations)

        if "flavor" in lowered and any(word in lowered for word in ("best", "top", "highest", "performing")):
            best_flavor = self._best_item(flavors, "roas")
            if best_flavor:
                active = best_flavor.get("active", {})
                return (
                    f"{best_flavor['product_flavor'].title()} is performing best based on "
                    f"active ROAS of {active.get('roas', 0):.2f}."
                )

        if "campaign" in lowered and any(word in lowered for word in ("worst", "lowest", "underperform")):
            worst_flavor = self._worst_item(flavors, "roas")
            if worst_flavor:
                active = worst_flavor.get("active", {})
                return (
                    f"{worst_flavor['product_flavor'].title()} is the weakest campaign/flavor by "
                    f"active ROAS of {active.get('roas', 0):.2f}."
                )

        if "campaign" in lowered and "roas" in lowered:
            best_flavor = self._best_item(flavors, "roas")
            if best_flavor:
                active = best_flavor.get("active", {})
                return (
                    f"{best_flavor['product_flavor'].title()} has the highest active ROAS "
                    f"at {active.get('roas', 0):.2f}."
                )

        if "spent" in lowered or "spend" in lowered:
            top_spend = self._best_item(flavors, "spend")
            if top_spend:
                active = top_spend.get("active", {})
                return (
                    f"{top_spend['product_flavor'].title()} spent the most with "
                    f"${active.get('spend', 0):,.2f} in active spend."
                )

        if "revenue" in lowered:
            top_revenue = self._best_item(flavors, "revenue")
            if top_revenue:
                active = top_revenue.get("active", {})
                return (
                    f"{top_revenue['product_flavor'].title()} generated the most active revenue "
                    f"with ${active.get('revenue', 0):,.2f}."
                )

        return None

    def _best_item(self, items: list[dict], metric: str) -> dict | None:
        return max(items, key=lambda item: item.get("active", {}).get(metric, 0), default=None)

    def _worst_item(self, items: list[dict], metric: str) -> dict | None:
        return min(items, key=lambda item: item.get("active", {}).get(metric, 0), default=None)

    def _find_dimension(self, question: str) -> str | None:
        lowered = question.lower()
        for dimension in ("placement", "device", "geography", "age", "gender", "audience", "hour"):
            if re.search(rf"\b{dimension}\b", lowered):
                return {
                    "age": "age_band",
                    "audience": "audience_type",
                    "hour": "hour_of_day",
                }.get(dimension, dimension)
        return None
