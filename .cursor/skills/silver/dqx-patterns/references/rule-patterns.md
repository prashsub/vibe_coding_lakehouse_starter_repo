# DQX Rule Definition Patterns

## Pattern 1: YAML Configuration (Declarative)

**Best for:** Version-controlled, reusable check definitions

**File: `src/<layer>/dqx_checks.yml`**

```yaml
# DQX Quality Checks for Silver Transactions
# Criticality: error (drops records) | warn (logs but passes)

# NOT NULL checks
- name: transaction_id_not_null
  criticality: error
  check:
    function: is_not_null_and_not_empty
    arguments:
      column: transaction_id
  metadata:
    check_type: completeness
    layer: silver
    entity: transactions
    business_owner: Revenue Analytics

- name: store_number_not_null
  criticality: error
  check:
    function: is_not_null
    arguments:
      column: store_number
  metadata:
    check_type: referential_integrity
    layer: silver

# Range checks
- name: positive_price
  criticality: error
  check:
    function: is_greater_than
    arguments:
      column: final_sales_price
      limit: 0
  metadata:
    check_type: validity
    business_rule: "Prices must be positive"

- name: reasonable_quantity
  criticality: warn  # Warning only (doesn't drop)
  check:
    function: is_in_range
    arguments:
      column: quantity_sold
      min_limit: -50
      max_limit: 100
  metadata:
    check_type: reasonableness
    business_rule: "Quantities outside range are unusual"

# Date checks
- name: valid_transaction_date
  criticality: error
  check:
    function: is_greater_than_or_equal_to
    arguments:
      column: transaction_date
      limit: "2020-01-01"
  metadata:
    check_type: temporal_validity

# Custom SQL expression
- name: discount_not_exceeds_price
  criticality: error
  check:
    function: sql_expr
    arguments:
      column: transaction_id  # Reference column
      sql_expr: "(multi_unit_discount + coupon_discount + loyalty_discount) <= final_sales_price"
  metadata:
    check_type: business_logic
    business_rule: "Total discounts cannot exceed sale price"
```

## Pattern 2: Python Programmatic Definition

**Best for:** Dynamic rule generation, conditional logic

```python
# src/<layer>/dqx_checks_generator.py
from databricks.labs.dqx import check_funcs
from databricks.labs.dqx.rule import DQRowRule, DQDatasetRule, DQForEachColRule

def get_silver_transaction_checks():
    """Generate DQX checks for silver_transactions programmatically."""
    
    checks = []
    
    # Row-level checks (applied to each row)
    checks.extend([
        DQRowRule(
            name="transaction_id_not_null",
            criticality="error",
            check_func=check_funcs.is_not_null_and_not_empty,
            column="transaction_id",
            user_metadata={
                "check_type": "completeness",
                "layer": "silver",
                "entity": "transactions"
            }
        ),
        DQRowRule(
            name="positive_price",
            criticality="error",
            check_func=check_funcs.is_greater_than,
            column="final_sales_price",
            limit=0,
            user_metadata={
                "check_type": "validity",
                "business_rule": "Prices must be positive"
            }
        ),
        DQRowRule(
            name="reasonable_quantity",
            criticality="warn",  # Warning only
            check_func=check_funcs.is_in_range,
            column="quantity_sold",
            min_limit=-50,
            max_limit=100,
            user_metadata={
                "check_type": "reasonableness"
            }
        ),
    ])
    
    # Dataset-level checks (applied to entire DataFrame)
    checks.extend([
        DQDatasetRule(
            name="no_duplicate_transaction_ids",
            criticality="error",
            check_func=check_funcs.has_no_duplicate_values,
            column="transaction_id",
            user_metadata={
                "check_type": "uniqueness"
            }
        ),
        DQDatasetRule(
            name="min_record_count",
            criticality="warn",
            check_func=check_funcs.has_min_row_count,
            min_count=1000,
            user_metadata={
                "check_type": "volume",
                "business_rule": "Expect at least 1000 daily transactions"
            }
        ),
    ])
    
    # For-each-column checks (applied to multiple columns)
    required_columns = ["store_number", "upc_code", "transaction_date"]
    
    for col in required_columns:
        checks.append(
            DQRowRule(
                name=f"{col}_not_null",
                criticality="error",
                check_func=check_funcs.is_not_null,
                column=col,
                user_metadata={
                    "check_type": "completeness",
                    "generated": "for_each_column"
                }
            )
        )
    
    return checks

def get_dimension_checks(dim_name: str, key_column: str):
    """Reusable dimension check generator."""
    return [
        DQRowRule(
            name=f"{key_column}_not_null",
            criticality="error",
            check_func=check_funcs.is_not_null_and_not_empty,
            column=key_column,
            user_metadata={
                "dimension": dim_name,
                "check_type": "completeness"
            }
        ),
        DQDatasetRule(
            name=f"no_duplicate_{key_column}",
            criticality="error",
            check_func=check_funcs.has_no_duplicate_values,
            column=key_column,
            user_metadata={
                "dimension": dim_name,
                "check_type": "uniqueness"
            }
        ),
    ]
```

## Pattern 3: Delta Table Storage (Production Pattern)

**Best for:** Large-scale environments, centralized governance

```python
# src/<layer>/dqx_checks_manager.py
from databricks.labs.dqx.engine import DQEngine
from databricks.labs.dqx.config import TableChecksStorageConfig
from databricks.sdk import WorkspaceClient
from pyspark.sql import SparkSession
import yaml

def load_checks_from_yaml(yaml_path: str):
    """Load checks from YAML file."""
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)

def save_checks_to_delta(
    spark: SparkSession,
    checks: list,
    catalog: str,
    schema: str,
    table_name: str = "dqx_quality_checks"
):
    """
    Save quality checks to Delta table for governance and history.
    
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
    from datetime import datetime
    import json
    
    dq_engine = DQEngine(WorkspaceClient())
    
    # Create fully qualified table name
    checks_table = f"{catalog}.{schema}.{table_name}"
    
    # Convert checks to Delta-friendly format
    check_records = []
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
            "created_by": spark.sql("SELECT current_user() as user").collect()[0]["user"],
            "entity": check.get("metadata", {}).get("entity", ""),
            "layer": check.get("metadata", {}).get("layer", ""),
            "version": 1
        }
        check_records.append(record)
    
    # Create DataFrame and save to Delta
    checks_df = spark.createDataFrame(check_records)
    
    # ⚠️ CRITICAL: Delete old checks before inserting new ones
    # This ensures obsolete checks are removed from Delta table
    if spark.catalog.tableExists(checks_table):
        from delta.tables import DeltaTable
        
        delta_table = DeltaTable.forName(spark, checks_table)
        
        # ✅ DELETE all existing checks for this entity
        # This removes obsolete checks that no longer exist in code
        entity_name = check_records[0].get("entity", "")
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

def load_checks_from_delta(
    spark: SparkSession,
    catalog: str,
    schema: str,
    entity: str = None,
    table_name: str = "dqx_quality_checks"
):
    """Load checks from Delta table."""
    import json
    
    checks_table = f"{catalog}.{schema}.{table_name}"
    
    # Query checks
    query = f"SELECT * FROM {checks_table} WHERE 1=1"
    if entity:
        query += f" AND entity = '{entity}'"
    
    checks_df = spark.sql(query)
    
    # Convert back to DQX format
    checks = []
    for row in checks_df.collect():
        check = {
            "name": row.check_name,
            "criticality": row.criticality,
            "check": {
                "function": row.check_function,
                "arguments": json.loads(row.arguments)
            },
            "metadata": json.loads(row.metadata)
        }
        checks.append(check)
    
    return checks
```

## Quality Checks Storage Patterns

### Pattern: YAML → Delta Workflow

**Integrated with Gold Table Setup Job:**

```yaml
# resources/gold_table_setup_job.yml
resources:
  jobs:
    gold_table_setup_job:
      name: "[${bundle.target}] Gold Table Setup with DQX"
      
      tasks:
        # Existing table creation task
        - task_key: create_gold_tables
          python_task:
            python_file: ../src/company_gold/create_gold_tables.py
        
        # NEW: Store DQX checks in Delta
        - task_key: store_dqx_checks
          depends_on:
            - task_key: create_gold_tables
          python_task:
            python_file: ../src/company_gold/store_dqx_checks.py
            parameters:
              - "--catalog=${catalog}"
              - "--schema=${gold_schema}"
          libraries:
            - pypi:
                package: databricks-labs-dqx==0.8.0
```

## Metadata Enrichment

**Add comprehensive metadata to all checks:**

```yaml
# src/company_silver/dqx_checks.yml with rich metadata
- name: transaction_id_not_null
  criticality: error
  check:
    function: is_not_null_and_not_empty
    arguments:
      column: transaction_id
  metadata:
    # Classification
    check_type: completeness
    check_category: data_integrity
    
    # Ownership
    business_owner: Revenue Analytics Team
    technical_owner: Data Engineering
    data_steward: revenue-stewards@company.com
    
    # Context
    layer: silver
    entity: transactions
    domain: sales
    
    # Business rules
    business_rule: "Every transaction must have a unique identifier"
    failure_impact: "High - Cannot track transaction lineage"
    remediation: "Check source POS system for ID generation issues"
    
    # Lifecycle
    created_date: "2025-01-15"
    created_by: "data-eng@company.com"
    last_reviewed: "2025-01-15"
    review_frequency: quarterly
    
    # Compliance
    regulatory_requirement: "SOX compliance - transaction traceability"
    retention_period: "7_years"
    
    # Tags
    tags:
      - critical
      - financial_reporting
      - sox_compliance
```

## Custom Check Functions

**Define reusable custom validation logic:**

```python
# src/company_silver/custom_dqx_checks.py
"""
Custom DQX check functions for business-specific validations.
"""

from pyspark.sql import Column
from pyspark.sql.functions import col

def is_valid_store_format(column_name: str) -> Column:
    """
    Check if store number follows company format: S-####
    
    Returns:
        Boolean Column indicating validity
    """
    return col(column_name).rlike(r'^S-\d{4}$')

def discount_within_policy(
    price_col: str,
    multi_discount_col: str,
    coupon_discount_col: str,
    loyalty_discount_col: str,
    max_discount_pct: float = 0.50
) -> Column:
    """
    Check if total discounts don't exceed company policy (50% by default).
    
    Args:
        price_col: Original price column name
        multi_discount_col: Multi-unit discount column
        coupon_discount_col: Coupon discount column
        loyalty_discount_col: Loyalty discount column
        max_discount_pct: Maximum allowed discount percentage
    
    Returns:
        Boolean Column indicating policy compliance
    """
    total_discount = (
        col(multi_discount_col) + 
        col(coupon_discount_col) + 
        col(loyalty_discount_col)
    )
    max_allowed = col(price_col) * max_discount_pct
    return total_discount <= max_allowed

def is_valid_upc(column_name: str) -> Column:
    """
    Check if UPC code is valid (12-14 digits).
    
    Returns:
        Boolean Column indicating UPC validity
    """
    from pyspark.sql.functions import length
    upc_length = length(col(column_name))
    return (upc_length >= 12) & (upc_length <= 14) & col(column_name).rlike(r'^\d+$')

# Use custom checks in DQX
from databricks.labs.dqx.rule import DQRowRule

custom_checks = [
    DQRowRule(
        name="valid_store_format",
        criticality="error",
        check_func=is_valid_store_format,
        column="store_number",
        user_metadata={
            "check_type": "format_validation",
            "custom": True
        }
    ),
    DQRowRule(
        name="discount_within_policy",
        criticality="warn",
        check_func=discount_within_policy,
        column="final_sales_price",  # Reference column
        user_metadata={
            "check_type": "business_policy",
            "policy": "MAX_DISCOUNT_50_PCT",
            "custom": True
        }
    ),
]
```
