# DQX Integration Guide

## Pattern 1: Integration with DLT Silver Layer

**Enhanced Silver table with DQX:**

```python
# src/company_silver/silver_transactions_dqx.py
import dlt
from pyspark.sql.functions import col, current_timestamp
from databricks.labs.dqx.engine import DQEngine
from databricks.labs.dqx.config import FileChecksStorageConfig
from databricks.sdk import WorkspaceClient

# Initialize DQX engine (once per notebook)
dq_engine = DQEngine(WorkspaceClient())

# Load checks from YAML
checks_path = "dqx_checks.yml"
checks = dq_engine.load_checks(config=FileChecksStorageConfig(location=checks_path))

def get_source_table(table_name, source_schema_key="bronze_schema"):
    """Helper to get fully qualified table name."""
    from pyspark.sql import SparkSession
    spark = SparkSession.getActiveSession()
    catalog = spark.conf.get("catalog")
    schema = spark.conf.get(source_schema_key)
    return f"{catalog}.{schema}.{table_name}"

@dlt.table(
    name="silver_transactions_dqx",
    comment="""Silver layer transactions with DQX validation providing detailed 
    failure diagnostics and flexible quarantine strategies""",
    table_properties={
        "quality": "silver",
        "delta.enableChangeDataFeed": "true",
        "delta.enableRowTracking": "true",
        "layer": "silver",
        "validation_framework": "dqx",
        "contains_pii": "false"
    },
    cluster_by_auto=True
)
def silver_transactions_dqx():
    """
    Silver transactions with DQX quality validation.
    
    DQX provides:
    - Detailed failure diagnostics (why checks failed)
    - Flexible marking/flagging of invalid records
    - Metadata enrichment for tracking
    """
    bronze_df = dlt.read_stream(get_source_table("bronze_transactions"))
    
    # Apply DQX checks and get results with diagnostics
    result_df = dq_engine.apply_checks(
        input_df=bronze_df,
        checks=checks
    )
    
    # Result DataFrame includes:
    # - Original columns
    # - dq_check_result: PASS/FAIL per row
    # - dq_check_failures: Array of failed check names
    # - dq_check_details: Detailed failure information
    
    # Add processing metadata
    result_df = result_df.withColumn("processed_timestamp", current_timestamp())
    
    return result_df

@dlt.table(
    name="silver_transactions_dqx_quarantine",
    comment="Quarantine table for records that failed DQX critical checks",
    table_properties={
        "quality": "quarantine",
        "layer": "silver",
        "validation_framework": "dqx"
    },
    cluster_by_auto=True
)
def silver_transactions_dqx_quarantine():
    """
    Quarantine failed records with rich diagnostic information.
    
    Use dq_check_failures and dq_check_details columns to understand
    exactly why records failed validation.
    """
    full_df = dlt.read("silver_transactions_dqx")
    
    # Filter for failed records
    quarantine_df = full_df.filter(col("dq_check_result") == "FAIL")
    
    # Add quarantine metadata
    quarantine_df = (
        quarantine_df
        .withColumn("quarantine_timestamp", current_timestamp())
        .withColumn("requires_review", col("dq_check_failures").isNotNull())
    )
    
    return quarantine_df

@dlt.view(
    name="silver_transactions_dqx_pass",
    comment="View of records that passed all DQX checks"
)
def silver_transactions_dqx_pass():
    """Only records that passed validation."""
    full_df = dlt.read("silver_transactions_dqx")
    return full_df.filter(col("dq_check_result") == "PASS")
```

## Pattern 2: Split Valid/Invalid Records

**Alternative pattern for cleaner separation:**

```python
# src/company_silver/silver_transactions_dqx_split.py
import dlt
from databricks.labs.dqx.engine import DQEngine
from databricks.sdk import WorkspaceClient

dq_engine = DQEngine(WorkspaceClient())

@dlt.table(
    name="silver_transactions_valid",
    comment="Valid transactions that passed all DQX checks",
    table_properties={
        "quality": "silver",
        "validation_status": "passed"
    },
    cluster_by_auto=True
)
def silver_transactions_valid():
    """Only valid records (no DQX metadata columns)."""
    bronze_df = dlt.read_stream(get_source_table("bronze_transactions"))
    
    # Apply checks and split
    valid_df, invalid_df = dq_engine.apply_checks_by_metadata_and_split(
        input_df=bronze_df,
        checks=checks
    )
    
    return valid_df  # Clean, no DQX columns

@dlt.table(
    name="silver_transactions_quarantine",
    comment="Invalid transactions with detailed DQX failure diagnostics",
    table_properties={
        "quality": "quarantine",
        "validation_status": "failed"
    },
    cluster_by_auto=True
)
def silver_transactions_quarantine():
    """Failed records with diagnostic columns."""
    bronze_df = dlt.read_stream(get_source_table("bronze_transactions"))
    
    # Apply checks and split
    valid_df, invalid_df = dq_engine.apply_checks_by_metadata_and_split(
        input_df=bronze_df,
        checks=checks
    )
    
    # invalid_df includes:
    # - dq_check_failures: Array of failed check names
    # - dq_check_details: Detailed failure reasons
    # - dq_validation_timestamp: When validation occurred
    
    return invalid_df
```

## Pattern 3: Gold Layer Pre-Merge Validation (Production Pattern)

**Validate aggregated data before MERGE with proper error handling and quarantine:**

**File 1: `src/company_gold/dqx_gold_checks.py`** (Centralized check definitions)

```python
"""
DQX quality checks for Gold layer tables.
Pure Python file for standard imports.
"""

from databricks.labs.dqx.engine import DQEngine
from databricks.sdk import WorkspaceClient
from pyspark.sql import SparkSession
from delta.tables import DeltaTable
from typing import List, Dict, Tuple, Optional
from pyspark.sql import DataFrame

def get_fact_sales_daily_checks() -> List[Dict]:
    """Get all DQX checks for fact_sales_daily table."""
    return [
        # Error-level checks (quarantine failures)
        {
            "name": "non_negative_net_revenue",
            "criticality": "error",
            "check": {
                "function": "is_not_less_than",  # ✅ Correct function name
                "arguments": {
                    "column": "net_revenue",
                    "limit": 0  # ✅ Use 'limit', not 'value'; int, not float
                }
            },
            "metadata": {
                "check_type": "validity",
                "business_rule": "Net revenue cannot be negative after returns",
                "failure_impact": "Critical - Invalid financial reporting",
                "layer": "gold",
                "entity": "fact_sales_daily"
            }
        },
        {
            "name": "positive_transaction_count",
            "criticality": "error",
            "check": {
                "function": "is_greater_than",  # ✅ Correct function name
                "arguments": {
                    "column": "transaction_count",
                    "limit": 0  # ✅ Integer value
                }
            },
            "metadata": {
                "check_type": "validity",
                "business_rule": "Daily aggregates must have at least one transaction",
                "failure_impact": "High - Empty aggregation indicates data issue",
                "layer": "gold",
                "entity": "fact_sales_daily"
            }
        },
        
        # Warning-level checks (log but allow)
        {
            "name": "reasonable_daily_revenue",
            "criticality": "warn",
            "check": {
                "function": "is_not_greater_than",
                "arguments": {
                    "column": "net_revenue",
                    "limit": 100000  # ✅ Integer
                }
            },
            "metadata": {
                "check_type": "reasonableness",
                "business_rule": "Daily revenue > $100K at store-product-day level is unusual",
                "failure_impact": "Low - Requires investigation but not blocking",
                "layer": "gold",
                "entity": "fact_sales_daily"
            }
        }
    ]

def apply_dqx_validation(
    spark: SparkSession,
    df: DataFrame,
    catalog: str,
    schema: str,
    entity: str,
    enable_quarantine: bool = True
) -> Tuple[DataFrame, Optional[DataFrame], Dict]:
    """
    Apply DQX validation to a DataFrame before MERGE.
    
    Args:
        spark: SparkSession
        df: DataFrame to validate
        catalog: Unity Catalog name
        schema: Schema name
        entity: Entity name (e.g., "fact_sales_daily")
        enable_quarantine: If True, split into valid/invalid DataFrames
    
    Returns:
        (valid_df, invalid_df, validation_stats)
    """
    # Initialize DQX engine
    dq_engine = DQEngine(WorkspaceClient())
    
    # Load checks for this entity
    if entity == "fact_sales_daily":
        checks = get_fact_sales_daily_checks()
    # Add other entities as needed
    else:
        raise ValueError(f"Unknown entity: {entity}")
    
    print(f"\n  Applying {len(checks)} DQX quality checks...")
    
    # ✅ CRITICAL: Use metadata-based API for dict checks
    if enable_quarantine:
        valid_df, invalid_df = dq_engine.apply_checks_by_metadata_and_split(df, checks)
    else:
        validated_df = dq_engine.apply_checks_by_metadata(df, checks)
        return validated_df, None, {}
    
    # Calculate validation stats
    valid_count = valid_df.count()
    invalid_count = invalid_df.count() if invalid_df is not None else 0
    total_count = valid_count + invalid_count
    
    validation_stats = {
        "total": total_count,
        "valid": valid_count,
        "invalid": invalid_count,
        "pass_rate_pct": round((valid_count / total_count * 100), 2) if total_count > 0 else 0
    }
    
    print(f"  ✓ Validation complete:")
    print(f"    Total: {total_count:,} records")
    print(f"    Valid: {valid_count:,} ({validation_stats['pass_rate_pct']}%)")
    print(f"    Invalid: {invalid_count:,}")
    
    if invalid_count > 0:
        print(f"\n  ⚠️  {invalid_count:,} records failed validation")
        print(f"    Quarantine details available in {catalog}.{schema}.{entity}_quarantine")
    
    return valid_df, invalid_df, validation_stats
```

**File 2: `src/company_gold/merge_gold_tables.py`** (Updated with DQX integration)

```python
"""
Gold layer MERGE with DQX pre-validation.
Ensures only quality data enters Gold layer.
"""

from pyspark.sql import SparkSession
from delta.tables import DeltaTable
from dqx_gold_checks import apply_dqx_validation  # ✅ Standard import
import argparse

def merge_fact_sales_daily(
    spark: SparkSession,
    catalog: str,
    silver_schema: str,
    gold_schema: str
):
    """Merge fact_sales_daily from Silver to Gold with DQX validation."""
    
    silver_table = f"{catalog}.{silver_schema}.silver_transactions"
    gold_table = f"{catalog}.{gold_schema}.fact_sales_daily"
    
    transactions = spark.table(silver_table)
    
    # Aggregate daily sales
    from pyspark.sql.functions import sum as spark_sum, count, when, col
    
    daily_sales = (
        transactions
        .groupBy("store_number", "upc_code", "transaction_date")
        .agg(
            spark_sum(when(col("quantity_sold") > 0, col("final_sales_price")).otherwise(0)).alias("gross_revenue"),
            spark_sum(col("final_sales_price")).alias("net_revenue"),
            spark_sum(when(col("quantity_sold") > 0, col("quantity_sold")).otherwise(0)).alias("units_sold"),
            count("*").alias("transaction_count")
        )
    )
    
    # ✅ DQX PRE-MERGE VALIDATION
    valid_sales, invalid_sales, validation_stats = apply_dqx_validation(
        spark=spark,
        df=daily_sales,
        catalog=catalog,
        schema=gold_schema,
        entity="fact_sales_daily",
        enable_quarantine=True
    )
    
    # Handle quarantine records if any
    if invalid_sales is not None and validation_stats["invalid"] > 0:
        quarantine_table = f"{gold_table}_quarantine"
        
        print(f"\n  Saving {validation_stats['invalid']:,} invalid records to quarantine...")
        
        # Save to quarantine table with mergeSchema for DQX metadata columns
        invalid_sales.write \
            .format("delta") \
            .mode("append") \
            .option("mergeSchema", "true") \
            .saveAsTable(quarantine_table)
        
        print(f"  ✓ Quarantine table: {quarantine_table}")
        print(f"    Query failures: SELECT * FROM {quarantine_table}")
    
    # Only merge valid records
    if validation_stats["valid"] == 0:
        print(f"\n  ❌ No valid records to merge! All records failed validation.")
        print(f"     Check quarantine table for details: {catalog}.{gold_schema}.fact_sales_daily_quarantine")
        return
    
    print(f"\n  Proceeding to MERGE {validation_stats['valid']:,} validated records...")
    
    # MERGE into Gold (using validated DataFrame)
    delta_gold = DeltaTable.forName(spark, gold_table)
    
    delta_gold.alias("target").merge(
        valid_sales.alias("source"),  # ✅ Use validated DataFrame
        """target.store_number = source.store_number 
           AND target.upc_code = source.upc_code 
           AND target.transaction_date = source.transaction_date"""
    ).whenMatchedUpdate(set={
        "net_revenue": "source.net_revenue",
        "units_sold": "source.units_sold",
        "transaction_count": "source.transaction_count",
        "record_updated_timestamp": "source.record_updated_timestamp"
    }).whenNotMatchedInsertAll(
    ).execute()
    
    print(f"✓ Merged {validation_stats['valid']:,} validated records into fact_sales_daily")
    if validation_stats["invalid"] > 0:
        print(f"  ({validation_stats['invalid']:,} records quarantined)")
```

**File 3: `resources/gold_merge_job.yml`** (2-step workflow)

```yaml
resources:
  jobs:
    gold_merge_job:
      name: "[${bundle.target}] Gold Layer - MERGE with DQX"
      description: "Merges from Silver to Gold with DQX pre-validation using serverless compute"
      
      # ✅ CRITICAL: Define DQX library at environment level
      environments:
        - environment_key: default
          spec:
            dependencies:
              - "databricks-labs-dqx==0.8.0"
      
      tasks:
        # Step 1: Store/update DQX checks in Delta table
        - task_key: store_dqx_checks
          environment_key: default
          notebook_task:
            notebook_path: ../src/company_gold/store_dqx_gold_checks.py
            base_parameters:
              catalog: ${var.catalog}
              gold_schema: ${var.gold_schema}
        
        # Step 2: MERGE with DQX validation (depends on checks being stored)
        - task_key: merge_gold_tables
          depends_on:
            - task_key: store_dqx_checks
          environment_key: default
          notebook_task:
            notebook_path: ../src/company_gold/merge_gold_tables.py
            base_parameters:
              catalog: ${var.catalog}
              silver_schema: ${var.silver_schema}
              gold_schema: ${var.gold_schema}
      
      schedule:
        quartz_cron_expression: "0 0 4 * * ?"  # Daily at 4 AM
        timezone_id: "America/New_York"
        pause_status: PAUSED  # Enable manually
      
      tags:
        environment: ${bundle.target}
        project: company_demo
        layer: gold
        compute_type: serverless
        job_type: merge
```

## DQX vs. DLT Expectations Comparison

### Feature Matrix

| Feature | DLT Expectations | DQX | Recommendation |
|---------|-----------------|-----|----------------|
| Row-level validation | ✅ Yes | ✅ Yes | Both work |
| Failure diagnostics | ❌ Basic | ✅ Detailed | DQX for debugging |
| Auto-profiling | ❌ No | ✅ Yes | DQX for discovery |
| Quarantine strategies | ✅ Drop/fail | ✅ Drop/mark/flag | DQX more flexible |
| YAML configuration | ❌ No | ✅ Yes | DQX for declarative |
| Streaming support | ✅ Native | ✅ Yes | Both work |
| Delta table storage | ❌ No | ✅ Yes | DQX for governance |
| Custom dashboards | ❌ No | ✅ Yes | DQX for visualization |
| Learning curve | ✅ Simple | ⚠️ Moderate | DLT easier |
| External dependency | ✅ Built-in | ⚠️ External lib | DLT simpler |

### Migration Strategy

**Hybrid Approach (Recommended):**

```python
# Use BOTH DLT expectations AND DQX for complementary benefits

import dlt
from databricks.labs.dqx.engine import DQEngine
from data_quality_rules import get_critical_rules_for_table

dq_engine = DQEngine(WorkspaceClient())
dqx_checks = dq_engine.load_checks(...)

@dlt.table(...)
# Keep existing DLT expectations for critical rules (fast, built-in)
@dlt.expect_all_or_fail(get_critical_rules_for_table("silver_transactions"))
def silver_transactions():
    """
    Hybrid validation:
    1. DLT expectations: Critical rules (fast fail)
    2. DQX: Detailed diagnostics and metadata enrichment
    """
    bronze_df = dlt.read_stream(get_source_table("bronze_transactions"))
    
    # Apply DQX for detailed diagnostics (doesn't drop, just marks)
    dqx_result = dq_engine.apply_checks(bronze_df, dqx_checks)
    
    # DQX adds diagnostic columns but DLT expectations enforce drops
    return dqx_result
```

## Common Patterns

### ❌ Don't: Replace all DLT expectations immediately
```python
# BAD: Removing proven DLT patterns
@dlt.table(...)
# @dlt.expect_all_or_fail(...)  # ❌ Removed without reason
def silver_data():
    return dq_engine.apply_checks(...)  # Only DQX
```

### ✅ Do: Start with targeted use cases
```python
# GOOD: Add DQX where it provides clear value
@dlt.table(...)
@dlt.expect_all_or_fail(get_critical_rules_for_table("silver_data"))
def silver_data():
    """
    Use DLT for critical enforcement.
    Use DQX for detailed diagnostics and flexible quarantine.
    """
    df = dlt.read_stream(get_source_table("bronze_data"))
    
    # Add DQX for rich diagnostics
    return dq_engine.apply_checks(df, checks)
```

### ❌ Don't: Duplicate validation logic
```python
# BAD: Same rules in DLT and DQX
@dlt.expect("not_null", "col IS NOT NULL")  # ❌ Duplicated
@dlt.expect("positive", "col > 0")  # ❌ Duplicated

def table():
    df = read_data()
    # DQX checks for same rules ❌
    return dq_engine.apply_checks(df, [
        {"check": {"function": "is_not_null", "arguments": {"column": "col"}}},
        {"check": {"function": "is_greater_than", "arguments": {"column": "col", "limit": 0}}}
    ])
```

### ✅ Do: Use complementary approaches
```python
# GOOD: DLT for enforcement, DQX for diagnostics
@dlt.expect_all_or_fail(get_critical_rules_for_table("silver_data"))
def table():
    df = read_data()
    
    # DQX adds diagnostic metadata (doesn't drop, just marks)
    # Focus on warning-level rules or complex business logic
    return dq_engine.apply_checks(df, warning_checks)
```
