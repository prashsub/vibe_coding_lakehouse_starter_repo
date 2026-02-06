# Data Analysis Workflows

## Usage Examples

### Scenario 1: Debug Bronze → Silver Data Flow

```python
# Compare record counts
compare_tables(bronze_schema, "bronze_transactions", 
               silver_schema, "silver_transactions")

# Check for data quality issues
check_data_quality(silver_schema, "silver_transactions")
```

### Scenario 2: Validate Gold Layer Aggregations

```python
# Explore fact table
df = explore_table(gold_schema, "fact_sales_daily", limit=20)

# Check for null measures
check_data_quality(gold_schema, "fact_sales_daily")
```

### Scenario 3: Investigate Missing Rows

```python
# List all tables in Silver
list_tables(silver_schema)

# Compare row counts across layers
bronze_df = spark.table(f"{catalog}.{bronze_schema}.bronze_data")
silver_df = spark.table(f"{catalog}.{silver_schema}.silver_data")

print(f"Bronze: {bronze_df.count():,}")
print(f"Silver: {silver_df.count():,}")
print(f"Dropped: {bronze_df.count() - silver_df.count():,}")
```

## Step-by-Step Analysis Workflows

### Workflow 1: Initial Data Discovery

1. **List all tables in each layer**
   ```python
   list_tables(bronze_schema)
   list_tables(silver_schema)
   list_tables(gold_schema)
   ```

2. **Explore key tables**
   ```python
   df = explore_table(silver_schema, "silver_transactions", limit=10)
   ```

3. **Check data quality**
   ```python
   check_data_quality(silver_schema, "silver_transactions")
   ```

### Workflow 2: Data Quality Investigation

1. **Identify problematic tables**
   ```python
   # List all tables
   list_tables(silver_schema)
   ```

2. **Check for nulls and duplicates**
   ```python
   check_data_quality(silver_schema, "problematic_table")
   ```

3. **Compare across layers**
   ```python
   compare_tables(bronze_schema, "bronze_table", 
                  silver_schema, "silver_table")
   ```

### Workflow 3: Schema Validation

1. **Verify schema matches expectations**
   ```python
   df = explore_table(gold_schema, "fact_sales_daily")
   df.printSchema()
   ```

2. **Check table properties**
   ```python
   show_table_properties(gold_schema, "fact_sales_daily")
   ```

3. **Validate column names match YAML**
   ```python
   # Compare actual columns to expected schema
   expected_cols = ["store_key", "product_key", "date_key", "net_revenue"]
   actual_cols = df.columns
   
   missing = set(expected_cols) - set(actual_cols)
   extra = set(actual_cols) - set(expected_cols)
   
   if missing:
       print(f"⚠️  Missing columns: {missing}")
   if extra:
       print(f"⚠️  Extra columns: {extra}")
   ```

## Quick Exploration Commands

```python
# List all tables in each layer
list_tables(bronze_schema)
# list_tables(silver_schema)
# list_tables(gold_schema)

# Explore a specific table
# df = explore_table(bronze_schema, "bronze_store_dim", limit=10)

# Check data quality
# check_data_quality(silver_schema, "silver_transactions")

# Compare Bronze vs Silver
# compare_tables(bronze_schema, "bronze_transactions", silver_schema, "silver_transactions")
```
