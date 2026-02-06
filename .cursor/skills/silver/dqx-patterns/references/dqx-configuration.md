# DQX Configuration and Setup

## Installation Patterns

### As Library Dependency (Recommended for Pipelines)

**⚠️ CRITICAL: Serverless Compute Library Configuration**

**For serverless compute, ALWAYS specify libraries at environment level, NOT task level.**

**❌ WRONG - Task-level libraries:**
```yaml
# This will FAIL on serverless compute
resources:
  jobs:
    my_job:
      tasks:
        - task_key: my_task
          notebook_task:
            notebook_path: ../src/script.py
          libraries:  # ❌ NOT supported for serverless
            - pypi:
                package: databricks-labs-dqx==0.8.0
```

**Error:** `Libraries field is not supported for serverless task, please specify libraries in environment.`

**✅ CORRECT - Environment-level libraries:**
```yaml
# resources/<layer>_job.yml
resources:
  jobs:
    silver_dq_job:
      name: "[${bundle.target}] Silver DQ with DQX"
      
      # ✅ Define dependencies at environment level
      environments:
        - environment_key: default
          spec:
            dependencies:
              - "databricks-labs-dqx==0.8.0"
      
      tasks:
        - task_key: apply_dqx_checks
          environment_key: default  # ✅ Reference environment
          notebook_task:
            notebook_path: ../src/<layer>/apply_dqx_checks.py
```

**Notebook Installation:**
```python
# Install in notebook (if not using bundle)
%pip install databricks-labs-dqx==0.8.0
dbutils.library.restartPython()
```

### As Workspace Tool (For Advanced Features)

**CLI Installation (Optional - provides workflows and dashboards):**
```bash
# Install DQX tool in workspace
databricks labs install dqx

# Installs:
# - Profiling workflow (auto-generate rule candidates)
# - Quality checking workflow (apply rules)
# - Quality dashboard (visualization)
# - Configuration management

# Open dashboards
databricks labs dqx open-dashboards
```

## ⚠️ DQX API Reference (Production-Critical)

### Correct DQX Function Names

**ALWAYS use the exact function names from the [official DQX API](https://databrickslabs.github.io/dqx/docs/reference/api/check_funcs/).**

#### Row-Level Check Functions

| Use Case | ✅ Correct Function | ❌ WRONG (Don't Use) | Parameters | Example |
|----------|---------------------|----------------------|------------|---------|
| Column >= value | `is_not_less_than` | `has_min`, `is_greater_than_or_equal_to` | `column, limit` | `is_not_less_than("revenue", 0)` |
| Column <= value | `is_not_greater_than` | `has_max`, `is_less_than_or_equal_to` | `column, limit` | `is_not_greater_than("discount", 100)` |
| Min <= col <= max | `is_in_range` | `is_between` | `column, min_limit, max_limit` | `is_in_range("pct", 0, 100)` |
| Column in list | `is_in_list` | `is_in`, `is_in_values` | `column, allowed` | `is_in_list("status", ["A","B"])` |
| Column > value | `is_greater_than` | ✅ Correct | `column, limit` | `is_greater_than("qty", 0)` |
| Column < value | `is_less_than` | ✅ Correct | `column, limit` | `is_less_than("returns", 10)` |
| Not null | `is_not_null` | ✅ Correct | `column` | `is_not_null("id")` |
| Unique values | `is_unique` | `has_unique_key`, `has_no_duplicates` | `columns` (list) | `is_unique(["id"])` |

#### Dataset-Level Check Functions

| Use Case | ✅ Correct Function | Parameters | Example |
|----------|---------------------|------------|---------|
| No duplicate values | `has_no_duplicate_values` | `column` | `has_no_duplicate_values("transaction_id")` |
| Minimum row count | `has_min_row_count` | `min_count` | `has_min_row_count(1000)` |
| Maximum row count | `has_max_row_count` | `max_count` | `has_max_row_count(1000000)` |

**Reference:** [DQX Check Functions API Documentation](https://databrickslabs.github.io/dqx/docs/reference/api/check_funcs/)

### Correct Parameter Names

**DQX is STRICT about parameter names. Using wrong names causes immediate errors.**

#### ❌ Common Parameter Name Mistakes

```python
# ❌ WRONG - Using 'value' instead of 'limit'
{
    "function": "is_not_less_than",
    "arguments": {
        "column": "revenue",
        "value": 0  # ❌ ERROR: Unexpected argument 'value'
    }
}

# ❌ WRONG - Using 'values' instead of 'allowed'
{
    "function": "is_in_list",
    "arguments": {
        "column": "status",
        "values": ["A", "B", "C"]  # ❌ ERROR: Unexpected argument 'values'
    }
}

# ❌ WRONG - Using 'min_value'/'max_value' instead of 'min_limit'/'max_limit'
{
    "function": "is_in_range",
    "arguments": {
        "column": "percentage",
        "min_value": 0,   # ❌ ERROR: Unexpected argument 'min_value'
        "max_value": 100  # ❌ ERROR: Unexpected argument 'max_value'
    }
}
```

#### ✅ Correct Parameter Names

```python
# ✅ CORRECT - Using 'limit' for comparison functions
{
    "function": "is_not_less_than",
    "arguments": {
        "column": "revenue",
        "limit": 0  # ✅ Correct parameter name
    }
}

# ✅ CORRECT - Using 'allowed' for list membership
{
    "function": "is_in_list",
    "arguments": {
        "column": "status",
        "allowed": ["A", "B", "C"]  # ✅ Correct parameter name
    }
}

# ✅ CORRECT - Using 'min_limit'/'max_limit' for range checks
{
    "function": "is_in_range",
    "arguments": {
        "column": "percentage",
        "min_limit": 0,    # ✅ Correct parameter name
        "max_limit": 100   # ✅ Correct parameter name
    }
}
```

### Data Type Requirements

**DQX requires INTEGER types for limits, NOT floats.**

#### ❌ WRONG - Using float values
```python
{
    "function": "is_not_greater_than",
    "arguments": {
        "column": "return_rate_pct",
        "limit": 50.0  # ❌ ERROR: Argument 'limit' should be of type 'int'
    }
}

{
    "function": "is_in_range",
    "arguments": {
        "column": "discount_pct",
        "min_limit": 0.0,    # ❌ ERROR: Should be int
        "max_limit": 100.0   # ❌ ERROR: Should be int
    }
}
```

**Error Message:**
> `Argument 'limit' should be of type 'int | datetime.date | datetime.datetime | str | pyspark.sql.column.Column | None', not float`

#### ✅ CORRECT - Using integer values
```python
{
    "function": "is_not_greater_than",
    "arguments": {
        "column": "return_rate_pct",
        "limit": 50  # ✅ Integer
    }
}

{
    "function": "is_in_range",
    "arguments": {
        "column": "discount_pct",
        "min_limit": 0,    # ✅ Integer
        "max_limit": 100   # ✅ Integer
    }
}
```

### DQX API Method Selection

**CRITICAL: Choose the correct API method based on how checks are defined.**

#### Metadata-Based API (For Dict/YAML Checks)

**Use when checks are defined as dictionaries or loaded from YAML:**

```python
from databricks.labs.dqx.engine import DQEngine
from databricks.sdk import WorkspaceClient

dq_engine = DQEngine(WorkspaceClient())

# Checks defined as dicts (from YAML or Python)
checks = [
    {
        "name": "revenue_non_negative",
        "criticality": "error",
        "check": {
            "function": "is_not_less_than",
            "arguments": {"column": "revenue", "limit": 0}
        }
    }
]

# ✅ CORRECT - Use metadata-based API
valid_df, invalid_df = dq_engine.apply_checks_by_metadata_and_split(df, checks)

# OR for validation without splitting
validated_df = dq_engine.apply_checks_by_metadata(df, checks)
```

**❌ WRONG - Using code-based API for dict checks:**
```python
# ❌ This will FAIL with dict checks
valid_df, invalid_df = dq_engine.apply_checks_and_split(df, checks)
```

**Error Message:**
> `Use 'apply_checks_by_metadata_and_split' to pass checks as list of dicts instead.`

#### Code-Based API (For DQRowRule/DQDatasetRule Objects)

**Use when checks are defined as DQX rule objects:**

```python
from databricks.labs.dqx.rule import DQRowRule
from databricks.labs.dqx import check_funcs

# Checks defined as DQX rule objects
checks = [
    DQRowRule(
        name="revenue_non_negative",
        criticality="error",
        check_func=check_funcs.is_not_less_than,
        column="revenue",
        limit=0
    )
]

# ✅ CORRECT - Use code-based API
valid_df, invalid_df = dq_engine.apply_checks_and_split(df, checks)
```

### Spark Connect Compatibility

**CRITICAL: Serverless compute uses Spark Connect, which doesn't support JVM-dependent APIs.**

#### ❌ WRONG - Using sparkContext (not Spark Connect compatible)
```python
# ❌ This FAILS on serverless compute
current_user = spark.sparkContext.sparkUser()
```

**Error Message:**
> `[JVM_ATTRIBUTE_NOT_SUPPORTED] Attribute sparkContext is not supported in Spark Connect as it depends on the JVM.`

#### ✅ CORRECT - Spark Connect compatible alternatives
```python
# ✅ Get current user via SQL
try:
    current_user = spark.sql("SELECT current_user() as user").collect()[0]["user"]
except:
    current_user = "unknown"

# ✅ Get session ID
session_id = spark.sparkSession.sessionId

# ✅ Get Spark version
spark_version = spark.version
```

**Rule:** Always use SQL queries or DataFrame APIs instead of `sparkContext` when deploying to serverless.

## Common DQX Errors and Solutions

### Error 1: Function Not Defined

**Error Message:**
> `function 'has_min' is not defined`

**Cause:** Using incorrect DQX function name

**Solution:** Always use [official DQX function names](https://databrickslabs.github.io/dqx/docs/reference/api/check_funcs/)
- ❌ `has_min` → ✅ `is_not_less_than`
- ❌ `has_max` → ✅ `is_not_greater_than`
- ❌ `is_in` → ✅ `is_in_list`
- ❌ `has_unique_key` → ✅ `is_unique`

### Error 2: Unexpected Argument

**Error Message:**
> `Unexpected argument 'value' for function 'is_not_less_than'. Expected arguments are: ['column', 'limit']`

**Cause:** Using wrong parameter name

**Solution:** Use correct parameter names
- ❌ `"value": 0` → ✅ `"limit": 0`
- ❌ `"values": [...]` → ✅ `"allowed": [...]`
- ❌ `"min_value"/"max_value"` → ✅ `"min_limit"/"max_limit"`

### Error 3: Wrong Data Type for Argument

**Error Message:**
> `Argument 'limit' should be of type 'int | datetime.date | datetime.datetime | str | pyspark.sql.column.Column | None', not float`

**Cause:** Using float instead of int

**Solution:** Use integer types for all limit parameters
- ❌ `"limit": 50.0` → ✅ `"limit": 50`
- ❌ `"min_limit": 0.0` → ✅ `"min_limit": 0`
- ❌ `"max_limit": 100.0` → ✅ `"max_limit": 100`

### Error 4: Wrong API Method for Check Type

**Error Message:**
> `Use 'apply_checks_by_metadata_and_split' to pass checks as list of dicts instead.`

**Cause:** Using code-based API for dictionary/YAML checks

**Solution:** Use metadata-based API methods
```python
# ❌ WRONG for dict checks
valid_df, invalid_df = dq_engine.apply_checks_and_split(df, checks)

# ✅ CORRECT for dict checks
valid_df, invalid_df = dq_engine.apply_checks_by_metadata_and_split(df, checks)
```

### Error 5: Spark Connect Incompatibility

**Error Message:**
> `[JVM_ATTRIBUTE_NOT_SUPPORTED] Attribute sparkContext is not supported in Spark Connect as it depends on the JVM.`

**Cause:** Using `sparkContext` in serverless compute

**Solution:** Use Spark Connect-compatible alternatives
```python
# ❌ WRONG
current_user = spark.sparkContext.sparkUser()

# ✅ CORRECT
current_user = spark.sql("SELECT current_user() as user").collect()[0]["user"]
```

### Error 6: Serverless Library Configuration

**Error Message:**
> `Libraries field is not supported for serverless task, please specify libraries in environment.`

**Cause:** Library specified at task level instead of environment level

**Solution:** Move library dependency to environment level
```yaml
# ❌ WRONG
tasks:
  - task_key: my_task
    libraries:
      - pypi: package_name

# ✅ CORRECT
environments:
  - environment_key: default
    spec:
      dependencies:
        - "databricks-labs-dqx==0.8.0"

tasks:
  - task_key: my_task
    environment_key: default
```

### Error 7: Obsolete Checks Persisting in Delta Table

**Symptom:** Old checks that no longer exist in code still appear in validation errors

**Cause:** Delta table MERGE only updates/inserts, never deletes

**Solution:** Use DELETE-then-INSERT pattern
```python
# ✅ CORRECT: Delete old checks before inserting new ones
if spark.catalog.tableExists(checks_table):
    delta_table = DeltaTable.forName(spark, checks_table)
    
    # DELETE all existing checks for this entity
    delta_table.delete(f"entity = '{entity}'")
    
    # Then INSERT all current checks
    checks_df.write.format("delta").mode("append").saveAsTable(checks_table)
```

### Error 8: Import Errors in Serverless

**Error Message:**
> `ModuleNotFoundError: No module named 'dqx_gold_checks'`

**Cause:** Trying to import a Databricks notebook (with header) as a module

**Solution:** Ensure check definitions are in pure Python files (`.py`) without `# Databricks notebook source` header.
