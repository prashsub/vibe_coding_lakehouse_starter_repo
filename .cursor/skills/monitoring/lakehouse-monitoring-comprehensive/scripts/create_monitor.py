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


def wait_for_monitor_initialization(
    workspace_client: WorkspaceClient,
    table_name: str,
    timeout_minutes: int = 20
):
    """
    Wait for a single monitor to initialize by polling status.

    Preferred over wait_with_progress() — proceeds as soon as monitor is active
    rather than always waiting the maximum time.

    Args:
        workspace_client: Databricks WorkspaceClient instance
        table_name: Fully qualified table name
        timeout_minutes: Maximum wait time (default 20 min)

    Returns:
        bool: True if monitor reached ACTIVE status, False on timeout
    """
    from databricks.sdk.service.catalog import MonitorInfoStatus

    print(f"\nWaiting for {table_name} monitor (timeout: {timeout_minutes} min)...")

    start_time = time.time()
    timeout_seconds = timeout_minutes * 60
    check_interval = 60

    while (time.time() - start_time) < timeout_seconds:
        try:
            monitor_info = workspace_client.quality_monitors.get(table_name=table_name)

            if monitor_info.status == MonitorInfoStatus.MONITOR_STATUS_ACTIVE:
                elapsed_minutes = (time.time() - start_time) / 60
                print(f"✓ Monitor active after {elapsed_minutes:.1f} minutes")
                return True

            elapsed = int((time.time() - start_time) / 60)
            print(f"  Status: {monitor_info.status} ({elapsed}/{timeout_minutes} min)")
            time.sleep(check_interval)

        except Exception as e:
            print(f"  Error checking status: {str(e)}")
            time.sleep(check_interval)

    print(f"✗ Timeout waiting for monitor initialization")
    return False


def wait_for_all_monitors(
    workspace_client: WorkspaceClient,
    catalog: str,
    schema: str,
    table_names: list,
    timeout_minutes: int = 20
):
    """
    Wait for multiple monitors to initialize concurrently.

    Polls all pending monitors each cycle and removes them as they
    reach ACTIVE status. Returns when all are active or timeout.

    Args:
        workspace_client: Databricks WorkspaceClient instance
        catalog: Catalog name
        schema: Schema name
        table_names: List of table names (without catalog.schema prefix)
        timeout_minutes: Maximum wait time (default 20 min)

    Returns:
        bool: True if all monitors active, False if any timed out
    """
    from databricks.sdk.service.catalog import MonitorInfoStatus

    print(f"\nWaiting for {len(table_names)} monitor(s) (timeout: {timeout_minutes} min)...")

    start_time = time.time()
    timeout_seconds = timeout_minutes * 60
    check_interval = 60

    fully_qualified_tables = [f"{catalog}.{schema}.{t}" for t in table_names]
    pending_tables = set(fully_qualified_tables)

    while pending_tables and (time.time() - start_time) < timeout_seconds:
        elapsed_minutes = (time.time() - start_time) / 60

        for table in list(pending_tables):
            try:
                monitor_info = workspace_client.quality_monitors.get(table_name=table)

                if monitor_info.status == MonitorInfoStatus.MONITOR_STATUS_ACTIVE:
                    print(f"✓ {table} - ACTIVE")
                    pending_tables.remove(table)
                else:
                    print(f"  {table} - {monitor_info.status} ({elapsed_minutes:.1f} min)")
            except Exception as e:
                print(f"  {table} - Error: {str(e)}")

        if pending_tables:
            time.sleep(check_interval)

    if pending_tables:
        print(f"\n✗ Timeout: {len(pending_tables)} monitor(s) still pending")
        return False

    elapsed = (time.time() - start_time) / 60
    print(f"\n✓ All monitors active after {elapsed:.1f} minutes!")
    return True
