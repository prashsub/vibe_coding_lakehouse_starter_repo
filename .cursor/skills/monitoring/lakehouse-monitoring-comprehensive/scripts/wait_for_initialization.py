"""
Wait for Lakehouse Monitor Initialization

Polls monitor status until all monitors reach ACTIVE state.
Preferred over timer-based waiting because it proceeds as soon as
monitors are ready rather than always waiting the maximum time.

Usage:
  databricks bundle run wait_for_monitor_initialization -t dev
"""

import argparse
import time

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import MonitorInfoStatus


def wait_for_monitor_initialization(
    w: WorkspaceClient,
    table_name: str,
    timeout_minutes: int = 20,
):
    """
    Wait for a single monitor to initialize by polling status.

    Preferred over timer-based waiting — proceeds as soon as monitor is active.

    Args:
        w: WorkspaceClient
        table_name: Fully qualified table name
        timeout_minutes: Maximum wait time (default 20 min)

    Returns:
        True if monitor reached ACTIVE status, False on timeout
    """
    print(f"\nWaiting for {table_name} monitor initialization...")
    print(f"  This typically takes 15-20 minutes...")

    start_time = time.time()
    timeout_seconds = timeout_minutes * 60
    check_interval = 60  # Check every minute

    while (time.time() - start_time) < timeout_seconds:
        try:
            monitor_info = w.quality_monitors.get(table_name=table_name)

            if monitor_info.status == MonitorInfoStatus.MONITOR_STATUS_ACTIVE:
                elapsed_minutes = (time.time() - start_time) / 60
                print(f"✓ Monitor active after {elapsed_minutes:.1f} minutes")
                return True

            elapsed = int((time.time() - start_time) / 60)
            print(
                f"  Status: {monitor_info.status} (waited {elapsed}/{timeout_minutes} min)"
            )
            time.sleep(check_interval)

        except Exception as e:
            print(f"  Error checking status: {str(e)}")
            time.sleep(check_interval)

    print(f"✗ Timeout waiting for monitor initialization")
    return False


def wait_for_all_monitors(
    w: WorkspaceClient,
    catalog: str,
    schema: str,
    table_names: list,
    timeout_minutes: int = 20,
):
    """
    Wait for multiple monitors to initialize concurrently.

    Polls all pending monitors each cycle and removes them as they
    reach ACTIVE status. Returns when all are active or timeout.

    Args:
        w: WorkspaceClient
        catalog: Catalog name
        schema: Schema name
        table_names: List of table names (without catalog.schema prefix)
        timeout_minutes: Maximum wait time (default 20 min)

    Returns:
        True if all monitors active, False if any timed out
    """
    print(f"\nWaiting for {len(table_names)} monitor(s) to initialize...")
    print(f"Timeout: {timeout_minutes} minutes\n")

    start_time = time.time()
    timeout_seconds = timeout_minutes * 60
    check_interval = 60

    fully_qualified_tables = [f"{catalog}.{schema}.{t}" for t in table_names]
    pending_tables = set(fully_qualified_tables)

    while pending_tables and (time.time() - start_time) < timeout_seconds:
        elapsed_minutes = (time.time() - start_time) / 60

        for table in list(pending_tables):
            try:
                monitor_info = w.quality_monitors.get(table_name=table)

                if monitor_info.status == MonitorInfoStatus.MONITOR_STATUS_ACTIVE:
                    print(f"✓ {table} - ACTIVE")
                    pending_tables.remove(table)
                else:
                    print(
                        f"  {table} - {monitor_info.status} (waited {elapsed_minutes:.1f} min)"
                    )

            except Exception as e:
                print(f"  {table} - Error: {str(e)}")

        if pending_tables:
            time.sleep(check_interval)

    if pending_tables:
        print(f"\n✗ Timeout: {len(pending_tables)} monitor(s) still pending:")
        for table in pending_tables:
            print(f"  - {table}")
        return False
    else:
        elapsed = (time.time() - start_time) / 60
        print(f"\n✓ All monitors active after {elapsed:.1f} minutes!")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Wait for Monitor Initialization"
    )
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--schema", required=True)
    parser.add_argument(
        "--timeout", type=int, default=20, help="Timeout in minutes"
    )

    args = parser.parse_args()

    w = WorkspaceClient()

    # ================================================================
    # List tables with monitors to wait for.
    # Update this list to match your setup_monitors script.
    # ================================================================
    monitored_tables = [
        "fact_sales_daily",
        "dim_store",
        # ... add more tables
    ]

    success = wait_for_all_monitors(
        w, args.catalog, args.schema, monitored_tables, args.timeout
    )

    if not success:
        raise RuntimeError(
            "Monitor initialization timeout — some monitors did not reach ACTIVE status"
        )

    print("\n✅ All monitors initialized. You can now query monitoring tables.")


if __name__ == "__main__":
    main()
