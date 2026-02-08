# Tagging Standards

> **Document Owner:** Platform Architecture Team | **Status:** Approved | **Last Updated:** February 2026

## Overview

This document establishes enterprise-wide tagging standards for cost allocation, governance compliance, and operational visibility. Tags apply to:

- **Unity Catalog Securables** — Governed tags for catalogs, schemas, tables, and columns
- **Workflows** — Asset Bundle tags for jobs and pipelines
- **Serverless Compute** — Budget policies for notebooks, jobs, and model serving

---

## Golden Rules

| ID | Rule | Severity |
|----|------|----------|
| **TG-01** | All workflows (jobs, pipelines) must have required tags | Critical |
| **TG-02** | Use Governed Tags for UC securables (showback/chargeback) | Critical |
| **TG-03** | Serverless resources must use approved budget policies | Critical |

---

## TG-01: Workflow Tags

All jobs and pipelines defined in Asset Bundles must include tags for cost allocation and operational tracking.

### Required Tags

| Tag | Required | Values | Description |
|-----|----------|--------|-------------|
| `team` | Yes | Team name | Owning team for cost allocation |
| `cost_center` | Yes | CC-XXXX | Finance cost center code |
| `environment` | Yes | `dev`, `staging`, `prod` | Deployment environment |
| `project` | Recommended | Project name | Project or initiative name |
| `layer` | Recommended | `bronze`, `silver`, `gold` | Data layer |
| `job_type` | Recommended | `setup`, `pipeline`, `merge`, `ml` | Workload category |

### Job Tags Example

```yaml
resources:
  jobs:
    gold_merge_job:
      name: "[${bundle.target}] Gold Merge Job"
      tags:
        team: data-engineering
        cost_center: CC-1234
        environment: ${bundle.target}
        project: customer-360
        layer: gold
        job_type: merge
```

### Pipeline Tags Example

```yaml
resources:
  pipelines:
    silver_pipeline:
      name: "[${bundle.target}] Silver Pipeline"
      tags:
        team: data-engineering
        cost_center: CC-1234
        environment: ${bundle.target}
        project: customer-360
        layer: silver
        pipeline_type: streaming
```

### Querying Workflow Costs

```sql
SELECT 
    usage_date,
    custom_tags:team AS team,
    custom_tags:cost_center AS cost_center,
    custom_tags:project AS project,
    SUM(list_cost) AS total_cost
FROM system.billing.usage
WHERE custom_tags:team IS NOT NULL
GROUP BY 1, 2, 3, 4
ORDER BY total_cost DESC;
```

---

## TG-02: Unity Catalog Governed Tags

Governed Tags are account-level tags with enforced allowed values, ensuring consistent metadata across all workspaces.

### Required Governed Tags

| Tag | Apply To | Allowed Values | Purpose |
|-----|----------|----------------|---------|
| `cost_center` | Catalogs | Organization codes | Financial allocation |
| `business_unit` | Catalogs | Department names | Organizational grouping |
| `data_owner` | Schemas | Email or team name | Accountability |
| `data_classification` | Tables | `public`, `internal`, `confidential`, `restricted` | Security level |
| `pii` | Columns | `true`, `false` | PII indicator |
| `pii_type` | Columns | `email`, `phone`, `ssn`, `name`, `address`, `dob`, `financial` | PII categorization |

### Applying Tags by Level

**Catalog-level:**
```sql
ALTER CATALOG sales_data SET TAGS ('cost_center' = 'CC-1234');
ALTER CATALOG sales_data SET TAGS ('business_unit' = 'Sales');
```

**Schema-level:**
```sql
ALTER SCHEMA sales_data.gold SET TAGS ('data_owner' = 'analytics-team@company.com');
```

**Table-level:**
```sql
ALTER TABLE gold.dim_customer SET TAGS ('data_classification' = 'confidential');
```

**Column-level (PII):**
```sql
ALTER TABLE gold.dim_customer
ALTER COLUMN email SET TAGS ('pii' = 'true', 'pii_type' = 'email');

ALTER TABLE gold.dim_customer
ALTER COLUMN phone SET TAGS ('pii' = 'true', 'pii_type' = 'phone');

ALTER TABLE gold.dim_customer
ALTER COLUMN ssn SET TAGS ('pii' = 'true', 'pii_type' = 'ssn');
```

### Governed vs User-Defined Tags

| Feature | Governed Tags | User-Defined Tags |
|---------|---------------|-------------------|
| Policy enforcement | Required | Optional |
| Predefined values | Enforced | Any value |
| Permission control | ASSIGN permission | Any user with MANAGE |
| Inheritance | To children | Manual only |
| Cross-workspace consistency | Account-level | Workspace-specific |

### Tag Inheritance

Governed tags inherit from parent to child objects:

```
Catalog (cost_center = CC-1234)
  └── Schema (inherits cost_center)
        └── Table (inherits cost_center)
              └── Column (inherits cost_center)
```

### PII Type Reference

| Type | Description | Column Examples |
|------|-------------|-----------------|
| `email` | Email addresses | customer_email, contact_email |
| `phone` | Phone numbers | mobile_phone, work_phone |
| `ssn` | Social security numbers | ssn, tax_id |
| `name` | Full or partial names | customer_name, first_name |
| `address` | Physical addresses | street_address, mailing_address |
| `dob` | Date of birth | birth_date, dob |
| `financial` | Financial account numbers | account_number, credit_card |

### Querying Governed Tags

**Find all PII columns:**
```sql
SELECT 
    table_catalog,
    table_schema,
    table_name,
    column_name,
    tag_value AS pii_type
FROM system.information_schema.column_tags
WHERE tag_name = 'pii_type';
```

**Tables by classification:**
```sql
SELECT 
    table_catalog,
    table_schema,
    table_name,
    tag_value AS data_classification
FROM system.information_schema.table_tags
WHERE tag_name = 'data_classification';
```

**Cost centers by catalog:**
```sql
SELECT 
    catalog_name,
    tag_value AS cost_center
FROM system.information_schema.catalog_tags
WHERE tag_name = 'cost_center';
```

---

## TG-03: Serverless Budget Policies

Serverless compute (notebooks, jobs, pipelines, model serving) uses budget policies for cost allocation and governance.

### Setting Up Budget Policies

1. Navigate to **Settings** → **Compute** → **Serverless budget policies**
2. Create policy with required tags (team, cost_center, environment)
3. Assign **User** or **Manager** permission to groups
4. Users select policy when creating serverless resources

### Budget Policy Tags

Budget policies should enforce:

| Tag | Required | Description |
|-----|----------|-------------|
| `team` | Yes | Team name for cost allocation |
| `cost_center` | Yes | Finance cost center code |
| `environment` | Yes | dev, staging, or prod |
| `project` | Recommended | Project or initiative |

### Querying Serverless Costs

```sql
SELECT 
    usage_date,
    sku_name,
    custom_tags:team AS team,
    custom_tags:cost_center AS cost_center,
    SUM(list_cost) AS total_cost
FROM system.billing.usage
WHERE sku_name LIKE '%SERVERLESS%'
  AND custom_tags:cost_center IS NOT NULL
GROUP BY 1, 2, 3, 4
ORDER BY usage_date DESC, total_cost DESC;
```

---

## Validation Checklist

### Workflow Tags
- [ ] All jobs have `team` tag
- [ ] All jobs have `cost_center` tag
- [ ] All jobs have `environment` tag (using `${bundle.target}`)
- [ ] All pipelines have required tags

### Governed Tags
- [ ] Catalogs tagged with `cost_center` and `business_unit`
- [ ] Schemas tagged with `data_owner`
- [ ] Confidential tables tagged with `data_classification`
- [ ] All PII columns tagged with `pii = true`
- [ ] All PII columns tagged with `pii_type`

### Serverless Budget Policies
- [ ] Budget policies created for each team/cost center
- [ ] Required tags enforced in policy
- [ ] Teams assigned appropriate permissions
- [ ] Policy selection required for serverless resources

---

## Quick Reference

### Required Tags by Context

| Context | Required Tags |
|---------|---------------|
| **Jobs (Asset Bundle)** | `team`, `cost_center`, `environment` |
| **Pipelines (Asset Bundle)** | `team`, `cost_center`, `environment` |
| **Catalogs (Governed)** | `cost_center`, `business_unit` |
| **Schemas (Governed)** | `data_owner` |
| **Tables (Governed)** | `data_classification` (if confidential/restricted) |
| **Columns (Governed)** | `pii`, `pii_type` (if contains PII) |
| **Serverless (Budget Policy)** | `team`, `cost_center`, `environment` |

### Tag Query Patterns

```sql
-- Cost by team (all compute)
SELECT custom_tags:team, SUM(list_cost) 
FROM system.billing.usage 
GROUP BY 1;

-- PII column inventory
SELECT * FROM system.information_schema.column_tags 
WHERE tag_name = 'pii';

-- Tables by classification
SELECT * FROM system.information_schema.table_tags 
WHERE tag_name = 'data_classification';

-- Serverless cost by budget policy
SELECT custom_tags:cost_center, SUM(list_cost)
FROM system.billing.usage
WHERE sku_name LIKE '%SERVERLESS%'
GROUP BY 1;
```

---

## Related Documents

- [Data Governance](01-data-governance.md)
- [Naming & Comment Standards](05-naming-comment-standards.md)
- [Data Quality Standards](07-data-quality-standards.md)
- [Unity Catalog Tables](../platform-architecture/12-unity-catalog-tables.md)
- [Cluster Policies](../platform-architecture/13-cluster-policies.md)

---

## References

- [Unity Catalog Governed Tags](https://docs.databricks.com/en/data-governance/unity-catalog/tags.html)
- [Usage Attribution Tags](https://docs.databricks.com/en/admin/account-settings/usage-detail-tags.html)
- [Serverless Budget Policies](https://docs.databricks.com/en/admin/usage/serverless-budget-policies.html)
