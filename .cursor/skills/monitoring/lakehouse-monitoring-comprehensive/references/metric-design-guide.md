# Metric Design Guide: Planning Your Monitoring Strategy

## Overview

Use this guide to plan your monitoring strategy BEFORE writing any code. Fill in the requirements template, then use the patterns below to design custom metrics.

## Step 1: Fill in Requirements

Copy `assets/templates/monitoring-requirements-template.md` and complete all sections.

### Project Context

| Field | Value |
|-------|-------|
| **Project Name** | _________________ (e.g., retail_analytics, patient_outcomes) |
| **Gold Catalog.Schema** | _________________ (e.g., my_catalog.my_project_gold) |
| **Monitoring Schema** | _________________ (e.g., my_catalog.my_project_gold_monitoring) |
| **Monitoring Owner** | _________________ (team/email for alerts) |

### Tables to Monitor (2-5 critical tables)

| # | Table Name | Type | Monitor Mode | Priority | Alert On |
|---|-----------|------|-------------|----------|----------|
| 1 | fact_sales_daily | Fact | time_series | High | Row count drop >10%, Revenue anomaly |
| 2 | dim_customer | Dimension | snapshot | Medium | New PII detected, SCD2 version explosion |
| 3 | ____________ | ______ | ________ | _______ | _________________________ |
| 4 | ____________ | ______ | ________ | _______ | _________________________ |

**Monitor Priority:**
- **High:** Core business tables, real-time decisions, revenue-impacting
- **Medium:** Important but not critical, daily reports
- **Low:** Reference data, rarely changes

**Monitor Mode:**
- **time_series:** Tables with a timestamp column (most fact tables)
- **snapshot:** Tables without temporal dimension (most dimension tables)

## Step 2: Design Custom Metrics

### Metric Categories by Table Type

**For Fact Tables — Choose what to monitor:**

- [ ] Revenue/Amount metrics (daily totals) — AGGREGATE: `SUM(revenue)`
- [ ] Volume metrics (transaction counts, units sold) — AGGREGATE: `SUM(count)`
- [ ] Averages (transaction value, price per unit) — DERIVED: `revenue / NULLIF(count, 0)`
- [ ] Rates (return rate, conversion rate) — DERIVED: `returns / NULLIF(total, 0) * 100`
- [ ] Drift detection (identify anomalies) — DRIFT: `{{current_df}}.metric - {{base_df}}.metric`

**For Dimension Tables — Choose what to monitor:**

- [ ] Row counts (total records) — AGGREGATE: `COUNT(*)`
- [ ] Distinct counts (unique entities) — AGGREGATE: `COUNT(DISTINCT entity_id)`
- [ ] SCD2 checks (versions per entity, current records) — DERIVED: `total / NULLIF(distinct, 0)`
- [ ] Data freshness (last updated timestamp) — AGGREGATE: `MAX(updated_timestamp)`

### Custom Metrics Template: Fact Table

| Metric Type | Metric Name | Definition | Input Columns |
|------------|-------------|------------|---------------|
| AGGREGATE | total_daily_revenue | `SUM(net_revenue)` | `:table` |
| AGGREGATE | total_transactions | `SUM(transaction_count)` | `:table` |
| DERIVED | avg_transaction_value | `total_daily_revenue / NULLIF(total_transactions, 0)` | `:table` |
| DRIFT | revenue_drift_pct | `(({{current_df}}.total_daily_revenue - {{base_df}}.total_daily_revenue) / NULLIF({{base_df}}.total_daily_revenue, 0)) * 100` | `:table` |

### Custom Metrics Template: Dimension Table

| Metric Type | Metric Name | Definition | Input Columns |
|------------|-------------|------------|---------------|
| AGGREGATE | total_records | `COUNT(*)` | `:table` |
| AGGREGATE | distinct_entities | `COUNT(DISTINCT entity_id)` | `:table` |
| DERIVED | versions_per_entity | `total_records / NULLIF(distinct_entities, 0)` | `:table` |

**CRITICAL:** For table-level business KPIs, **ALWAYS use `input_columns=[":table"]` for ALL related metrics** (AGGREGATE, DERIVED, DRIFT). This ensures they're stored in the same row and can be cross-referenced.

## Step 3: Define Alert Strategy

| Table | Metric | Threshold | Action |
|-------|--------|-----------|--------|
| fact_sales_daily | row_count | < 90% of 7-day avg | Alert team |
| fact_sales_daily | total_daily_revenue | > 2 std dev from mean | Investigate |
| dim_customer | distinct_customers | Sudden 20% drop | Alert immediately |
| _____________ | ______________ | _________________ | _____________ |

## Metric Syntax Quick Reference

### AGGREGATE

```python
MonitorMetric(
    type=MonitorMetricType.CUSTOM_METRIC_TYPE_AGGREGATE,
    name="total_daily_revenue",
    input_columns=[":table"],
    definition="SUM(net_revenue)",  # ✅ Raw SQL on table columns
    output_data_type=T.StructField("output", T.DoubleType()).json()
)
```

### DERIVED (NO {{ }} templates!)

```python
MonitorMetric(
    type=MonitorMetricType.CUSTOM_METRIC_TYPE_DERIVED,
    name="avg_transaction_value",
    input_columns=[":table"],
    definition="total_daily_revenue / NULLIF(total_transactions, 0)",  # ✅ Direct reference
    output_data_type=T.StructField("output", T.DoubleType()).json()
)
```

### DRIFT (MUST use {{ }} templates!)

```python
MonitorMetric(
    type=MonitorMetricType.CUSTOM_METRIC_TYPE_DRIFT,
    name="revenue_drift_pct",
    input_columns=[":table"],
    definition="(({{current_df}}.total_daily_revenue - {{base_df}}.total_daily_revenue) / NULLIF({{base_df}}.total_daily_revenue, 0)) * 100",  # ✅ Window comparison
    output_data_type=T.StructField("output", T.DoubleType()).json()
)
```

## Design Monitoring Strategy Checklist

- [ ] **Tables identified:** 2-5 critical Gold tables selected
- [ ] **Monitor mode chosen:** time_series (with timestamp) or snapshot (without)
- [ ] **Custom metrics defined:** Per table with business justification
- [ ] **Metric grain decided:** `:table` (most common) or per-column
- [ ] **Alert thresholds set:** Per metric with action plan
- [ ] **Metric types balanced:** AGGREGATE → DERIVED → DRIFT pipeline
- [ ] **input_columns consistent:** All related metrics use same value
