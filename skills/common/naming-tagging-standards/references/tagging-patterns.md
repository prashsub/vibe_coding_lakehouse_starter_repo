# Tagging Patterns Reference

Detailed tagging standards for cost allocation, governance, and operational visibility.

## Workflow Tags (Asset Bundles)

### Required Tags

| Tag | Required | Values | Description |
|-----|----------|--------|-------------|
| `team` | Yes | Team name | Owning team for cost allocation |
| `cost_center` | Yes | CC-XXXX | Finance cost center code |
| `environment` | Yes | `dev`, `staging`, `prod` | Deployment environment |
| `project` | Recommended | Project name | Project or initiative |
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

---

## Unity Catalog Governed Tags

### Required Tags by Level

| Tag | Apply To | Allowed Values | Purpose |
|-----|----------|----------------|---------|
| `cost_center` | Catalogs | Organization codes | Financial allocation |
| `business_unit` | Catalogs | Department names | Organizational grouping |
| `data_owner` | Schemas | Email or team name | Accountability |
| `data_classification` | Tables | `public`, `internal`, `confidential`, `restricted` | Security level |
| `pii` | Columns | `true`, `false` | PII indicator |
| `pii_type` | Columns | `email`, `phone`, `ssn`, `name`, `address`, `dob`, `financial` | PII categorization |

### Applying Tags

```sql
-- Catalog-level
ALTER CATALOG sales_data SET TAGS ('cost_center' = 'CC-1234');
ALTER CATALOG sales_data SET TAGS ('business_unit' = 'Sales');

-- Schema-level
ALTER SCHEMA sales_data.gold SET TAGS ('data_owner' = 'analytics-team@company.com');

-- Table-level
ALTER TABLE gold.dim_customer SET TAGS ('data_classification' = 'confidential');

-- Column-level (PII)
ALTER TABLE gold.dim_customer
ALTER COLUMN email SET TAGS ('pii' = 'true', 'pii_type' = 'email');

ALTER TABLE gold.dim_customer
ALTER COLUMN phone SET TAGS ('pii' = 'true', 'pii_type' = 'phone');

ALTER TABLE gold.dim_customer
ALTER COLUMN ssn SET TAGS ('pii' = 'true', 'pii_type' = 'ssn');
```

### Tag Inheritance

Governed tags inherit from parent to child:

```
Catalog (cost_center = CC-1234)
  └── Schema (inherits cost_center)
        └── Table (inherits cost_center)
              └── Column (inherits cost_center)
```

### Governed vs User-Defined Tags

| Feature | Governed Tags | User-Defined Tags |
|---------|---------------|-------------------|
| Policy enforcement | Required | Optional |
| Predefined values | Enforced | Any value |
| Permission control | ASSIGN permission | MANAGE permission |
| Inheritance | To children | Manual only |
| Cross-workspace | Account-level | Workspace-specific |

### PII Type Reference

| Type | Description | Column Examples |
|------|-------------|-----------------|
| `email` | Email addresses | `customer_email`, `contact_email` |
| `phone` | Phone numbers | `mobile_phone`, `work_phone` |
| `ssn` | Social security numbers | `ssn`, `tax_id` |
| `name` | Full or partial names | `customer_name`, `first_name` |
| `address` | Physical addresses | `street_address`, `mailing_address` |
| `dob` | Date of birth | `birth_date`, `dob` |
| `financial` | Financial account numbers | `account_number`, `credit_card` |

---

## Serverless Budget Policies

### Setup Steps

1. Navigate to **Settings** > **Compute** > **Serverless budget policies**
2. Create policy with required tags (`team`, `cost_center`, `environment`)
3. Assign **User** or **Manager** permission to groups
4. Users select policy when creating serverless resources

### Required Tags

| Tag | Required | Description |
|-----|----------|-------------|
| `team` | Yes | Team name for cost allocation |
| `cost_center` | Yes | Finance cost center code |
| `environment` | Yes | `dev`, `staging`, `prod` |
| `project` | Recommended | Project or initiative |

---

## Cost Query Patterns

### Workflow Costs by Team

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

### Serverless Costs

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

### Quick Cost Queries

```sql
-- Cost by team (all compute)
SELECT custom_tags:team, SUM(list_cost)
FROM system.billing.usage
GROUP BY 1;

-- Serverless cost by budget policy
SELECT custom_tags:cost_center, SUM(list_cost)
FROM system.billing.usage
WHERE sku_name LIKE '%SERVERLESS%'
GROUP BY 1;
```

---

## Governance Query Patterns

### Find All PII Columns

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

### Tables by Classification

```sql
SELECT
    table_catalog,
    table_schema,
    table_name,
    tag_value AS data_classification
FROM system.information_schema.table_tags
WHERE tag_name = 'data_classification';
```

### Cost Centers by Catalog

```sql
SELECT
    catalog_name,
    tag_value AS cost_center
FROM system.information_schema.catalog_tags
WHERE tag_name = 'cost_center';
```
