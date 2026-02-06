# Domain Index Summaries

This document contains detailed domain index summaries for the skill navigation system. Token estimates reflect the **post-restructuring** SKILL.md sizes (all under 500 lines). Detailed content is in each skill's `references/` directory.

---

## Semantic Layer Index

**Skills in domain:** 4 skills

| Skill | SKILL.md | references/ | scripts/ | assets/ |
|---|---|---|---|---|
| `metric-views-patterns` | ~1.4K | yaml-reference, validation-checklist, advanced-patterns | validate_metric_view.py | metric-view-template.yaml |
| `databricks-table-valued-functions` | ~1.3K | tvf-patterns, genie-integration | — | tvf-template.sql |
| `genie-space-patterns` | ~1.5K | configuration-guide, agent-instructions, troubleshooting, trusted-assets | — | genie-space-config.yaml |
| `genie-space-export-import-api` | ~1.1K | api-reference, workflow-patterns, troubleshooting | export/import scripts | — |

**Key Patterns (load full skill for details):**
1. Metric views use `WITH METRICS LANGUAGE YAML` syntax
2. TVFs must have STRING parameters for Genie compatibility
3. Genie Spaces need comprehensive agent instructions
4. Export/Import uses `serialized_space` JSON format

**When to load full skills:**
- Creating metric views → Load `metric-views-patterns`, then `references/yaml-reference.md`
- Creating TVFs → Load `databricks-table-valued-functions`, then `references/tvf-patterns.md`
- Setting up Genie Space → Load `genie-space-patterns`, then `references/configuration-guide.md`
- API automation → Load `genie-space-export-import-api`, then run `scripts/export_genie_space.py`

---

## Gold Layer Index

**Skills in domain:** 7 skills

| Skill | SKILL.md | references/ | scripts/ | assets/ |
|---|---|---|---|---|
| `gold-layer-merge-patterns` | ~1.3K | — | — | scd-type1, scd-type2, fact-table merge templates |
| `gold-delta-merge-deduplication` | ~1.4K | dedup-patterns | check_duplicates.py | — |
| `gold-layer-documentation` | ~1.1K | documentation-templates, llm-optimization | — | gold-table-docs.yaml |
| `mermaid-erd-patterns` | ~1.2K | erd-syntax-reference | — | erd-template.md |
| `gold-layer-schema-validation` | ~1.1K | validation-patterns | validate_schema.py | — |
| `fact-table-grain-validation` | ~1.2K | grain-patterns | validate_grain.py | — |
| `yaml-driven-gold-setup` | ~1.8K | yaml-schema | — | gold-table-template.yaml |

**Key Patterns:**
1. Always deduplicate before MERGE to prevent duplicate key errors
2. Use explicit column mapping (Silver → Gold names may differ)
3. Fact tables: verify grain (transaction vs aggregated)
4. SCD2 dimensions need `is_current` filtering

**When to load full skills:**
- Duplicate key errors → Load `gold-delta-merge-deduplication`, then `references/dedup-patterns.md`
- Creating Gold tables → Load `yaml-driven-gold-setup`, copy `assets/templates/gold-table-template.yaml`
- Documentation → Load `gold-layer-documentation`, then `references/llm-optimization.md`
- MERGE operations → Load `gold-layer-merge-patterns`, copy appropriate merge template from `assets/templates/`

---

## Infrastructure Index

**Skills in domain:** 5 skills

| Skill | SKILL.md | references/ | scripts/ | assets/ |
|---|---|---|---|---|
| `databricks-asset-bundles` | ~1.2K | configuration-guide, job-patterns, common-errors | validate_bundle.py | bundle-template.yaml |
| `schema-management-patterns` | ~0.7K | — | — | create-schema.sql |
| `databricks-table-properties` | ~1.0K | — | — | table-properties.sql |
| `unity-catalog-constraints` | ~0.8K | constraint-patterns, validation-guide | apply_constraints.py | constraints-template.sql |
| `databricks-python-imports` | ~1.9K | — | — | — |

**Key Patterns:**
1. Use `notebook_task` not `python_task` in DABs
2. Use `base_parameters` dict, not CLI-style `parameters`
3. Schemas created programmatically with `CREATE SCHEMA IF NOT EXISTS`
4. Constraints applied via `ALTER TABLE` after table creation
5. Python imports: use `dbutils.widgets.get()` for DAB notebooks, `argparse` for local scripts

**When to load full skills:**
- Deployment issues → Load `databricks-asset-bundles`, then `references/common-errors.md`
- New DAB setup → Load `databricks-asset-bundles`, copy `assets/templates/bundle-template.yaml`
- Constraint errors → Load `unity-catalog-constraints`, then `references/constraint-patterns.md`
- Python imports → Load `databricks-python-imports` (self-contained, no references needed)

---

## Monitoring Index

**Skills in domain:** 3 skills

| Skill | SKILL.md | references/ | scripts/ | assets/ |
|---|---|---|---|---|
| `lakehouse-monitoring-comprehensive` | ~1.7K | monitor-configuration, custom-metrics, deployment-guide | create_monitor.py | monitor-config.yaml |
| `databricks-aibi-dashboards` | ~1.4K | dashboard-json-reference, widget-patterns, deployment-guide | deploy_dashboard.py, validate_*.py | dashboard-template.json |
| `sql-alerting-patterns` | ~1.8K | alert-patterns | — | alert-config.yaml |

**Key Patterns:**
1. Custom metrics use `input_columns=[":table"]` for table-level KPIs
2. Dashboard JSON uses `page.layout` for positioning
3. Alerts use config-driven YAML deployment

**When to load full skills:**
- Setting up monitoring → Load `lakehouse-monitoring-comprehensive`, then `references/monitor-configuration.md`
- Creating dashboards → Load `databricks-aibi-dashboards`, then `references/widget-patterns.md`
- Setting up alerts → Load `sql-alerting-patterns`, copy `assets/templates/alert-config.yaml`

---

## Silver Layer Index

**Skills in domain:** 2 skills

| Skill | SKILL.md | references/ | scripts/ | assets/ |
|---|---|---|---|---|
| `dlt-expectations-patterns` | ~1.7K | expectation-patterns, quarantine-patterns | — | expectations-config.yaml |
| `dqx-patterns` | ~1.3K | dqx-configuration, rule-patterns, integration-guide | setup_dqx.py | dqx-rules.yaml |

**Key Patterns:**
1. DLT expectations stored in Unity Catalog Delta table
2. Use `@dlt.expect_all_or_drop()` for strict enforcement
3. DQX provides richer diagnostics than DLT expectations
4. Pre-merge validation catches issues before Gold

**When to load full skills:**
- DLT pipeline → Load `dlt-expectations-patterns`, then `references/expectation-patterns.md`
- Advanced validation → Load `dqx-patterns`, then `references/rule-patterns.md`
- Quarantine setup → Load `dlt-expectations-patterns`, then `references/quarantine-patterns.md`

---

## Bronze Layer Index

**Skills in domain:** 1 skill

| Skill | SKILL.md | references/ | scripts/ | assets/ |
|---|---|---|---|---|
| `faker-data-generation` | ~1.0K | faker-providers | generate_data.py | faker-config.yaml |

**Key Patterns:**
1. Use Faker with configurable corruption rates
2. Generate realistic but identifiable test data
3. Include edge cases for Silver layer testing

---

## ML Index

**Skills in domain:** 1 skill

| Skill | SKILL.md | references/ | scripts/ | assets/ |
|---|---|---|---|---|
| `mlflow-mlmodels-patterns` | ~1.1K | experiment-patterns, model-registry, dab-integration, feature-store-patterns, data-quality-patterns, troubleshooting | setup_experiment.py | ml-job-config.yaml |

**Key Patterns:**
1. Use `/Shared/` experiment paths (not `/Users/`)
2. Don't define experiments in Asset Bundles
3. Log datasets inside `mlflow.start_run()` context
4. Inline helpers (don't import modules in DAB notebooks)

---

## Exploration Index

**Skills in domain:** 1 skill

| Skill | SKILL.md | references/ | scripts/ | assets/ |
|---|---|---|---|---|
| `adhoc-exploration-notebooks` | ~0.9K | notebook-patterns, analysis-workflows | — | exploration-notebook.py |

**Key Patterns:**
1. Dual format: .py for workspace, .ipynb for local Jupyter
2. Magic commands only work in workspace, not Databricks Connect
3. Standard helper functions: list_tables, explore_table, check_data_quality

---

## Planning Index

**Skills in domain:** 1 skill

| Skill | SKILL.md | references/ | scripts/ | assets/ |
|---|---|---|---|---|
| `project-plan-methodology` | ~1.6K | phase-details, estimation-guide | — | project-plan-template.md |

**Key Patterns:**
1. 5-phase structure (Bronze → Gold → Use Cases → Agents → Frontend)
2. Agent Domain Framework (Cost, Security, Performance, Reliability, Quality)
3. 7 Phase 3 addendums pattern

---

## Admin Index

**Skills in domain:** 4 skills

| Skill | SKILL.md | references/ | scripts/ | assets/ |
|---|---|---|---|---|
| `cursor-rules` | ~0.3K | — | — | — |
| `self-improvement` | ~1.7K | LEARNING-FORMAT | create-skill.sh | skill-template.md |
| `documentation-organization` | ~0.9K | — | organize_docs.sh | — |
| `cursor-rule-to-skill` | ~1.5K | CURSOR-RULE-FORMAT, PROGRESSIVE-DISCLOSURE | convert-rule-to-skill.py | skill-template.md |

**Key Patterns:**
1. Rules/skills use kebab-case naming
2. Self-improvement triggered by "learn from this", "remember this pattern"
3. Documentation organized into docs/ subdirectories
4. Rule-to-skill conversion follows AgentSkills.io spec
