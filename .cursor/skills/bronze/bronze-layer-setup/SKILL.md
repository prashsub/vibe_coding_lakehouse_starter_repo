---
name: bronze-layer-setup
description: End-to-end Bronze layer creation for testing and demos. Creates table DDLs, generates fake data with Faker, copies from existing sources, and configures Asset Bundle jobs. Covers Unity Catalog compliance, Change Data Feed, automatic liquid clustering, and governance metadata. Use when setting up Bronze layer tables, creating test/demo data, rapid prototyping Medallion Architecture, or bootstrapping a new Databricks project. For Faker-specific patterns (corruption rates, function signatures, provider examples), load the faker-data-generation skill.
metadata:
  author: databricks-sa
  version: "1.0"
  domain: bronze
---

# Bronze Layer Setup

Create Bronze layer tables with test data for rapid prototyping of Medallion Architecture.

## When to Use

- Setting up Bronze layer tables for a new project
- Creating test/demo data for Silver/Gold layer development
- Rapid prototyping of Medallion Architecture
- Bootstrapping a Databricks project with realistic test data
- Copying data from existing sources to a new Bronze schema

**For Faker-specific patterns** (corruption rates, function signatures, provider examples), load the [`faker-data-generation`](../faker-data-generation/SKILL.md) skill instead.

## Core Philosophy

The Bronze layer in this approach is optimized for **testing, demos, and rapid prototyping**:

- Quick setup with realistic test data
- Faker data generation as the primary method
- Unity Catalog compliance (proper governance metadata)
- Change Data Feed enabled for downstream Silver/Gold testing
- Automatic liquid clustering for query optimization
- Flexible data sources (generate, copy, or reference existing)
- **NOT for production ingestion** (use separate ingestion pipelines for that)

## Quick Start (30 minutes)

**What You'll Create:**
1. `setup_tables.py` - DDL definitions for all Bronze tables
2. `generate_dimensions.py` - Faker-based dimension data generator
3. `generate_facts.py` - Faker-based fact data generator (with FK integrity)
4. `bronze_setup_job.yml` + `bronze_data_generator_job.yml` - Asset Bundle jobs

**Fast Track:**
```bash
# 1. Deploy setup job
databricks bundle deploy -t dev

# 2. Create tables
databricks bundle run bronze_setup_job -t dev

# 3. Generate data (dimensions -> facts in sequence)
databricks bundle run bronze_data_generator_job -t dev
```

**Key Decisions:**
- **Data Source:** Faker (recommended) | Existing tables | External copy
- **Record Counts:** Dimensions: 100-200 | Facts: 1,000-10,000
- **Tables Needed:** 5-10 tables (dimensions + facts)

**Output:** Bronze Delta tables with Change Data Feed enabled, ready for Silver layer testing

## Workflow

### Step 1: Gather Requirements (15 min)

Fill in the requirements template: [references/requirements-template.md](references/requirements-template.md)

- Project name, entity list (5-10 tables), data source approach
- Domain taxonomy, data classification, record counts
- Business/technical ownership

### Step 2: Choose Data Source Approach

Three approaches detailed in [references/data-source-approaches.md](references/data-source-approaches.md):

| Approach | Best For | Time |
|---|---|---|
| **A: Faker** (recommended) | Demos, testing, learning | 30-45 min |
| **B: Existing tables** | Reusing real data structures | 15-20 min |
| **C: External copy** | CSV, databases, other workspaces | 20-30 min |

### Step 3: Create Table DDLs (30 min)

Use the setup script template: [scripts/setup_tables.py](scripts/setup_tables.py)

**File structure to create:**
```
src/{project}_bronze/
├── __init__.py                # Package initialization
├── setup_tables.py            # Table DDL definitions
├── generate_dimensions.py     # Generate dimension data with Faker
├── generate_facts.py          # Generate fact data with Faker
└── copy_from_source.py        # Optional: Copy from existing source
```

**Critical DDL rules:**
- `CLUSTER BY AUTO` on all tables (never specify columns manually)
- `delta.enableChangeDataFeed = true` (required for Silver)
- Standard audit columns: `ingestion_timestamp`, `source_file`
- Mark tables as `data_purpose = testing_demo`, `is_production = false`

### Step 4: Generate or Load Data (30-45 min)

**Option A (Faker):** Use the `faker-data-generation` skill for patterns.
- Generate dimensions first (for FK integrity)
- Generate facts with references to dimension keys
- Use seeded Faker for reproducibility

**Option B/C (Copy):** Use the copy script template: [scripts/copy_from_source.py](scripts/copy_from_source.py)

### Step 5: Configure Asset Bundle Jobs (15 min)

Use the job templates:
- [assets/templates/bronze-setup-job.yaml](assets/templates/bronze-setup-job.yaml) - Table creation job
- [assets/templates/bronze-data-generator-job.yaml](assets/templates/bronze-data-generator-job.yaml) - Data generation job

### Step 6: Deploy & Validate (15 min)

Run validation queries: [references/validation-queries.md](references/validation-queries.md)

## Critical Rules

### Required TBLPROPERTIES

Every Bronze table must include:

```sql
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'layer' = 'bronze',
    'source_system' = '{source}',
    'domain' = '{domain}',
    'entity_type' = '{dimension|fact}',
    'contains_pii' = '{true|false}',
    'data_classification' = '{confidential|internal|public}',
    'business_owner' = '{team}',
    'technical_owner' = 'Data Engineering',
    'data_purpose' = 'testing_demo',
    'is_production' = 'false'
)
```

### Table Naming Convention

- Dimensions: `bronze_{entity}_dim` (e.g., `bronze_store_dim`, `bronze_product_dim`)
- Facts: `bronze_{entity}` (e.g., `bronze_transactions`, `bronze_inventory`)
- Date dimension: `bronze_date_dim` (SQL-generated, not Faker)

### Data Generation Order

1. **Dimensions first** - Create master data tables
2. **Date dimension** - Generated via SQL SEQUENCE (not Faker)
3. **Facts last** - Load dimension keys for FK integrity

## Related Skills

| Skill | Use When |
|---|---|
| [`faker-data-generation`](../faker-data-generation/SKILL.md) | Faker corruption patterns, function signatures, provider examples |
| [`databricks-table-properties`](../../common/databricks-table-properties/SKILL.md) | Detailed TBLPROPERTIES by layer |
| [`databricks-asset-bundles`](../../common/databricks-asset-bundles/SKILL.md) | DAB configuration, serverless jobs, deployment |
| [`schema-management-patterns`](../../common/schema-management-patterns/SKILL.md) | Schema creation, Predictive Optimization |

## Reference Files

- **[references/requirements-template.md](references/requirements-template.md)** - Fill-in template for project requirements, entity list, data classification, ownership
- **[references/data-source-approaches.md](references/data-source-approaches.md)** - Detailed patterns for all 3 data source approaches (Faker, Existing, Copy)
- **[references/validation-queries.md](references/validation-queries.md)** - Validation SQL queries and implementation checklist

## Scripts

- **[scripts/setup_tables.py](scripts/setup_tables.py)** - Template table creation notebook with DDL patterns, audit columns, governance metadata
- **[scripts/copy_from_source.py](scripts/copy_from_source.py)** - Template copy-from-source notebook for Approach B/C

## Asset Templates

- **[assets/templates/bronze-setup-job.yaml](assets/templates/bronze-setup-job.yaml)** - Asset Bundle job for table creation
- **[assets/templates/bronze-data-generator-job.yaml](assets/templates/bronze-data-generator-job.yaml)** - Asset Bundle job for Faker data generation with dependency chain

## References

- [Unity Catalog](https://docs.databricks.com/unity-catalog/)
- [Delta Lake](https://docs.databricks.com/delta/)
- [Asset Bundles](https://docs.databricks.com/dev-tools/bundles/)
- [Faker Library](https://faker.readthedocs.io/)
