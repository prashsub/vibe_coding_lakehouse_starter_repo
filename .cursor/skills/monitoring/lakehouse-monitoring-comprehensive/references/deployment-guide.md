# Lakehouse Monitoring Deployment Guide

## Document Monitor Output Tables for Genie

**⚠️ CRITICAL:** After monitors initialize (~15 min), add detailed descriptions to output tables so Genie/LLMs can understand the metrics for natural language queries.

**Problem:** By default, Lakehouse Monitoring creates `_profile_metrics` and `_drift_metrics` tables with no descriptions. Custom metrics appear as columns with no context, making Genie unable to interpret them correctly.

**Solution:** Add table and column comments after monitors initialize.

## Documentation Registry Pattern

Create a centralized metric descriptions dictionary:

```python
# monitor_utils.py

METRIC_DESCRIPTIONS = {
    # Format: "metric_name": "Business meaning. Technical: calculation details."
    
    # Cost metrics
    "total_daily_cost": "Total daily cost in list prices. Business: Primary FinOps metric for budgeting. Technical: SUM(list_cost), aggregated per time window.",
    "tag_coverage_pct": "Percentage of cost covered by tags. Business: FinOps maturity KPI (target: >90%). Technical: tagged_cost / total_cost * 100.",
    
    # Job metrics
    "success_rate": "Job success rate percentage. Business: Primary reliability KPI (target: >95%). Technical: success_count / total_runs * 100.",
    "p99_duration_minutes": "P99 job duration. Business: Critical SLA threshold for worst-case scenarios. Technical: PERCENTILE(duration, 0.99).",
    
    # Drift metrics
    "cost_drift_pct": "Period-over-period cost change. Business: Budget variance indicator (alert if >10%). Technical: (current - baseline) / baseline * 100.",
}

MONITOR_TABLE_DESCRIPTIONS = {
    "fact_usage": {
        "profile_table": "Lakehouse Monitoring profile metrics for fact_usage. Contains daily cost aggregations, tag coverage, SKU breakdowns. Use column_name=':table' for table-level KPIs. Business: Primary source for FinOps dashboards.",
        "drift_table": "Lakehouse Monitoring drift metrics for fact_usage. Contains period-over-period cost comparisons. Business: Alert source for budget variance monitoring."
    },
    # ... more tables
}
```

## Documentation Function

```python
def document_monitor_output_tables(
    spark,
    catalog: str,
    gold_schema: str,
    table_name: str
) -> dict:
    """
    Add Genie-friendly descriptions to Lakehouse Monitoring output tables.
    
    Run AFTER monitors initialize (~15 min after creation).
    """
    monitoring_schema = f"{gold_schema}_monitoring"
    profile_table = f"{catalog}.{monitoring_schema}.{table_name}_profile_metrics"
    drift_table = f"{catalog}.{monitoring_schema}.{table_name}_drift_metrics"
    
    results = {"profile_metrics": "NOT_FOUND", "drift_metrics": "NOT_FOUND"}
    
    # Get table descriptions
    table_descs = MONITOR_TABLE_DESCRIPTIONS.get(table_name, {})
    profile_desc = table_descs.get("profile_table", f"Profile metrics for {table_name}")
    
    # Document profile_metrics table
    try:
        # Check if table exists
        spark.sql(f"DESCRIBE TABLE {profile_table}")
        
        # Add table comment
        escaped_desc = profile_desc.replace("'", "''")
        spark.sql(f"ALTER TABLE {profile_table} SET TBLPROPERTIES ('comment' = '{escaped_desc}')")
        print(f"  ✓ Added table comment to {table_name}_profile_metrics")
        
        # Add column comments for custom metrics
        columns_documented = 0
        for metric_name, description in METRIC_DESCRIPTIONS.items():
            try:
                escaped_col_desc = description.replace("'", "''")
                spark.sql(f"ALTER TABLE {profile_table} ALTER COLUMN {metric_name} COMMENT '{escaped_col_desc}'")
                columns_documented += 1
            except Exception:
                pass  # Column may not exist in this table
        
        print(f"  ✓ Documented {columns_documented} custom metric columns")
        results["profile_metrics"] = f"SUCCESS: {columns_documented} columns"
        
    except Exception as e:
        if "TABLE_OR_VIEW_NOT_FOUND" in str(e):
            print(f"  ⚠ Table not found (monitor may still be initializing)")
            results["profile_metrics"] = "NOT_READY"
        else:
            results["profile_metrics"] = f"ERROR: {str(e)[:50]}"
    
    # Similar pattern for drift_metrics table...
    
    return results
```

## Integration with Setup Workflow

```python
# setup_all_monitors.py

def main():
    # 1. Create all monitors
    results = setup_all_monitors(workspace_client, catalog, gold_schema, spark)
    
    # 2. Wait for tables to be created (async operation)
    if not skip_wait:
        wait_for_monitor_tables(minutes=15)
        
        # 3. Document tables for Genie AFTER tables exist
        print("Documenting Monitor Tables for Genie...")
        doc_results = document_all_monitor_tables(spark, catalog, gold_schema)
        
        doc_success = sum(
            1 for table_results in doc_results.values()
            for status in table_results.values()
            if "SUCCESS" in status
        )
        print(f"  Documented {doc_success} monitoring tables for Genie")
```

## Documentation Job (Run Separately)

For monitors that already exist, run documentation as a separate job:

```yaml
# lakehouse_monitors_job.yml

lakehouse_monitoring_document_job:
  name: "[${bundle.target}] Document Monitoring Tables for Genie"
  description: "Adds descriptions to Lakehouse Monitor output tables for Genie/LLM understanding"
  
  tasks:
    - task_key: document_all_monitors
      notebook_task:
        notebook_path: ../../src/monitoring/document_monitors.py
        base_parameters:
          catalog: ${var.catalog}
          gold_schema: ${var.gold_schema}
```

## Description Format Guidelines

**Dual-Purpose Format:** Business meaning + Technical details

```python
# ✅ GOOD: Both business and technical context
"success_rate": "Job success rate percentage. Business: Primary reliability KPI (target: >95%). Technical: success_count / total_runs * 100."

# ❌ BAD: Only technical
"success_rate": "success_count / total_runs * 100"

# ❌ BAD: Only business (no calculation)
"success_rate": "Measure of job reliability"
```

**Key Elements:**
- **One-line business description**: What decision this metric informs
- **Business context**: Target values, stakeholders, use cases
- **Technical context**: Calculation formula, data type, source

## Validation Checklist

- [ ] Metric descriptions include business meaning AND technical calculation
- [ ] Table descriptions explain purpose and how to query (column_name=':table')
- [ ] Documentation runs AFTER monitors initialize (~15 min)
- [ ] Custom metric columns documented in correct table (AGGREGATE/DERIVED → profile, DRIFT → drift)
- [ ] Error handling for tables that don't exist yet

## Genie Integration Benefits

| Without Documentation | With Documentation |
|----------------------|-------------------|
| Genie sees: `tag_coverage_pct` (no context) | Genie sees: "Percentage of cost covered by tags. Business: FinOps maturity KPI (target: >90%)..." |
| User asks: "Show tag coverage" → ❓ | User asks: "Show tag coverage" → ✅ Correct metric selected |
| Manual metric lookup required | Natural language queries work |

## Query Patterns

### Query Pattern 1: Table-Level AGGREGATE (Direct SELECT)

**Recommended for business KPIs**

```sql
-- Python: input_columns=[":table"]

SELECT 
  window.start,
  window.end,
  -- All table-level metrics available directly
  total_gross_revenue,
  total_net_revenue,
  total_transactions,
  avg_transaction_amount
FROM fact_sales_daily_profile_metrics
WHERE log_type = 'INPUT'
  AND column_name = ':table'  -- ✅ All table-level metrics here
  AND COALESCE(slice_key, 'No Slice') = :slice_key
ORDER BY window.start DESC
```

### Query Pattern 2: DERIVED Metrics (Direct SELECT)

```sql
-- Python: input_columns=[":table"]

SELECT 
  window.start,
  window.end,
  overall_return_rate,
  units_per_transaction,
  revenue_per_unit,
  discount_intensity
FROM fact_sales_daily_profile_metrics
WHERE log_type = 'INPUT'
  AND column_name = ':table'  -- All DERIVED metrics here
  AND COALESCE(slice_key, 'No Slice') = :slice_key
```

### Query Pattern 3: DRIFT Metrics (Separate Table)

```sql
-- Python: input_columns=[":table"]

SELECT 
  window.start,
  drift_type,
  revenue_drift_pct,
  transaction_drift_pct,
  unit_sales_drift_pct
FROM fact_sales_daily_drift_metrics
WHERE drift_type = 'CONSECUTIVE'  -- or 'BASELINE'
  AND column_name = ':table'
  AND COALESCE(slice_key, 'No Slice') = :slice_key
ORDER BY window.start DESC
```

### AI/BI Dashboard Dataset Patterns

**Dataset Type 1: Table-Level Business KPIs (Direct SELECT)**

```sql
-- No PIVOT needed for table-level metrics!
SELECT 
  window.start AS date,
  window.end,
  COALESCE(slice_key, 'No Slice') AS slice_key_display,
  COALESCE(slice_value, 'No Slice') AS slice_value_display,
  total_net_revenue,
  total_transactions,
  avg_transaction_amount,
  overall_return_rate,
  discount_intensity
FROM fact_sales_daily_profile_metrics
WHERE log_type = 'INPUT'
  AND column_name = ':table'  -- ✅ All table-level metrics in one row
  AND slice_key_display = :slice_key
  AND slice_value_display = :slice_value
ORDER BY date DESC
```

### Query Pattern 4: Basic Profile Metrics (Built-in)

```sql
-- Built-in profile statistics (row count, null rates)
-- These are available without custom metrics
SELECT
  window.start,
  window.end,
  column_name,
  null_count,
  row_count,
  (null_count / NULLIF(row_count, 0)) * 100 as null_percentage
FROM {catalog}.{monitoring_schema}.{table}_profile_metrics
WHERE log_type = 'INPUT'
  AND column_name = ':table'
ORDER BY window.start DESC
LIMIT 10;
```

### Query Pattern 5: Ad-Hoc Ratio Calculation (Alternative to DERIVED)

When you need to calculate ratios that aren't pre-defined as DERIVED metrics, you can compute them directly from AGGREGATE columns in the same row:

```sql
-- Ad-hoc ratio calculation from AGGREGATE metrics in same row
SELECT
  window.start,
  window.end,
  total_daily_revenue / NULLIF(total_transactions, 0) as avg_transaction_value,
  total_daily_revenue / NULLIF(total_daily_units, 0) as avg_unit_price,
  (total_return_amount / NULLIF(total_daily_revenue + total_return_amount, 0)) * 100 as return_rate_pct
FROM {catalog}.{monitoring_schema}.{table}_profile_metrics
WHERE log_type = 'INPUT'
  AND column_name = ':table'
  AND COALESCE(slice_key, 'No Slice') = :slice_key
ORDER BY window.start DESC
LIMIT 10;
```

**Note:** The direct SELECT approach (Query Pattern 2) is preferred when DERIVED metrics are defined in the monitor. The ad-hoc approach is useful for exploratory analysis when you need ratios that aren't pre-defined as DERIVED metrics.

## Complete Workflow Example

```python
def main():
    """Setup Lakehouse monitoring with graceful error handling."""
    
    # Check SDK compatibility
    if not MONITORING_AVAILABLE:
        print("⚠️  Skipping monitoring - incompatible SDK version")
        return
    
    catalog, schema = get_parameters()
    spark = SparkSession.getActiveSession()
    workspace_client = WorkspaceClient()
    
    # Tables to monitor with their types
    monitoring_config = [
        ("fact_sales_daily", "time_series"),
        ("fact_inventory_snapshot", "snapshot"),
    ]
    
    monitors_created = []
    
    for table, monitor_type in monitoring_config:
        try:
            monitor = create_table_monitor(
                workspace_client, 
                catalog, 
                schema, 
                table,
                monitor_type
            )
            if monitor:
                monitors_created.append(table)
        except Exception as e:
            print(f"⚠️  Continuing after error with {table}: {e}")
            continue
    
    print("\n" + "=" * 80)
    print("✓ Lakehouse Monitoring setup completed")
    print("=" * 80)
    print(f"\nMonitors successfully created: {len(monitors_created)}")
    for table in monitors_created:
        print(f"  • {table}")
    
    # Wait for tables to be created
    if monitors_created:
        print("\n⏱️  Waiting 15 minutes for monitor initialization...")
        wait_with_progress(minutes=15)
        
        # Document monitoring tables
        print("\n📝 Documenting monitoring tables...")
        for table in monitors_created:
            document_monitoring_tables(spark, catalog, schema, table)
        
        print("\n✅ Monitoring setup complete with documentation!")
```
