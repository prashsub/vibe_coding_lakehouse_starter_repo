---
name: dqx-patterns
description: Databricks DQX framework patterns for advanced data quality validation with detailed failure insights and flexible quarantine strategies. Use when implementing Silver/Gold layer validation, needing richer diagnostics than DLT expectations, or requiring pre-merge validation with detailed failure tracking. Supports YAML configuration, Delta table storage, and serverless compute compatibility.
metadata:
  author: databricks-sa
  version: "1.0"
  domain: silver-layer
---
# DQX Data Quality Framework Patterns

## Overview

DQX is a Python-based data quality framework from Databricks Labs that validates PySpark DataFrames with richer diagnostics than standard DLT expectations. This skill provides patterns for integrating DQX into medallion architecture pipelines with YAML configuration, Delta table storage, and serverless compute compatibility.

**Key Benefits:**
- ✅ Detailed diagnostic information on why data quality checks fail
- ✅ Flexible quarantine strategies (drop, mark, flag)
- ✅ Pre-write validation before saving data
- ✅ Centralized quality dashboards across all layers
- ✅ Delta table storage for governance and history

## When to Use This Skill

### ✅ Use DQX When:
- Need detailed diagnostic information on why data quality checks fail
- Want auto-profiling to suggest quality rules based on data patterns
- Need flexible quarantine strategies (drop, mark, flag)
- Require pre-write validation before saving data
- Want centralized quality dashboards across all layers
- Need to store quality check history in Delta tables

### ❌ Continue with Standard DLT Expectations When:
- Current DLT expectations + Lakehouse Monitoring are sufficient
- Don't need granular failure diagnostics
- Want to minimize external dependencies
- Simple pass/fail validation is adequate

## Quick Reference

### Installation (Serverless)

**✅ CORRECT - Environment-level libraries:**
```yaml
resources:
  jobs:
    silver_dq_job:
      environments:
        - environment_key: default
          spec:
            dependencies:
              - "databricks-labs-dqx==0.8.0"
      tasks:
        - task_key: apply_dqx_checks
          environment_key: default
          notebook_task:
            notebook_path: ../src/<layer>/apply_dqx_checks.py
```

**❌ WRONG - Task-level libraries (fails on serverless):**
```yaml
tasks:
  - task_key: my_task
    libraries:  # ❌ NOT supported for serverless
      - pypi:
          package: databricks-labs-dqx==0.8.0
```

### API Method Selection

**CRITICAL: Choose the correct API method based on how checks are defined.**

**For Dict/YAML Checks (Metadata-Based API):**
```python
from databricks.labs.dqx.engine import DQEngine
from databricks.sdk import WorkspaceClient

dq_engine = DQEngine(WorkspaceClient())
checks = [{"name": "...", "check": {...}}]  # Dict format

# ✅ CORRECT - Use metadata-based API
valid_df, invalid_df = dq_engine.apply_checks_by_metadata_and_split(df, checks)
```

**For DQRowRule Objects (Code-Based API):**
```python
from databricks.labs.dqx.rule import DQRowRule
from databricks.labs.dqx import check_funcs

checks = [DQRowRule(name="...", check_func=check_funcs.is_not_null, ...)]

# ✅ CORRECT - Use code-based API
valid_df, invalid_df = dq_engine.apply_checks_and_split(df, checks)
```

## Critical Rules

### 1. Function Names (ALWAYS use official API)

**Reference:** [DQX Check Functions API](https://databrickslabs.github.io/dqx/docs/reference/api/check_funcs/)

| Use Case | ✅ Correct | ❌ Wrong |
|----------|-----------|----------|
| Column >= value | `is_not_less_than` | `has_min`, `is_greater_than_or_equal_to` |
| Column <= value | `is_not_greater_than` | `has_max`, `is_less_than_or_equal_to` |
| Min <= col <= max | `is_in_range` | `is_between` |
| Column in list | `is_in_list` | `is_in`, `is_in_values` |
| Unique values | `is_unique` | `has_unique_key`, `has_no_duplicates` |

### 2. Parameter Names (STRICT - wrong names cause errors)

| Parameter Type | ✅ Correct | ❌ Wrong |
|----------------|-----------|----------|
| Comparison limit | `limit` | `value` |
| List membership | `allowed` | `values` |
| Range minimum | `min_limit` | `min_value` |
| Range maximum | `max_limit` | `max_value` |

### 3. Data Types (INTEGER for limits, NOT floats)

```python
# ❌ WRONG
{"function": "is_not_greater_than", "arguments": {"column": "pct", "limit": 50.0}}

# ✅ CORRECT
{"function": "is_not_greater_than", "arguments": {"column": "pct", "limit": 50}}
```

### 4. Spark Connect Compatibility (Serverless)

**❌ WRONG:**
```python
current_user = spark.sparkContext.sparkUser()  # Fails on serverless
```

**✅ CORRECT:**
```python
current_user = spark.sql("SELECT current_user() as user").collect()[0]["user"]
```

### 5. Delta Table Storage (DELETE-then-INSERT pattern)

**CRITICAL:** Always delete old checks before inserting new ones to remove obsolete rules.

```python
if spark.catalog.tableExists(checks_table):
    delta_table = DeltaTable.forName(spark, checks_table)
    delta_table.delete(f"entity = '{entity_name}'")  # ✅ Delete first
    checks_df.write.format("delta").mode("append").saveAsTable(checks_table)
```

## Core Patterns

### Pattern 1: YAML Configuration (Declarative)

**Best for:** Version-controlled, reusable check definitions

```yaml
# src/<layer>/dqx_checks.yml
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
```

**See:** `references/rule-patterns.md` for complete YAML examples

### Pattern 2: Gold Layer Pre-Merge Validation

**Validate aggregated data before MERGE:**

```python
from dqx_gold_checks import apply_dqx_validation

# Aggregate data
daily_sales = transactions.groupBy(...).agg(...)

# ✅ DQX PRE-MERGE VALIDATION
valid_sales, invalid_sales, stats = apply_dqx_validation(
    spark=spark,
    df=daily_sales,
    catalog=catalog,
    schema=gold_schema,
    entity="fact_sales_daily",
    enable_quarantine=True
)

# Save quarantine records
if stats["invalid"] > 0:
    invalid_sales.write.format("delta").mode("append").saveAsTable(quarantine_table)

# Only merge valid records
delta_gold.alias("target").merge(valid_sales.alias("source"), ...).execute()
```

**See:** `references/integration-guide.md` for complete Gold layer patterns

### Pattern 3: DLT Integration (Hybrid Approach)

**Use BOTH DLT expectations AND DQX for complementary benefits:**

```python
import dlt
from databricks.labs.dqx.engine import DQEngine

dq_engine = DQEngine(WorkspaceClient())

@dlt.table(...)
@dlt.expect_all_or_drop(get_critical_rules_for_table("silver_transactions"))
def silver_transactions():
    """
    Hybrid validation:
    1. DLT expectations: Critical rules (fast fail)
    2. DQX: Detailed diagnostics and metadata enrichment
    """
    bronze_df = dlt.read_stream(get_source_table("bronze_transactions"))
    
    # Apply DQX for detailed diagnostics (doesn't drop, just marks)
    return dq_engine.apply_checks_by_metadata(bronze_df, dqx_checks)
```

**See:** `references/integration-guide.md` for DLT integration patterns

## Reference Files

### Configuration and Setup
- **`references/dqx-configuration.md`** - Installation patterns, API reference, function names, parameter names, data types, Spark Connect compatibility, common errors and solutions

### Rule Definition Patterns
- **`references/rule-patterns.md`** - YAML configuration, Python programmatic definition, Delta table storage, metadata enrichment, custom check functions

### Integration Patterns
- **`references/integration-guide.md`** - DLT Silver layer integration, split valid/invalid records, Gold layer pre-merge validation, DQX vs DLT comparison, migration strategy

## Scripts

### Setup Utility
- **`scripts/setup_dqx.py`** - Creates DQX quality checks Delta table and initializes configuration. Run before deploying DQX-enabled pipelines.

**Usage:**
```bash
python scripts/setup_dqx.py --catalog <catalog> --schema <schema>
```

## Templates

### DQX Rules Template
- **`assets/templates/dqx-rules.yaml`** - Template YAML file with examples for Silver and Gold layer checks. Copy and customize for your tables.

## Validation Checklist

### Check Definitions
- [ ] All function names match [DQX API documentation](https://databrickslabs.github.io/dqx/docs/reference/api/check_funcs/)
- [ ] Parameter names are correct (`limit` not `value`, `allowed` not `values`)
- [ ] Data types are correct (int not float for limits)
- [ ] Metadata includes business context (business_rule, failure_impact)
- [ ] Critical checks use `criticality: error`
- [ ] Warning checks use `criticality: warn`

### Code Implementation
- [ ] Using `apply_checks_by_metadata_and_split()` for dict checks
- [ ] Using `apply_checks_and_split()` for DQRowRule/DQDatasetRule objects
- [ ] Using Spark Connect-compatible APIs (no `sparkContext`)
- [ ] Delta table persistence uses DELETE-then-INSERT pattern
- [ ] Quarantine tables created for invalid records
- [ ] Only valid records are merged
- [ ] Check definitions are in pure Python files (not notebooks)

### Workflow Configuration
- [ ] DQX library at environment level (not task level)
- [ ] 2-step workflow: store checks → validate and merge
- [ ] Proper task dependencies configured
- [ ] Environment references correct in all tasks

## Common Errors

### Error 1: Function Not Defined
**Solution:** Use [official DQX function names](https://databrickslabs.github.io/dqx/docs/reference/api/check_funcs/)

### Error 2: Unexpected Argument
**Solution:** Use correct parameter names (`limit` not `value`, `allowed` not `values`)

### Error 3: Wrong Data Type
**Solution:** Use integer types for all limit parameters (not floats)

### Error 4: Wrong API Method
**Solution:** Use `apply_checks_by_metadata_and_split()` for dict checks, `apply_checks_and_split()` for rule objects

### Error 5: Spark Connect Incompatibility
**Solution:** Use SQL queries instead of `sparkContext` methods

### Error 6: Serverless Library Configuration
**Solution:** Move library dependency to environment level (not task level)

**See:** `references/dqx-configuration.md` for detailed error solutions

## References

### Official Documentation
- [DQX GitHub Repository](https://github.com/databrickslabs/dqx)
- [DQX Installation Guide](https://databrickslabs.github.io/dqx/docs/installation/)
- [DQX User Guide](https://databrickslabs.github.io/dqx/docs/guide/)
- [DQX Check Functions API](https://databrickslabs.github.io/dqx/docs/reference/api/check_funcs/)

### Related Skills
- `dlt-expectations-patterns` - DLT expectations patterns (complementary)
- `databricks-python-imports` - Pure Python module patterns (critical for DQX file structure)
- `databricks-asset-bundles` - Serverless configuration patterns
