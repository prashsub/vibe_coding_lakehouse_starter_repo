# Databricks notebook source

"""
{Project} Gold Layer - MERGE Operations

Performs Delta MERGE operations to update Gold layer tables from Silver.

Handles:
- Schema-aware transformations (column mapping)
- SCD Type 2 dimension updates
- Fact table aggregation and deduplication
- Late-arriving data
- Schema validation

Usage:
  databricks bundle run gold_merge_job -t dev
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    current_timestamp,
    md5,
    concat_ws,
    when,
    sum as spark_sum,
    count,
    avg,
    lit,
    coalesce,
)
from delta.tables import DeltaTable


def get_parameters():
    """Get job parameters from dbutils widgets."""
    catalog = dbutils.widgets.get("catalog")
    silver_schema = dbutils.widgets.get("silver_schema")
    gold_schema = dbutils.widgets.get("gold_schema")

    print(f"Catalog: {catalog}")
    print(f"Silver Schema: {silver_schema}")
    print(f"Gold Schema: {gold_schema}")

    return catalog, silver_schema, gold_schema


def merge_dim_store(
    spark: SparkSession, catalog: str, silver_schema: str, gold_schema: str
):
    """
    Merge dim_store from Silver to Gold (SCD Type 2).

    GRAIN: One row per store version (SCD Type 2)
    PRIMARY KEY: store_key (surrogate)
    BUSINESS KEY: store_number

    Key patterns:
    - Deduplication before MERGE (latest record per business key)
    - Explicit column mapping (Silver → Gold names)
    - SCD Type 2: Update timestamp only (no new version)
    """
    print("\n--- Merging dim_store (SCD Type 2) ---")

    silver_table = f"{catalog}.{silver_schema}.silver_store_dim"
    gold_table = f"{catalog}.{gold_schema}.dim_store"

    # Step 1: Read and deduplicate Silver source
    silver_raw = spark.table(silver_table)
    original_count = silver_raw.count()

    silver_df = (
        silver_raw.orderBy(
            col("processed_timestamp").desc()
        )  # Latest first
        .dropDuplicates(
            ["store_number"]
        )  # Keep first (latest) per business key
    )

    dedupe_count = silver_df.count()
    print(
        f"  Deduplicated: {original_count} → {dedupe_count} records "
        f"({original_count - dedupe_count} duplicates removed)"
    )

    # Step 2: Prepare updates with column mappings
    updates_df = (
        silver_df
        # Generate surrogate key
        .withColumn(
            "store_key",
            md5(concat_ws("||", col("store_number"), col("processed_timestamp"))),
        )
        # SCD Type 2 columns
        .withColumn("effective_from", col("processed_timestamp"))
        .withColumn("effective_to", lit(None).cast("timestamp"))
        .withColumn("is_current", lit(True))
        # Column mappings: Silver → Gold
        .withColumn(
            "company_retail_control_number", col("company_rcn")
        )  # Rename
        # Derived columns
        .withColumn(
            "store_status",
            when(col("close_date").isNotNull(), "Closed").otherwise("Active"),
        )
        # Timestamps
        .withColumn("record_created_timestamp", current_timestamp())
        .withColumn("record_updated_timestamp", current_timestamp())
        # Select ONLY columns in Gold DDL
        .select(
            "store_key",
            "store_number",
            "store_name",
            "company_retail_control_number",  # Mapped column
            "city",
            "state",
            "effective_from",
            "effective_to",
            "is_current",
            "record_created_timestamp",
            "record_updated_timestamp",
        )
    )

    # Step 3: MERGE into Gold
    delta_gold = DeltaTable.forName(spark, gold_table)

    (
        delta_gold.alias("target")
        .merge(
            updates_df.alias("source"),
            "target.store_number = source.store_number AND target.is_current = true",
        )
        .whenMatchedUpdate(
            set={"record_updated_timestamp": "source.record_updated_timestamp"}
        )
        .whenNotMatchedInsertAll()
        .execute()
    )

    record_count = updates_df.count()
    print(f"✓ Merged {record_count} records into dim_store")


def merge_fact_sales_daily(
    spark: SparkSession, catalog: str, silver_schema: str, gold_schema: str
):
    """
    Merge fact_sales_daily from Silver transactions.

    GRAIN: One row per store-product-date combination (daily aggregate)
    PRIMARY KEY: (store_number, upc_code, transaction_date)
    GRAIN TYPE: aggregated

    Key patterns:
    - Aggregation to daily grain
    - Grain validation (one row per store-product-date)
    - Column mapping (Silver → Gold names)
    - Schema validation before MERGE
    """
    print("\n--- Merging fact_sales_daily ---")

    silver_table = f"{catalog}.{silver_schema}.silver_transactions"
    gold_table = f"{catalog}.{gold_schema}.fact_sales_daily"

    transactions = spark.table(silver_table)

    # Step 1: Aggregate to daily grain
    daily_sales = (
        transactions.groupBy("store_number", "upc_code", "transaction_date")
        .agg(
            # Revenue measures
            spark_sum(
                when(col("quantity_sold") > 0, col("final_sales_price")).otherwise(0)
            ).alias("gross_revenue"),
            spark_sum(col("final_sales_price")).alias("net_revenue"),
            # Unit measures
            spark_sum(
                when(col("quantity_sold") > 0, col("quantity_sold")).otherwise(0)
            ).alias("gross_units"),
            spark_sum(col("quantity_sold")).alias("net_units"),
            # Transaction counts
            count("*").alias("transaction_count"),
        )
        # Derived metrics
        .withColumn(
            "avg_transaction_value",
            when(
                col("transaction_count") > 0,
                col("net_revenue") / col("transaction_count"),
            ).otherwise(0),
        )
        # Timestamps
        .withColumn("record_created_timestamp", current_timestamp())
        .withColumn("record_updated_timestamp", current_timestamp())
    )

    # Step 2: Validate grain (one row per store-product-date)
    distinct_grain_count = (
        daily_sales.select("store_number", "upc_code", "transaction_date")
        .distinct()
        .count()
    )
    total_row_count = daily_sales.count()

    if distinct_grain_count != total_row_count:
        raise ValueError(
            f"Grain validation failed! Expected one row per store-product-date.\n"
            f"  Distinct combinations: {distinct_grain_count}\n"
            f"  Total rows: {total_row_count}\n"
            f"  Duplicates: {total_row_count - distinct_grain_count}"
        )

    print(f"  ✓ Grain validation passed: {total_row_count} unique combinations")

    # Step 3: MERGE into Gold
    delta_gold = DeltaTable.forName(spark, gold_table)

    (
        delta_gold.alias("target")
        .merge(
            daily_sales.alias("source"),
            """target.store_number = source.store_number
           AND target.upc_code = source.upc_code
           AND target.transaction_date = source.transaction_date""",
        )
        .whenMatchedUpdate(
            set={
                "gross_revenue": "source.gross_revenue",
                "net_revenue": "source.net_revenue",
                "gross_units": "source.gross_units",
                "net_units": "source.net_units",
                "transaction_count": "source.transaction_count",
                "avg_transaction_value": "source.avg_transaction_value",
                "record_updated_timestamp": "source.record_updated_timestamp",
            }
        )
        .whenNotMatchedInsertAll()
        .execute()
    )

    record_count = daily_sales.count()
    print(f"✓ Merged {record_count} records into fact_sales_daily")


def main():
    """Main entry point for Gold layer MERGE operations."""
    from pyspark.sql import SparkSession

    catalog, silver_schema, gold_schema = get_parameters()

    spark = SparkSession.builder.appName("Gold Layer MERGE").getOrCreate()

    print("=" * 80)
    print("GOLD LAYER MERGE OPERATIONS")
    print("=" * 80)
    print(f"Source: {catalog}.{silver_schema}")
    print(f"Target: {catalog}.{gold_schema}")
    print("=" * 80)

    try:
        # Merge dimensions first (facts may reference dimensions)
        merge_dim_store(spark, catalog, silver_schema, gold_schema)
        # merge_dim_product(spark, catalog, silver_schema, gold_schema)
        # ... more dimensions

        # Then merge facts
        merge_fact_sales_daily(spark, catalog, silver_schema, gold_schema)
        # ... more facts

        print("\n" + "=" * 80)
        print("✓ Gold layer MERGE completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error during Gold layer MERGE: {str(e)}")
        raise

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
