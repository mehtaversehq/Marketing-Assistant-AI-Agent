# Marketing Assistant AI Agent

## Overview

Marketing Assistant AI Agent is a Python-based analytics assistant for campaign performance data. It validates campaign CSV files, computes deterministic KPI analysis, generates JSON and Markdown reports, and can optionally use a local Ollama model for narrative summaries and Q&A.

The project is designed around a simple principle: AI should explain validated metrics, not replace deterministic business logic.

## Business Problem

Marketers often work across scattered campaign data, business documents, and performance metrics. This makes campaign analysis slow, repetitive, and fragmented. A useful assistant should organize the data, calculate reliable metrics, and explain the results in plain language without inventing unsupported conclusions.

## What the System Does

The system reads sample campaign CSVs, validates the records, computes active-vs-historical performance metrics, identifies strong and weak campaign segments, writes structured outputs, and answers common questions from the generated analysis artifacts.

Ollama is optional. If Ollama is not running, the deterministic analytics pipeline still works and the app uses fallback summaries and rule-based answers for common metric questions.

## Features

- Campaign CSV validation
- KPI analysis for spend, revenue, conversions, ROAS, and conversion rate
- Active vs historical campaign comparison
- Product flavor and segment performance analysis
- JSON output generation
- Markdown report generation
- Optional Ollama-powered AI summaries and Q&A
- Deterministic fallback answers when Ollama is unavailable

## Architecture

```text
CSV input
-> validation
-> KPI analysis
-> summary generation
-> Markdown report
-> optional Ollama narrative/chat
```

The core pipeline is deterministic Python. Ollama is only used for natural-language explanation after the metrics have already been computed.

## Project Structure

```text
.
├── README.md
├── pyproject.toml
├── requirements.txt
├── data/
│   ├── campaign_csvs/
│   └── business_documents/
├── docs/
│   ├── architecture.md
│   ├── output_schema.md
│   └── deprecated/
├── knowledge/
├── outputs/
│   ├── analysis.json
│   ├── summary.json
│   └── report.md
├── src/
│   └── mktaiproject/
│       ├── main.py
│       ├── analysis/
│       ├── chat/
│       ├── llm/
│       ├── pipeline/
│       ├── reporting/
│       └── validation/
└── tests/
```

## Setup

From the outer workspace folder, enter the project folder first:

```bash
cd mktaiproject
```

Create or activate a Python environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project if you want package entry points:

```bash
python3 -m pip install -e .
```

The active deterministic pipeline uses only the Python standard library.

## Running Tests

Run these commands from the `mktaiproject/` folder.

```bash
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
```

If you are not using the virtual environment:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Running the Pipeline

Run this command from the `mktaiproject/` folder:

```bash
PYTHONPATH=src python3 -m mktaiproject.main run
```

If your terminal is still in the outer `mktAIProject/` folder, use:

```bash
PYTHONPATH=mktaiproject/src python3 -m mktaiproject.main run
```

Ask a question after generating artifacts:

```bash
PYTHONPATH=src python3 -m mktaiproject.main ask "Which flavor is performing best?"
```

Show output paths:

```bash
PYTHONPATH=src python3 -m mktaiproject.main show
```

## Generated Outputs

- `outputs/analysis.json`: structured KPI analysis, validation notes, segment highlights, and recommendations
- `outputs/summary.json`: generated or fallback narrative summary
- `outputs/report.md`: readable Markdown report for review or sharing

These files are small demo artifacts. Running the pipeline refreshes them.

## Optional Ollama Integration

The app expects Ollama at `http://localhost:11434` when local LLM narration is desired.

Optional environment variables:

```bash
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=qwen3:8b
```

If Ollama is not running at `localhost:11434`, the system does not crash. It returns a clean fallback summary and answers common metric questions from deterministic analysis results.

## Known Limitations

- Ollama must be running for local LLM narration and fully natural-language chat.
- Fallback Q&A is rule-based and covers common metric questions.
- The sample data is intentionally small and portfolio-oriented.
- The archived CrewAI scaffold is not part of the active pipeline unless intentionally restored.

## Future Improvements

- Better deterministic Q&A fallback
- More campaign schemas
- Streamlit or web dashboard
- Better visualization
- More robust local LLM model selection
- Support for business documents and meeting notes

## Portfolio Summary

Built a Python-based marketing assistant AI system that validates campaign data, computes KPI metrics, generates structured JSON/Markdown reports, and supports optional local LLM-powered campaign narration and Q&A through Ollama. The system separates deterministic business logic from AI-generated explanation, making it more reliable for decision support.

Tags: Python, AI Agent, Data Analysis, Report Generation, Decision Support, Marketing Analytics, Local LLM, Ollama
