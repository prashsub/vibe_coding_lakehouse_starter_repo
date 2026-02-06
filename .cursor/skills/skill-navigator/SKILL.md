---
name: skill-navigator
description: Intelligent skill navigation system with tiered loading for context-efficient agent operation. Routes tasks to the correct domain skill based on keyword detection. Each skill uses progressive disclosure with references/, scripts/, and assets/ directories. Use this skill as the entry point for any Databricks-related task to determine which specialized skills to load and how to navigate within them.
metadata:
  author: databricks-sa
  version: "2.0"
  domain: meta
---

# Skill Navigator: Context-Aware Tiered Loading System

## Purpose

This navigation skill implements **tiered context loading** to keep total context under Claude Opus's 200K token limit. After restructuring, ALL SKILL.md files are lightweight (< 2K tokens each). The heavy content lives in `references/` files loaded on demand.

**For detailed domain index summaries, see:** [references/domain-indexes.md](references/domain-indexes.md)

---

## CRITICAL: Skill Structure (Post-Restructuring)

Every skill now follows **progressive disclosure**:

```
skill-name/
├── SKILL.md            # ~1-2K tokens — overview, critical rules, quick reference
├── references/         # Loaded ON DEMAND — detailed patterns, API docs, checklists
│   ├── patterns.md
│   └── guide.md
├── scripts/            # EXECUTED, not read — validation utilities, setup tools
│   └── validate.py
└── assets/
    └── templates/      # Templates — YAML, SQL, JSON starters
        └── template.yaml
```

### How to Navigate Within a Skill

1. **Read SKILL.md first** (~1-2K tokens) — Contains overview, critical rules, and links
2. **Read specific references/ files** only when you need detailed patterns for the task
3. **Execute scripts/** as black-box utilities — don't read source unless necessary
4. **Copy assets/templates/** as starting points for new files

**Key insight:** You can now safely load 5-10 SKILL.md files simultaneously. Context pressure comes from loading multiple `references/` files, not from SKILL.md files themselves.

---

## Context Budget Management

**Claude Opus Context Limit:** 200K tokens
**Target Operating Budget:** 40-60K tokens (for optimal performance)
**Maximum Skill Budget:** 80K tokens (leaves room for code/files)

| Tier | Purpose | Token Budget | Content |
|---|---|---|---|
| **Tier 1: Core** | Always loaded | ~4K tokens | 4 core SKILL.md files |
| **Tier 2: Domain Index** | Loaded on domain detection | ~2K per domain | Domain summaries |
| **Tier 3: SKILL.md** | Loaded on specific task | ~1-2K each | Individual skill overview |
| **Tier 4: References** | Loaded on demand | ~2-8K each | Detailed patterns & guides |

---

## Tier 1: Core Skills (Always Loaded)

**Budget: ~4K tokens** — Essential for every interaction

| Skill | Location | ~Tokens | Purpose |
|---|---|---|---|
| `skill-navigator` | `.cursor/skills/skill-navigator/SKILL.md` | ~1.5K | This navigation system |
| `databricks-expert-agent` | `.cursor/skills/common/databricks-expert-agent/SKILL.md` | ~1.2K | Core agent behavior |
| `cursor-rules` | `.cursor/skills/admin/cursor-rules/SKILL.md` | ~0.3K | Rules management |
| `documentation-organization` | `.cursor/skills/admin/documentation-organization/SKILL.md` | ~0.9K | Documentation standards |

---

## Tier 2: Domain Detection & Index Loading

When a domain is detected, load the domain index summary from [references/domain-indexes.md](references/domain-indexes.md).

### Domain Detection Keywords

| Domain | Keywords | Index to Load |
|---|---|---|
| **Semantic Layer** | metric view, TVF, Genie, semantic | Semantic Layer Index |
| **Gold Layer** | Gold, merge, fact, dimension, SCD2 | Gold Layer Index |
| **Infrastructure** | deploy, Asset Bundle, job, workflow, imports | Infrastructure Index |
| **Monitoring** | monitoring, dashboard, alert | Monitoring Index |
| **Silver Layer** | DLT, Silver, expectations, quality | Silver Layer Index |
| **Bronze Layer** | Bronze, Faker, synthetic, ingestion | Bronze Layer Index |
| **ML** | MLflow, model, training, inference | ML Index |

---

## Tier 3: Task-Specific Skill Loading

Load the specific SKILL.md for the task. All are lightweight (~1-2K tokens each).

| Skill | ~Tokens | Has refs/ | Has scripts/ | Has assets/ |
|---|---|---|---|---|
| `databricks-asset-bundles` | ~1.2K | 3 files | 1 file | 1 template |
| `lakehouse-monitoring-comprehensive` | ~1.7K | 3 files | 1 file | 1 template |
| `dqx-patterns` | ~1.3K | 3 files | 1 file | 1 template |
| `mlflow-mlmodels-patterns` | ~1.1K | 6 files | 1 file | 1 template |
| `databricks-aibi-dashboards` | ~1.4K | 3 files | 3 files | 1 template |
| `metric-views-patterns` | ~1.4K | 3 files | 1 file | 1 template |
| `dlt-expectations-patterns` | ~1.7K | 2 files | — | 1 template |
| `genie-space-patterns` | ~1.5K | 4 files | — | 1 template |
| `genie-space-export-import-api` | ~1.1K | 3 files | 2 files | — |
| `databricks-table-valued-functions` | ~1.3K | 2 files | — | 1 template |
| `gold-layer-documentation` | ~1.1K | 3 files | — | 1 template |
| `unity-catalog-constraints` | ~0.8K | 2 files | 1 file | 1 template |
| `sql-alerting-patterns` | ~1.8K | 1 file | — | 1 template |
| `project-plan-methodology` | ~1.6K | 2 files | — | 1 template |
| `mermaid-erd-patterns` | ~1.2K | 3 files | — | 1 template |
| `adhoc-exploration-notebooks` | ~0.9K | 2 files | — | 1 template |
| `fact-table-grain-validation` | ~1.2K | 1 file | 1 file | — |
| `gold-layer-schema-validation` | ~1.1K | 2 files | 1 file | — |
| `gold-delta-merge-deduplication` | ~1.4K | 1 file | 1 file | — |
| `yaml-driven-gold-setup` | ~1.8K | 1 file | — | 1 template |
| `gold-layer-merge-patterns` | ~1.3K | — | — | 3 templates |
| `faker-data-generation` | ~1.0K | 1 file | 1 file | 1 template |
| `databricks-python-imports` | ~1.9K | — | — | — |
| `databricks-table-properties` | ~1.0K | — | — | 1 template |
| `schema-management-patterns` | ~0.7K | — | — | 1 template |
| `self-improvement` | ~1.7K | 1 file | 1 file | 1 template |
| `cursor-rule-to-skill` | ~1.5K | 2 files | 1 file | 1 template |

---

## Progressive Loading Strategy

### Step 1: Initial Detection (~4K tokens)
```
User Request → Tier 1 already loaded (4 core SKILL.md files)
```

### Step 2: Domain Routing (~6K tokens total)
```
Detect domain keywords → Read domain index from references/domain-indexes.md
Example: "metric view" → Semantic Layer index section
```

### Step 3: Load Skill Overview (~7-8K tokens total)
```
Identify task → Read the specific SKILL.md (~1-2K tokens)
Example: "fix duplicate key" → Read gold-delta-merge-deduplication/SKILL.md
```

### Step 4: Deep Dive into References (as needed)
```
Need detailed patterns → Read specific references/ file from the skill
Example: Need dedup SQL → Read references/dedup-patterns.md
```

### Step 5: Execute Scripts or Copy Templates (as needed)
```
Need validation → Run scripts/validate.py
Need starter file → Copy assets/templates/template.yaml
```

---

## Task Detection & Skill Routing Table

| Task Keywords | Domain | Skill to Load |
|---|---|---|
| "metric view", "semantic" | Semantic | metric-views-patterns |
| "TVF", "function" | Semantic | databricks-table-valued-functions |
| "Genie Space", "Genie setup" | Semantic | genie-space-patterns |
| "Genie API", "export/import" | Semantic | genie-space-export-import-api |
| "Gold merge", "MERGE" | Gold | gold-layer-merge-patterns |
| "duplicate key" | Gold | gold-delta-merge-deduplication |
| "Gold documentation" | Gold | gold-layer-documentation |
| "ERD", "diagram" | Gold | mermaid-erd-patterns |
| "schema validation" | Gold | gold-layer-schema-validation |
| "fact grain" | Gold | fact-table-grain-validation |
| "YAML setup" | Gold | yaml-driven-gold-setup |
| "deploy", "Asset Bundle" | Infra | databricks-asset-bundles |
| "schema", "CREATE SCHEMA" | Infra | schema-management-patterns |
| "table properties" | Infra | databricks-table-properties |
| "constraints", "PK/FK" | Infra | unity-catalog-constraints |
| "Python imports" | Infra | databricks-python-imports |
| "monitoring", "Lakehouse" | Monitor | lakehouse-monitoring-comprehensive |
| "dashboard", "AI/BI" | Monitor | databricks-aibi-dashboards |
| "alert", "SQL alert" | Monitor | sql-alerting-patterns |
| "DLT", "expectations" | Silver | dlt-expectations-patterns |
| "DQX", "validation" | Silver | dqx-patterns |
| "Faker", "synthetic" | Bronze | faker-data-generation |
| "MLflow", "model" | ML | mlflow-mlmodels-patterns |
| "exploration notebook" | Explore | adhoc-exploration-notebooks |
| "project plan" | Plan | project-plan-methodology |
| "improve skills" | Admin | self-improvement |

---

## Context Budget Monitoring

### Green Zone (0-20K tokens)
- Load multiple SKILL.md files freely
- Load 2-3 reference files

### Yellow Zone (20-50K tokens)
- Continue loading SKILL.md files (they're lightweight)
- Be selective about which references/ to load
- Prefer running scripts/ over reading them

### Red Zone (50K+ tokens)
- Reference skill paths instead of loading
- Execute scripts as black boxes
- Consider splitting task into phases

---

## Complete Skill Directory Map

```
.cursor/skills/
├── skill-navigator/SKILL.md                              # This navigator
│
├── admin/
│   ├── cursor-rules/SKILL.md                             # Rule/skill creation standards
│   └── documentation-organization/SKILL.md               # Documentation structure
│       └── scripts/organize_docs.sh
│
├── bronze/
│   └── faker-data-generation/SKILL.md                    # Synthetic data with Faker
│       ├── references/faker-providers.md
│       ├── scripts/generate_data.py
│       └── assets/templates/faker-config.yaml
│
├── common/
│   ├── databricks-expert-agent/SKILL.md                  # Core SA agent behavior
│   │   └── references/extraction-patterns.md
│   ├── databricks-asset-bundles/SKILL.md                 # DAB YAML configuration
│   │   ├── references/{configuration-guide,job-patterns,common-errors}.md
│   │   ├── scripts/validate_bundle.py
│   │   └── assets/templates/bundle-template.yaml
│   ├── schema-management-patterns/SKILL.md               # Schema management
│   │   └── assets/templates/create-schema.sql
│   ├── databricks-table-properties/SKILL.md              # Table properties
│   │   └── assets/templates/table-properties.sql
│   ├── unity-catalog-constraints/SKILL.md                # PK/FK constraints
│   │   ├── references/{constraint-patterns,validation-guide}.md
│   │   ├── scripts/apply_constraints.py
│   │   └── assets/templates/constraints-template.sql
│   └── databricks-python-imports/SKILL.md                # Python imports
│
├── semantic-layer/
│   ├── metric-views-patterns/SKILL.md                    # Metric view YAML + SQL
│   │   ├── references/{yaml-reference,validation-checklist,advanced-patterns}.md
│   │   ├── scripts/validate_metric_view.py
│   │   └── assets/templates/metric-view-template.yaml
│   ├── databricks-table-valued-functions/SKILL.md        # TVFs for Genie
│   │   ├── references/{tvf-patterns,genie-integration}.md
│   │   └── assets/templates/tvf-template.sql
│   ├── genie-space-patterns/SKILL.md                     # Genie Space setup
│   │   ├── references/{configuration-guide,agent-instructions,troubleshooting}.md
│   │   └── assets/templates/genie-space-config.yaml
│   └── genie-space-export-import-api/SKILL.md            # Genie API automation
│       ├── references/{api-reference,workflow-patterns,troubleshooting}.md
│       └── scripts/{export,import}_genie_space.py
│
├── gold/
│   ├── gold-layer-merge-patterns/SKILL.md                # MERGE operations
│   │   └── assets/templates/{scd-type1,scd-type2,fact-table}-merge.py
│   ├── gold-delta-merge-deduplication/SKILL.md           # Dedup before MERGE
│   │   └── references/dedup-patterns.md
│   ├── gold-layer-documentation/SKILL.md                 # Gold doc standards
│   │   ├── references/{documentation-templates,llm-optimization}.md
│   │   └── assets/templates/gold-table-docs.yaml
│   ├── mermaid-erd-patterns/SKILL.md                     # ERD diagrams
│   │   ├── references/erd-syntax-reference.md
│   │   └── assets/templates/erd-template.md
│   ├── gold-layer-schema-validation/SKILL.md             # Schema validation
│   │   ├── references/validation-patterns.md
│   │   └── scripts/validate_schema.py
│   ├── fact-table-grain-validation/SKILL.md              # Grain validation
│   │   ├── references/grain-patterns.md
│   │   └── scripts/validate_grain.py
│   └── yaml-driven-gold-setup/SKILL.md                   # YAML-driven tables
│       └── assets/templates/gold-table-template.yaml
│
├── silver/
│   ├── dlt-expectations-patterns/SKILL.md                # DLT expectations
│   │   ├── references/{expectation-patterns,quarantine-patterns}.md
│   │   └── assets/templates/expectations-config.yaml
│   └── dqx-patterns/SKILL.md                             # DQX framework
│       ├── references/{dqx-configuration,rule-patterns,integration-guide}.md
│       ├── scripts/setup_dqx.py
│       └── assets/templates/dqx-rules.yaml
│
├── ml/
│   └── mlflow-mlmodels-patterns/SKILL.md                 # MLflow patterns
│       ├── references/{experiment-patterns,model-registry,dab-integration,...}.md
│       ├── scripts/setup_experiment.py
│       └── assets/templates/ml-job-config.yaml
│
├── monitoring/
│   ├── lakehouse-monitoring-comprehensive/SKILL.md       # Monitoring guide
│   │   ├── references/{monitor-configuration,custom-metrics,deployment-guide}.md
│   │   └── scripts/create_monitor.py
│   ├── databricks-aibi-dashboards/SKILL.md               # AI/BI dashboards
│   │   ├── references/{dashboard-json-reference,widget-patterns,deployment-guide}.md
│   │   ├── scripts/{deploy_dashboard,validate_*}.py
│   │   └── assets/templates/dashboard-template.json
│   └── sql-alerting-patterns/SKILL.md                    # SQL alerting
│       ├── references/alert-patterns.md
│       └── assets/templates/alert-config.yaml
│
├── planning/
│   └── project-plan-methodology/SKILL.md                 # Project planning
│       ├── references/{phase-details,estimation-guide}.md
│       └── assets/templates/project-plan-template.md
│
├── exploration/
│   └── adhoc-exploration-notebooks/SKILL.md              # Exploration notebooks
│       ├── references/notebook-patterns.md
│       └── assets/templates/exploration-notebook.py
│
├── self-improvement/SKILL.md                             # Agent learning
│   ├── references/LEARNING-FORMAT.md
│   └── scripts/create-skill.sh
│
└── cursor-rule-to-skill/SKILL.md                         # Rule conversion
    ├── references/{CURSOR-RULE-FORMAT,PROGRESSIVE-DISCLOSURE}.md
    └── scripts/convert-rule-to-skill.py
```

---

## Maintenance

When adding new skills:
1. Calculate token size (`wc -l SKILL.md` — roughly lines/2.5 = tokens in K)
2. Ensure SKILL.md is under 500 lines; use references/ for detailed content
3. Assign to appropriate domain
4. Update [references/domain-indexes.md](references/domain-indexes.md) with the new skill
5. Update the Task Detection & Routing Table above
6. Update the Complete Skill Directory Map above
