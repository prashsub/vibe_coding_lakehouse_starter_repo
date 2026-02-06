---
name: gold-layer-implementation
description: End-to-end orchestrator for implementing Gold layer tables, merge scripts, FK constraints, and Asset Bundle jobs from YAML schema definitions. Guides users through YAML-driven table creation, Silver-to-Gold MERGE operations (SCD Type 1/2 dimensions, aggregated/transaction facts), foreign key constraint application, Asset Bundle job configuration, and post-deployment validation. Orchestrates mandatory dependencies on Gold skills (yaml-driven-gold-setup, gold-layer-schema-validation, gold-layer-merge-patterns, gold-layer-documentation, gold-delta-merge-deduplication, fact-table-grain-validation, mermaid-erd-patterns) and common skills (databricks-asset-bundles, databricks-table-properties, databricks-python-imports, schema-management-patterns, unity-catalog-constraints, databricks-expert-agent). Use when implementing Gold layer from YAML designs, creating table setup scripts, writing merge scripts, deploying Gold layer jobs, or troubleshooting Gold layer implementation errors.
license: Apache-2.0
metadata:
  author: databricks-sa
  version: "1.0.0"
  domain: gold
  dependencies:
    - yaml-driven-gold-setup
    - gold-layer-schema-validation
    - gold-layer-merge-patterns
    - gold-layer-documentation
    - gold-delta-merge-deduplication
    - fact-table-grain-validation
    - mermaid-erd-patterns
    - databricks-asset-bundles
    - databricks-table-properties
    - databricks-python-imports
    - schema-management-patterns
    - unity-catalog-constraints
    - databricks-expert-agent
---

# Gold Layer Implementation Orchestrator

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

**MANDATORY:** Complete `gold-layer-design` skill first. The following must exist:
- [ ] YAML schema files in `gold_layer_design/yaml/{domain}/*.yaml`
- [ ] ERD documentation (`erd_master.md`)
- [ ] Column lineage documentation (`COLUMN_LINEAGE.csv`)

## Critical Dependencies (Read at Indicated Phase)

### Gold-Domain Skills

| Skill | Read At | Purpose |
|-------|---------|---------|
| `yaml-driven-gold-setup` | Phase 1 | YAML-to-DDL patterns, setup script structure |
| `gold-layer-documentation` | Phase 1 | Dual-purpose descriptions, table properties |
| `gold-layer-merge-patterns` | Phase 2 | SCD Type 1/2, fact aggregation, column mapping |
| `gold-delta-merge-deduplication` | Phase 2 | Deduplication before MERGE (mandatory) |
| `fact-table-grain-validation` | Phase 2 | Grain inference from PK, pre-merge validation |
| `gold-layer-schema-validation` | Phase 2 | DataFrame-to-DDL schema validation |
| `mermaid-erd-patterns` | Phase 5 | Cross-reference created tables against ERD |

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
3. `merge_gold_tables.py` — Merge Silver to Gold with explicit column mapping
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

### Fast Track

```bash
# 1. Deploy setup job (creates tables from YAML)
databricks bundle deploy -t dev
databricks bundle run gold_setup_job -t dev

# 2. Verify tables created
# SHOW TABLES IN {catalog}.{gold_schema}

# 3. Run merge job (Silver to Gold)
databricks bundle run gold_merge_job -t dev
```

---

## Step-by-Step Workflow

### Phase 1: YAML-Driven Table Creation (30 min)

**MANDATORY: Read each skill below using the Read tool BEFORE writing any code for this phase:**

1. `.cursor/skills/gold/yaml-driven-gold-setup/SKILL.md` — YAML-to-DDL patterns, `find_yaml_base()`, `build_create_table_ddl()`
2. `.cursor/skills/gold/gold-layer-documentation/SKILL.md` — Dual-purpose column descriptions, naming conventions
3. `.cursor/skills/common/databricks-table-properties/SKILL.md` — Standard TBLPROPERTIES by layer
4. `.cursor/skills/common/unity-catalog-constraints/SKILL.md` — PK/FK `ALTER TABLE` patterns, NOT NULL requirements
5. `.cursor/skills/common/schema-management-patterns/SKILL.md` — `CREATE SCHEMA IF NOT EXISTS` pattern

**Activities:**
1. Create `setup_tables.py` — Single generic script reads ALL YAML files, creates tables
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

**Output:** `src/{project}_gold/setup_tables.py` and `src/{project}_gold/add_fk_constraints.py`

See `references/setup-script-patterns.md` for complete implementation patterns.
See `references/fk-constraint-patterns.md` for FK constraint details.
See `scripts/setup_tables_template.py` for starter template.
See `scripts/add_fk_constraints_template.py` for starter template.

---

### Phase 2: MERGE Script Implementation (2 hours)

**MANDATORY: Read each skill below using the Read tool BEFORE writing any merge code:**

1. `.cursor/skills/gold/gold-layer-merge-patterns/SKILL.md` — SCD Type 1/2, fact aggregation, column mapping, `spark_sum` alias
2. `.cursor/skills/gold/gold-delta-merge-deduplication/SKILL.md` — Deduplication before MERGE (ALWAYS required, prevents `DELTA_MULTIPLE_SOURCE_ROW_MATCHING_TARGET_ROW_IN_MERGE`)
3. `.cursor/skills/gold/fact-table-grain-validation/SKILL.md` — Grain inference from PK, transaction vs aggregated patterns
4. `.cursor/skills/gold/gold-layer-schema-validation/SKILL.md` — `validate_merge_schema()`, DataFrame-to-DDL checks
5. `.cursor/skills/common/databricks-python-imports/SKILL.md` — Pure Python modules, avoid `sys.path` issues in serverless

**Activities:**
1. Create `merge_gold_tables.py` with separate functions per table
2. Implement dimension merges (SCD Type 1 or Type 2)
3. Implement fact merges (aggregation to match grain)
4. Add deduplication before every MERGE (MANDATORY)
5. Add explicit column mapping (Silver to Gold names)
6. Add schema validation before merge
7. Add grain validation for fact tables
8. Merge dimensions FIRST, then facts (dependency order)

**For Each Dimension Table:**

1. **Deduplicate** — `.orderBy(col("processed_timestamp").desc()).dropDuplicates([business_key])`
2. **Map columns** — `.withColumn("gold_name", col("silver_name"))` for every rename
3. **Generate surrogate key** — `md5(concat_ws("||", ...))` for SCD Type 2
4. **Add SCD columns** — `effective_from`, `effective_to`, `is_current` for Type 2
5. **Select explicitly** — Only columns in Gold DDL (no `select("*")`)
6. **Validate schema** — `validate_merge_schema()` before merge
7. **MERGE** — Match on business key (+ `is_current = true` for SCD2)

**For Each Fact Table:**

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

**Output:** `src/{project}_gold/merge_gold_tables.py`

See `references/merge-script-patterns.md` for complete SCD1/SCD2/fact patterns.
See `scripts/merge_gold_tables_template.py` for starter template.

---

### Phase 3: Asset Bundle Configuration (30 min)

**MANDATORY: Read this skill using the Read tool BEFORE creating job YAML files:**

1. `.cursor/skills/common/databricks-asset-bundles/SKILL.md` — Job YAML patterns, serverless config, `notebook_task` vs `python_task`, `base_parameters`, sync

**Activities:**
1. Add YAML sync to `databricks.yml` — `gold_layer_design/yaml/**/*.yaml`
2. Create `gold_setup_job.yml` with two tasks (setup tables then add FK constraints)
3. Create `gold_merge_job.yml` with scheduled merge execution
4. Add PyYAML dependency to job environment
5. Configure serverless environment
6. Add tags (environment, layer, job_type)

**Critical Rules (from `databricks-asset-bundles`):**
- Use `notebook_task` not `python_task`
- Use `base_parameters` dict (not CLI-style `parameters`)
- PyYAML dependency: `pyyaml>=6.0` in environment spec
- YAML sync is CRITICAL — without it, `setup_tables.py` cannot find schemas
- FK task depends on setup task (`depends_on`)
- Merge job has optional schedule (PAUSED in dev, enabled in prod)

**Output:** Updated `databricks.yml`, `resources/gold/gold_setup_job.yml`, `resources/gold/gold_merge_job.yml`

See `references/asset-bundle-job-patterns.md` for complete job templates.
See `assets/templates/gold-setup-job-template.yml` and `assets/templates/gold-merge-job-template.yml`.

---

### Phase 4: Deployment and Testing (30 min)

**Activities:**
1. Deploy: `databricks bundle deploy -t dev`
2. Run setup job: `databricks bundle run gold_setup_job -t dev`
3. Verify tables created: `SHOW TABLES IN {catalog}.{gold_schema}`
4. Verify PKs: `SHOW CREATE TABLE {catalog}.{gold_schema}.{table}`
5. Verify FKs: `DESCRIBE TABLE EXTENDED {catalog}.{gold_schema}.{table}`
6. Run merge job: `databricks bundle run gold_merge_job -t dev`
7. Verify record counts, grain, FK relationships, SCD Type 2

See `references/validation-queries.md` for complete validation SQL.

---

### Phase 5: Post-Implementation Validation (30 min)

**MANDATORY: Read this skill using the Read tool to cross-reference created tables against ERD:**

1. `.cursor/skills/gold/mermaid-erd-patterns/SKILL.md` — Verify all ERD entities have corresponding tables, all relationships match FK constraints

**Activities:**
1. ERD cross-reference — Compare created tables against `erd_master.md` to confirm nothing was missed
2. Schema validation — DataFrame columns match DDL for all merge functions
3. Grain validation — No duplicate rows at PRIMARY KEY level
4. FK integrity — No orphaned foreign key references
5. SCD Type 2 — Exactly one `is_current = true` per business key
6. Data quality — Record counts, NULL checks, range validations
7. Audit timestamps — `record_created_timestamp` and `record_updated_timestamp` populated

See `references/validation-queries.md` for complete SQL queries.

---

## File Organization

```
project_root/
├── databricks.yml                              # Bundle config (sync YAMLs!)
├── gold_layer_design/
│   └── yaml/                                   # Source of Truth (from design phase)
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
6. **FK Constraints After PKs** — Foreign keys in a SEPARATE script that runs AFTER all tables and their PKs exist. Never inline FK in CREATE TABLE.
7. **Schema Extraction Over Generation** — Extract table/column names from YAML files. Never hardcode or generate from scratch.

## Common Issues Quick Reference

| Issue | Error | Solution | Skill Reference |
|-------|-------|----------|-----------------|
| YAML not found | `FileNotFoundError` | Add to `databricks.yml` sync | `databricks-asset-bundles` |
| PyYAML missing | `ModuleNotFoundError` | Add `pyyaml>=6.0` to environment | `databricks-asset-bundles` |
| Duplicate key MERGE | `DELTA_MULTIPLE_SOURCE_ROW_MATCHING_TARGET_ROW_IN_MERGE` | Deduplicate before merge | `gold-delta-merge-deduplication` |
| Column not found | `UNRESOLVED_COLUMN` | Add explicit column mapping | `gold-layer-schema-validation` |
| Grain duplicates | Multiple rows per PK | Fix aggregation to match PK | `fact-table-grain-validation` |
| Variable shadows function | `'int' object is not callable` | Rename variable (e.g., `count` to `record_count`) | `gold-layer-merge-patterns` |
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
- [ ] Error handling with try/except and debug logging

### Deployment Phase
- [ ] Asset Bundle jobs use `notebook_task` (not `python_task`)
- [ ] Parameters use `base_parameters` dict
- [ ] FK task `depends_on` setup task
- [ ] Merge job has schedule (PAUSED in dev)
- [ ] Tags applied (environment, layer, job_type)

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

- **[Setup Script Patterns](references/setup-script-patterns.md)** — YAML-driven table creation, `find_yaml_base()`, `build_create_table_ddl()`, PK application
- **[FK Constraint Patterns](references/fk-constraint-patterns.md)** — FK constraint application after PKs, error handling, YAML FK format
- **[Merge Script Patterns](references/merge-script-patterns.md)** — SCD Type 1/2 dimension merges, fact aggregation merges, column mapping, deduplication
- **[Asset Bundle Job Patterns](references/asset-bundle-job-patterns.md)** — gold_setup_job.yml, gold_merge_job.yml, databricks.yml sync
- **[Validation Queries](references/validation-queries.md)** — Schema, grain, FK integrity, SCD Type 2 validation SQL
- **[Common Issues](references/common-issues.md)** — YAML not found, PyYAML missing, duplicate key MERGE, column mismatch, grain duplicates

## External References

- [Delta Lake MERGE](https://docs.delta.io/latest/delta-update.html#upsert-into-a-table-using-merge)
- [Unity Catalog Constraints](https://docs.databricks.com/data-governance/unity-catalog/constraints.html)
- [Databricks Asset Bundles](https://docs.databricks.com/dev-tools/bundles/)
- [AgentSkills.io Specification](https://agentskills.io/specification)
