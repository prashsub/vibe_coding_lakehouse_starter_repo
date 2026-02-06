# Quick Start Guide: Lakehouse Monitoring Setup

## Overview

**Goal:** Automated data quality and drift monitoring for critical Gold tables
**Time Estimate:** 2 hours

**What You'll Create:**
1. Monitor setup script with custom business metrics
2. Initialization wait script with status polling
3. Asset Bundle job for deployment

## Fast Track

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import (
    MonitorMetric, MonitorMetricType, MonitorTimeSeries, MonitorSnapshot
)
from pyspark.sql import types as T

w = WorkspaceClient()

# 1. Define custom metrics (AGGREGATE → DERIVED → DRIFT)
custom_metrics = [
    MonitorMetric(
        type=MonitorMetricType.CUSTOM_METRIC_TYPE_AGGREGATE,
        name="total_revenue",
        input_columns=[":table"],
        definition="SUM(net_revenue)",
        output_data_type=T.StructField("output", T.DoubleType()).json()
    ),
    MonitorMetric(
        type=MonitorMetricType.CUSTOM_METRIC_TYPE_DERIVED,
        name="avg_revenue",
        input_columns=[":table"],
        definition="total_revenue / NULLIF(row_count, 0)",  # ✅ NO {{ }} for DERIVED
        output_data_type=T.StructField("output", T.DoubleType()).json()
    ),
    MonitorMetric(
        type=MonitorMetricType.CUSTOM_METRIC_TYPE_DRIFT,
        name="revenue_change",
        input_columns=[":table"],
        definition="{{current_df}}.total_revenue - {{base_df}}.total_revenue",  # ✅ MUST use {{ }} for DRIFT
        output_data_type=T.StructField("output", T.DoubleType()).json()
    ),
]

# 2. Create monitor
monitor = w.quality_monitors.create(
    table_name=f"{catalog}.{schema}.fact_sales_daily",
    assets_dir=f"/Workspace/Shared/lakehouse_monitoring/{catalog}/{schema}",
    output_schema_name=f"{catalog}.{schema}_monitoring",
    time_series=MonitorTimeSeries(
        timestamp_col="transaction_date",
        granularities=["1 day"]
    ),
    custom_metrics=custom_metrics
)

# 3. Wait for async initialization (15-20 minutes!)
```

## Critical Patterns

- **ALL related metrics MUST use SAME `input_columns`** (e.g., all use `[":table"]`)
- **DERIVED references aggregate names directly** (NO `{{ }}` template syntax)
- **DRIFT MUST use `{{current_df}}` and `{{base_df}}` templates** for window comparison
- **`output_data_type` MUST be `T.StructField("output", T.DoubleType()).json()`** (NOT string `"double"`)
- **Wait for async refresh** before querying metrics (15-20 minutes)
- **Custom metrics stored in profile table** — AGGREGATE/DERIVED in `{table}_profile_metrics`, DRIFT in `{table}_drift_metrics`

## Metric Query Patterns

```sql
-- AGGREGATE & DERIVED: column_name = ':table'
SELECT
  window.start,
  window.end,
  total_revenue,
  avg_revenue
FROM {catalog}.{monitoring_schema}.{table}_profile_metrics
WHERE log_type = 'INPUT'
  AND column_name = ':table'
ORDER BY window.start DESC;

-- DRIFT: separate table
SELECT
  window.start,
  drift_type,
  revenue_change
FROM {catalog}.{monitoring_schema}.{table}_drift_metrics
WHERE drift_type = 'CONSECUTIVE'
  AND column_name = ':table'
ORDER BY window.start DESC;
```

**Output:** Automated monitoring with dashboards in monitor assets directory.

## Implementation Checklist

### Phase 1: Design (30 min)
- [ ] Identify tables to monitor (2-5 critical Gold tables)
- [ ] Define custom metrics for each table (use `metric-design-guide.md`)
- [ ] Decide metric grain (`:table` or per-column)
- [ ] Define alert thresholds

### Phase 2: Setup Script (1 hour)
- [ ] Copy `scripts/setup_monitors_template.py` as starting point
- [ ] Define monitor functions per table (see `example-monitor-definitions.md`)
- [ ] Implement complete cleanup (delete existing monitors + output tables)
- [ ] Add error handling (raise on failure)
- [ ] Use `MonitorMetric` SDK objects with correct syntax

### Phase 3: Initialization Wait (30 min)
- [ ] Run setup script to create monitors
- [ ] Run `scripts/wait_for_initialization.py` to poll for ACTIVE status
- [ ] Wait for monitors to activate (15-20 minutes)

### Phase 4: Validation (30 min)
- [ ] Query profile metrics (table-level with `column_name = ':table'`)
- [ ] Query custom metrics (appear as NEW COLUMNS, not separate table)
- [ ] Verify drift metrics in separate `_drift_metrics` table
- [ ] Document monitoring tables for Genie (see `deployment-guide.md`)

## Next Steps

After monitoring is set up:
1. **Dashboards** — Create AI/BI dashboards from monitoring tables
2. **Alerts** — Set up SQL alerts on monitoring metrics
3. **Genie** — Add monitoring tables to Genie Space with descriptions
