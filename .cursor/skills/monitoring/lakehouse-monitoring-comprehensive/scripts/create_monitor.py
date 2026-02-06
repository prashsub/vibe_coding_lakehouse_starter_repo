"""
Lakehouse Monitor Creation Utility

This script provides reusable functions for creating Lakehouse Monitoring monitors
with comprehensive error handling and best practices.
"""

from databricks.sdk import WorkspaceClient
from databricks.sdk.errors import ResourceAlreadyExists, ResourceDoesNotExist
from databricks.sdk.service.catalog import (
    MonitorTimeSeries,
    MonitorSnapshot,
    MonitorMetric,
    MonitorMetricType,
    MonitorCronSchedule
)
from pyspark.sql import SparkSession
import time


def create_table_monitor(
    workspace_client: WorkspaceClient,
    catalog: str,
    schema: str,
    table: str,
    monitor_type: str = "time_series",
    timestamp_col: str = None,
    custom_metrics: list = None,
    slicing_exprs: list = None,
    schedule_cron: str = "0 0 2 * * ?",
    schedule_timezone: str = "America/New_York"
):
    """
    Create Lakehouse monitor with comprehensive error handling.
    
    Args:
        workspace_client: Databricks WorkspaceClient instance
        catalog: Catalog name
        schema: Schema name
        table: Table name
        monitor_type: "snapshot" or "time_series"
        timestamp_col: Timestamp column name (required for time_series)
        custom_metrics: List of MonitorMetric objects
        slicing_exprs: List of column expressions for dimensional analysis
        schedule_cron: Quartz cron expression
        schedule_timezone: IANA timezone identifier
    
    Returns:
        MonitorInfo object or None if creation skipped
    """
    table_name = f"{catalog}.{schema}.{table}"
    
    print(f"Creating {monitor_type} monitor for {table_name}...")
    
    try:
        # Configure monitor based on type
        if monitor_type == "snapshot":
            config = {"snapshot": MonitorSnapshot()}
        elif monitor_type == "time_series":
            if not timestamp_col:
                raise ValueError("timestamp_col required for time_series monitors")
            config = {
                "time_series": MonitorTimeSeries(
                    timestamp_col=timestamp_col,
                    granularities=["1 day"]
                )
            }
        else:
            raise ValueError(f"Unknown monitor_type: {monitor_type}")
        
        monitor = workspace_client.quality_monitors.create(
            table_name=table_name,
            assets_dir=f"/Workspace/Shared/lakehouse_monitoring/{catalog}/{schema}",
            output_schema_name=f"{catalog}.{schema}_monitoring",
            **config,
            custom_metrics=custom_metrics or [],
            slicing_exprs=slicing_exprs or [],
            schedule=MonitorCronSchedule(
                quartz_cron_expression=schedule_cron,
                timezone_id=schedule_timezone
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


def delete_monitor_if_exists(
    workspace_client: WorkspaceClient,
    table_name: str,
    spark: SparkSession = None
):
    """
    Complete cleanup: monitor definition + output tables.
    
    Args:
        workspace_client: Databricks WorkspaceClient instance
        table_name: Fully qualified table name
        spark: SparkSession instance (optional, will get active if None)
    
    Returns:
        bool: True if monitor was deleted, False if didn't exist
    """
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


def wait_with_progress(minutes: int = 15):
    """
    Wait with progress updates for monitor initialization.
    
    Args:
        minutes: Number of minutes to wait
    """
    wait_seconds = minutes * 60
    for elapsed in range(0, wait_seconds, 60):
        progress_pct = (elapsed / wait_seconds) * 100
        remaining = wait_seconds - elapsed
        print(f"⏱️  Progress: {progress_pct:.1f}% | Remaining: {remaining//60}m")
        time.sleep(60)
    print(f"✓ Wait completed - tables should be ready")
