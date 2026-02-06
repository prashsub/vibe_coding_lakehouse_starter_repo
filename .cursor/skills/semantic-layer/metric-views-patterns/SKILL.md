---
name: metric-views-patterns
description: Standard patterns for creating Databricks Metric Views with semantic metadata for Genie and AI/BI. Use when creating metric views, troubleshooting metric view creation errors, validating schema references before deployment, implementing joins (including snowflake schema patterns), or optimizing metric views for Genie natural language queries.
metadata:
  author: databricks-sa
  version: "1.0"
  domain: semantic-layer
---

# Metric Views Patterns for Genie & AI/BI

## Overview

Metric Views provide a semantic layer for natural language queries via Genie and AI/BI dashboards. This skill standardizes the YAML structure for comprehensive, LLM-friendly metric definitions following Databricks Metric View Specification v1.1.

**Key Capabilities:**
- Create metric views with proper SQL syntax (`WITH METRICS LANGUAGE YAML`)
- Validate schemas before deployment to prevent 100% of common errors
- Structure joins (direct and snowflake schema patterns)
- Optimize comments for Genie natural language queries
- Handle SCD2 dimensions with proper `is_current` filtering

## When to Use This Skill

Use this skill when:
- Creating new metric views for Genie Spaces
- Troubleshooting metric view creation errors
- Validating schema references before deployment
- Implementing joins (including transitive relationships)
- Optimizing metric views for Genie natural language queries
- Ensuring compliance with v1.1 specification

## Critical Rules

### ⚠️ CRITICAL: Correct SQL Syntax

**Metric views MUST be created using `WITH METRICS LANGUAGE YAML` syntax:**

```python
create_sql = f"""
CREATE OR REPLACE VIEW {fully_qualified_name}
WITH METRICS
LANGUAGE YAML
COMMENT '{view_comment_escaped}'
AS $$
{yaml_str}
$$
"""
```

**Key Requirements:**
1. `WITH METRICS` - Identifies the view as a metric view
2. `LANGUAGE YAML` - Specifies YAML format
3. `AS $$ ... $$` - YAML content wrapped in dollar-quote delimiters
4. No SELECT statement - The YAML definition IS the view definition
5. `version` field - Must be included in each metric view YAML

**❌ WRONG:** Regular view with TBLPROPERTIES (creates regular VIEW, not METRIC_VIEW)

### ⚠️ CRITICAL: v1.1 Unsupported Fields

**These fields will cause errors and MUST NOT be used:**

| Field | Error | Action |
|-------|-------|--------|
| `name` | `Unrecognized field "name"` | ❌ NEVER include - name is in CREATE VIEW statement |
| `time_dimension` | `Unrecognized field "time_dimension"` | ❌ Remove entirely |
| `window_measures` | `Unrecognized field "window_measures"` | ❌ Remove entirely - calculate in SQL/Python |
| `join_type` | Unsupported | ❌ Remove - defaults to LEFT OUTER JOIN |
| `table` (in joins) | `Missing required creator property 'source'` | ✅ Use `source` instead |

### ⚠️ MANDATORY: Pre-Creation Schema Validation

**ALWAYS validate schemas BEFORE creating metric view YAML. 100% of deployment failures are preventable schema issues.**

**Schema Validation Checklist:**
- [ ] Verified source table schema (ran DESCRIBE TABLE or checked YAML)
- [ ] Verified all joined table schemas
- [ ] Created column reference checklist for all tables
- [ ] Validated every dimension `expr` column exists
- [ ] Validated every measure `expr` column exists
- [ ] Validated join key columns exist in both tables
- [ ] Verified no transitive joins (all joins are source → table)
- [ ] For COUNT measures, verified primary key column exists
- [ ] For SCD2 joins, verified `is_current` column exists

See `references/validation-checklist.md` for detailed validation steps.

### ⚠️ CRITICAL: Source Table Selection

**Rule:** Revenue/bookings/transactions → FACT table. Property/host counts → DIMENSION table.

**❌ WRONG:** Revenue from dimension table (under-reports by 4x)
```yaml
source: ${catalog}.${schema}.dim_property  # ❌ Wrong for revenue!
```

**✅ CORRECT:** Revenue from fact table
```yaml
source: ${catalog}.${schema}.fact_booking_daily  # ✅ Correct for revenue!
```

### ⚠️ CRITICAL: Transitive Join Limitations

**Metric Views v1.1 DO NOT support transitive/chained joins.**

**❌ WRONG:** Transitive join (not supported)
```yaml
joins:
  - name: dim_property
    source: catalog.schema.dim_property
    'on': source.property_id = dim_property.property_id
  - name: dim_destination
    source: catalog.schema.dim_destination
    'on': dim_property.destination_id = dim_destination.destination_id  # ❌ ERROR!
```

**✅ CORRECT:** Use snowflake schema (nested joins) or denormalize fact table

See `references/advanced-patterns.md` for snowflake schema patterns.

## Quick Reference

### YAML Structure (v1.1)

```yaml
version: "1.1"
comment: >
  PURPOSE: [One-line description]
  BEST FOR: [Question 1] | [Question 2] | [Question 3]
  NOT FOR: [What to avoid] (use [correct_asset] instead)
  DIMENSIONS: [dim1], [dim2], [dim3]
  MEASURES: [measure1], [measure2], [measure3]
  SOURCE: [fact_table] ([domain] domain)
  JOINS: [dim_table1] ([description])
  NOTE: [Critical caveats]

source: ${catalog}.${gold_schema}.<fact_table>

joins:
  - name: <dim_table_alias>
    source: ${catalog}.${gold_schema}.<dim_table>
    'on': source.<fk> = <dim_table_alias>.<pk> AND <dim_table_alias>.is_current = true

dimensions:
  - name: <dimension_name>
    expr: source.<column>
    comment: <Business description>
    display_name: <User-Friendly Name>
    synonyms: [<alt1>, <alt2>]

measures:
  - name: <measure_name>
    expr: SUM(source.<column>)
    comment: <Business description>
    display_name: <User-Friendly Name>
    format:
      type: currency|number|percentage
      currency_code: USD
      decimal_places:
        type: exact|all
        places: 2
    synonyms: [<alt1>, <alt2>]
```

### Column References

- **Main table columns:** Use `source.` prefix in all `expr` fields
- **Joined table columns:** Use join `name` as prefix (e.g., `dim_store.column_name`)
- **Never reference table names directly:** Use `source.` or `{join_name}.`

### Join Requirements

- Each join **MUST have** `name`, `source`, and `'on'` fields (quoted!)
- ON clause uses `source.` for main table, join name for joined table
- Each join must be direct: `source.fk = dim.pk` (NOT `dim1.fk = dim2.pk`)
- SCD2 joins must include `AND {dim_table}.is_current = true`

## Core Patterns

### Standardized Comment Format (v3.0)

Use structured format for Genie optimization:

```yaml
comment: >
  PURPOSE: Comprehensive cost analytics for Databricks billing and usage analysis.
  
  BEST FOR: Total spend by workspace | Cost trend over time | SKU cost breakdown
  
  NOT FOR: Commit/contract tracking (use commit_tracking) | Real-time cost alerts
  
  DIMENSIONS: usage_date, workspace_name, sku_name, owner, tag_team
  
  MEASURES: total_cost, total_dbus, cost_7d, cost_30d
  
  SOURCE: fact_usage (billing domain)
  
  JOINS: dim_workspace (workspace details), dim_sku (SKU details)
  
  NOTE: Cost values are list prices. Actual billed amounts may differ.
```

### Dimension Patterns

**Geographic:**
```yaml
- name: store_number
  expr: source.store_number
  comment: Store identifier for location-based analysis
  display_name: Store Number
  synonyms: [store id, location number, store code]
```

**Time (from dim_date):**
```yaml
- name: month_name
  expr: dim_date.month_name
  comment: Month name for seasonal analysis
  display_name: Month
  synonyms: [month]
```

### Measure Patterns

**Revenue:**
```yaml
- name: total_revenue
  expr: SUM(source.net_revenue)
  comment: Total net revenue after discounts and returns
  display_name: Total Revenue
  format:
    type: currency
    currency_code: USD
    decimal_places:
      type: exact
      places: 2
    abbreviation: compact
  synonyms: [revenue, sales, net revenue]
```

**Count:**
```yaml
- name: booking_count
  expr: COUNT(source.booking_id)  # ✅ Use primary key, not SUM(count_column)
  comment: Total number of transactions
  display_name: Booking Count
  format:
    type: number
    decimal_places:
      type: all
  synonyms: [bookings, transactions]
```

See `references/advanced-patterns.md` for complete examples.

## Python Script Error Handling

**⚠️ CRITICAL: Jobs Must Fail if Metric Views Don't Create**

```python
def create_metric_view(spark, catalog, schema, view_name, metric_view):
    fqn = f"{catalog}.{schema}.{view_name}"
    
    # Drop existing table/view to avoid conflicts
    try:
        spark.sql(f"DROP VIEW IF EXISTS {fqn}")
        spark.sql(f"DROP TABLE IF EXISTS {fqn}")
    except:
        pass
    
    try:
        create_sql = f"""
        CREATE VIEW {fqn}
        WITH METRICS
        LANGUAGE YAML
        COMMENT '{comment}'
        AS $$
{yaml_str}
        $$
        """
        spark.sql(create_sql)
        return True
    except Exception as e:
        print(f"✗ Error creating {view_name}: {e}")
        return False

def main():
    metric_views = load_metric_views_yaml(catalog, schema)
    failed_views = []
    
    for view_name, metric_view in metric_views:
        if not create_metric_view(spark, catalog, schema, view_name, metric_view):
            failed_views.append(view_name)
    
    if failed_views:
        raise RuntimeError(
            f"Failed to create {len(failed_views)} metric view(s): "
            f"{', '.join(failed_views)}"
        )
```

## Common Mistakes to Avoid

❌ **Don't:**
- Include `name` field in YAML (name is in CREATE VIEW statement)
- Use `time_dimension` or `window_measures` (not supported in v1.1)
- Assume column names without validating schemas
- Use transitive joins (dim1.fk = dim2.pk)
- Source revenue metrics from dimension tables

✅ **Do:**
- Validate all schemas before writing YAML
- Use structured comment format for Genie
- Use `source.` prefix for main table columns
- Use join name prefix for joined table columns
- Include `is_current = true` for SCD2 joins

## Reference Files

- **`references/yaml-reference.md`** - Complete YAML structure, fields, and syntax
- **`references/validation-checklist.md`** - Detailed pre-creation validation steps
- **`references/advanced-patterns.md`** - Dimension/measure patterns, joins, snowflake schema

## Scripts

- **`scripts/validate_metric_view.py`** - Validation utility to check column references before deployment

**Usage:**
```bash
python scripts/validate_metric_view.py \
  --yaml-file src/semantic/metric_views/revenue_analytics_metrics.yaml \
  --gold-yaml-dir gold_layer_design/yaml
```

## Assets

- **`assets/templates/metric-view-template.yaml`** - Starter template for new metric views

## References

### Official Documentation
- [Metric Views SQL Creation](https://docs.databricks.com/aws/en/metric-views/create/sql)
- [Metric Views YAML Reference](https://docs.databricks.com/aws/en/metric-views/yaml-ref)
- [Metric Views Semantic Metadata](https://docs.databricks.com/aws/en/metric-views/semantic-metadata)
- [Metric Views Joins](https://docs.databricks.com/aws/en/metric-views/joins)

### Related Skills
- `databricks-table-valued-functions` - TVF patterns for Genie
- `genie-space-patterns` - Genie Space setup

## Version History

- **v3.0** (Dec 19, 2025) - Standardized structured comment format
- **v2.0** (Dec 16, 2025) - Genie optimization patterns from production post-mortem
- **v1.0** (Oct 2025) - Initial rule based on metric view deployment learnings
