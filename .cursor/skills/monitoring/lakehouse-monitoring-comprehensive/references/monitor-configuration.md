# Monitor Configuration Reference

## Import with Graceful Fallback

```python
# ✅ CORRECT: Try-except for optional monitoring classes
try:
    from databricks.sdk.service.catalog import (
        MonitorTimeSeries, 
        MonitorSnapshot, 
        MonitorMetric, 
        MonitorMetricType, 
        MonitorCronSchedule
    )
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False
    print("⚠️  Lakehouse Monitoring classes not available in this SDK version")

# Check before use
if not MONITORING_AVAILABLE:
    print("⚠️  Skipping monitoring setup - SDK version incompatible")
    return
```

## Exception Handling

```python
from databricks.sdk.errors import ResourceAlreadyExists, ResourceDoesNotExist

try:
    monitor = workspace_client.quality_monitors.create(
        table_name=f"{catalog}.{schema}.{table}",
        # ... configuration
    )
    print(f"✓ Monitor created for {table}")
except ResourceAlreadyExists:
    print(f"⚠️  Monitor for {table} already exists - skipping")
except ResourceDoesNotExist:
    print(f"⚠️  Table {table} does not exist - skipping monitor creation")
except Exception as e:
    print(f"⚠️  Failed to create monitor for {table}: {e}")
```

## Monitor Mode Configuration

**Critical Rule: Always Specify ONE of: `snapshot`, `time_series`, or `inference_log`**

```python
# ❌ WRONG: No mode specified
monitor = workspace_client.quality_monitors.create(
    table_name=table_name,
    # ❌ ERROR: Must specify snapshot, time_series, or inference_log
)

# ✅ CORRECT: Snapshot mode
monitor = workspace_client.quality_monitors.create(
    table_name=table_name,
    snapshot=MonitorSnapshot(),  # ✅ For non-temporal data
    custom_metrics=[...],
)

# ✅ CORRECT: Time series mode
monitor = workspace_client.quality_monitors.create(
    table_name=table_name,
    time_series=MonitorTimeSeries(
        timestamp_col="transaction_date",
        granularities=["1 day"]
    ),
    custom_metrics=[...],
)
```

**When to Use Each Mode:**

| Mode | Use Case | Example |
|------|----------|---------|
| `snapshot` | Daily snapshots without time dimension | `fact_inventory_snapshot` |
| `time_series` | Temporal data with timestamp column | `fact_sales_daily` |
| `inference_log` | ML model inference monitoring | Model prediction tables |

## Complete Monitor Creation Template

```python
def create_table_monitor(
    workspace_client: WorkspaceClient, 
    catalog: str, 
    schema: str,
    table: str,
    monitor_type: str = "time_series"
):
    """
    Create Lakehouse monitor with comprehensive error handling.
    
    Args:
        monitor_type: "snapshot" or "time_series"
    """
    table_name = f"{catalog}.{schema}.{table}"
    
    print(f"Creating {monitor_type} monitor for {table_name}...")
    
    try:
        # Configure monitor based on type
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
            custom_metrics=[
                # See Custom Metrics Design section below
            ],
            slicing_exprs=["store_number", "upc_code"],  # Dimensional analysis
            schedule=MonitorCronSchedule(
                quartz_cron_expression="0 0 2 * * ?",  # Daily at 2 AM
                timezone_id="America/New_York"
            )
        )
        
        print(f"✓ Monitor created for {table_name}")
        if hasattr(monitor, 'table_name'):
            print(f"  Table: {monitor.table_name}")
        if hasattr(monitor, 'dashboard_id'):
            print(f"  Dashboard: {monitor.dashboard_id}")
        
        return monitor
        
    except ResourceAlreadyExists:
        print(f"⚠️  Monitor for {table} already exists - skipping")
        return None
        
    except ResourceDoesNotExist:
        print(f"⚠️  Table {table} does not exist - skipping monitor creation")
        return None
        
    except Exception as e:
        print(f"❌ Failed to create monitor for {table}: {str(e)}")
        raise
```

## Async Operations Pattern

**Critical Rule: Wait for Table Creation**

Lakehouse Monitoring creates output tables asynchronously:
1. Monitor API call returns immediately (~30 seconds)
2. Initial profiling runs in background (~15 minutes)
3. Tables don't exist until profiling completes

```python
def wait_with_progress(minutes: int = 15):
    """Wait with progress updates."""
    wait_seconds = minutes * 60
    for elapsed in range(0, wait_seconds, 60):
        progress_pct = (elapsed / wait_seconds) * 100
        remaining = wait_seconds - elapsed
        print(f"⏱️  Progress: {progress_pct:.1f}% | Remaining: {remaining//60}m")
        time.sleep(60)
    print(f"✓ Wait completed - tables should be ready")

# Use in workflow
create_sales_monitor(workspace_client, catalog, schema)
wait_with_progress(minutes=15)  # ✅ Wait for async table creation
document_monitoring_tables(spark, catalog, schema)  # ✅ Now tables exist
```

## Complete Monitor Cleanup Pattern

**Critical Rule: Delete Monitor AND Output Tables**

Problem: Deleting a monitor doesn't delete its output tables, causing schema conflicts.

```python
def delete_monitor_if_exists(workspace_client: WorkspaceClient, table_name: str, spark=None):
    """Complete cleanup: monitor definition + output tables."""
    from pyspark.sql import SparkSession
    
    if spark is None:
        spark = SparkSession.getActiveSession()
    
    try:
        # 1. Check if monitor exists
        workspace_client.quality_monitors.get(table_name=table_name)
        
        # 2. Delete monitor definition
        print(f"  Deleting existing monitor for {table_name}...")
        workspace_client.quality_monitors.delete(table_name=table_name)
        print(f"  ✓ Existing monitor deleted")
        
        # 3. Parse table name to construct monitoring table names
        catalog, schema, table = table_name.split(".")
        monitoring_schema = f"{schema}_monitoring"
        
        # 4. Drop profile_metrics table
        profile_table = f"{catalog}.{monitoring_schema}.{table}_profile_metrics"
        print(f"  Dropping profile metrics table: {profile_table}...")
        spark.sql(f"DROP TABLE IF EXISTS {profile_table}")
        print(f"  ✓ Profile metrics table dropped")
        
        # 5. Drop drift_metrics table
        drift_table = f"{catalog}.{monitoring_schema}.{table}_drift_metrics"
        print(f"  Dropping drift metrics table: {drift_table}...")
        spark.sql(f"DROP TABLE IF EXISTS {drift_table}")
        print(f"  ✓ Drift metrics table dropped")
        
        return True
        
    except ResourceDoesNotExist:
        return False  # Silent success - nothing to delete
    except Exception as e:
        print(f"  ⚠️  Error checking/deleting monitor: {str(e)}")
        return False

# Use before creating new monitor
delete_monitor_if_exists(workspace_client, sales_table, spark)
create_sales_monitor(workspace_client, catalog, schema)
```

## Monitor Update Pattern

**⚠️ CRITICAL:** `quality_monitors.update()` is a **REPLACEMENT operation, not a MERGE**. If you omit fields (especially `custom_metrics`), they are **DELETED**.

**✅ CORRECT: Import from Pure Python Configuration File**

```python
# monitor_configs.py (pure Python file - NOT a notebook)
"""Centralized Monitor Configuration for Lakehouse Monitoring"""

from databricks.sdk.service.catalog import (
    MonitorTimeSeries, MonitorSnapshot, MonitorMetric, 
    MonitorMetricType, MonitorCronSchedule
)
import pyspark.sql.types as T

def get_all_monitor_configs(catalog: str, schema: str):
    """Get all monitor configurations with FULL custom metrics"""
    return [
        {
            "table_name": f"{catalog}.{schema}.fact_sales_daily",
            "custom_metrics": [... 99 metrics ...],  # ✅ MUST include all metrics
            "slicing_exprs": ["store_number"],
        }
    ]
```

```python
# update_monitors.py (notebook)
from monitor_configs import get_all_monitor_configs
from databricks.sdk import WorkspaceClient

def main():
    catalog, schema = get_parameters()
    workspace_client = WorkspaceClient()
    
    # ✅ Get FULL configuration including all custom metrics
    monitor_configs = get_all_monitor_configs(catalog, schema)
    
    # Verify custom metrics are included
    for config in monitor_configs:
        custom_metrics = config.get('custom_metrics', [])
        print(f"Updating with {len(custom_metrics)} custom metrics")
    
    # Update with full configuration
    for config in monitor_configs:
        workspace_client.quality_monitors.update(**config)
```

**Update Behavior:**

| What You Pass | What Happens |
|---------------|--------------|
| `custom_metrics=None` | ❌ Deletes all custom metrics |
| `custom_metrics=[]` | ❌ Deletes all custom metrics |
| Omit `custom_metrics` | ❌ Deletes all custom metrics |
| `custom_metrics=[...]` | ✅ Replaces with provided list |

## API Parameters Reference

### MonitorTimeSeries Parameters

- `timestamp_col` (str): Column name containing timestamp
- `granularities` (list[str]): Time windows, e.g., `["1 day", "1 week"]`

### MonitorSnapshot Parameters

- No parameters required (empty constructor)

### MonitorCronSchedule Parameters

- `quartz_cron_expression` (str): Quartz cron format, e.g., `"0 0 2 * * ?"`
- `timezone_id` (str): IANA timezone, e.g., `"America/New_York"`

### quality_monitors.create() Parameters

- `table_name` (str): Fully qualified table name
- `assets_dir` (str): Workspace path for monitor assets
- `output_schema_name` (str): Schema for output tables
- `snapshot` OR `time_series` OR `inference_log`: Monitor mode (required)
- `custom_metrics` (list[MonitorMetric]): Custom metric definitions
- `slicing_exprs` (list[str]): Column expressions for dimensional analysis
- `schedule` (MonitorCronSchedule): Execution schedule
