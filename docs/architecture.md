# Architecture

Marketing Assistant AI Agent uses deterministic Python for data handling and metric calculation. The optional LLM layer only explains the computed results.

## Flow

```text
CLI command
-> load campaign CSVs from data/campaign_csvs/
-> validate required fields and basic numeric integrity
-> calculate KPI metrics and segment highlights
-> generate deterministic or Ollama-assisted summary
-> write JSON and Markdown artifacts to outputs/
-> answer questions using the latest artifacts
```

## Main Modules

- `src/mktaiproject/main.py`: CLI entry point.
- `src/mktaiproject/validation/`: CSV loading, type coercion, and validation.
- `src/mktaiproject/analysis/`: deterministic KPI and segment analysis.
- `src/mktaiproject/reporting/`: artifact storage and summary generation.
- `src/mktaiproject/llm/`: optional Ollama client.
- `src/mktaiproject/chat/`: Q&A over generated analysis artifacts.
- `src/mktaiproject/pipeline/`: orchestration from input data to outputs.

## Design Choice

The project intentionally separates metric calculation from text generation. This keeps business logic auditable and makes missing Ollama a graceful fallback case instead of a pipeline failure.
