# Output Schema

The pipeline writes three artifacts under `outputs/`.

## `analysis.json`

Structured analysis used by reports and chat.

Main fields:

- `generated_at`: UTC timestamp for the run.
- `dataset_summaries`: row counts, columns, numeric fields, dimensions, and date ranges.
- `validation_issues`: validation warnings or errors.
- `headline_metrics`: active, historical, and delta metrics for spend, revenue, conversions, clicks, impressions, ROAS, and conversion rate.
- `flavor_performance`: active and historical metrics by product flavor.
- `segment_highlights`: strongest and weakest segments across placement, device, geography, age band, gender, audience type, and hour of day.
- `hourly_highlights`: best and worst hours by dataset type.
- `recommendations`: deterministic action suggestions.
- `source_files`: CSV files used in the analysis.

## `summary.json`

Narrative summary metadata.

Main fields:

- `status`: `generated` when Ollama produced the narrative, `fallback` when deterministic summary was used.
- `narrative`: plain-text summary.

## `report.md`

Markdown report for human review.

Sections:

- Dataset Overview
- Validation Notes
- Narrative
- Recommended Actions
