---
name: adhoc-exploration-notebooks
description: Create dual-format ad-hoc exploration notebooks for Databricks workspace (.py) and local Jupyter (.ipynb) with Databricks Connect. Use when building data exploration tools, debugging data quality issues, or creating interactive analysis notebooks. Supports widget fallback patterns, helper functions for table discovery, and proper Spark session initialization for both environments.
metadata:
  author: prashanth subrahmanyam
  version: "1.0"
  domain: exploration
  role: utility
  standalone: true
  last_verified: "2026-02-07"
  volatility: low
---
# Ad-Hoc Exploration Notebook Patterns

## Overview

Every data product should include exploration notebooks in **two formats** to support different development workflows: Databricks workspace format (`.py`) for interactive use in Databricks UI, and Jupyter format (`.ipynb`) for local development with Databricks Connect. Magic commands (`%pip`, `%sql`, `dbutils.library.restartPython()`) only work in Databricks workspace, not with Databricks Connect or local execution.

## When to Use This Skill

- Building data exploration tools for Bronze/Silver/Gold layers
- Debugging data quality issues
- Creating interactive analysis notebooks
- Validating schema changes
- Testing query patterns before production

## Critical Rules

### 1. Dual-Format Requirement

**CRITICAL:** Create both `.py` (Databricks workspace) and `.ipynb` (local Jupyter) formats.

**Why:** Magic commands (`%pip`, `%sql`, `dbutils.library.restartPython()`) only work in Databricks workspace, not with Databricks Connect.

### 2. Spark Session Initialization

**CRITICAL:** Must specify either `.serverless()` or `.clusterId()` - default will fail:

```python
# ✅ CORRECT
spark = DatabricksSession.builder.serverless().profile("profile").getOrCreate()
# OR
spark = DatabricksSession.builder.clusterId("cluster-id").getOrCreate()

# ❌ WRONG
spark = DatabricksSession.builder.getOrCreate()  # Exception: Cluster id or serverless required
```

### 3. Widget Fallback Pattern

Always use widget fallback pattern for cross-environment compatibility:

```python
# Default values
catalog = "default_catalog"

# Try widgets (Databricks workspace), fall back to defaults
try:
    dbutils.widgets.text("catalog", catalog, "Catalog")
    catalog = dbutils.widgets.get("catalog")
except Exception:
    # Widgets not available (Databricks Connect)
    pass
```

## Quick Reference

### File Structure

```
src/exploration/
├── adhoc_exploration.py              # Databricks workspace format
├── adhoc_exploration.ipynb           # Local Jupyter format
├── requirements.txt                  # Python dependencies
├── README.md                         # Full documentation
└── QUICKSTART.md                     # 5-minute setup guide
```

### Standard Helper Functions

Every exploration notebook should include:

1. **Table Discovery:** `list_tables(schema_name)` - List all tables with metadata
2. **Table Exploration:** `explore_table(schema_name, table_name, limit)` - Schema + sample data
3. **Data Quality:** `check_data_quality(schema_name, table_name)` - Null counts, duplicates
4. **Comparison:** `compare_tables(schema1, table1, schema2, table2)` - Compare across layers
5. **Governance:** `show_table_properties(schema_name, table_name)` - View metadata tags

See [Notebook Patterns](references/notebook-patterns.md) for complete implementations.

## Core Patterns

### Databricks Workspace Format (.py)

**Key Features:**
- `# Databricks notebook source` header
- `# COMMAND ----------` cell separators
- `# MAGIC %md` for markdown cells
- Widget support with fallback pattern
- Magic commands work (`%pip`, `%sql`)

See [Notebook Patterns](references/notebook-patterns.md) for complete template.

### Local Jupyter Format (.ipynb)

**Key Features:**
- Standard Jupyter notebook format
- No Databricks-specific headers
- No magic commands
- Direct variable assignment (no widgets)
- Setup instructions in markdown cell

**Requirements:**
```txt
databricks-sdk[notebook]>=0.28.0
pyspark>=3.5.0
```

### Asset Bundle Integration

**Critical:** Include `.py` extension in notebook path:

```yaml
notebook_task:
  notebook_path: ../src/exploration/adhoc_exploration.py  # ✅ Include .py extension
  base_parameters:
    catalog: ${var.catalog}
```

See [Notebook Patterns](references/notebook-patterns.md) for complete YAML example.

## Common Mistakes to Avoid

### ❌ Mistake 1: Missing .serverless() or .clusterId()
```python
# ❌ DON'T: Use default builder
spark = DatabricksSession.builder.getOrCreate()
# Exception: Cluster id or serverless are required
```

### ✅ Correct: Specify execution environment
```python
spark = DatabricksSession.builder.serverless().profile("profile").getOrCreate()
```

### ❌ Mistake 2: Forgetting File Extension in Bundle
```yaml
# ❌ DON'T: Omit .py extension
notebook_path: ../src/exploration/adhoc_exploration
# Error: notebook not found
```

### ✅ Correct: Include .py extension
```yaml
notebook_path: ../src/exploration/adhoc_exploration.py
```

### ❌ Mistake 3: Using Magic Commands Locally
```python
# ❌ DON'T: Use magic commands
%pip install 'databricks-sdk[notebook]'
# SyntaxError: invalid syntax
```

### ✅ Correct: Install packages before running
```bash
pip install -r requirements.txt
```

## Validation Checklist

### File Structure
- [ ] Both `.py` and `.ipynb` formats created
- [ ] `requirements.txt` with dependencies
- [ ] README.md with full documentation
- [ ] QUICKSTART.md with 5-minute setup

### .py File (Databricks Workspace)
- [ ] Has `# Databricks notebook source` header
- [ ] Uses `# COMMAND ----------` cell separators
- [ ] Markdown cells use `# MAGIC %md`
- [ ] Initializes Spark with `.serverless()` or `.clusterId()`
- [ ] Uses widget fallback pattern
- [ ] All helper functions defined

### .ipynb File (Local Jupyter)
- [ ] Standard Jupyter notebook format
- [ ] No Databricks-specific headers
- [ ] No magic commands
- [ ] Direct variable assignment (no widgets)
- [ ] Setup instructions in markdown cell
- [ ] Same helper functions as .py

### Helper Functions
- [ ] `list_tables()` - Table discovery
- [ ] `explore_table()` - Schema + samples
- [ ] `check_data_quality()` - DQ checks
- [ ] `compare_tables()` - Layer comparison
- [ ] `show_table_properties()` - Governance metadata

## Reference Files

### Notebook Patterns
[references/notebook-patterns.md](references/notebook-patterns.md) - Complete code patterns for both `.py` and `.ipynb` formats, helper function implementations, widget fallback patterns, Spark session initialization, and Asset Bundle integration.

## Assets

### Exploration Notebook Template
[assets/templates/exploration-notebook.py](assets/templates/exploration-notebook.py) - Starter notebook template with all standard helper functions and widget fallback patterns.

## References

### Official Databricks Documentation
- [Databricks Connect](https://docs.databricks.com/dev-tools/databricks-connect.html)
- [Databricks Notebooks](https://docs.databricks.com/notebooks/)
- [Databricks SDK for Python](https://databricks-sdk-py.readthedocs.io/)

### Related Patterns
- [Databricks Asset Bundles](../common/databricks-asset-bundles/SKILL.md) - Deployment patterns
- [Python File Imports](../common/databricks-python-imports/SKILL.md) - Sharing code between notebooks
- [DLT Expectations](../silver/dlt-expectations-patterns/SKILL.md) - DQ rules and validation
