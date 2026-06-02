from __future__ import annotations

import json

from mktaiproject.llm import OllamaClient
from mktaiproject.models import AnalysisResult


class InsightNarrator:
    """Create a human-readable campaign summary.

    Ollama is optional. If the local model server is unavailable, this class
    still returns a deterministic summary from computed metrics.
    """

    def __init__(self, client: OllamaClient | None = None) -> None:
        self.client = client or OllamaClient()

    def summarize(self, analysis: AnalysisResult) -> dict[str, str]:
        """Return an LLM narrative when available, otherwise a fallback narrative."""
        payload = {
            "headline_metrics": analysis.headline_metrics,
            "flavor_performance": analysis.flavor_performance,
            "hourly_highlights": analysis.hourly_highlights,
            "recommendations": analysis.recommendations,
            "validation_issues": [
                {"dataset": issue.dataset, "severity": issue.severity, "message": issue.message}
                for issue in analysis.validation_issues
            ],
        }
        prompt = (
            "You are summarizing marketing campaign performance for a marketer.\n"
            "Stay grounded in the provided JSON. Do not invent metrics.\n"
            "Return plain text with these headings:\n"
            "Executive Summary\nWhat Happened\nWhy It Happened\nRecommended Actions\nUncertainty\n\n"
            f"{json.dumps(payload, indent=2)}"
        )
        system = (
            "You are a careful marketing analyst. Every claim must be backed by the input. "
            "State uncertainty clearly when data is limited."
        )
        response = self.client.generate(prompt=prompt, system=system, temperature=0.1)
        if response.ok and response.content:
            return {"narrative": response.content, "status": "generated"}

        return {
            "status": "fallback",
            "narrative": self._fallback_narrative(analysis, response.error or "Ollama unavailable."),
        }

    def _fallback_narrative(self, analysis: AnalysisResult, error: str) -> str:
        active = analysis.headline_metrics["active"]
        historical = analysis.headline_metrics["historical"]
        best_flavor = analysis.flavor_performance[0]["product_flavor"] if analysis.flavor_performance else "unknown"
        worst_flavor = analysis.flavor_performance[-1]["product_flavor"] if analysis.flavor_performance else "unknown"
        return (
            "Executive Summary\n"
            f"Ollama was unavailable, so this summary was generated from deterministic metrics only. {error}\n\n"
            "What Happened\n"
            f"Active spend was {active['spend']:.2f} with revenue {active['revenue']:.2f}, "
            f"versus historical spend {historical['spend']:.2f} and revenue {historical['revenue']:.2f}.\n\n"
            "Why It Happened\n"
            f"{best_flavor} leads the active flavor set while {worst_flavor} is the weakest current flavor by ROAS.\n\n"
            "Recommended Actions\n"
            + "\n".join(f"- {item}" for item in analysis.recommendations)
            + "\n\nUncertainty\n"
            "Interpretation is limited to the available CSV datasets and their precomputed metrics."
        )
