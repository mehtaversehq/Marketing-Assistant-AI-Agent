# Marketing Insights Report

## Dataset Overview
- active_campaign_performance_month.csv: 3 rows, date range 2026-03-01 to 2026-03-01
- active_hourly_breakdown_month.csv: 6480 rows, date range 2026-03-01 to 2026-03-30
- historical_campaign_performance_month.csv: 3 rows, date range 2025-11-15 to 2025-11-15
- historical_hourly_breakdown_month.csv: 6480 rows, date range 2025-11-15 to 2025-12-14

## Validation Notes
- No validation issues detected.

## Narrative
Executive Summary
Ollama was unavailable, so this summary was generated from deterministic metrics only. Ollama is not reachable at http://localhost:11434.

What Happened
Active spend was 15772.94 with revenue 4023.54, versus historical spend 15944.29 and revenue 2679.38.

Why It Happened
strawberry leads the active flavor set while vanilla is the weakest current flavor by ROAS.

Recommended Actions
- Active campaign ROAS is ahead of the historical baseline; scale only the best-performing segments.
- Prioritize strawberry creative testing and review why vanilla lags on ROAS.
- Shift budget away from hour_of_day=23.0 and toward hour_of_day=22.0 if volume holds.

Uncertainty
Interpretation is limited to the available CSV datasets and their precomputed metrics.

## Recommended Actions
- Active campaign ROAS is ahead of the historical baseline; scale only the best-performing segments.
- Prioritize strawberry creative testing and review why vanilla lags on ROAS.
- Shift budget away from hour_of_day=23.0 and toward hour_of_day=22.0 if volume holds.
