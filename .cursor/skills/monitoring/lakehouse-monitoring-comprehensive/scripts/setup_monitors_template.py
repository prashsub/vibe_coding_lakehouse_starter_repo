"""
Lakehouse Monitoring Setup Template

Creates Lakehouse Monitors for Gold layer tables with custom business metrics.

Critical Patterns:
- Complete cleanup (delete existing monitors + output tables)
- Async initialization (wait 15-20 minutes after creation)
- Error handling (jobs must fail if monitors fail)
- Table-level metrics use input_columns=[":table"]
- MUST use MonitorMetric SDK objects (not plain dicts)
- MUST use T.StructField("output", T.DoubleType()).json() for output_data_type

Usage:
  databricks bundle run setup_lakehouse_monitoring -t dev

See references/example-monitor-definitions.md for concrete metric definitions.
"""

import argparse
import time

from databricks.sdk import WorkspaceClient
from databricks.sdk.errors import ResourceAlreadyExists, ResourceDoesNotExist
from databricks.sdk.service.catalog import (
    MonitorTimeSeries,
    MonitorSnapshot,
    MonitorMetric,
    MonitorMetricType,
    MonitorCronSchedule,
)
from pyspark.sql import SparkSession
from pyspark.sql import types as T


def delete_existing_monitor(
    w: WorkspaceClient, table_name: str, spark: SparkSession = None
):
    """
    Delete existing monitor AND output tables.

    Critical: Deleting a monitor alone doesn't delete its output tables,
    causing schema conflicts on recreation. Always drop both.
    """
    if spark is None:
        spark = SparkSession.getActiveSession()

    try:
        print(f"  Checking for existing monitor on {table_name}...")
        w.quality_monitors.get(table_name=table_name)

        # Delete monitor definition
        print(f"  Deleting existing monitor...")
        w.quality_monitors.delete(table_name=table_name)
        print(f"  ✓ Deleted existing monitor")

        # Drop output tables to avoid schema conflicts
        catalog, schema, table = table_name.split(".")
        monitoring_schema = f"{schema}_monitoring"

        profile_table = f"{catalog}.{monitoring_schema}.{table}_profile_metrics"
        drift_table = f"{catalog}.{monitoring_schema}.{table}_drift_metrics"

        print(f"  Dropping output tables...")
        spark.sql(f"DROP TABLE IF EXISTS {profile_table}")
        spark.sql(f"DROP TABLE IF EXISTS {drift_table}")
        print(f"  ✓ Output tables dropped")

        time.sleep(5)  # Brief pause after deletion

    except ResourceDoesNotExist:
        pass  # No monitor to delete — silent success
    except Exception as e:
        if "does not exist" not in str(e).lower():
            print(f"  Warning: {str(e)}")


def create_monitor_with_custom_metrics(
    w: WorkspaceClient,
    table_name: str,
    monitor_type: str,
    custom_metrics: list,
    timestamp_col: str = None,
    slicing_exprs: list = None,
    spark: SparkSession = None,
):
    """
    Create Lakehouse Monitor with custom business metrics.

    Args:
        w: Databricks WorkspaceClient
        table_name: Fully qualified table name (catalog.schema.table)
        monitor_type: "time_series" or "snapshot"
        custom_metrics: List of MonitorMetric objects
        timestamp_col: Required for time_series monitors
        slicing_exprs: Optional dimensional analysis columns
        spark: SparkSession (for cleanup)

    Returns:
        Monitor info or None if creation failed
    """
    print(f"\nCreating {monitor_type} monitor for {table_name}...")

    # Delete existing monitor first (including output tables)
    delete_existing_monitor(w, table_name, spark)

    try:
        # Configure monitor mode
        if monitor_type == "time_series":
            if not timestamp_col:
                raise ValueError("timestamp_col required for time_series monitors")
            config = {
                "time_series": MonitorTimeSeries(
                    timestamp_col=timestamp_col,
                    granularities=["1 day"]
                )
            }
        elif monitor_type == "snapshot":
            config = {"snapshot": MonitorSnapshot()}
        else:
            raise ValueError(f"Unknown monitor_type: {monitor_type}")

        # Determine output schema
        catalog = table_name.split(".")[0]
        schema = table_name.split(".")[1]

        # Create monitor
        monitor_info = w.quality_monitors.create(
            table_name=table_name,
            assets_dir=f"/Workspace/Shared/lakehouse_monitoring/{catalog}/{schema}",
            output_schema_name=f"{catalog}.{schema}_monitoring",
            **config,
            custom_metrics=custom_metrics,
            slicing_exprs=slicing_exprs or [],
        )

        print(f"✓ Monitor created for {table_name}")
        if hasattr(monitor_info, "table_name"):
            print(f"  Table: {monitor_info.table_name}")
        if hasattr(monitor_info, "dashboard_id"):
            print(f"  Dashboard: {monitor_info.dashboard_id}")

        return monitor_info

    except ResourceAlreadyExists:
        print(f"⚠️  Monitor already exists for {table_name} - skipping")
        return None
    except ResourceDoesNotExist:
        print(f"⚠️  Table {table_name} does not exist - skipping")
        return None
    except Exception as e:
        print(f"✗ Error creating monitor for {table_name}: {str(e)}")
        return None


# ============================================================================
# MONITOR DEFINITIONS
# ============================================================================
# Define your table-specific monitor functions below.
# See references/example-monitor-definitions.md for concrete examples
# with fact_sales_daily (9 metrics) and dim_store (4 metrics).
#
# Pattern:
#   def create_{table}_monitor(w, catalog, schema):
#       table_name = f"{catalog}.{schema}.{table}"
#       custom_metrics = [MonitorMetric(...), ...]
#       return create_monitor_with_custom_metrics(w, table_name, ...)
# ============================================================================


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main entry point for Lakehouse Monitoring setup.

    Creates monitors for critical Gold tables with custom metrics.
    Tracks successes and failures, and raises on any failure.
    """
    parser = argparse.ArgumentParser(description="Setup Lakehouse Monitoring")
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--gold_schema", required=True)

    args = parser.parse_args()

    # Initialize
    w = WorkspaceClient()
    spark = SparkSession.getActiveSession()

    print("=" * 80)
    print("LAKEHOUSE MONITORING SETUP")
    print("=" * 80)
    print(f"Catalog: {args.catalog}")
    print(f"Schema: {args.gold_schema}")
    print("=" * 80)

    try:
        # Track created monitors
        monitors_created = []
        monitors_failed = []

        # ==================================================================
        # CREATE MONITORS
        # Add your monitor creation calls here, e.g.:
        #
        # result = create_fact_sales_daily_monitor(w, args.catalog, args.gold_schema)
        # if result:
        #     monitors_created.append("fact_sales_daily")
        # else:
        #     monitors_failed.append("fact_sales_daily")
        # ==================================================================

        print("\n" + "=" * 80)
        print(f"Monitor Creation Summary:")
        print(f"  Created: {len(monitors_created)} ({', '.join(monitors_created)})")
        print(
            f"  Failed: {len(monitors_failed)} ({', '.join(monitors_failed) if monitors_failed else 'None'})"
        )
        print("=" * 80)

        if monitors_failed:
            raise RuntimeError(
                f"Failed to create {len(monitors_failed)} monitor(s): "
                f"{', '.join(monitors_failed)}"
            )

        print("\n✓ All monitors created successfully!")
        print("\n⚠️  IMPORTANT: Monitors need 15-20 minutes to initialize.")
        print("   Run wait_for_initialization.py before querying metrics.")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
