---
name: databricks-aibi-dashboards
description: Production-grade patterns for Databricks AI/BI (Lakeview) dashboards. Prevents visualization errors, deployment failures, and maintenance issues through widget-query alignment, number formatting, parameter configuration, monitoring table patterns, chart scale properties, and automated deployment workflows.
metadata:
  author: databricks-sa
  version: "1.0"
  domain: monitoring
  keywords:
    - databricks
    - ai/bi
    - lakeview
    - dashboards
    - monitoring
    - visualization
    - deployment
    - widget configuration
    - sql validation
---

# Databricks AI/BI Dashboards

## Overview

This skill provides comprehensive patterns for building production-grade Databricks AI/BI (Lakeview) dashboards. These patterns were developed from 100+ production deployments and prevent common visualization errors, deployment failures, and maintenance issues.

**Key Capabilities:**
- Widget-query column alignment validation
- Number formatting rules (percentages, currency, plain numbers)
- Parameter configuration (time ranges, multi-select, text input)
- Monitoring table query patterns (window structs, CASE pivots, custom drift metrics)
- Chart configuration (pie, bar, line, area, table widgets)
- Pre-deployment SQL validation (90% reduction in dev loop time)
- UPDATE-or-CREATE deployment pattern (preserves URLs and permissions)
- Variable substitution (no hardcoded schemas)

## When to Use This Skill

Use this skill when:
- **Building AI/BI dashboards** - Creating new dashboards with proper widget configurations
- **Troubleshooting visualization errors** - Fixing "no fields to visualize", empty charts, or formatting issues
- **Deploying dashboards via API** - Automating dashboard deployment with UPDATE-or-CREATE pattern
- **Validating dashboard queries** - Pre-deployment SQL validation to catch errors before deployment
- **Querying monitoring tables** - Accessing Lakehouse Monitoring profile and drift metrics
- **Configuring parameters** - Setting up time ranges, filters, and multi-select parameters

## Quick Reference

### Top 5 Critical Rules

| Rank | Issue | Prevention |
|------|-------|------------|
| 1 | Widget-Query Column Mismatch | Always use explicit SQL aliases matching widget `fieldName` |
| 2 | Incorrect Number Formatting | Return raw numbers, not formatted strings |
| 3 | Missing Parameter Definitions | Define ALL parameters in dataset's `parameters` array |
| 4 | Monitoring Table Schema | Use `CASE` pivots on `column_name`, access `window.start` |
| 5 | Pie Chart Scale Missing | Add explicit `scale` to both `color` and `angle` encodings |

### Widget-Query Alignment

**Rule:** Widget `fieldName` MUST exactly match query output column alias.

```sql
-- ✅ CORRECT
SELECT COUNT(*) AS total_queries FROM ...
-- Widget: "fieldName": "total_queries"

-- ❌ WRONG
SELECT COUNT(*) AS query_count FROM ...
-- Widget: "fieldName": "total_queries"  -- MISMATCH!
```

### Number Formatting

| Format Type | Expects | Example |
|-------------|---------|---------|
| `number-plain` | Raw number | `1234` → `1,234` |
| `number-percent` | 0-1 decimal (×100) | `0.85` → `85%` |
| `number-currency` | Raw number | `1234.56` → `$1,234.56` |

**Never use:** `FORMAT_NUMBER()`, `CONCAT('$', ...)`, or `CONCAT(..., '%')` in queries.

### Monitoring Table Patterns

```sql
-- ✅ CORRECT - Access window struct
SELECT window.start AS window_start FROM monitoring_table
WHERE window.start BETWEEN :time_range.min AND :time_range.max

-- ✅ CORRECT - CASE pivot for generic metrics
SELECT 
  window.start AS window_start,
  MAX(CASE WHEN column_name = 'success_rate' THEN avg END) AS success_rate_pct
FROM fact_job_run_timeline_profile_metrics
WHERE window.start BETWEEN :time_range.min AND :time_range.max
GROUP BY window.start

-- ✅ CORRECT - Custom drift metrics are direct columns
SELECT 
  window.start AS window_start,
  success_rate_drift,  -- Direct column!
  cost_drift_pct       -- Direct column!
FROM fact_job_run_timeline_drift_metrics
WHERE column_name = ':table' AND drift_type = 'CONSECUTIVE'
```

### Chart Scale Requirements

**Pie Charts:**
```json
{
  "encodings": {
    "color": { "fieldName": "category", "scale": { "type": "categorical" } },
    "angle": { "fieldName": "value", "scale": { "type": "quantitative" } }
  }
}
```

**Bar Charts:**
```json
{
  "encodings": {
    "x": { "fieldName": "category", "scale": { "type": "categorical" } },
    "y": { "fieldName": "value", "scale": { "type": "quantitative" } }
  }
}
```

## Critical Rules

### 1. Widget-Query Column Alignment

**MUST:** Widget `fieldName` exactly matches query output alias.

**Common Mismatches:**
- Widget expects `total_queries`, query returns `query_count` → Alias as `total_queries`
- Widget expects `warehouse_name`, query returns `compute_type` → Alias as `warehouse_name`
- Widget expects `unique_users`, query returns `distinct_users` → Alias as `unique_users`

**Validation:** Use `validate_widget_encodings.py` script before deployment.

### 2. Number Formatting

**MUST:** Return raw numbers, let widgets format them.

**Rules:**
- Percentages: Return 0-1 decimal (e.g., `0.85` for 85%)
- Currency: Return raw numeric (e.g., `1234.56` for $1,234.56)
- Never use `FORMAT_NUMBER()` or string concatenation in queries

### 3. Parameter Configuration

**MUST:** Define ALL parameters in dataset's `parameters` array.

**Time Range Pattern:**
```json
{
  "keyword": "time_range",
  "dataType": "DATETIME_RANGE",
  "defaultSelection": {
    "range": {
      "min": { "dataType": "DATETIME", "value": "now-30d/d" },
      "max": { "dataType": "DATETIME", "value": "now/d" }
    }
  }
}
```

**SQL Access:**
```sql
WHERE date BETWEEN :time_range.min AND :time_range.max
```

### 4. Monitoring Table Schema

**MUST:** Use correct access patterns for monitoring tables.

**Window Struct:**
- Use `window.start` not `window_start`
- Access as `window.start AS window_start`

**Generic Metrics:**
- Use `CASE` pivot on `column_name` field
- Pattern: `MAX(CASE WHEN column_name = 'metric_name' THEN avg END) AS metric_name`

**Custom Drift Metrics:**
- Stored as **direct columns** (not in `avg_delta`)
- Filter: `WHERE column_name = ':table' AND drift_type = 'CONSECUTIVE'`

### 5. Chart Scale Properties

**MUST:** Add explicit `scale` to chart encodings.

**Required Scales:**
- Pie: `color.scale: categorical`, `angle.scale: quantitative`
- Bar: `x.scale: categorical`, `y.scale: quantitative`
- Line: `x.scale: temporal`, `y.scale: quantitative`, `color.scale: categorical`
- Area: `x.scale: temporal`, `y.scale: quantitative`, `color.scale: categorical`

## Core Patterns

### Variable Substitution

**NEVER hardcode schemas.** Always use variables:

```sql
-- ✅ CORRECT
FROM ${catalog}.${gold_schema}.fact_usage
FROM ${catalog}.${gold_schema}_monitoring.fact_usage_profile_metrics

-- ❌ WRONG
FROM prashanth_catalog.gold.fact_usage
```

**Substitution in Python:**
```python
json_str = json_str.replace('${catalog}', catalog)
json_str = json_str.replace('${gold_schema}', gold_schema)
```

### UPDATE-or-CREATE Deployment

**Pattern:** Use Workspace Import API with `overwrite: true`

**Benefits:**
- Preserves dashboard URLs and permissions
- Single code path for CREATE and UPDATE
- No manual dashboard creation required

**Implementation:** See `scripts/deploy_dashboard.py`

### Pre-Deployment Validation

**Strategy:** Validate queries with `SELECT LIMIT 1` before deployment

**Benefits:**
- 90% reduction in dev loop time
- Catches ALL errors at once (not one-by-one)
- Validates runtime errors (not just syntax)

**Scripts:**
- `validate_dashboard_queries.py` - SQL validation
- `validate_widget_encodings.py` - Widget-query alignment

### Multi-Series Charts

**Pattern:** Use `UNION ALL` to combine series

```sql
SELECT date, 'Average' AS metric, AVG(value) AS value FROM table GROUP BY date
UNION ALL
SELECT date, 'P95' AS metric, PERCENTILE_APPROX(value, 0.95) AS value FROM table GROUP BY date
ORDER BY date, metric
```

**Widget Encoding:**
```json
{
  "x": { "fieldName": "date", "scale": { "type": "temporal" } },
  "y": { "fieldName": "value", "scale": { "type": "quantitative" } },
  "color": { "fieldName": "metric", "scale": { "type": "categorical" } }
}
```

### Stacked Area Charts

**Pattern:** Use `stack: "zero"` in y encoding

```json
{
  "y": {
    "fieldName": "run_count",
    "scale": { "type": "quantitative" },
    "stack": "zero"  // CRITICAL for stacking
  }
}
```

## Reference Documentation

Detailed patterns and examples are organized in reference files:

- **[Dashboard JSON Reference](references/dashboard-json-reference.md)** - JSON structure, page layouts, dataset configuration, variable substitution, widget versions, naming conventions
- **[Widget Patterns](references/widget-patterns.md)** - Widget-query alignment, number formatting, parameters, chart configurations, multi-series charts, error fixes
- **[Deployment Guide](references/deployment-guide.md)** - UPDATE-or-CREATE pattern, variable substitution, SQL validation, monitoring queries, best practices, checklists

## Scripts

Automation scripts for deployment and validation:

- **[deploy_dashboard.py](scripts/deploy_dashboard.py)** - UPDATE-or-CREATE deployment with variable substitution
  ```python
  from scripts.deploy_dashboard import deploy_dashboards
  deploy_dashboards(workspace_client, dashboard_dir, catalog, gold_schema, warehouse_id)
  ```

- **[validate_dashboard_queries.py](scripts/validate_dashboard_queries.py)** - Pre-deployment SQL validation
  ```bash
  python scripts/validate_dashboard_queries.py
  ```
  Catches: `UNRESOLVED_COLUMN`, `TABLE_OR_VIEW_NOT_FOUND`, `UNBOUND_SQL_PARAMETER`, `DATATYPE_MISMATCH`

- **[validate_widget_encodings.py](scripts/validate_widget_encodings.py)** - Widget-query alignment validation
  ```bash
  python scripts/validate_widget_encodings.py
  ```
  Catches: Column alias mismatches, missing columns

## Assets

- **[dashboard-template.json](assets/templates/dashboard-template.json)** - Starter dashboard JSON with dataset, time range parameter, KPI widget, and page layout. Copy and modify for new dashboards.

## Common Error Messages

| Error | Cause | Fix |
|-------|-------|-----|
| "no fields to visualize" | Widget `fieldName` doesn't match query alias | Align column aliases |
| "UNRESOLVED_COLUMN" | Column doesn't exist | Check schema, use correct column |
| "UNBOUND_SQL_PARAMETER" | Parameter not defined | Add to `parameters` array |
| "Unable to render visualization" | Pie chart missing scale | Add `scale` to encodings |
| Empty chart with data | Wrong number format | Return raw numbers, not strings |
| 0% or 0 in counter | Formatted string or wrong percentage | Return 0-1 decimal for percent |

## Validation Checklist

**Pre-Deployment:**
- [ ] SQL Validation passed - All queries return results without error
- [ ] Widget Encoding Validation passed - All fieldNames match query aliases
- [ ] Git diff reviewed - No accidental deletions or regressions
- [ ] Local testing done - Validated in dev environment

**Widget-Query Alignment:**
- [ ] Widget `fieldName` matches query output alias exactly
- [ ] Format type matches expected value type (raw numbers for percent/currency)
- [ ] All parameters are defined in dataset's `parameters` array
- [ ] Time range uses correct access pattern (`:time_range.min`, `:time_range.max`)

**Monitoring Query Validation:**
- [ ] Uses `window.start` not `window_start`
- [ ] Custom AGGREGATE/DERIVED metrics selected as direct columns
- [ ] Schema is `${catalog}.${gold_schema}_monitoring`
- [ ] Includes `WHERE column_name = ':table' AND slice_key IS NULL`

**Chart Validation:**
- [ ] Pie charts: `color.scale: categorical`, `angle.scale: quantitative`
- [ ] Bar charts: `x.scale: categorical`, `y.scale: quantitative`
- [ ] Table widgets: Uses `version: 2`, no invalid properties

## References

### Official Documentation
- [AI/BI Lakeview Dashboards](https://docs.databricks.com/dashboards/lakeview/)
- [System Tables Overview](https://docs.databricks.com/aws/en/admin/system-tables/)
- [Lakehouse Monitoring](https://docs.databricks.com/lakehouse-monitoring/)
- [Workspace Dashboard API](https://learn.microsoft.com/en-us/azure/databricks/dashboards/tutorials/workspace-dashboard-api)

### Related Skills
- `lakehouse-monitoring-comprehensive` - Monitoring setup patterns
- `sql-alerting-patterns` - SQL alert configuration
