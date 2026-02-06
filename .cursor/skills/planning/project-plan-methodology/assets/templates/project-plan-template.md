# Phase X: [Phase Name]

## Overview

**Status:** 📋 Planned | 🚧 In Progress | ✅ Complete  
**Dependencies:** [List dependencies]  
**Effort Estimate:** [X weeks/days]  
**Owner:** [Name/Team]

## Objectives

- [Objective 1]
- [Objective 2]
- [Objective 3]

## Agent Domain Organization

All artifacts MUST be organized by Agent Domain:

- 💰 **Cost** - FinOps, budgets, chargeback
- 🔒 **Security** - Access audit, compliance
- ⚡ **Performance** - Query optimization, capacity
- 🔄 **Reliability** - Job health, SLAs
- ✅ **Quality** - Data quality, governance

## Artifacts by Domain

### 💰 Cost Agent Domain

#### [Artifact Name]

**Type:** [TVF | Metric View | Dashboard | Alert | ML Model | Monitor | Genie Space]  
**Gold Tables:** `fact_usage`, `dim_sku`  
**Business Questions:** "What are the top cost drivers?"  
**Dependencies:** [List dependencies]  
**Status:** 📋 Planned | 🚧 In Progress | ✅ Complete

**Description:**
[Detailed description of what this artifact does]

**Example:**
```sql
-- For TVFs, Metric Views, Alerts
SELECT ...
FROM ${catalog}.${gold_schema}.fact_usage
WHERE ...
```

**LLM-Friendly Comment:**
```sql
COMMENT 'LLM: [Description of what it does, when to use it, example questions]'
```

---

### 🔒 Security Agent Domain

[Repeat structure for Security domain]

---

### ⚡ Performance Agent Domain

[Repeat structure for Performance domain]

---

### 🔄 Reliability Agent Domain

[Repeat structure for Reliability domain]

---

### ✅ Quality Agent Domain

[Repeat structure for Quality domain]

---

## Summary Table

| Artifact | Type | Domain | Gold Tables | Status | Dependencies |
|----------|------|--------|-------------|--------|---------------|
| [Name] | TVF | 💰 Cost | `fact_usage` | ✅ Complete | Gold layer |
| [Name] | Metric View | 💰 Cost | `fact_usage` | 🚧 In Progress | Gold layer |

## Artifact Count Summary

| Domain | TVFs | Metric Views | Dashboards | Alerts | ML Models | Monitors | Genie Spaces |
|--------|------|--------------|------------|--------|-----------|----------|-------------|
| 💰 Cost | X | X | X | X | X | X | X |
| 🔒 Security | X | X | X | X | X | X | X |
| ⚡ Performance | X | X | X | X | X | X | X |
| 🔄 Reliability | X | X | X | X | X | X | X |
| ✅ Quality | X | X | X | X | X | X | X |
| **Total** | X | X | X | X | X | X | X |

## Success Criteria

| Criterion | Target | Status |
|-----------|--------|--------|
| All domains covered | 5 domains | ✅ |
| Minimum artifact counts | [See standards] | 🚧 |
| Gold layer references | 100% | ✅ |
| LLM-friendly comments | 100% | ✅ |
| Testing complete | All artifacts | 🚧 |

## SQL Query Standards

### Gold Layer Reference Pattern

**ALWAYS use Gold layer tables, NEVER system tables directly.**

```sql
-- ❌ WRONG: Direct system table reference
FROM system.billing.usage

-- ✅ CORRECT: Gold layer reference with variables
FROM ${catalog}.${gold_schema}.fact_usage
```

### Standard Variable References

```sql
-- Catalog and schema (from parameters)
${catalog}.${gold_schema}.table_name

-- Date parameters (STRING type for Genie compatibility)
WHERE usage_date BETWEEN CAST(start_date AS DATE) AND CAST(end_date AS DATE)

-- SCD Type 2 dimension joins
LEFT JOIN dim_workspace w 
    ON f.workspace_id = w.workspace_id 
    AND w.is_current = TRUE
```

### LLM-Friendly Comments

All artifacts must have comments that help LLMs (Genie, AI/BI) understand:

```sql
COMMENT 'LLM: Returns top N cost contributors by workspace and SKU for a date range.
Use this for cost optimization, chargeback analysis, and identifying spending hotspots.
Parameters: start_date, end_date (YYYY-MM-DD format), optional top_n (default 10).
Example questions: "What are the top 10 cost drivers?" or "Which workspace spent most?"'
```

## Artifact Naming Conventions

| Artifact | Pattern | Example |
|----------|---------|---------|
| TVF | `get_<domain>_<metric>` | `get_cost_by_tag` |
| Metric View | `<domain>_analytics_metrics` | `cost_analytics_metrics` |
| Dashboard | `<Domain> <Purpose> Dashboard` | `Cost Attribution Dashboard` |
| Alert | `<DOMAIN>-NNN` | `COST-001` |
| ML Model | `<Purpose> <Type>` | `Budget Forecaster` |
| Monitor | `<table> Monitor` | `Cost Data Quality Monitor` |
| Genie Space | `<Domain> <Purpose>` | `Cost Intelligence` |
| AI Agent | `<Domain> Agent` | `Cost Agent` |

## Common Mistakes to Avoid

### ❌ DON'T: Mix system tables and Gold tables

```sql
-- BAD: Direct system table
FROM system.billing.usage u
JOIN ${catalog}.${gold_schema}.dim_workspace w ...
```

### ❌ DON'T: Forget Agent Domain classification

```markdown
## get_slow_queries (BAD - no domain)

## ⚡ Performance Agent: get_slow_queries (GOOD)
```

### ❌ DON'T: Create artifacts without cross-addendum updates

When adding a TVF, also consider:
- Does it need a Metric View counterpart?
- Should there be an Alert?
- Is it Dashboard-worthy?

### ❌ DON'T: Use DATE parameters in TVFs (Genie incompatible)

```sql
-- BAD
start_date DATE

-- GOOD
start_date STRING COMMENT 'Format: YYYY-MM-DD'
```

## References

- [Related Cursor Rules](.cursor/rules/...)
- [Official Documentation](https://docs.databricks.com/...)

## Notes

[Any additional notes, learnings, or considerations]
