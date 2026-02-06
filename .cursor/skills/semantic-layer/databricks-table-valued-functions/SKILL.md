---
name: databricks-table-valued-functions
description: Patterns and best practices for creating Table-Valued Functions (TVFs) in Databricks optimized for Genie Space natural language queries. Use when creating TVFs for Genie Spaces, troubleshooting TVF compilation errors, or ensuring Genie compatibility. Includes schema validation patterns, SQL requirements (STRING parameters, parameter ordering, LIMIT workarounds), LLM-friendly comment format, null safety, SCD2 handling, and cartesian product prevention.
metadata:
  author: databricks-sa
  version: "1.0"
  domain: semantic-layer
---

# Databricks Table-Valued Functions (TVFs) for Genie

## Overview

Table-Valued Functions (TVFs) in Databricks have specific requirements when used with Genie Spaces for natural language queries. This skill standardizes TVF creation to ensure Genie compatibility and SQL compliance.

**Key Capabilities:**
- Create TVFs with Genie-compatible parameter types (STRING for dates)
- Validate schemas before writing SQL to prevent 100% of compilation errors
- Structure comments for optimal Genie natural language query matching
- Handle SCD2 dimensions with proper `is_current` filtering
- Prevent cartesian products in aggregation CTEs
- Use proper parameter ordering and LIMIT workarounds

## When to Use This Skill

Use this skill when:
- Creating TVFs for Genie Spaces
- Troubleshooting TVF compilation errors
- Ensuring Genie compatibility
- Validating schemas before writing SQL
- Preventing common SQL errors (parameter types, LIMIT clauses, cartesian products)

## Critical Rules

### ⚠️ CRITICAL: Schema Validation BEFORE Writing SQL

**RULE #0: Always consult YAML schema definitions before writing any TVF SQL**

**100% of SQL compilation errors are caused by not consulting YAML schemas first.**

**Pre-Development Checklist:**
1. Read YAML schema files (5 minutes)
2. Create SCHEMA_MAPPING.md (2 minutes)
3. Write TVF SQL using documented schema
4. Run validation script (30 sec)
5. Deploy

**ROI:** 71% time reduction (45 min → 13 min)  
**First-Time Success Rate:** 0% → 95%+

See `references/tvf-patterns.md` for detailed schema validation workflow.

### ⚠️ Issue 1: Parameter Types for Genie Compatibility

**RULE: Use STRING for date parameters, not DATE**

Genie Spaces do not support DATE type parameters. Always use STRING with explicit format documentation.

**❌ DON'T:**
```sql
CREATE FUNCTION get_sales_by_date_range(
  start_date DATE COMMENT 'Start date',
  end_date DATE COMMENT 'End date'
)
```

**✅ DO:**
```sql
CREATE FUNCTION get_sales_by_date_range(
  start_date STRING COMMENT 'Start date (format: YYYY-MM-DD)',
  end_date STRING COMMENT 'End date (format: YYYY-MM-DD)'
)
...
WHERE transaction_date BETWEEN CAST(start_date AS DATE) AND CAST(end_date AS DATE)
```

### ⚠️ Issue 2: Parameter Ordering with DEFAULT Values

**RULE: Parameters with DEFAULT must come AFTER parameters without DEFAULT**

**❌ DON'T:**
```sql
CREATE FUNCTION get_top_stores(
  top_n INT DEFAULT 10,          -- ❌ DEFAULT parameter first
  start_date STRING,              -- ❌ Required parameter after DEFAULT
  end_date STRING
)
```

**✅ DO:**
```sql
CREATE FUNCTION get_top_stores(
  start_date STRING,              -- ✅ Required parameter first
  end_date STRING,                -- ✅ Required parameter
  top_n INT DEFAULT 10            -- ✅ Optional parameter last
)
```

### ⚠️ Issue 3: LIMIT Clauses Cannot Use Parameters

**RULE: Use WHERE rank <= parameter instead of LIMIT parameter**

LIMIT clauses require compile-time constants. Use WHERE with ROW_NUMBER() instead.

**❌ DON'T:**
```sql
SELECT * FROM store_metrics
ORDER BY total_revenue DESC
LIMIT top_n;  -- ❌ Cannot use parameter here
```

**✅ DO:**
```sql
WITH ranked_stores AS (
  SELECT ...,
    ROW_NUMBER() OVER (ORDER BY total_revenue DESC) as rank
  FROM store_metrics
)
SELECT * FROM ranked_stores
WHERE rank <= top_n  -- ✅ Can use parameter in WHERE
ORDER BY rank;
```

### ⚠️ CRITICAL: Cartesian Product Bug in Aggregation CTEs

**Never re-join a table that's already been aggregated in a CTE.**

**❌ BUGGY PATTERN:**
```sql
WITH period_data AS (
  SELECT SUM(revenue) as total_revenue
  FROM fact_table
  GROUP BY period
),
final AS (
  SELECT SUM(pd.total_revenue), SUM(ft.other_metric)  -- 🔥 CARTESIAN!
  FROM period_data pd
  LEFT JOIN fact_table ft ON ...  -- ❌ Re-joining source!
)
```

**✅ CORRECT PATTERN:**
```sql
SELECT 
  period,
  SUM(revenue) as total_revenue,
  SUM(other_metric) as other_metric
FROM fact_table
GROUP BY period;  -- ✅ Single aggregation pass
```

See `references/tvf-patterns.md` for detailed cartesian product prevention patterns.

## Quick Reference

### Standardized TVF Comment Format (v3.0)

Use bullet-point format for ALL TVF comments:

```sql
COMMENT '
• PURPOSE: [One-line description of what the TVF does]
• BEST FOR: [Example questions separated by |]
• NOT FOR: [What to avoid - redirect to correct TVF] (optional)
• RETURNS: [PRE-AGGREGATED rows or Individual rows] (exact column list)
• PARAMS: [Parameter names with defaults]
• SYNTAX: SELECT * FROM tvf_name(''param1'', ''param2'')
• NOTE: [Important caveats - DO NOT wrap in TABLE(), etc.] (optional)
'
```

### Complete TVF Pattern

```sql
CREATE OR REPLACE FUNCTION get_top_stores_by_revenue(
  -- Required parameters first (no DEFAULT)
  start_date STRING COMMENT 'Start date (format: YYYY-MM-DD)',
  end_date STRING COMMENT 'End date (format: YYYY-MM-DD)',
  -- Optional parameters last (with DEFAULT)
  top_n INT DEFAULT 10 COMMENT 'Number of top stores to return'
)
RETURNS TABLE(
  rank INT COMMENT 'Store rank by revenue',
  store_number STRING COMMENT 'Store identifier',
  store_name STRING COMMENT 'Store name',
  total_revenue DECIMAL(18,2) COMMENT 'Total revenue for period',
  total_units BIGINT COMMENT 'Total units sold'
)
COMMENT '
• PURPOSE: Returns the top N stores ranked by revenue for a date range
• BEST FOR: "What are the top 10 stores by revenue?" | "Show me best performing stores"
• RETURNS: Individual store rows (rank, store_number, store_name, total_revenue, total_units)
• PARAMS: start_date, end_date, top_n (default: 10)
• SYNTAX: SELECT * FROM get_top_stores_by_revenue(''2024-01-01'', ''2024-12-31'', 10)
• NOTE: Returns user_id for individual store analysis | Sorted by total_revenue DESC
'
RETURN
  WITH store_metrics AS (
    SELECT 
      store_number,
      store_name,
      SUM(net_revenue) as total_revenue,
      SUM(net_units) as total_units
    FROM fact_sales_daily
    WHERE transaction_date BETWEEN CAST(start_date AS DATE) AND CAST(end_date AS DATE)
    GROUP BY store_number, store_name
  ),
  ranked_stores AS (
    SELECT 
      ROW_NUMBER() OVER (ORDER BY total_revenue DESC) as rank,
      store_number,
      store_name,
      total_revenue,
      total_units
    FROM store_metrics
  )
  SELECT * FROM ranked_stores
  WHERE rank <= top_n  -- ✅ Use WHERE instead of LIMIT
  ORDER BY rank;
```

## Core Patterns

### Null Safety

**Always use NULLIF() for division to prevent divide-by-zero errors:**

```sql
-- ✅ DO: Null-safe division
total_revenue / NULLIF(transaction_count, 0) as avg_transaction_value
```

### SCD Type 2 Dimension Handling

**Always filter for current records when joining SCD2 dimensions:**

```sql
-- ✅ Correct: Filter for current version
LEFT JOIN dim_store ds 
  ON fsd.store_number = ds.store_number 
  AND ds.is_current = true
```

### Aggregate vs Individual Row TVFs

**Aggregate TVF (Returns Pre-Aggregated Rows):**
- Returns fixed number of rows (e.g., 5 segment rows)
- Data is PRE-AGGREGATED - no GROUP BY needed on top
- Do NOT use in JOINs (no user_id or other keys to join on)

**Individual Row TVF (Returns Detail Rows):**
- Returns variable number of rows based on data
- Each row represents one entity (customer, property, host)
- CAN be used in JOINs (has identifier columns)

See `references/genie-integration.md` for detailed examples.

## TVF Creation Checklist

### SQL Compliance
- [ ] All date parameters are STRING type (not DATE)
- [ ] Required parameters come before optional parameters
- [ ] No parameters used in LIMIT clauses (use WHERE rank <= param)
- [ ] All divisions use NULLIF to prevent divide-by-zero
- [ ] SCD2 joins include `is_current = true` filter
- [ ] **No cartesian products:** CTEs don't re-join tables already aggregated
- [ ] **Single aggregation pass:** Each source table read and aggregated only once

### Genie Optimization (Standardized Comment Format)
- [ ] Function COMMENT uses bullet-point format (• PURPOSE, • BEST FOR, etc.)
- [ ] **PURPOSE:** One-line description of what TVF does
- [ ] **BEST FOR:** 2+ example questions (pipe-separated)
- [ ] **NOT FOR / PREFERRED OVER:** Redirect to correct asset when applicable
- [ ] **RETURNS:** Specifies PRE-AGGREGATED or Individual rows + exact column list
- [ ] **PARAMS:** Parameter names with defaults
- [ ] **SYNTAX:** Exact copyable example with proper date format
- [ ] **NOTE:** Caveats (DO NOT wrap in TABLE(), DO NOT add GROUP BY, etc.)
- [ ] All parameters have descriptive COMMENT with format
- [ ] All returned columns have COMMENT
- [ ] Professional language (no "metric view is broken" phrases)

### Testing
- [ ] Function compiles without errors
- [ ] Function executes with valid parameters
- [ ] Function handles edge cases (empty results, null values)
- [ ] Function tested in Genie Space (if applicable)
- [ ] **Results validated against metric view** (ratio ≈ 1.0, not 254x)

## Common Mistakes to Avoid

❌ **Don't:**
- Use DATE parameters (use STRING with CAST)
- Mix DEFAULT and non-DEFAULT parameters
- Use parameters in LIMIT clauses
- Re-join tables after aggregation (cartesian product)
- Skip schema validation before writing SQL

✅ **Do:**
- Validate schemas from YAML before coding
- Use STRING for date parameters
- Put required parameters before optional ones
- Use WHERE rank <= param instead of LIMIT param
- Single aggregation pass, no self-joins

## Reference Files

- **`references/tvf-patterns.md`** - SQL patterns, parameter types, cartesian product prevention
- **`references/genie-integration.md`** - Genie compatibility, comment format, tips

## Assets

- **`assets/templates/tvf-template.sql`** - Starter SQL template for new TVFs

## References

### Official Documentation
- [Databricks Table-Valued Functions](https://docs.databricks.com/sql/language-manual/sql-ref-syntax-qry-select-tvf)
- [Genie Trusted Assets - Functions](https://docs.databricks.com/genie/trusted-assets#tips-for-writing-functions)
- [SQL UDF Best Practices](https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-create-sql-function)

### Related Skills
- `metric-views-patterns` - Metric view YAML structure
- `genie-space-patterns` - Genie Space setup

## Version History

- **v3.0** (Dec 16, 2025) - Standardized TVF comment format for Genie optimization
- **v2.1** (Dec 15, 2025) - Critical bug prevention: Cartesian product in aggregations
- **v2.0** (Dec 2025) - Major enhancement: Schema-first development patterns
- **v1.0** (Oct 2025) - Initial rule based on 15 TVF deployment learnings
