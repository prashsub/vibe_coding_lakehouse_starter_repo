# Convert Gold Layer Implementation Prompt to Agent Skill

## Objective

Convert `context/prompts/03b-gold-layer-implementation-prompt.md` into a properly structured Agent Skill that orchestrates existing Gold layer and common skills to guide users through the complete Gold layer implementation process (table creation, merge scripts, FK constraints, Asset Bundle jobs, and validation).

## Source Material

- **Source Prompt:** `context/prompts/03b-gold-layer-implementation-prompt.md`
- **Predecessor Skill:** `skills/gold/gold-layer-design/SKILL.md` (design orchestrator — this implementation skill is its natural successor)

## Conversion Instructions

Follow the `cursor-rule-to-skill` methodology to create a new Agent Skill with the following specifications:

### 1. Skill Metadata

```yaml
---
name: gold-layer-implementation
description: End-to-end orchestrator for implementing Gold layer tables, merge scripts, FK constraints, and Asset Bundle jobs from YAML schema definitions. Guides users through YAML-driven table creation, Silver-to-Gold MERGE operations (SCD Type 1/2 dimensions, aggregated/transaction facts), foreign key constraint application, Asset Bundle job configuration, and post-deployment validation. Orchestrates mandatory dependencies on Gold skills (yaml-driven-gold-setup, gold-layer-schema-validation, gold-layer-merge-patterns, gold-layer-documentation, gold-delta-merge-deduplication, fact-table-grain-validation) and common skills (databricks-asset-bundles, databricks-table-properties, databricks-python-imports, schema-management-patterns, unity-catalog-constraints, databricks-expert-agent). Use when implementing Gold layer from YAML designs, creating table setup scripts, writing merge scripts, deploying Gold layer jobs, or troubleshooting Gold layer implementation errors.
license: Apache-2.0
metadata:
  author: databricks-sa
  version: "1.0.0"
  domain: gold
  dependencies:
    # Gold-domain skills (primary)
    - yaml-driven-gold-setup
    - gold-layer-schema-validation
    - gold-layer-merge-patterns
    - gold-layer-documentation
    - gold-delta-merge-deduplication
    - fact-table-grain-validation
    # Common skills (infrastructure)
    - databricks-asset-bundles
    - databricks-table-properties
    - databricks-python-imports
    - schema-management-patterns
    - unity-catalog-constraints
    - databricks-expert-agent
---
```

### 2. Skill Structure

Create the following directory structure:

```
skills/gold/gold-layer-implementation/
├── SKILL.md                                        # Main orchestration workflow
├── references/
│   ├── setup-script-patterns.md                   # Extract from Step 1 (setup_tables.py patterns)
│   ├── fk-constraint-patterns.md                  # Extract from Step 1 (add_fk_constraints.py patterns)
│   ├── merge-script-patterns.md                   # Extract from Step 2 (merge_gold_tables.py patterns)
│   ├── asset-bundle-job-patterns.md               # Extract from Step 3 (gold_setup_job.yml, gold_merge_job.yml)
│   ├── validation-queries.md                      # Extract from Validation Queries section
│   └── common-issues.md                           # Extract from Common Issues & Solutions section
├── scripts/
│   ├── setup_tables_template.py                   # Template for YAML-driven table creation
│   ├── add_fk_constraints_template.py             # Template for FK constraint application
│   └── merge_gold_tables_template.py              # Template for Silver-to-Gold merge
└── assets/
    └── templates/
        ├── gold-setup-job-template.yml            # DAB job template for table setup
        ├── gold-merge-job-template.yml            # DAB job template for merge operations
        └── implementation-checklist.md            # Complete implementation checklist
```

### 3. SKILL.md Content Structure

The main SKILL.md should be structured as follows. Keep it **under 500 lines** — extract detailed patterns, full code examples, and troubleshooting into `references/` files.

```markdown
# Gold Layer Implementation Orchestrator

## Overview

This skill orchestrates the complete Gold layer implementation process, transforming YAML schema designs into production-ready Delta tables with merge scripts, FK constraints, and Asset Bundle jobs. It is the natural successor to the `gold-layer-design` skill.

**Predecessor:** `gold-layer-design` skill (YAML files must exist before using this skill)

**Core Philosophy:** YAML as Single Source of Truth — Python reads YAML at runtime, DDL is generated dynamically, schema changes require YAML edits only.

## When to Use This Skill

- Implementing Gold layer tables from completed YAML designs
- Creating generic YAML-driven table setup scripts
- Writing Silver-to-Gold MERGE scripts (dimensions and facts)
- Applying FK constraints after table creation
- Configuring Asset Bundle jobs for Gold layer deployment
- Troubleshooting Gold layer implementation errors (duplicate keys, schema mismatches, grain violations)

## Prerequisites

⚠️ **MANDATORY:** Complete `gold-layer-design` skill first. The following must exist:
- [ ] YAML schema files in `gold_layer_design/yaml/{domain}/*.yaml`
- [ ] ERD documentation (`erd_master.md`)
- [ ] Column lineage documentation (`COLUMN_LINEAGE.csv`)

## Critical Dependencies (Read at Indicated Phase)

This skill orchestrates the following skills. Each MUST be read and followed at the phase where it is invoked:

### Gold-Domain Skills

| Skill | Read At | Purpose |
|-------|---------|---------|
| `yaml-driven-gold-setup` | Phase 1 | YAML-to-DDL patterns, setup script structure |
| `gold-layer-documentation` | Phase 1 | Dual-purpose descriptions, table properties |
| `gold-layer-merge-patterns` | Phase 2 | SCD Type 1/2, fact aggregation, column mapping |
| `gold-delta-merge-deduplication` | Phase 2 | Deduplication before MERGE (mandatory) |
| `fact-table-grain-validation` | Phase 2 | Grain inference from PK, pre-merge validation |
| `gold-layer-schema-validation` | Phase 2 | DataFrame-to-DDL schema validation |

### Common Skills

| Skill | Read At | Purpose |
|-------|---------|---------|
| `databricks-asset-bundles` | Phase 3 | Job YAML patterns, serverless config, sync |
| `databricks-table-properties` | Phase 1 | Standard TBLPROPERTIES by layer |
| `unity-catalog-constraints` | Phase 1 | PK/FK constraint application patterns |
| `schema-management-patterns` | Phase 1 | CREATE SCHEMA IF NOT EXISTS |
| `databricks-python-imports` | Phase 2 | Pure Python modules, avoid sys.path issues |
| `databricks-expert-agent` | All | Schema extraction over generation principle |

## Quick Start (3-4 hours)

### What You'll Create

1. `setup_tables.py` — Generic script reads YAML, creates all tables dynamically
2. `add_fk_constraints.py` — Apply FK constraints AFTER all PKs exist
3. `merge_gold_tables.py` — Merge Silver → Gold with explicit column mapping
4. `gold_setup_job.yml` — Asset Bundle job for table setup + FK constraints
5. `gold_merge_job.yml` — Asset Bundle job for periodic MERGE operations

### Deliverables Checklist

**Setup Scripts:**
- [ ] `src/{project}_gold/setup_tables.py` — Generic YAML-driven table creation
- [ ] `src/{project}_gold/add_fk_constraints.py` — FK constraint application
- [ ] Verify: `databricks bundle run gold_setup_job -t dev`

**Merge Scripts:**
- [ ] `src/{project}_gold/merge_gold_tables.py` — Silver-to-Gold MERGE
- [ ] Dimension merges (SCD Type 1 or 2) with deduplication
- [ ] Fact merges with aggregation and grain validation
- [ ] Verify: `databricks bundle run gold_merge_job -t dev`

**Asset Bundle Jobs:**
- [ ] `resources/gold/gold_setup_job.yml` — Setup + FK constraints (two tasks)
- [ ] `resources/gold/gold_merge_job.yml` — Periodic merge with schedule
- [ ] YAML files synced in `databricks.yml`

**Validation:**
- [ ] Tables created with PKs
- [ ] FK constraints applied
- [ ] Grain validated (no duplicates)
- [ ] Schema validated (DataFrame matches DDL)
- [ ] Record counts verified

### Fast Track

```bash
# 1. Deploy setup job (creates tables from YAML)
databricks bundle deploy -t dev
databricks bundle run gold_setup_job -t dev

# 2. Verify tables created
# SHOW TABLES IN {catalog}.{gold_schema}

# 3. Run merge job (Silver → Gold)
databricks bundle run gold_merge_job -t dev
```

---

## Step-by-Step Workflow

### Phase 1: YAML-Driven Table Creation (30 min)

**Read and Follow These Skills:**
```
skills/gold/yaml-driven-gold-setup/SKILL.md
skills/gold/gold-layer-documentation/SKILL.md
skills/common/databricks-table-properties/SKILL.md
skills/common/unity-catalog-constraints/SKILL.md
skills/common/schema-management-patterns/SKILL.md
```

**Activities:**
1. Create `setup_tables.py` — Single generic script that reads ALL YAML files and creates tables
2. Create `add_fk_constraints.py` — Applies FK constraints AFTER all PKs exist
3. Define standard table properties (CDF, row tracking, auto-optimize, layer=gold)
4. Handle schema creation with `CREATE SCHEMA IF NOT EXISTS`
5. Enable Predictive Optimization on Gold schema

**Key Implementation Rules:**
- FK constraints via `ALTER TABLE` AFTER all PKs exist (never inline in CREATE TABLE)
- PK columns must be NOT NULL in YAML
- Use `CREATE OR REPLACE TABLE` for idempotent setup
- Include error handling with try/except for constraint application
- YAML directory discovery pattern (`find_yaml_base()`)
- PyYAML dependency in job environment

**Skill Dependency — `unity-catalog-constraints`:**
- Surrogate keys as PRIMARY KEYS (not business keys)
- FK constraints reference surrogate PKs
- NOT NULL requirement for PK columns
- Apply constraints via ALTER TABLE after creation

**Skill Dependency — `databricks-table-properties`:**
- Standard Gold layer TBLPROPERTIES (CDF, row tracking, deletion vectors, auto-optimize)
- Domain and entity_type metadata tags
- Grain property for fact tables

**Output:** `src/{project}_gold/setup_tables.py` and `src/{project}_gold/add_fk_constraints.py`

See `references/setup-script-patterns.md` for complete implementation patterns.
See `references/fk-constraint-patterns.md` for FK constraint details.
See `scripts/setup_tables_template.py` for starter template.
See `scripts/add_fk_constraints_template.py` for starter template.

---

### Phase 2: MERGE Script Implementation (2 hours)

**Read and Follow These Skills:**
```
skills/gold/gold-layer-merge-patterns/SKILL.md
skills/gold/gold-delta-merge-deduplication/SKILL.md
skills/gold/fact-table-grain-validation/SKILL.md
skills/gold/gold-layer-schema-validation/SKILL.md
skills/common/databricks-python-imports/SKILL.md
```

**Activities:**
1. Create `merge_gold_tables.py` with separate functions per table
2. Implement dimension merges (SCD Type 1 or Type 2)
3. Implement fact merges (aggregation to match grain)
4. Add deduplication before every MERGE (MANDATORY)
5. Add explicit column mapping (Silver → Gold names)
6. Add schema validation before merge
7. Add grain validation for fact tables
8. Merge dimensions FIRST, then facts (dependency order)

**For Each Dimension Table:**

Apply patterns from `gold-layer-merge-patterns` and `gold-delta-merge-deduplication`:

1. **Deduplicate** — `.orderBy(col("processed_timestamp").desc()).dropDuplicates([business_key])`
2. **Map columns** — `.withColumn("gold_name", col("silver_name"))` for every rename
3. **Generate surrogate key** — `md5(concat_ws("||", ...))` for SCD Type 2
4. **Add SCD columns** — `effective_from`, `effective_to`, `is_current` for Type 2
5. **Select explicitly** — Only columns in Gold DDL (no `select("*")`)
6. **Validate schema** — `validate_merge_schema()` before merge
7. **MERGE** — Match on business key (+ `is_current = true` for SCD2)

**For Each Fact Table:**

Apply patterns from `gold-layer-merge-patterns`, `fact-table-grain-validation`, and `gold-delta-merge-deduplication`:

1. **Infer grain** — Read PRIMARY KEY from DDL to determine grain type
2. **Aggregate** — `.groupBy(grain_columns).agg(...)` for aggregated facts
3. **Validate grain** — Verify one row per grain combination
4. **Map columns** — Explicit column mapping
5. **Select explicitly** — Only columns in Gold DDL
6. **Validate schema** — `validate_merge_schema()` before merge
7. **MERGE** — Match on composite PK (all grain columns)

**Critical Rules (from dependency skills):**
- ALWAYS deduplicate Silver before MERGE (prevents `DELTA_MULTIPLE_SOURCE_ROW_MATCHING_TARGET_ROW_IN_MERGE`)
- Deduplication key MUST match MERGE condition key
- Use `spark_sum` not `sum` (avoid shadowing Python builtins)
- Never name variables `count`, `sum`, `min`, `max` (shadows PySpark functions)
- Cast `DATE_TRUNC` results to DATE type
- Inline helper functions or use pure Python modules (not notebook imports)

**Skill Dependency — `gold-delta-merge-deduplication`:**
- `.orderBy(col("processed_timestamp").desc())` then `.dropDuplicates([business_key])`
- Log deduplication metrics: `{original_count} → {dedupe_count}`
- Deduplication key MUST match MERGE join key

**Skill Dependency — `fact-table-grain-validation`:**
- Composite PK = aggregated grain → use `.groupBy()` + `.agg()`
- Single PK = transaction grain → pass through (no aggregation)
- Entity + date PK = snapshot grain → deduplication only
- Validate: `distinct_grain_count == total_row_count`

**Skill Dependency — `gold-layer-schema-validation`:**
- DDL is runtime source of truth (not YAML)
- Validate DataFrame columns match target table
- Use `validate_merge_schema()` before every merge

**Output:** `src/{project}_gold/merge_gold_tables.py`

See `references/merge-script-patterns.md` for complete SCD1/SCD2/fact patterns.
See `scripts/merge_gold_tables_template.py` for starter template.

---

### Phase 3: Asset Bundle Configuration (30 min)

**Read and Follow This Skill:**
```
skills/common/databricks-asset-bundles/SKILL.md
```

**Activities:**
1. Add YAML sync to `databricks.yml` — `gold_layer_design/yaml/**/*.yaml`
2. Create `gold_setup_job.yml` with two tasks (setup tables → add FK constraints)
3. Create `gold_merge_job.yml` with scheduled merge execution
4. Add PyYAML dependency to job environment
5. Configure serverless environment
6. Add tags (environment, layer, job_type)

**Critical Rules (from `databricks-asset-bundles`):**
- Use `notebook_task` not `python_task`
- Use `base_parameters` dict (not CLI-style `parameters`)
- PyYAML dependency: `pyyaml>=6.0` in environment spec
- YAML sync is CRITICAL — without it, `setup_tables.py` can't find schemas
- FK task depends on setup task (`depends_on`)
- Merge job has optional schedule (PAUSED in dev, enabled in prod)

**Output:** 
- Updated `databricks.yml` (sync section)
- `resources/gold/gold_setup_job.yml`
- `resources/gold/gold_merge_job.yml`

See `references/asset-bundle-job-patterns.md` for complete job templates.
See `assets/templates/gold-setup-job-template.yml` for starter template.
See `assets/templates/gold-merge-job-template.yml` for starter template.

---

### Phase 4: Deployment and Testing (1 hour)

**Activities:**
1. Deploy: `databricks bundle deploy -t dev`
2. Run setup job: `databricks bundle run gold_setup_job -t dev`
3. Verify tables created: `SHOW TABLES IN {catalog}.{gold_schema}`
4. Verify PKs: `SHOW CREATE TABLE {catalog}.{gold_schema}.{table}`
5. Verify FKs: `DESCRIBE TABLE EXTENDED {catalog}.{gold_schema}.{table}`
6. Run merge job: `databricks bundle run gold_merge_job -t dev`
7. Verify record counts
8. Verify grain (no duplicates at PK level)
9. Verify FK relationships (no orphaned records)
10. Verify SCD Type 2 (`is_current` flag, no overlapping effective dates)

**Output:** Validated Gold layer tables with data

See `references/validation-queries.md` for complete validation SQL.

---

### Phase 5: Post-Implementation Validation (30 min)

**Activities:**
1. Schema validation — DataFrame columns match DDL for all merge functions
2. Grain validation — No duplicate rows at PRIMARY KEY level
3. FK integrity — No orphaned foreign key references
4. SCD Type 2 — Exactly one `is_current = true` per business key
5. Data quality — Record counts, NULL checks, range validations
6. Audit timestamps — `record_created_timestamp` and `record_updated_timestamp` populated

**Output:** Validation report (pass/fail per category)

See `references/validation-queries.md` for complete SQL queries.

---

## File Organization

```
project_root/
├── databricks.yml                              # Bundle config (sync YAMLs!)
├── gold_layer_design/
│   └── yaml/                                   # ← Source of Truth (from design phase)
│       └── {domain}/
│           └── {table}.yaml
├── src/
│   └── {project}_gold/
│       ├── setup_tables.py                     # Phase 1: Generic YAML-driven setup
│       ├── add_fk_constraints.py               # Phase 1: FK constraint application
│       └── merge_gold_tables.py                # Phase 2: Silver-to-Gold MERGE
└── resources/
    └── gold/
        ├── gold_setup_job.yml                  # Phase 3: Setup + FK job
        └── gold_merge_job.yml                  # Phase 3: Merge job
```

## Key Implementation Principles

1. **YAML as Source of Truth** — `setup_tables.py` reads YAML at runtime. Schema changes = YAML edits only. No embedded DDL strings.

2. **Deduplication Always** — Every MERGE must deduplicate Silver first. No exceptions. Use `.orderBy(col("processed_timestamp").desc()).dropDuplicates([business_key])`.

3. **Explicit Column Mapping** — Never assume Silver names match Gold. Use `.withColumn("gold_name", col("silver_name"))` for every rename.

4. **Schema Validation Before Merge** — Call `validate_merge_schema()` before every Delta MERGE to catch mismatches early.

5. **Grain Validation for Facts** — Infer grain from PRIMARY KEY. Composite PK = aggregated. Single PK = transaction. Always validate before merge.

6. **FK Constraints After PKs** — Foreign keys in a SEPARATE script that runs AFTER all tables (and their PKs) exist. Never inline FK in CREATE TABLE.

7. **Schema Extraction Over Generation** — Extract table/column names from YAML files. Never hardcode or generate from scratch.

## Common Issues Quick Reference

| Issue | Error | Solution | Skill Reference |
|-------|-------|----------|-----------------|
| YAML not found | `FileNotFoundError` | Add to `databricks.yml` sync | `databricks-asset-bundles` |
| PyYAML missing | `ModuleNotFoundError` | Add `pyyaml>=6.0` to environment | `databricks-asset-bundles` |
| Duplicate key MERGE | `DELTA_MULTIPLE_SOURCE_ROW_MATCHING_TARGET_ROW_IN_MERGE` | Deduplicate before merge | `gold-delta-merge-deduplication` |
| Column not found | `UNRESOLVED_COLUMN` | Add explicit column mapping | `gold-layer-schema-validation` |
| Grain duplicates | Multiple rows per PK | Fix aggregation to match PK | `fact-table-grain-validation` |
| Variable shadows function | `'int' object is not callable` | Rename variable (e.g., `count` → `record_count`) | `gold-layer-merge-patterns` |
| FK constraint fails | `Table/column not found` | Run FK script AFTER setup script | `unity-catalog-constraints` |

See `references/common-issues.md` for detailed solutions.

## Validation Checklist

### Setup Phase
- [ ] YAML files exist in `gold_layer_design/yaml/`
- [ ] YAML files synced in `databricks.yml`
- [ ] `setup_tables.py` reads YAML dynamically (no hardcoded DDL)
- [ ] PyYAML dependency in job environment
- [ ] Schema created with `CREATE SCHEMA IF NOT EXISTS`
- [ ] Predictive Optimization enabled
- [ ] Tables created with `CLUSTER BY AUTO`
- [ ] Standard TBLPROPERTIES applied (CDF, row tracking, etc.)
- [ ] PKs added via `ALTER TABLE` after creation
- [ ] FK constraints in separate script, runs after setup

### Merge Phase
- [ ] Deduplication before EVERY merge (mandatory)
- [ ] Deduplication key matches MERGE condition key
- [ ] Explicit column mapping for ALL renames
- [ ] No variable names shadow PySpark functions
- [ ] Schema validation before merge
- [ ] Grain validation for fact tables
- [ ] Dimensions merged BEFORE facts
- [ ] SCD Type 2 includes `is_current` filter in merge condition
- [ ] Aggregated facts use `.groupBy()` matching composite PK
- [ ] Error handling with try/except
- [ ] Debug logging (record counts, deduplication metrics)

### Deployment Phase
- [ ] Asset Bundle jobs use `notebook_task` (not `python_task`)
- [ ] Parameters use `base_parameters` dict
- [ ] FK task `depends_on` setup task
- [ ] Merge job has schedule (PAUSED in dev)
- [ ] Tags applied (environment, layer, job_type)

### Validation Phase
- [ ] Tables created with correct columns
- [ ] PK constraints applied
- [ ] FK constraints applied
- [ ] No grain duplicates
- [ ] No orphaned FK references
- [ ] SCD Type 2: one `is_current = true` per business key
- [ ] Record counts verified

## Time Estimates

| Phase | Duration | Activities |
|-------|----------|------------|
| Phase 1: Setup scripts | 30 min | setup_tables.py + add_fk_constraints.py |
| Phase 2: Merge scripts | 2 hours | Dimension + fact merges with validation |
| Phase 3: Asset Bundle | 30 min | Job YAML files + databricks.yml sync |
| Phase 4: Deployment | 30 min | Deploy, run, verify |
| Phase 5: Validation | 30 min | Schema, grain, FK, SCD2 checks |
| **Total** | **3-4 hours** | For 3-5 tables |

## Next Steps After Implementation

After Gold layer implementation is complete and validated:
1. **Metric Views** — Create semantic metric views from Gold tables
2. **TVFs** — Create Table-Valued Functions for Genie integration
3. **Monitoring** — Set up Lakehouse Monitoring with custom metrics
4. **Genie Space** — Configure Genie Space with Gold tables, metric views, and TVFs

## Reference Files

- **[Setup Script Patterns](references/setup-script-patterns.md)** — Complete YAML-driven table creation patterns, `find_yaml_base()`, `build_create_table_ddl()`, `create_table()`, PK application
- **[FK Constraint Patterns](references/fk-constraint-patterns.md)** — FK constraint application after PKs, error handling, YAML FK format
- **[Merge Script Patterns](references/merge-script-patterns.md)** — Complete SCD Type 1/2 dimension merges, fact table aggregation merges, column mapping, deduplication
- **[Asset Bundle Job Patterns](references/asset-bundle-job-patterns.md)** — gold_setup_job.yml, gold_merge_job.yml, databricks.yml sync configuration
- **[Validation Queries](references/validation-queries.md)** — Schema validation SQL, grain validation, FK integrity, SCD Type 2 checks
- **[Common Issues](references/common-issues.md)** — YAML not found, PyYAML missing, duplicate key MERGE, column mismatch, grain duplicates

## External References

- [Delta Lake MERGE](https://docs.delta.io/latest/delta-update.html#upsert-into-a-table-using-merge)
- [Unity Catalog Constraints](https://docs.databricks.com/data-governance/unity-catalog/constraints.html)
- [Databricks Asset Bundles](https://docs.databricks.com/dev-tools/bundles/)
- [AgentSkills.io Specification](https://agentskills.io/specification)
```

### 4. Reference Files to Extract

Create the following reference files by extracting and organizing content from the original prompt:

1. **references/setup-script-patterns.md** — Extract from Step 1 of the prompt:
   - `find_yaml_base()` function with multiple path resolution
   - `load_yaml()` function
   - `escape_sql_string()` function
   - `build_create_table_ddl()` function with full column DDL, properties, CLUSTER BY AUTO
   - `create_table()` function with PK constraint application
   - `get_parameters()` with dbutils widgets
   - `main()` entry point with domain iteration
   - Standard table properties dict (`STANDARD_PROPERTIES`)
   - Error handling patterns

2. **references/fk-constraint-patterns.md** — Extract from the `add_fk_constraints.py` section:
   - YAML FK format (`foreign_keys: [columns, references]`)
   - `apply_fk_constraints()` function with error handling
   - FK naming convention (`fk_{table}_{idx}`)
   - Why FKs must run after all PKs exist
   - Error handling for missing referenced tables

3. **references/merge-script-patterns.md** — Extract from Step 2 of the prompt:
   - SCD Type 2 dimension merge pattern (full `merge_dim_store` example)
   - Fact table aggregation merge pattern (full `merge_fact_sales_daily` example)
   - Deduplication pattern (orderBy + dropDuplicates)
   - Column mapping pattern (withColumn for renames)
   - Surrogate key generation (md5 + concat_ws)
   - Schema validation before merge
   - Grain validation before merge
   - Main entry point with dimension-first ordering
   - Import patterns (spark_sum, avoid shadowing)

4. **references/asset-bundle-job-patterns.md** — Extract from Step 3 of the prompt:
   - `databricks.yml` sync configuration (CRITICAL: include YAML files)
   - `gold_setup_job.yml` with two-task structure (setup → FK constraints)
   - `gold_merge_job.yml` with schedule and email notifications
   - PyYAML dependency in environment spec
   - Tags pattern (environment, layer, job_type)
   - Notebook path conventions (`../../src/{project}_gold/...`)

5. **references/validation-queries.md** — Extract from the Validation Queries section:
   - Schema validation SQL (`SHOW TABLES`, `SHOW CREATE TABLE`, `DESCRIBE TABLE EXTENDED`)
   - Grain validation SQL (distinct vs total count, duplicate finder)
   - FK integrity SQL (orphaned records check)
   - SCD Type 2 validation SQL (multiple current versions, overlapping dates)

6. **references/common-issues.md** — Extract from the Common Issues & Solutions section:
   - Issue 1: YAML files not found → sync in databricks.yml
   - Issue 2: PyYAML not available → add dependency
   - Issue 3: Duplicate key MERGE error → deduplication before merge
   - Issue 4: Column name mismatch → explicit column mapping
   - Issue 5: Grain duplicates → aggregation matches PRIMARY KEY
   - Add: Variable shadows PySpark function → rename variable
   - Add: FK constraint fails → separate script after PKs

### 5. Scripts to Create

Create the following template scripts by extracting code from the source prompt:

1. **scripts/setup_tables_template.py** — Extract the complete `setup_tables.py` code from Step 1 of the prompt. Include:
   - Full docstring with usage instructions
   - `get_parameters()`, `find_yaml_base()`, `load_yaml()`, `escape_sql_string()`
   - `build_create_table_ddl()` with column DDL, properties, CLUSTER BY AUTO
   - `create_table()` with PK constraint application and error handling
   - `main()` with schema creation, predictive optimization, domain iteration

2. **scripts/add_fk_constraints_template.py** — Extract the complete `add_fk_constraints.py` code from Step 1. Include:
   - Full docstring
   - `get_parameters()`, `find_yaml_base()`, `load_yaml()`
   - `apply_fk_constraints()` with error handling
   - `main()` with domain iteration

3. **scripts/merge_gold_tables_template.py** — Extract the complete `merge_gold_tables.py` code from Step 2. Include:
   - Full docstring
   - Import block with `spark_sum` alias
   - `get_parameters()` with catalog, silver_schema, gold_schema
   - `merge_dim_store()` — SCD Type 2 example with deduplication, surrogate key, column mapping
   - `merge_fact_sales_daily()` — Aggregation example with grain validation
   - `main()` with dimension-first ordering and error handling

### 6. Assets/Templates to Create

1. **assets/templates/gold-setup-job-template.yml** — DAB job template for table setup with:
   - Serverless environment with PyYAML dependency
   - Two-task structure (setup_all_tables → add_fk_constraints)
   - `base_parameters` for catalog, gold_schema, domain
   - Tags, email notifications, timeout

2. **assets/templates/gold-merge-job-template.yml** — DAB job template for merge operations with:
   - Single merge task
   - `base_parameters` for catalog, silver_schema, gold_schema
   - Optional schedule (PAUSED by default)
   - Tags, email notifications, timeout

3. **assets/templates/implementation-checklist.md** — Complete implementation checklist covering:
   - Phase 1: Setup (6 items)
   - Phase 2: Table Creation (6 items)
   - Phase 3: MERGE Implementation (8 items)
   - Phase 4: Testing (7 items)
   - Phase 5: Validation (5 items)

### 7. Dependency Orchestration Details

The SKILL.md must clearly indicate WHEN each dependency skill should be read and followed:

| Phase | Skills to Read | Why |
|-------|---------------|-----|
| **Phase 1: Setup** | `yaml-driven-gold-setup`, `gold-layer-documentation`, `databricks-table-properties`, `unity-catalog-constraints`, `schema-management-patterns` | YAML-to-DDL patterns, table properties, PK/FK constraints, schema creation |
| **Phase 2: Merge** | `gold-layer-merge-patterns`, `gold-delta-merge-deduplication`, `fact-table-grain-validation`, `gold-layer-schema-validation`, `databricks-python-imports` | SCD patterns, deduplication, grain validation, schema validation, import patterns |
| **Phase 3: DAB** | `databricks-asset-bundles` | Job YAML, sync config, serverless environment |
| **All Phases** | `databricks-expert-agent` | Schema extraction over generation principle |

### 8. Key Differences from Design Orchestrator

The implementation skill differs from the design skill in these critical ways:

| Aspect | Design Orchestrator | Implementation Orchestrator |
|--------|--------------------|-----------------------------|
| **Input** | Silver table schemas, business requirements | YAML schema files (from design phase) |
| **Output** | YAML files, ERDs, documentation | Python scripts, Asset Bundle jobs, deployed tables |
| **Primary focus** | What tables to create | How to create and populate them |
| **Deliverables** | Documentation (ERD, lineage, onboarding) | Code (setup, merge, DAB jobs) |
| **Runtime artifacts** | None | Delta tables with constraints and data |
| **Key principle** | Dual-purpose documentation | YAML as runtime source of truth |
| **Time** | 4-8 hours | 3-4 hours |

### 9. Validation Requirements

Before finalizing the skill:

- [ ] `name` is lowercase with hyphens: `gold-layer-implementation`
- [ ] `description` is under 1024 chars and includes WHAT and WHEN
- [ ] SKILL.md body is under 500 lines (detailed content in references/)
- [ ] All 12 dependency skills are explicitly referenced with read-at-phase guidance
- [ ] Progressive disclosure pattern used (main workflow in SKILL, details in references)
- [ ] All deliverables clearly identified in checklist
- [ ] YAML-as-source-of-truth principle is prominent
- [ ] Deduplication-before-merge is marked as MANDATORY
- [ ] Grain validation is covered for fact tables
- [ ] Schema validation is covered before merge
- [ ] Common issues reference the correct dependency skills
- [ ] File organization structure is complete
- [ ] Time estimates included
- [ ] Next steps reference downstream skills (metric views, TVFs, monitoring, Genie)

## Execution Steps

1. **Read the `cursor-rule-to-skill` skill** to understand conversion methodology
2. **Read the existing `gold-layer-design` skill** to understand orchestrator patterns
3. **Create the skill directory structure** as specified in Section 2
4. **Write the main SKILL.md** following the structure provided in Section 3
5. **Extract content to reference files** from the original prompt (Section 4)
6. **Create template scripts** in scripts/ (Section 5)
7. **Create Asset Bundle templates** in assets/templates/ (Section 6)
8. **Validate the skill** using the checklist in Section 9
9. **Update the skill-navigator** to include the new `gold-layer-implementation` skill

## Success Criteria

The converted skill is successful when:
- A user can follow it to implement a complete Gold layer from YAML designs
- All 5 deliverables are created (setup.py, fk.py, merge.py, setup_job.yml, merge_job.yml)
- Setup script reads YAML dynamically (no hardcoded DDL)
- Merge scripts deduplicate, validate schema, validate grain
- FK constraints are applied in separate script after PKs
- All 12 dependency skills are orchestrated at the correct phases
- Common implementation errors are caught by validation patterns
- Asset Bundle jobs deploy and run successfully
- Gold tables contain correct data from Silver layer
