#!/usr/bin/env python
from __future__ import annotations

import argparse
import json

from mktaiproject.chat import MarketingChatbot
from mktaiproject.pipeline import MarketingInsightsPipeline
from mktaiproject.reporting import ArtifactStore


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser for the portfolio demo application."""
    parser = argparse.ArgumentParser(description="Local marketing insights pipeline powered by deterministic analysis and Ollama.")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("run", help="Load campaign data, analyze it, and write fresh artifacts.")

    ask_parser = subparsers.add_parser("ask", help="Ask a grounded question against the latest analysis artifacts.")
    ask_parser.add_argument("question", help="Question to answer using the latest analysis artifacts.")

    subparsers.add_parser("show", help="Print the latest generated analysis paths.")
    return parser


def run() -> dict[str, str]:
    """CLI entry point used by `python3 -m mktaiproject.main`."""
    args = build_parser().parse_args()
    command = args.command or "run"

    if command == "run":
        try:
            result = MarketingInsightsPipeline().run()
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        print(json.dumps(result, indent=2))
        return result

    if command == "ask":
        answer = MarketingChatbot().answer(args.question)
        print(answer)
        return {"answer": answer}

    if command == "show":
        store = ArtifactStore()
        payload = {
            "analysis_path": str(store.analysis_path),
            "summary_path": str(store.summary_path),
            "report_path": str(store.report_path),
        }
        print(json.dumps(payload, indent=2))
        return payload

    raise SystemExit(f"Unsupported command: {command}")

if __name__ == "__main__":
    run()
