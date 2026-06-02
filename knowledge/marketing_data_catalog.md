# Marketing Data Catalog

The active sample campaign data lives in `data/campaign_csvs/` and includes four CSV files.

## Campaign Performance Files

`active_campaign_performance_month.csv`
- Grain: one row per active ad/ad set/product flavor summary.
- Use for: top-level active campaign performance, spend, revenue, ROAS, conversions, and budget fields.

`historical_campaign_performance_month.csv`
- Grain: one row per historical ad/ad set/product flavor summary.
- Use for: baseline comparisons between current and previous campaign performance.

## Hourly Breakdown Files

`active_hourly_breakdown_month.csv`
- Grain: one row per active hourly user-level event record.
- Use for: time-of-day patterns, placement/device/geography breakdowns, and active segment performance.

`historical_hourly_breakdown_month.csv`
- Grain: one row per historical hourly user-level event record.
- Use for: historical hourly patterns and segmented comparisons against active data.

## Guidance

- Treat the CSV datasets as the source of truth for campaign metrics.
- Prefer campaign performance files for summarized KPI comparisons.
- Prefer hourly breakdown files for segmentation, trends, and timing analysis.
- When a precise value is needed, use `outputs/analysis.json` or inspect the relevant CSV directly rather than inferring.
