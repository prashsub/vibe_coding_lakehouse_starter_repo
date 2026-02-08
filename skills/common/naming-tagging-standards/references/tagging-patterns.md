# Tagging Patterns Reference

Detailed tagging standards for cost allocation, governance, and operational visibility.

## Config Resolution Algorithm

**Every tag application follows this algorithm:**

```
1. Check: Does context/tagging-config.yaml exist?
   ├── YES → Read config, use customer values for all tags
   └── NO  → Use smart defaults:
             ├── team         → "data-engineering" + TODO comment
             ├── cost_center  → "UNSET-UPDATE-ME" + TODO comment
             ├── environment  → ${bundle.target} (always automatic)
             ├── project      → Inferred from catalog/repo name
             ├── data_classification → "internal" (safe default)
             └── PII tags     → SKIP entirely (never guess)
```

**Critical rules:**
- `environment` is **always** `${bundle.target}` — never from config, never hardcoded
- PII columns are **never** guessed — only tagged when declared in `pii_columns` config section
- When using defaults, **every** placeholder value gets a `# TODO: Update from context/tagging-config.yaml` comment

---

## Workflow Tags (Asset Bundles)

### Required Tags

| Tag | Required | Values | Config Path |
|-----|----------|--------|-------------|
| `team` | Yes | Team name | `workflow_tags.team` |
| `cost_center` | Yes | CC-XXXX | `workflow_tags.cost_center` |
| `environment` | Yes | `dev`, `staging`, `prod` | Always `${bundle.target}` |
| `project` | Recommended | Project name | `workflow_tags.project` |
| `layer` | Recommended | `bronze`, `silver`, `gold` | Derived from pipeline layer |
| `job_type` | Recommended | `setup`, `pipeline`, `merge`, `ml` | Derived from job purpose |

### Job Tags — With Customer Config

```yaml
# Values sourced from context/tagging-config.yaml
resources:
  jobs:
    gold_merge_job:
      name: "[${bundle.target}] Gold Merge Job"
      tags:
        team: analytics-engineering        # From config: workflow_tags.team
        cost_center: CC-5678               # From config: workflow_tags.cost_center
        environment: ${bundle.target}      # Always automatic
        project: retail-analytics          # From config: workflow_tags.project
        department: merchandising          # From config: workflow_tags.custom_tags.department
        layer: gold
        job_type: merge
```

### Job Tags — Without Customer Config (Smart Defaults)

```yaml
# Smart defaults — customer should review TODO items
resources:
  jobs:
    gold_merge_job:
      name: "[${bundle.target}] Gold Merge Job"
      tags:
        team: data-engineering             # TODO: Update from context/tagging-config.yaml
        cost_center: UNSET-UPDATE-ME       # TODO: Update from context/tagging-config.yaml
        environment: ${bundle.target}      # Always automatic
        project: wanderbricks              # Inferred from project context
        layer: gold
        job_type: merge
```

### Pipeline Tags — With Customer Config

```yaml
resources:
  pipelines:
    silver_pipeline:
      name: "[${bundle.target}] Silver Pipeline"
      tags:
        team: analytics-engineering        # From config: workflow_tags.team
        cost_center: CC-5678               # From config: workflow_tags.cost_center
        environment: ${bundle.target}      # Always automatic
        project: retail-analytics          # From config: workflow_tags.project
        layer: silver
        pipeline_type: streaming
```

### Pipeline Tags — Without Customer Config (Smart Defaults)

```yaml
resources:
  pipelines:
    silver_pipeline:
      name: "[${bundle.target}] Silver Pipeline"
      tags:
        team: data-engineering             # TODO: Update from context/tagging-config.yaml
        cost_center: UNSET-UPDATE-ME       # TODO: Update from context/tagging-config.yaml
        environment: ${bundle.target}      # Always automatic
        project: wanderbricks              # Inferred from project context
        layer: silver
        pipeline_type: streaming
```

---

## Unity Catalog Governed Tags

### Required Tags by Level

| Tag | Apply To | Config Path | Default |
|-----|----------|-------------|---------|
| `cost_center` | Catalogs | `governed_tags.catalog.cost_center` | `"UNSET-UPDATE-ME"` |
| `business_unit` | Catalogs | `governed_tags.catalog.business_unit` | Omitted |
| `data_owner` | Schemas | `governed_tags.schema.data_owner` | `"UNSET-UPDATE-ME"` |
| `data_classification` | Tables | `governed_tags.table_defaults.data_classification` | `"internal"` |
| `pii` | Columns | `pii_columns.[table]` entries | Skipped |
| `pii_type` | Columns | `pii_columns.[table].[column].pii_type` | Skipped |

### Applying Tags — With Customer Config

```sql
-- Values from context/tagging-config.yaml
-- Catalog-level
ALTER CATALOG retail_data SET TAGS ('cost_center' = 'CC-5678');
ALTER CATALOG retail_data SET TAGS ('business_unit' = 'Retail');

-- Schema-level
ALTER SCHEMA retail_data.gold SET TAGS ('data_owner' = 'retail-data-team@acme.com');

-- Table-level (per-table override from config, or table_defaults)
ALTER TABLE gold.dim_customer SET TAGS ('data_classification' = 'confidential');
ALTER TABLE gold.fact_orders SET TAGS ('data_classification' = 'internal');

-- Column-level PII (only columns declared in pii_columns config section)
ALTER TABLE gold.dim_customer
ALTER COLUMN email SET TAGS ('pii' = 'true', 'pii_type' = 'email');

ALTER TABLE gold.dim_customer
ALTER COLUMN phone_number SET TAGS ('pii' = 'true', 'pii_type' = 'phone');

ALTER TABLE gold.dim_customer
ALTER COLUMN customer_name SET TAGS ('pii' = 'true', 'pii_type' = 'name');
```

### Applying Tags — Without Customer Config (Smart Defaults)

```sql
-- Smart defaults — PII tagging is SKIPPED entirely
ALTER CATALOG prod_sales_catalog SET TAGS ('cost_center' = 'UNSET-UPDATE-ME');  -- TODO: Update from context/tagging-config.yaml
-- business_unit omitted — no value available

ALTER SCHEMA prod_sales_catalog.gold SET TAGS ('data_owner' = 'UNSET-UPDATE-ME');  -- TODO: Update from context/tagging-config.yaml

ALTER TABLE gold.dim_customer SET TAGS ('data_classification' = 'internal');  -- Safe default

-- PII tagging skipped: supply context/tagging-config.yaml with pii_columns section to enable
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
