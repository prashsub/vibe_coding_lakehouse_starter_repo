"""
DQX Setup Utility

Creates DQX quality checks Delta table and initializes configuration.
Run this before deploying DQX-enabled pipelines.
"""

from pyspark.sql import SparkSession
from delta.tables import DeltaTable
import argparse
import json
from datetime import datetime

def create_dqx_checks_table(
    spark: SparkSession,
    catalog: str,
    schema: str,
    table_name: str = "dqx_quality_checks"
):
    """
    Create DQX quality checks Delta table for centralized governance.
    
    Table Schema:
    - check_id: string (unique identifier)
    - check_name: string
    - criticality: string (error|warn)
    - check_function: string
    - target_column: string
    - arguments: string (JSON)
    - metadata: string (JSON)
    - created_timestamp: timestamp
    - created_by: string
    - entity: string (table name)
    - layer: string (bronze|silver|gold)
    - version: int
    """
    checks_table = f"{catalog}.{schema}.{table_name}"
    
    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {checks_table} (
            check_id STRING NOT NULL,
            check_name STRING NOT NULL,
            criticality STRING NOT NULL,
            check_function STRING NOT NULL,
            target_column STRING,
            arguments STRING NOT NULL,
            metadata STRING,
            created_timestamp TIMESTAMP NOT NULL,
            created_by STRING,
            entity STRING,
            layer STRING,
            version INT
        )
        USING DELTA
        CLUSTER BY AUTO
        COMMENT 'DQX quality checks registry for centralized governance'
    """)
    
    print(f"✓ Created DQX checks table: {checks_table}")
    return checks_table


def save_checks_to_delta(
    spark: SparkSession,
    checks: list,
    catalog: str,
    schema: str,
    table_name: str = "dqx_quality_checks"
):
    """
    Save quality checks to Delta table for governance and history.
    
    Uses DELETE-then-INSERT pattern to remove obsolete checks.
    """
    checks_table = f"{catalog}.{schema}.{table_name}"
    
    # Convert checks to Delta-friendly format
    check_records = []
    current_user = spark.sql("SELECT current_user() as user").collect()[0]["user"]
    
    for check in checks:
        record = {
            "check_id": check.get("name", ""),
            "check_name": check.get("name", ""),
            "criticality": check.get("criticality", "warn"),
            "check_function": check["check"]["function"],
            "target_column": check["check"]["arguments"].get("column", ""),
            "arguments": json.dumps(check["check"]["arguments"]),
            "metadata": json.dumps(check.get("metadata", {})),
            "created_timestamp": datetime.now(),
            "created_by": current_user,
            "entity": check.get("metadata", {}).get("entity", ""),
            "layer": check.get("metadata", {}).get("layer", ""),
            "version": 1
        }
        check_records.append(record)
    
    # Create DataFrame
    checks_df = spark.createDataFrame(check_records)
    
    # ⚠️ CRITICAL: Delete old checks before inserting new ones
    if spark.catalog.tableExists(checks_table):
        delta_table = DeltaTable.forName(spark, checks_table)
        
        # DELETE all existing checks for this entity
        entity_name = check_records[0].get("entity", "") if check_records else ""
        if entity_name:
            delta_table.delete(f"entity = '{entity_name}'")
            print(f"  Deleted old checks for entity: {entity_name}")
        
        # Then INSERT all current checks
        checks_df.write.format("delta") \
            .mode("append") \
            .saveAsTable(checks_table)
        
        print(f"✓ Updated {len(check_records)} checks in {checks_table}")
    else:
        checks_df.write.format("delta").mode("overwrite").saveAsTable(checks_table)
        print(f"✓ Created checks table {checks_table}")
    
    return checks_table


def main():
    parser = argparse.ArgumentParser(description="Setup DQX quality checks table")
    parser.add_argument("--catalog", required=True, help="Unity Catalog name")
    parser.add_argument("--schema", required=True, help="Schema name")
    parser.add_argument("--table-name", default="dqx_quality_checks", help="Table name")
    args = parser.parse_args()
    
    spark = SparkSession.builder.appName("DQX Setup").getOrCreate()
    
    try:
        # Create table if it doesn't exist
        create_dqx_checks_table(
            spark=spark,
            catalog=args.catalog,
            schema=args.schema,
            table_name=args.table_name
        )
        
        print("\n" + "="*80)
        print("✓ DQX setup complete!")
        print("="*80)
        print(f"\nNext steps:")
        print(f"1. Load checks from YAML using save_checks_to_delta()")
        print(f"2. Deploy DQX-enabled pipelines")
        print(f"3. Query checks: SELECT * FROM {args.catalog}.{args.schema}.{args.table_name}")
        
    except Exception as e:
        print(f"\n❌ Error setting up DQX: {str(e)}")
        raise
    
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
