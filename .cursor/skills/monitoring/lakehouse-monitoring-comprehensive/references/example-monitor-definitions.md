# Example Monitor Definitions

## Overview

Concrete, production-ready monitor definitions for common Gold layer table types. All examples use correct SDK objects and syntax patterns.

**Required Imports:**

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import (
    MonitorMetric, MonitorMetricType, MonitorTimeSeries, MonitorSnapshot
)
from pyspark.sql import types as T
```

## Fact Table Monitor: fact_sales_daily

**Business Purpose:** Track daily sales revenue, transaction volume, and return patterns. Detect anomalies in revenue trends and purchasing behavior.

**Monitor Mode:** `time_series` (has `transaction_date` column)

**Custom Metrics:** 9 metrics (4 AGGREGATE → 3 DERIVED → 2 DRIFT)

```python
def get_fact_sales_daily_metrics():
    """
    Custom metrics for fact_sales_daily monitor.

    AGGREGATE metrics: Sum of daily totals from table columns
    DERIVED metrics: Calculated from AGGREGATE metrics (no re-scan)
    DRIFT metrics: Period-over-period comparison via window templates

    Critical: ALL metrics use input_columns=[":table"] for cross-referencing.
    """
    return [
        # ========================================
        # AGGREGATE METRICS (sum of daily totals)
        # ========================================
        MonitorMetric(
            type=MonitorMetricType.CUSTOM_METRIC_TYPE_AGGREGATE,
            name="total_daily_revenue",
            input_columns=[":table"],
            definition="SUM(net_revenue)",
            output_data_type=T.StructField("output", T.DoubleType()).json()
        ),
        MonitorMetric(
            type=MonitorMetricType.CUSTOM_METRIC_TYPE_AGGREGATE,
            name="total_daily_units",
            input_columns=[":table"],
            definition="SUM(net_units)",
            output_data_type=T.StructField("output", T.DoubleType()).json()
        ),
        MonitorMetric(
            type=MonitorMetricType.CUSTOM_METRIC_TYPE_AGGREGATE,
            name="total_transactions",
            input_columns=[":table"],
            definition="SUM(transaction_count)",
            output_data_type=T.StructField("output", T.DoubleType()).json()
        ),
        MonitorMetric(
            type=MonitorMetricType.CUSTOM_METRIC_TYPE_AGGREGATE,
            name="total_return_amount",
            input_columns=[":table"],
            definition="SUM(return_amount)",
            output_data_type=T.StructField("output", T.DoubleType()).json()
        ),

        # ========================================
        # DERIVED METRICS (calculated from AGGREGATE)
        # ✅ Direct reference to metric names - NO {{ }} templates
        # ========================================
        MonitorMetric(
            type=MonitorMetricType.CUSTOM_METRIC_TYPE_DERIVED,
            name="avg_transaction_value",
            input_columns=[":table"],
            definition="total_daily_revenue / NULLIF(total_transactions, 0)",
            output_data_type=T.StructField("output", T.DoubleType()).json()
        ),
        MonitorMetric(
            type=MonitorMetricType.CUSTOM_METRIC_TYPE_DERIVED,
            name="avg_unit_price",
            input_columns=[":table"],
            definition="total_daily_revenue / NULLIF(total_daily_units, 0)",
            output_data_type=T.StructField("output", T.DoubleType()).json()
        ),
        MonitorMetric(
            type=MonitorMetricType.CUSTOM_METRIC_TYPE_DERIVED,
            name="return_rate_pct",
            input_columns=[":table"],
            definition="(total_return_amount / NULLIF(total_daily_revenue + total_return_amount, 0)) * 100",
            output_data_type=T.StructField("output", T.DoubleType()).json()
        ),

        # ========================================
        # DRIFT METRICS (detect changes between windows)
        # ✅ MUST use {{current_df}} and {{base_df}} templates
        # ========================================
        MonitorMetric(
            type=MonitorMetricType.CUSTOM_METRIC_TYPE_DRIFT,
            name="revenue_percent_change",
            input_columns=[":table"],
            definition="(({{current_df}}.total_daily_revenue - {{base_df}}.total_daily_revenue) / NULLIF({{base_df}}.total_daily_revenue, 0)) * 100",
            output_data_type=T.StructField("output", T.DoubleType()).json()
        ),
        MonitorMetric(
            type=MonitorMetricType.CUSTOM_METRIC_TYPE_DRIFT,
            name="units_percent_change",
            input_columns=[":table"],
            definition="(({{current_df}}.total_daily_units - {{base_df}}.total_daily_units) / NULLIF({{base_df}}.total_daily_units, 0)) * 100",
            output_data_type=T.StructField("output", T.DoubleType()).json()
        ),
    ]
```

## Dimension Table Monitor: dim_store (SCD Type 2)

**Business Purpose:** Track store dimension health including record growth, SCD Type 2 version control, and entity counts.

**Monitor Mode:** `snapshot` (no timestamp column — dimension table)

**Custom Metrics:** 4 metrics (3 AGGREGATE → 1 DERIVED)

**Note:** No DRIFT metrics for snapshot monitors without a baseline table.

```python
def get_dim_store_metrics():
    """
    Custom metrics for dim_store (SCD Type 2 dimension).

    Monitors:
    - Total record growth
    - Distinct entity count (unique stores)
    - Current record count (is_current = true)
    - Versions per entity (SCD2 health check)

    Critical: ALL metrics use input_columns=[":table"].
    """
    return [
        # ========================================
        # AGGREGATE METRICS
        # ========================================
        MonitorMetric(
            type=MonitorMetricType.CUSTOM_METRIC_TYPE_AGGREGATE,
            name="total_store_records",
            input_columns=[":table"],
            definition="COUNT(*)",
            output_data_type=T.StructField("output", T.DoubleType()).json()
        ),
        MonitorMetric(
            type=MonitorMetricType.CUSTOM_METRIC_TYPE_AGGREGATE,
            name="distinct_stores",
            input_columns=[":table"],
            definition="COUNT(DISTINCT store_number)",
            output_data_type=T.StructField("output", T.DoubleType()).json()
        ),
        MonitorMetric(
            type=MonitorMetricType.CUSTOM_METRIC_TYPE_AGGREGATE,
            name="current_records",
            input_columns=[":table"],
            definition="SUM(CASE WHEN is_current = true THEN 1 ELSE 0 END)",
            output_data_type=T.StructField("output", T.DoubleType()).json()
        ),

        # ========================================
        # DERIVED METRICS
        # ✅ Direct reference - NO {{ }}
        # ========================================
        MonitorMetric(
            type=MonitorMetricType.CUSTOM_METRIC_TYPE_DERIVED,
            name="versions_per_store",
            input_columns=[":table"],
            definition="total_store_records / NULLIF(distinct_stores, 0)",
            output_data_type=T.StructField("output", T.DoubleType()).json()
        ),
    ]
```

## Creating the Monitor

```python
from scripts.create_monitor import create_table_monitor, delete_monitor_if_exists

# Fact table with time series
delete_monitor_if_exists(workspace_client, f"{catalog}.{schema}.fact_sales_daily", spark)
create_table_monitor(
    workspace_client=workspace_client,
    catalog=catalog,
    schema=schema,
    table="fact_sales_daily",
    monitor_type="time_series",
    timestamp_col="transaction_date",
    custom_metrics=get_fact_sales_daily_metrics(),
    slicing_exprs=["store_number", "upc_code"]
)

# Dimension table with snapshot
delete_monitor_if_exists(workspace_client, f"{catalog}.{schema}.dim_store", spark)
create_table_monitor(
    workspace_client=workspace_client,
    catalog=catalog,
    schema=schema,
    table="dim_store",
    monitor_type="snapshot",
    custom_metrics=get_dim_store_metrics()
)
```

## Adding DRIFT to Snapshot Monitors

Snapshot monitors require a baseline table for drift comparison:

```python
# Option 1: Provide baseline table
create_table_monitor(
    ...,
    monitor_type="snapshot",
    baseline_table=f"{catalog}.{schema}.dim_store_baseline",
    custom_metrics=[
        *get_dim_store_metrics(),
        MonitorMetric(
            type=MonitorMetricType.CUSTOM_METRIC_TYPE_DRIFT,
            name="store_count_drift",
            input_columns=[":table"],
            definition="{{current_df}}.distinct_stores - {{base_df}}.distinct_stores",
            output_data_type=T.StructField("output", T.DoubleType()).json()
        ),
    ]
)

# Option 2: Skip drift metrics for snapshots (simpler)
```
