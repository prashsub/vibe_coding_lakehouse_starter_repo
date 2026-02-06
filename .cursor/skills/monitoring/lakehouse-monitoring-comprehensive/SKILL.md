---
name: lakehouse-monitoring-comprehensive
description: Comprehensive guide for Databricks Lakehouse Monitoring - setup, custom metrics, querying, and best practices. Use when setting up Lakehouse Monitoring for Gold layer tables, creating custom business metrics, querying monitoring tables for dashboards, or troubleshooting monitor initialization failures. Includes setup patterns with graceful degradation, custom metric syntax (AGGREGATE, DERIVED, DRIFT), table-level business KPIs with input_columns=[":table"], query patterns for dashboards, async operations handling, monitor cleanup, and documentation for Genie integration.
metadata:
  author: databricks-sa
  version: "1.0"
  domain: monitoring
---

# Lakehouse Monitoring: Complete Guide for Gold Layer

## Overview

This skill provides comprehensive patterns for setting up Databricks Lakehouse Monitoring on Gold layer tables with custom business metrics, proper error handling, and Genie integration. It covers monitor creation, custom metric design, query patterns, and troubleshooting common issues.

## When to Use This Skill

- Setting up Lakehouse Monitoring for Gold layer tables
- Creating custom business metrics (AGGREGATE, DERIVED, DRIFT)
- Querying monitoring tables for dashboards
- Troubleshooting monitor initialization failures
- Documenting monitoring tables for Genie/LLM integration
- Updating existing monitors without losing custom metrics

## Core Principles

### Principle 1: Graceful Degradation
Monitor setup should handle SDK version differences, missing tables, and existing monitors gracefully.

### Principle 2: Business-First Metrics
Every custom metric must answer: **"What business decision would change based on this metric?"**

### Principle 3: Table-Level Business KPIs
**⚠️ CRITICAL:** For table-level business KPIs that reference each other, ALWAYS use `input_columns=[":table"]` for ALL metric types (AGGREGATE, DERIVED, DRIFT).

**Why This Matters:**
- DERIVED metrics can ONLY reference metrics in the same `column_name` row
- DRIFT metrics can ONLY compare metrics in the same `column_name` row  
- Mixing `input_columns` values breaks cross-references → NULL values

**Decision Tree:**
```
Is this a table-level business KPI?
├─ YES → Use input_columns=[":table"]
│        - Will be used in DERIVED metrics
│        - Will be compared in DRIFT metrics
│        - Represents overall business state
│        → ALL RELATED METRICS MUST USE [":table"]
│
└─ NO → Is it column-specific profiling?
         └─ YES → Use input_columns=["column_name"]
                  - Tracks column-specific statistics
                  - Won't be referenced by other metrics
                  - Pure data quality monitoring
```

### Principle 4: Where Custom Metrics Appear

**⚠️ CRITICAL:** Custom metrics appear as **NEW COLUMNS** in monitoring output tables:
- **AGGREGATE + DERIVED metrics** → `{table}_profile_metrics` table (as new columns)
- **DRIFT metrics** → `{table}_drift_metrics` table (as new columns)
- **There is NO separate `custom_metrics` table!**

## Quick Reference

### Monitor Creation Checklist

- [ ] Import monitoring classes with try-except for graceful degradation
- [ ] Check MONITORING_AVAILABLE before creating monitors
- [ ] Specify ONE of: snapshot, time_series, inference_log
- [ ] Handle ResourceAlreadyExists and ResourceDoesNotExist exceptions
- [ ] Use hasattr() for MonitorInfo attributes (SDK version differences)
- [ ] Delete existing monitor + tables before recreating
- [ ] Wait 15+ minutes after creation before querying tables
- [ ] Document tables for Genie AFTER monitors initialize

### Custom Metrics Checklist

- [ ] **CRITICAL:** All table-level business KPIs use `input_columns=[":table"]`
- [ ] All related metrics (AGGREGATE/DERIVED/DRIFT) use same `input_columns`
- [ ] No nested aggregations (use AGGREGATE → DERIVED pattern)
- [ ] Use DERIVED metrics for ratios/percentages
- [ ] NULLIF guards against division by zero
- [ ] All metrics have output_data_type specified (StructField.json() format)
- [ ] Metrics organized by business category with comments

### Query Patterns Checklist

- [ ] Use `log_type = 'INPUT'` (not 'OUTPUT')
- [ ] Filter to correct `column_name` value (`:table` for table-level metrics)
- [ ] Handle NULL slices with COALESCE
- [ ] Use PIVOT only for per-column metrics (rare)
- [ ] Direct SELECT for table-level metrics (common)

## Critical Rules

### Rule 1: Monitor Mode is Required

**❌ WRONG:** No mode specified
```python
monitor = workspace_client.quality_monitors.create(
    table_name=table_name,
    # Missing: snapshot, time_series, or inference_log
)
```

**✅ CORRECT:** Explicit mode
```python
monitor = workspace_client.quality_monitors.create(
    table_name=table_name,
    snapshot=MonitorSnapshot(),  # or time_series
    custom_metrics=[...],
)
```

### Rule 2: Consistent input_columns for Related Metrics

**❌ WRONG:** Mixing input_columns values
```python
MonitorMetric(
    name="total_gross_revenue",
    input_columns=["gross_revenue"],  # ← Stored in 'gross_revenue' row
    ...
)
MonitorMetric(
    name="overall_return_rate",
    input_columns=[":table"],  # ← Looks in ':table' row
    definition="(total_return_amount / NULLIF(total_gross_revenue, 0)) * 100"
    # ❌ Can't find total_gross_revenue!
)
```

**✅ CORRECT:** All use same input_columns
```python
MonitorMetric(
    name="total_gross_revenue",
    input_columns=[":table"],  # ✅ Table-level
    ...
)
MonitorMetric(
    name="overall_return_rate",
    input_columns=[":table"],  # ✅ Same location
    definition="(total_return_amount / NULLIF(total_gross_revenue, 0)) * 100"
)
```

### Rule 3: Update is Replacement, Not Merge

**⚠️ CRITICAL:** `quality_monitors.update()` is a **REPLACEMENT operation**. If you omit `custom_metrics`, they are **DELETED**.

**✅ CORRECT:** Always include full custom_metrics
```python
# Import from pure Python config file
from monitor_configs import get_all_monitor_configs

monitor_configs = get_all_monitor_configs(catalog, schema)
# ✅ Includes ALL custom metrics

for config in monitor_configs:
    workspace_client.quality_monitors.update(**config)
```

### Rule 4: output_data_type Format

**❌ WRONG:** String format (monitor creates but NEVER initializes!)
```python
MonitorMetric(
    output_data_type="double"  # String format not supported
)
```

**✅ CORRECT:** StructField.json() format
```python
from pyspark.sql import types as T

MonitorMetric(
    output_data_type=T.StructField("output", T.DoubleType()).json()
)
```

### Rule 5: DERIVED vs DRIFT Syntax

**DERIVED:** Direct reference (NO templates)
```python
# ✅ CORRECT
definition="(total_cancellations / NULLIF(total_bookings, 0)) * 100"

# ❌ WRONG
definition="({{total_cancellations}} / NULLIF({{total_bookings}}, 0)) * 100"
```

**DRIFT:** Template syntax (MUST use templates)
```python
# ✅ CORRECT
definition="{{current_df}}.daily_revenue - {{base_df}}.daily_revenue"

# ❌ WRONG
definition="daily_revenue"  # Missing window comparison
```

## Core Patterns

### Pattern 1: Monitor Creation with Error Handling

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.errors import ResourceAlreadyExists, ResourceDoesNotExist
from databricks.sdk.service.catalog import MonitorTimeSeries, MonitorSnapshot

def create_table_monitor(workspace_client, catalog, schema, table, monitor_type="time_series"):
    table_name = f"{catalog}.{schema}.{table}"
    
    try:
        if monitor_type == "snapshot":
            config = {"snapshot": MonitorSnapshot()}
        elif monitor_type == "time_series":
            config = {
                "time_series": MonitorTimeSeries(
                    timestamp_col="transaction_date",
                    granularities=["1 day"]
                )
            }
        
        monitor = workspace_client.quality_monitors.create(
            table_name=table_name,
            assets_dir=f"/Workspace/Shared/lakehouse_monitoring/{catalog}/{schema}",
            output_schema_name=f"{catalog}.{schema}_monitoring",
            **config,
            custom_metrics=[...],  # See custom-metrics.md
        )
        return monitor
        
    except ResourceAlreadyExists:
        print(f"⚠️  Monitor already exists - skipping")
        return None
    except ResourceDoesNotExist:
        print(f"⚠️  Table does not exist - skipping")
        return None
```

### Pattern 2: Complete Cleanup Before Recreation

```python
def delete_monitor_if_exists(workspace_client, table_name, spark):
    """Delete monitor AND output tables."""
    try:
        workspace_client.quality_monitors.get(table_name=table_name)
        workspace_client.quality_monitors.delete(table_name=table_name)
        
        catalog, schema, table = table_name.split(".")
        monitoring_schema = f"{schema}_monitoring"
        
        spark.sql(f"DROP TABLE IF EXISTS {catalog}.{monitoring_schema}.{table}_profile_metrics")
        spark.sql(f"DROP TABLE IF EXISTS {catalog}.{monitoring_schema}.{table}_drift_metrics")
        return True
    except ResourceDoesNotExist:
        return False  # Silent success

# Use before creating
delete_monitor_if_exists(workspace_client, table_name, spark)
create_table_monitor(...)
```

### Pattern 3: Wait for Async Table Creation

```python
def wait_with_progress(minutes: int = 15):
    """Wait with progress updates."""
    wait_seconds = minutes * 60
    for elapsed in range(0, wait_seconds, 60):
        progress_pct = (elapsed / wait_seconds) * 100
        remaining = wait_seconds - elapsed
        print(f"⏱️  Progress: {progress_pct:.1f}% | Remaining: {remaining//60}m")
        time.sleep(60)

# Use after creation
create_monitor(...)
wait_with_progress(minutes=15)  # ✅ Wait for async table creation
document_monitoring_tables(...)  # ✅ Now tables exist
```

### Pattern 4: Query Table-Level Metrics

```sql
-- For metrics with input_columns=[":table"]
SELECT 
  window.start,
  window.end,
  total_net_revenue,
  total_transactions,
  avg_transaction_amount,
  overall_return_rate
FROM fact_sales_daily_profile_metrics
WHERE log_type = 'INPUT'
  AND column_name = ':table'  -- ✅ All table-level metrics here
ORDER BY window.start DESC
```

## Reference Files

### [monitor-configuration.md](references/monitor-configuration.md)
Complete monitor configuration patterns including:
- Import with graceful fallback
- Exception handling patterns
- Monitor mode configuration (snapshot vs time_series)
- Complete monitor creation template
- Async operations handling
- Monitor cleanup patterns
- Monitor update patterns
- API parameters reference

### [custom-metrics.md](references/custom-metrics.md)
Comprehensive custom metrics guide including:
- Required imports
- Three metric types (AGGREGATE, DERIVED, DRIFT)
- Syntax patterns for each type
- Critical syntax rules
- Monitor mode and drift requirements
- Business-focused metric categories
- Custom metric limitations
- Metric organization patterns
- Where custom metrics appear

### [deployment-guide.md](references/deployment-guide.md)
Deployment and documentation guide including:
- Documenting monitor output tables for Genie
- Documentation registry pattern
- Documentation function implementation
- Integration with setup workflow
- Documentation job configuration
- Description format guidelines
- Query patterns for dashboards
- Complete workflow examples

## Scripts

### [create_monitor.py](scripts/create_monitor.py)
Reusable monitor creation utility with:
- `create_table_monitor()` - Create monitor with error handling
- `delete_monitor_if_exists()` - Complete cleanup (monitor + tables)
- `wait_with_progress()` - Wait for async table creation

**Usage:**
```python
from scripts.create_monitor import create_table_monitor, delete_monitor_if_exists

# Cleanup first
delete_monitor_if_exists(workspace_client, table_name, spark)

# Create monitor
monitor = create_table_monitor(
    workspace_client=workspace_client,
    catalog=catalog,
    schema=schema,
    table=table,
    monitor_type="time_series",
    timestamp_col="transaction_date",
    custom_metrics=[...]
)
```

## Troubleshooting

### Common Mistakes

1. **Mixing input_columns values** → DERIVED metrics return NULL
   - **Fix:** Use `input_columns=[":table"]` for all related metrics

2. **Not specifying monitor mode** → Creation fails
   - **Fix:** Always specify `snapshot` OR `time_series` OR `inference_log`

3. **Querying wrong column_name** → Returns NULL
   - **Fix:** Use `WHERE column_name = ':table'` for table-level metrics

4. **Updating without full custom_metrics** → All metrics deleted
   - **Fix:** Always include complete `custom_metrics` list in update

5. **Trying to document custom_metrics table** → Table doesn't exist
   - **Fix:** Document columns in `profile_metrics` and `drift_metrics` tables

### Production Deployment Errors

See [deployment-guide.md](references/deployment-guide.md) for detailed error patterns from production deployments:
- Using dictionaries instead of SDK objects
- Incorrect output_data_type format (silent killer)
- SDK version attribute differences
- Wrong monitor mode for table type
- DRIFT metric on snapshot without baseline
- INVALID_DERIVED_METRIC - Template syntax
- INVALID_DRIFT_METRIC - Missing window comparison

## References

### Official Documentation
- [Lakehouse Monitoring Guide](https://docs.databricks.com/lakehouse-monitoring/)
- [Monitor API Reference](https://docs.databricks.com/api/workspace/qualitymonitors/create)
- [Custom Metrics](https://learn.microsoft.com/azure/databricks/lakehouse-monitoring/custom-metrics)
- [Profile Metrics Table Schema](https://docs.databricks.com/lakehouse-monitoring/monitor-output#profile-metrics-table-schema)
- [Drift Metrics Table Schema](https://docs.databricks.com/lakehouse-monitoring/monitor-output#drift-metrics-table-schema)

## Summary

**Key Takeaways:**
- Always use `input_columns=[":table"]` for table-level business KPIs
- Custom metrics appear as NEW COLUMNS (no separate `custom_metrics` table)
- DERIVED metrics can only reference metrics in the same `column_name` row
- Wait 15+ minutes after creation for tables to be ready
- Always update with FULL configuration (never omit custom_metrics)
- Document metrics in `profile_metrics` and `drift_metrics` tables

**Next Steps:**
1. Read [monitor-configuration.md](references/monitor-configuration.md) for setup patterns
2. Review [custom-metrics.md](references/custom-metrics.md) for metric design
3. Use [deployment-guide.md](references/deployment-guide.md) for query patterns
4. Use [create_monitor.py](scripts/create_monitor.py) utility for implementation
