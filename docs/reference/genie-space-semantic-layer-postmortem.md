# Genie Space & Semantic Layer Post-Mortem

**Date:** December 2025  
**Scope:** Unified Genie Space implementation with Metric Views, TVFs, and ML Integration  
**Duration:** Full implementation cycle with 30+ benchmark questions tested

---

## Executive Summary

This post-mortem documents lessons learned from implementing a unified Genie Space for Wanderbricks vacation rental analytics. The implementation involved 6 metric views, 33 TVFs, 5 ML inference tables, and comprehensive General Instructions. Key findings reveal systematic patterns in semantic layer design, TVF architecture, and LLM guidance that can prevent 80%+ of issues in future implementations.

---

## Phase 1: Foundation Issues

### 1.1 Unity Catalog Namespace Requirements

**Issue:** SQL snippets in documentation lacked full UC 3-part namespace.

**Symptom:**
```sql
-- Missing namespace
SELECT * FROM revenue_analytics_metrics;
-- [TABLE_OR_VIEW_NOT_FOUND]
```

**Root Cause:** Documentation assumed current catalog/schema context.

**Fix:**
```sql
SELECT * FROM catalog.schema.revenue_analytics_metrics;
```

**Lesson:** Always use fully-qualified 3-part names (`catalog.schema.object`) in all documentation, examples, and benchmarks.

---

### 1.2 MEASURE() Function Syntax

**Issue:** `MEASURE()` function called with display names instead of column names.

**Symptom:**
```sql
MEASURE(`Total Revenue`)  -- ❌ Display name
-- [UNRESOLVED_COLUMN] Cannot resolve `Total Revenue`
```

**Root Cause:** Confusion between `display_name` (UI label) and `name` (column identifier) in metric view YAML.

**Fix:**
```sql
MEASURE(total_revenue)  -- ✅ Actual column name (snake_case)
```

**Lesson:** MEASURE() expects the metric `name` field (snake_case), not `display_name`. Document this explicitly in all examples.

---

## Phase 2: TVF Architecture Issues

### 2.1 Date Range Filtering

**Issue:** TVFs with hardcoded 90-day date ranges returned empty results.

**Symptom:** `get_payment_metrics` returned empty when sample data had older dates.

**Root Cause:** TVF assumed recent data; sample data spanned multiple years.

**Fix Options:**
1. Use wide date range: `'2020-01-01'` to `'2099-12-31'` unless a specific date range specified in the question
2. Make date filtering optional with sensible defaults
3. Standardize to 5-year range (1826 days) unless explicitly specified

**Lesson:** 
- Default date ranges should cover typical data scenarios
- Document expected data freshness in TVF comments
- Consider "all time" defaults with optional filtering

---

### 2.2 Cartesian Product in TVF Joins

**Issue:** `get_revenue_by_period` TVF returned 1000x inflated revenue.

**Symptom:**
| Source | Weekly Revenue |
|---|---|
| Metric View | ~$200K |
| TVF | ~$40M |

**Root Cause:** Self-join on `fact_booking_daily` after aggregation created cartesian product.

**Bad Pattern:**
```sql
WITH aggregated AS (
  SELECT ... FROM fact_booking_daily GROUP BY ...
)
SELECT ... 
FROM aggregated a
JOIN fact_booking_daily f ON ...  -- ❌ Joins back to same table!
```

**Fix:** Single aggregation without self-join.

**Lesson:** 
- Never join an aggregated CTE back to its source table
- Always validate TVF results against known metrics before deployment
- Compare TVF output to metric view output for sanity checking

---

### 2.3 Parameterized LIMIT Clause

**Issue:** TVF with parameter in LIMIT clause failed.

**Symptom:**
```sql
LIMIT p_top_n  -- ❌ [INVALID_LIMIT_LIKE_EXPRESSION.IS_UNFOLDABLE]
```

**Root Cause:** Databricks SQL doesn't support parameters directly in LIMIT.

**Fix Pattern:**
```sql
WITH ranked AS (
  SELECT *, ROW_NUMBER() OVER (ORDER BY metric DESC) as rank
  FROM ...
)
SELECT * FROM ranked WHERE rank <= p_top_n  -- ✅ Works
```

**Lesson:** Use `ROW_NUMBER() + WHERE rank <= param` pattern for parameterized top-N queries in TVFs.

---

### 2.4 TVF Returns Aggregate vs Individual Rows

**Issue:** Users attempted to JOIN TVFs that return aggregate statistics.

**Symptom:**
```sql
SELECT * FROM get_customer_segments() cs
JOIN fact_booking fb ON cs.user_id = fb.user_id  -- ❌ No user_id column!
```

**Root Cause:** `get_customer_segments` returns 5 aggregated rows (one per segment), not individual customers.

**Lesson:** 
- Clearly document whether TVF returns PRE-AGGREGATED data or individual rows
- Include explicit column list in TVF comment
- Add "NOT FOR" guidance when TVF should not be used for certain patterns

---

### 2.5 TVF Column Name Mismatches

**Issue:** Genie referenced column names that didn't exist in TVF output.

**Symptom:**
```sql
SELECT booking_count FROM get_host_performance()  -- ❌ Column is total_bookings
```

**Root Cause:** TVF comment didn't explicitly list returned column names.

**Fix:** Standardized TVF description format with explicit column list:
```sql
COMMENT '
• PURPOSE: [description]
• BEST FOR: [example questions]
• RETURNS: Individual rows (host_id, host_name, total_bookings, total_revenue)  -- ✅ Explicit columns
• PARAMS: start_date, end_date, top_n
• SYNTAX: SELECT * FROM tvf_name(params)
'
```

**Lesson:** Always list exact returned column names in TVF comments.

---

### 2.6 TVF Syntax Errors by Genie

**Issue:** Genie wrapped TVFs incorrectly or added unnecessary clauses.

**Symptoms:**
```sql
-- Wrong: TABLE() wrapper
SELECT * FROM TABLE(get_customer_segments())  -- ❌ NOT_A_SCALAR_FUNCTION

-- Wrong: Missing parameters
SELECT * FROM get_customer_segments()  -- ❌ WRONG_NUM_ARGS

-- Wrong: GROUP BY on pre-aggregated data
SELECT segment_name, COUNT(*) FROM get_customer_segments() GROUP BY segment_name  -- ❌ Unnecessary
```

**Fix:** Add explicit syntax guidance in TVF comments:
```sql
COMMENT '
...
• SYNTAX: SELECT * FROM tvf_name(''2020-01-01'', ''2024-12-31'')
• NOTE: DO NOT wrap in TABLE() | DO NOT add GROUP BY - data is already aggregated
'
```

**Lesson:** TVF comments must include:
- Exact syntax example with parameter format
- Explicit warnings about common misuse patterns

---

## Phase 3: Metric View Architecture Issues

### 3.1 Source Table Selection

**Issue:** Genie selected wrong metric view for revenue questions.

**Symptom:**
| Metric View | Property Type Revenue |
|---|---|
| `property_analytics_metrics` | ~$10M (wrong) |
| `revenue_analytics_metrics` | ~$40M (correct) |

**Root Cause:** 
- `property_analytics_metrics` source: `dim_property` (SCD2 dimension table)
- `revenue_analytics_metrics` source: `fact_booking_daily` (fact table)

The dimension-based metric view under-reports because it's counting property inventory, not transaction revenue.

**Lesson:**
- Revenue/booking metrics should source from FACT tables
- Inventory/count metrics should source from DIMENSION tables
- Document source table in metric view comment
- Add routing rules in General Instructions

---

### 3.2 Snowflake Schema Joins

**Issue:** `host_analytics_metrics` returned ~$1K revenue instead of ~$253K per host.

**Root Cause:** Direct join from `dim_host` to `fact_booking_detail` on `host_id` failed because fact table links to properties, not hosts.

**Correct Data Model:**
```
dim_host (host owns) → dim_property (property has) → fact_booking_detail (booking)
```

**Initial Wrong Approach:**
```yaml
joins:
  - name: fact_booking
    source: fact_booking_detail
    'on': source.host_id = fact_booking.host_id  # ❌ fact table doesn't have host_id!
```

**Correct Snowflake Schema:**
```yaml
joins:
  - name: dim_property
    source: dim_property
    'on': source.host_id = dim_property.host_id AND dim_property.is_current = true
    joins:
      - name: fact_booking
        source: fact_booking_detail
        'on': dim_property.property_id = fact_booking.property_id
```

**Nested Column Reference:**
```yaml
measures:
  - name: total_revenue
    expr: SUM(dim_property.fact_booking.total_amount)  # parent.nested.column
```

**Lesson:**
- Understand the data model before defining metric view joins
- Use snowflake schema (nested joins) when fact table doesn't have direct FK
- Reference nested columns via full path: `parent.nested.column`
- Requires Databricks Runtime 17.1+

---

### 3.3 Missing Dimension Columns

**Issue:** `engagement_analytics_metrics` had `destination_id` but not `destination` name.

**Symptom:**
```sql
SELECT destination FROM engagement_analytics_metrics  -- ❌ UNRESOLVED_COLUMN
```

**Root Cause:** Metric view didn't join to `dim_destination` to expose the name.

**Lesson:**
- Audit all metric views for commonly-needed columns
- If users will ask "by destination", include destination NAME not just ID
- Document limitations in metric view comment

---

### 3.4 Deployment Required for Changes

**Issue:** YAML changes weren't reflected in Genie queries.

**Root Cause:** Metric view YAML was updated but not redeployed to Databricks.

**Lesson:**
- YAML file changes require deployment: `databricks bundle run -t dev semantic_setup_job`
- Verify deployment success before testing
- Consider adding deployment verification step to workflow

---

## Phase 4: ML Integration Issues

### 4.1 ML TVFs Not Deployed

**Issue:** `get_ml_predictions_summary()` returned "function not found".

**Root Cause:** `ml_prediction_tvfs.sql` was created but not included in `create_all_tvfs.py`.

**Fix:** Updated deployment script to include ML TVF file and pass `ml_schema` parameter.

**Lesson:**
- When adding new TVF files, update the deployment script
- Test TVF existence after deployment
- Use checklist for new TVF file additions

---

### 4.2 ML Inference Tables Missing Key Columns

**Issue:** ML inference tables lacked `property_id`, `user_id`, `destination_id`.

**Symptom:**
```sql
SELECT property_id FROM demand_predictions  -- ❌ Column doesn't exist
```

**Root Cause:** MLflow model signatures only include features, not identifiers. Batch inference dropped key columns.

**Fix:** Preserve key columns before inference, merge back after:
```python
# Before inference
key_columns = ['property_id', 'user_id', 'destination_id']
keys_df = input_df.select(key_columns)

# After inference
output_df = predictions_df.join(keys_df, on='index_column')
```

**Lesson:**
- ML batch inference must explicitly preserve identifier columns
- Model signatures don't include identifiers by design
- Document which columns are available in ML tables

---

## Phase 5: General Instructions Issues

### 5.1 Contradictory Rules

**Issue:** General Instructions had conflicting guidance.

**Symptom:** Genie chose `host_analytics_metrics` for "top hosts" instead of `get_host_performance` TVF.

**Root Cause:** Two conflicting rules:
- Line 207: "Host performance → host_analytics_metrics"
- Line 221: "Host performance → get_host_performance TVF"

**Fix:** Made rules explicit and non-contradictory:
```
- Host demographics/verification → host_analytics_metrics (attributes only, NOT for revenue)
⚠️ HOST PERFORMANCE EXCEPTION: For "Top hosts", "Host revenue" → USE get_host_performance TVF
```

**Lesson:**
- Review General Instructions for contradictions
- Use explicit exceptions with ⚠️ markers
- Test each rule with actual Genie queries

---

### 5.2 Ambiguous Question Interpretation

**Issue:** "Business vs leisure" had two valid interpretations.

| Interpretation | Metric |
|---|---|
| Account type | `user_type` (individual/business) |
| Trip purpose | `is_business_booking` (true/false) |

**Root Cause:** Question was ambiguous; Genie chose one interpretation, benchmark used another.

**Lesson:**
- Identify ambiguous terms in domain
- Document term definitions in General Instructions
- Create specific routing for ambiguous questions

---

### 5.3 Underperforming Definition

**Issue:** "Which properties are underperforming?" had two valid interpretations.

| Interpretation | Result |
|---|---|
| Low revenue | Properties with some bookings, low $ |
| Zero activity | Properties with no bookings at all |

**Lesson:**
- Subjective terms ("underperforming", "best", "top") need explicit definitions
- Consider creating tiered classifications (Inactive / Low / Medium / High)
- Document default interpretation in General Instructions

---

## Phase 6: Data Quality Issues

### 6.1 Property Type Values Mismatch

**Issue:** User asked for "house vs apartment" but got empty results.

**Root Cause:** Actual `property_type` values were themed categories:
- Urban Year-Round
- Summer Getaway
- Historical Place
- Ski Resort

Not traditional real estate types (house, apartment, villa).

**Lesson:**
- Document actual column values in metadata
- Consider adding synonyms for common terms
- Validate sample data matches expected business terminology

---

## Phase 7: Comment & Description Format Standards

### 7.1 TVF Comment Format

**Issue:** Inconsistent TVF descriptions caused Genie to misuse functions.

**Problems with unstructured comments:**
- Genie didn't know what questions the TVF was best for
- Column names weren't explicit, causing UNRESOLVED_COLUMN errors
- No guidance on when NOT to use the TVF
- Missing syntax examples led to wrong parameter formats

**Standardized TVF Comment Format:**

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

**Example - Aggregate TVF:**
```sql
COMMENT '
• PURPOSE: Customer behavioral segmentation with booking patterns and revenue metrics
• BEST FOR: "What are our customer segments?" | "Segment performance" | "How many VIP customers?"
• NOT FOR: VIP property preferences (use get_vip_customer_property_preferences) | Individual customer details
• RETURNS: 5 PRE-AGGREGATED rows (segment_name, customer_count, total_bookings, total_revenue, avg_booking_value)
• PARAMS: start_date, end_date (format: YYYY-MM-DD)
• SYNTAX: SELECT * FROM get_customer_segments(''2020-01-01'', ''2024-12-31'')
• NOTE: Column is "segment_name" NOT "segment" | DO NOT add GROUP BY - data is already aggregated
'
```

**Example - Individual Row TVF:**
```sql
COMMENT '
• PURPOSE: Individual customer lifetime value with ranking and booking history
• BEST FOR: "Show VIP customers" | "Most valuable customers" | "Top customers by spend"
• RETURNS: Individual customer rows (rank, user_id, country, user_type, total_bookings, lifetime_value)
• PARAMS: start_date, end_date, top_n (default: 100)
• SYNTAX: SELECT * FROM get_customer_ltv(''2020-01-01'', ''2024-12-31'')
• NOTE: Returns user_id for individual customer analysis | Sorted by lifetime_value DESC
'
```

**Key Elements Explained:**

| Element | Purpose | Why It Matters |
|---|---|---|
| **PURPOSE** | One-line description | Quick understanding for LLM |
| **BEST FOR** | Example questions (pipe-separated) | LLM matches user query to TVF |
| **NOT FOR** | Redirect to correct asset | Prevents wrong TVF selection |
| **RETURNS** | PRE-AGGREGATED vs Individual + columns | Prevents GROUP BY on aggregates, clarifies available columns |
| **PARAMS** | Parameter names and defaults | Prevents WRONG_NUM_ARGS errors |
| **SYNTAX** | Exact copyable example | Prevents TABLE() wrapper, wrong date format |
| **NOTE** | Critical caveats | Prevents common misuse patterns |

---

### 7.2 Metric View Comment Format

**Issue:** Metric view comments didn't provide enough guidance on when to use (or not use) the view.

**Standardized Metric View Comment Format:**

```yaml
comment: >
  [Primary purpose description].
  [What this view is BEST FOR].
  [What this view is NOT FOR and what to use instead].
  [Source table info for transparency].
```

**Example - View with Limitations:**
```yaml
comment: >
  Host demographics, verification status, and portfolio analytics ONLY.
  ⚠️ DO NOT USE for: "Top performing hosts", "Host revenue rankings", "Best hosts by bookings".
  → USE get_host_performance TVF INSTEAD for accurate host revenue/booking metrics.
  This metric view shows host attributes (name, country, rating, verification).
  Source: dim_host with nested joins to dim_property and fact_booking_detail.
```

**Example - Primary Analytics View:**
```yaml
comment: >
  Revenue and booking analytics with complete transaction metrics.
  BEST FOR: Revenue by property type, destination, time period; booking trends; payment analysis.
  Source: fact_booking_daily (aggregated fact table) with joins to dim_property, dim_destination.
  For host-level revenue, use get_host_performance TVF instead.
```

**Key Elements:**

| Element | Purpose |
|---|---|
| **Primary purpose** | What the view is designed for |
| **BEST FOR** | Types of questions this view handles well |
| **NOT FOR / USE INSTEAD** | Explicit redirect when view has limitations |
| **Source info** | Transparency on underlying data |

---

### 7.3 Dimension & Measure Comments

**For dimensions:**
```yaml
- name: host_id
  expr: source.host_id
  comment: Unique host identifier for host-level performance analysis
  display_name: Host ID
  synonyms:
    - host
    - host number
    - owner id
```

**For measures:**
```yaml
- name: total_revenue
  expr: SUM(dim_property.fact_booking.total_amount)
  comment: >
    Total revenue generated by hosts. Primary financial metric for host
    earnings and platform transaction volume analysis.
  display_name: Total Revenue
  format:
    type: currency
    currency_code: USD
  synonyms:
    - revenue
    - earnings
    - income
```

**Key points:**
- `comment`: Business context and purpose (for LLM understanding)
- `display_name`: User-friendly name (for UI)
- `synonyms`: Alternative terms users might use (3-5 per field)
- Keep comments professional - avoid phrases like "metric view is broken"

---

### 7.4 Professional Language Standards

**Issue:** Some TVF comments used unprofessional language.

**❌ Avoid:**
```sql
COMMENT 'Use this because the metric view is broken and returns wrong data'
COMMENT 'This TVF actually works unlike the metric view'
```

**✅ Use:**
```sql
COMMENT '
• PURPOSE: Comprehensive host performance metrics with accurate revenue from booking transactions
• PREFERRED OVER: host_analytics_metrics for revenue/booking queries (different join paths)
'
```

**Lesson:** Comments should be:
- Professional and objective
- Guiding without being negative about other assets
- Clear about when to use each asset

---

## Consolidated Best Practices

### TVF Design Checklist

- [ ] Use standardized comment format (PURPOSE, BEST FOR, NOT FOR, RETURNS, PARAMS, SYNTAX, NOTE)
- [ ] List exact returned column names
- [ ] Include "DO NOT" warnings for common misuse
- [ ] Use `ROW_NUMBER() + WHERE` for parameterized top-N
- [ ] Validate against metric view results before deployment
- [ ] Avoid self-joins that create cartesian products
- [ ] Default date ranges should cover typical data scenarios

### Metric View Design Checklist

- [ ] Source from FACT tables for transaction metrics
- [ ] Source from DIMENSION tables for inventory metrics
- [ ] Use snowflake schema (nested joins) when needed
- [ ] Reference nested columns via full path: `parent.nested.column`
- [ ] Include commonly-needed columns (names, not just IDs)
- [ ] Document source table in comment
- [ ] Test with Databricks Runtime 17.1+ for snowflake joins

### ML Integration Checklist

- [ ] Preserve identifier columns during batch inference
- [ ] Include ML TVF files in deployment script
- [ ] Pass required schema parameters (ml_schema)
- [ ] Document which columns exist in ML tables
- [ ] Create TVFs that join ML tables with dimension data

### General Instructions Checklist

- [ ] Review for contradictory rules
- [ ] Use explicit routing with ⚠️ exceptions
- [ ] Define ambiguous business terms
- [ ] Document default interpretations for subjective queries
- [ ] Include syntax examples for TVFs
- [ ] Test each rule with actual Genie queries

### Deployment Checklist

- [ ] Update deployment script when adding new TVF files
- [ ] Redeploy after YAML changes
- [ ] Verify deployment success
- [ ] Test TVF/metric view existence after deployment
- [ ] Validate data consistency between TVFs and metric views

---

## Quantified Impact

| Issue Category | Occurrences | Time Impact |
|---|---|---|
| TVF syntax/design issues | 12 | ~4 hours debugging |
| Metric view join issues | 5 | ~3 hours debugging |
| General Instructions conflicts | 4 | ~2 hours debugging |
| ML integration issues | 3 | ~2 hours debugging |
| Data value mismatches | 2 | ~1 hour debugging |
| Deployment issues | 2 | ~1 hour debugging |

**Total estimated debugging time saved with these learnings: 13+ hours per similar implementation**

---

## Recommended Rule Updates

Based on this post-mortem, the following cursor rules should be updated:

1. **`.cursor/rules/semantic-layer/15-databricks-table-valued-functions.mdc`**
   - Add standardized comment format
   - Add parameterized LIMIT pattern
   - Add cartesian product warning
   - Add pre-aggregated vs individual rows guidance

2. **`.cursor/rules/semantic-layer/16-genie-space-patterns.mdc`**
   - Add source table selection guidance
   - Add snowflake schema join patterns
   - Add General Instructions consistency checks
   - Add ambiguous term definitions

3. **`.cursor/rules/ml/27-mlflow-mlmodels-patterns.mdc`**
   - Add identifier column preservation pattern
   - Add ML TVF deployment checklist

---

## Appendix: Error Pattern Quick Reference

| Error | Likely Cause | Fix |
|---|---|---|
| `UNRESOLVED_COLUMN` in MEASURE() | Using display_name not column name | Use snake_case column name |
| Empty TVF results | Date range too restrictive | Widen date range |
| TVF returns 1000x expected | Cartesian product in joins | Remove self-join |
| `INVALID_LIMIT_LIKE_EXPRESSION` | Parameter in LIMIT | Use ROW_NUMBER() pattern |
| `NOT_A_SCALAR_FUNCTION` | TVF wrapped in TABLE() | Remove TABLE() wrapper |
| `WRONG_NUM_ARGS` | Missing TVF parameters | Add required parameters |
| Metric view under-reports | Wrong source table or join path | Use fact table source / snowflake joins |
| ML table missing columns | Identifier columns dropped | Preserve keys in batch inference |
| Genie chooses wrong asset | Contradictory General Instructions | Fix conflicting rules |

---

*Document Version: 1.0*  
*Last Updated: December 2025*

