---
name: naming-tagging-standards
description: Enforces enterprise naming conventions (snake_case, table prefixes, approved abbreviations), dual-purpose COMMENT formats for tables/columns/TVFs/metric views, and tagging standards (workflow tags, UC governed tags, serverless budget policies). Use when creating tables, columns, constraints, functions, jobs, pipelines, metric views, applying COMMENTs, applying tags, or reviewing code for standards compliance. Triggers on "naming", "comment", "COMMENT", "tag", "PII", "cost_center", "snake_case", "dim_", "fact_", "governed tag", "budget policy".
metadata:
  author: prashanth subrahmanyam
  version: "1.0"
  domain: common
  role: shared
  used_by_stages: [1, 2, 3, 4, 5, 6, 7, 8, 9]
  called_by:
    - gold/00-gold-layer-design
    - bronze/00-bronze-layer-setup
    - silver/00-silver-layer-setup
    - gold/01-gold-layer-setup
    - planning/00-project-planning
    - semantic-layer/00-semantic-layer-setup
    - monitoring/00-observability-setup
    - ml/00-ml-pipeline-setup
    - genai-agents/00-genai-agents-setup
  last_verified: "2026-02-07"
  volatility: low
---

# Naming, Comment & Tagging Standards

Enterprise-wide standards for Databricks asset naming, SQL comments, and cost/governance tagging.

## Golden Rules

| ID | Rule | Severity |
|----|------|----------|
| **NC-01** | All object names use `snake_case` | Critical |
| **NC-02** | Tables prefixed by layer (`bronze_`, `silver_`) or entity type (`dim_`, `fact_`) | Critical |
| **NC-03** | No abbreviations except approved list | Required |
| **CM-01** | SQL block comments (`/* */`) for all DDL operations | Required |
| **CM-02** | Table COMMENT follows dual-purpose format | Critical |
| **CM-03** | Column COMMENT required for all columns | Critical |
| **CM-04** | TVF COMMENT follows v3.0 structured format | Critical |
| **TG-01** | All workflows must have required tags (`team`, `cost_center`, `environment`) | Critical |
| **TG-02** | Use Governed Tags for UC securables | Critical |
| **TG-03** | Serverless resources must use approved budget policies | Critical |

---

## Part 1: Naming Conventions

### Object Naming Patterns

| Object | Format | Example |
|--------|--------|---------|
| Catalog | `{env}_{domain}_catalog` | `prod_sales_catalog` |
| Schema | `{layer}` or `{domain}_{layer}` | `bronze`, `sales_gold` |
| Table | `{prefix}_{entity}` | `dim_customer`, `fact_orders` |
| Column | `{descriptive_name}` | `customer_id`, `order_date` |
| Constraint | `{type}_{table}[_{column}]` | `pk_dim_customer`, `fk_orders_customer` |
| Function | `get_{entity}_{action}` | `get_daily_sales` |
| Job | `[${bundle.target}] {Domain} - {Action} {Entity}` | `[dev] Sales - Merge Orders` |
| Pipeline | `[${bundle.target}] {Layer} {Domain} Pipeline` | `[dev] Silver Sales Pipeline` |

**Never use:** `camelCase`, `PascalCase`, `SCREAMING_CASE`, `kebab-case`, or spaces.

### Table Prefixes

| Layer/Type | Prefix | Example |
|------------|--------|---------|
| Bronze | `bronze_` | `bronze_raw_orders` |
| Silver | `silver_` | `silver_orders` |
| Gold Dimension | `dim_` | `dim_customer` |
| Gold Fact | `fact_` | `fact_sales` |
| Bridge | `bridge_` | `bridge_customer_product` |
| Aggregate | `agg_` | `agg_daily_sales` |
| Staging | `stg_` | `stg_customer_updates` |
| Quarantine | `_quarantine` suffix | `silver_orders_quarantine` |
| History | `_history` suffix | `dim_customer_history` |

### Approved Abbreviations (Use ONLY These)

`id`, `ts`, `dt`, `amt`, `qty`, `pct`, `num`, `cnt`, `avg`, `min`, `max`, `pk`, `fk`, `dim`, `fact`, `agg`, `stg`

**Forbidden:** `cust`, `prod`, `inv`, `trans`, `ord`, `emp` -- spell these out.

### Column Patterns

| Pattern | Format | Example |
|---------|--------|---------|
| Primary Key | `{entity}_id` or `{entity}_key` | `customer_id`, `store_key` |
| Foreign Key | Same as referenced PK | `customer_id` |
| Business Key | `{entity}_{identifier}` | `customer_number` |
| Surrogate Key | `{entity}_key` | `customer_key` (MD5) |
| Date | `{event}_date` | `order_date` |
| Timestamp | `{event}_timestamp` or `{event}_ts` | `created_ts` |
| Boolean | `is_{condition}` or `has_{thing}` | `is_active`, `has_discount` |
| Amount | `{type}_amount` or `{type}_amt` | `total_amount` |
| Count | `{thing}_count` or `{thing}_cnt` | `order_count` |
| SCD2 | `effective_from`, `effective_to`, `is_current` | Standard names |

For detailed naming examples, see [references/naming-conventions.md](references/naming-conventions.md).

---

## Part 2: Comment Conventions

### CM-01: SQL Block Comments

All DDL must include `/* */` block comments with purpose, grain, and source:

```sql
/*
 * Table: dim_customer
 * Layer: Gold | Domain: Sales
 * Grain: One row per customer per effective period.
 * Source: Silver layer silver_customers table.
 */
```

### CM-02: Table COMMENT (Dual-Purpose Format)

```
[One-line description]. Business: [use cases, consumers]. Technical: [grain, source, update frequency].
```

Examples:

```sql
-- Gold Dimension
COMMENT ON TABLE gold.dim_customer IS
'Customer dimension with SCD Type 2 history tracking. Business: Primary customer reference for segmentation and cohort analysis. Technical: MD5 surrogate key, is_current flag, daily merge from Silver.';

-- Gold Fact
COMMENT ON TABLE gold.fact_orders IS
'Daily order facts at customer-product-day grain. Business: Primary source for revenue reporting and sales dashboards. Technical: Composite PK, incremental merge, CDF enabled.';
```

### CM-03: Column COMMENT (Dual-Purpose Format)

```
[Brief definition]. Business: [how it's used]. Technical: [data type notes, source, calculation].
```

```sql
customer_key STRING NOT NULL
COMMENT 'Surrogate key for SCD Type 2 versioning. Business: Used for joining fact tables. Technical: MD5 hash of customer_id + effective_from.';

total_amount DECIMAL(18,2)
COMMENT 'Total order amount after discounts in USD. Business: Primary revenue metric. Technical: SUM(quantity * unit_price * (1 - discount_pct)).';
```

### CM-04: TVF COMMENT (v3.0 Structured Format)

```sql
COMMENT '
• PURPOSE: [One-line description of what the function returns].
• BEST FOR: [Query type 1] | [Query type 2] | [Query type 3]
• NOT FOR: [What to use instead] (use [alternative] instead)
• RETURNS: [PRE-AGGREGATED or DETAIL rows]
• PARAMS: [param1 (format)], [param2 (format)]
• SYNTAX: SELECT * FROM function_name(''param1'', ''param2'')
• NOTE: [Critical usage notes]
'
```

### Metric View COMMENT Format (YAML)

```yaml
comment: >
  PURPOSE: Cost analytics for billing analysis.
  BEST FOR: Total spend by workspace | Cost by SKU | Daily trends
  NOT FOR: Commit tracking (use commit_tracking) | Real-time alerts (use TVF)
  DIMENSIONS: usage_date, workspace_name, sku_name
  MEASURES: total_cost, total_dbus, tag_coverage_pct
  SOURCE: fact_usage (billing domain)
  JOINS: dim_workspace, dim_sku
  NOTE: Costs are list prices. Actual billed amounts may differ.
```

For complete comment examples, see [references/comment-templates.md](references/comment-templates.md).

---

## Part 3: Tagging Standards

### TG-01: Workflow Tags (Asset Bundles)

All jobs and pipelines **must** include:

| Tag | Required | Example |
|-----|----------|---------|
| `team` | Yes | `data-engineering` |
| `cost_center` | Yes | `CC-1234` |
| `environment` | Yes | `${bundle.target}` |
| `project` | Recommended | `customer-360` |
| `layer` | Recommended | `gold` |
| `job_type` | Recommended | `merge`, `setup`, `pipeline` |

```yaml
resources:
  jobs:
    gold_merge_job:
      tags:
        team: data-engineering
        cost_center: CC-1234
        environment: ${bundle.target}
        project: customer-360
        layer: gold
        job_type: merge
```

### TG-02: Unity Catalog Governed Tags

| Tag | Apply To | Allowed Values |
|-----|----------|----------------|
| `cost_center` | Catalogs | Organization codes |
| `business_unit` | Catalogs | Department names |
| `data_owner` | Schemas | Email or team name |
| `data_classification` | Tables | `public`, `internal`, `confidential`, `restricted` |
| `pii` | Columns | `true`, `false` |
| `pii_type` | Columns | `email`, `phone`, `ssn`, `name`, `address`, `dob`, `financial` |

```sql
-- Catalog
ALTER CATALOG sales_data SET TAGS ('cost_center' = 'CC-1234', 'business_unit' = 'Sales');
-- Schema
ALTER SCHEMA sales_data.gold SET TAGS ('data_owner' = 'analytics-team@company.com');
-- Table
ALTER TABLE gold.dim_customer SET TAGS ('data_classification' = 'confidential');
-- Column PII
ALTER TABLE gold.dim_customer ALTER COLUMN email SET TAGS ('pii' = 'true', 'pii_type' = 'email');
```

### TG-03: Serverless Budget Policies

Serverless compute resources require budget policies with `team`, `cost_center`, and `environment` tags.

For tag query patterns and serverless cost attribution, see [references/tagging-patterns.md](references/tagging-patterns.md).

---

## Validation Checklist

### Naming
- [ ] All objects use `snake_case`
- [ ] Tables have correct prefix (`dim_`, `fact_`, `bronze_`, `silver_`)
- [ ] Only approved abbreviations used
- [ ] Columns follow standard patterns (PK, FK, boolean, SCD2)
- [ ] Jobs/pipelines follow naming format

### Comments
- [ ] DDL includes `/* */` block comments
- [ ] All tables have dual-purpose COMMENT
- [ ] All columns have dual-purpose COMMENT
- [ ] TVFs have v3.0 structured COMMENT
- [ ] Metric views have structured comment in YAML

### Tags
- [ ] All jobs have `team`, `cost_center`, `environment` tags
- [ ] All pipelines have required tags
- [ ] Catalogs tagged with `cost_center` and `business_unit`
- [ ] Schemas tagged with `data_owner`
- [ ] Confidential tables tagged with `data_classification`
- [ ] PII columns tagged with `pii` and `pii_type`

---

## Additional Resources

- For detailed naming conventions and forbidden patterns, see [references/naming-conventions.md](references/naming-conventions.md)
- For complete comment templates with examples, see [references/comment-templates.md](references/comment-templates.md)
- For tagging patterns and cost query SQL, see [references/tagging-patterns.md](references/tagging-patterns.md)
