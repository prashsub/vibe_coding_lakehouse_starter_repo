---
name: gold-layer-design
description: End-to-end orchestrator for designing complete Gold layer schemas with ERDs, YAML files, lineage tracking, and comprehensive business documentation. Guides users through dimensional modeling, ERD creation (master/domain/summary based on table count), YAML schema generation, column-level lineage documentation, business onboarding guide creation, source table mapping, and design validation. Orchestrates mandatory dependencies on Gold skills (mermaid-erd-patterns, yaml-driven-gold-setup, gold-layer-documentation, fact-table-grain-validation, gold-layer-schema-validation, gold-layer-merge-patterns). Use when designing a Gold layer from scratch, creating dimensional models, documenting business processes, or preparing for Gold layer implementation.
license: Apache-2.0
metadata:
  author: databricks-sa
  version: "1.0.0"
  domain: gold
  dependencies:
    - mermaid-erd-patterns
    - yaml-driven-gold-setup
    - gold-layer-documentation
    - fact-table-grain-validation
    - gold-layer-schema-validation
    - gold-layer-merge-patterns
---

# Gold Layer Design Orchestrator

This skill orchestrates the complete Gold layer design process, ensuring all mandatory deliverables are created with proper dependencies on specialized Gold layer skills.

## When to Use This Skill

- Designing a Gold layer from scratch for a new project
- Creating dimensional models (facts and dimensions)
- Documenting business processes and data lineage
- Preparing for Gold layer implementation (before `03b-gold-layer-implementation-prompt`)
- Generating mandatory documentation (Business Onboarding Guide, Source Table Mapping, Column Lineage CSV)

## Critical Dependencies (Read at Indicated Phase)

This skill orchestrates the following skills. Each MUST be read and followed at the phase where it is invoked:

| Skill | Read At | Purpose |
|-------|---------|---------|
| `fact-table-grain-validation` | Phase 2 | Grain validation for fact tables |
| `mermaid-erd-patterns` | Phase 3 | ERD creation and organization strategy |
| `yaml-driven-gold-setup` | Phase 4 | YAML schema file structure and setup script |
| `gold-layer-documentation` | Phase 4 | Dual-purpose documentation standards |
| `gold-layer-schema-validation` | Phase 8 | Schema consistency validation |
| `gold-layer-merge-patterns` | Next Steps | Future implementation guidance |

## Quick Start (4-8 hours)

### Deliverables Checklist

**ERD Organization (based on table count):**
- [ ] Master ERD (`erd_master.md`) - ALWAYS required
- [ ] Domain ERDs (`erd/erd_{domain}.md`) - If 9+ tables
- [ ] Summary ERD (`erd_summary.md`) - If 20+ tables

**YAML Schemas (organized by domain):**
- [ ] `gold_layer_design/yaml/{domain}/dim_*.yaml` - Dimension schemas
- [ ] `gold_layer_design/yaml/{domain}/fact_*.yaml` - Fact schemas

**Mandatory Documentation (ALL required):**
- [ ] BUSINESS_ONBOARDING_GUIDE.md - Business processes + real-world stories
- [ ] COLUMN_LINEAGE.csv - Machine-readable column lineage
- [ ] COLUMN_LINEAGE.md - Human-readable lineage
- [ ] SOURCE_TABLE_MAPPING.csv - Source table inclusion/exclusion rationale
- [ ] DESIGN_SUMMARY.md - Design decisions
- [ ] DESIGN_GAP_ANALYSIS.md - Coverage analysis
- [ ] README.md - Navigation hub

### ERD Organization Decision

| Tables | Strategy | Required Deliverables |
|--------|----------|----------------------|
| 1-8 | Master only | `erd_master.md` |
| 9-20 | Master + Domain | `erd_master.md` + `erd/erd_{domain}.md` |
| 20+ | Master + Domain + Summary | `erd_master.md` + `erd_summary.md` + `erd/erd_{domain}.md` |

---

## Step-by-Step Workflow

### Phase 1: Requirements Gathering

**Collect the following project context:**

| Field | Example |
|-------|---------|
| Project Name | `retail_analytics` |
| Silver Schema | `my_project_silver` |
| Gold Schema | `my_project_gold` |
| Business Domain | `retail`, `healthcare`, `finance` |
| Primary Use Cases | sales reporting, inventory analysis |
| Key Stakeholders | Sales Ops, Finance Team |
| Reporting Frequency | Daily, Weekly, Monthly |

**Output:** Populated project context document

---

### Phase 2: Dimensional Model Design

**Read and Follow:** `references/dimensional-modeling-guide.md`

**Activities:**
1. Identify 2-5 dimensions with SCD type decisions (Type 1 vs Type 2)
2. Identify 1-3 facts with explicit grain definitions
3. Define measures and metrics with calculation logic
4. Define relationships (FK constraints)
5. Assign tables to domains (Location, Product, Time, Sales, etc.)

**MANDATORY: Read this skill using the Read tool BEFORE defining fact table grains:**

1. `.cursor/skills/gold/fact-table-grain-validation/SKILL.md` — Grain inference from PRIMARY KEY structure, transaction vs aggregated vs snapshot patterns, PK-grain decision tree

**Apply from skill:**
- Infer grain type from PRIMARY KEY structure (transaction, aggregated, snapshot)
- Document grain explicitly for each fact table
- Validate PRIMARY KEY matches grain type using decision tree

**Key Outputs:**
- Dimensions table (name, business key, SCD type, source Silver table)
- Facts table (name, grain, source Silver tables, update frequency)
- Measures table (name, data type, calculation logic, business purpose)
- Relationships table (fact FK → dimension PK, cardinality)
- Domain assignments table (table → domain mapping)

---

### Phase 3: ERD Creation

**MANDATORY: Read this skill using the Read tool BEFORE creating any ERD diagrams:**

1. `.cursor/skills/gold/mermaid-erd-patterns/SKILL.md` — ERD organization strategy (master/domain/summary), Mermaid syntax standards, domain emoji markers, relationship patterns, cross-domain references

**Activities:**
1. Count tables to determine ERD strategy (1-8, 9-20, 20+)
2. Create Master ERD (`erd_master.md`) with ALL tables grouped by domain
3. Create Domain ERDs (`erd/erd_{domain}.md`) if 9+ tables
4. Create Summary ERD (`erd_summary.md`) if 20+ tables
5. Add Domain Index table to Master ERD

**Critical Rules (from mermaid-erd-patterns):**
- Use domain emoji markers (🏪 Location, 📦 Product, 📅 Time, 💰 Sales, 📊 Inventory)
- Use `PK` markers only (no inline descriptions in ERD)
- Use `by_{column}` pattern for relationship labels
- Group all relationships at end of diagram
- Use bracketed notation for cross-domain references: `dim_store["🏪 dim_store (Location)"]`

**Outputs:**
- `gold_layer_design/erd_master.md` (ALWAYS)
- `gold_layer_design/erd_summary.md` (if 20+ tables)
- `gold_layer_design/erd/erd_{domain}.md` (if 9+ tables)

---

### Phase 4: YAML Schema Generation

**MANDATORY: Read each skill below using the Read tool BEFORE generating any YAML schema files:**

1. `.cursor/skills/gold/yaml-driven-gold-setup/SKILL.md` — YAML schema file structure, domain-organized directories, column definition format, PK/FK in YAML
2. `.cursor/skills/gold/gold-layer-documentation/SKILL.md` — Dual-purpose description pattern (`[Definition]. Business: [...]. Technical: [...].`), surrogate key naming, TBLPROPERTIES metadata, column comment standards

**Activities:**
1. Create domain-organized YAML directory structure (`yaml/{domain}/`)
2. Generate one YAML file per table using templates from `yaml-driven-gold-setup`
3. Include complete column definitions with lineage metadata
4. Document PRIMARY KEY and FOREIGN KEY constraints
5. Apply standard table properties (CDF, row tracking, auto-optimize)
6. Write dual-purpose descriptions following `gold-layer-documentation` patterns

**Critical Rules (from gold-layer-documentation):**
- Pattern: `[Definition]. Business: [context]. Technical: [details].`
- Surrogate keys as PRIMARY KEYS (not business keys)
- Include all TBLPROPERTIES (layer, domain, entity_type, grain, scd_type, etc.)
- Every column MUST have a `lineage:` section

**YAML Template Reference:** See `references/yaml-schema-patterns.md`

**Outputs:**
- `gold_layer_design/yaml/{domain}/{table}.yaml` for each table
- Domain-organized folder structure matching ERD domains

---

### Phase 5: Column-Level Lineage Documentation

**Read:** `references/lineage-documentation-guide.md`

**Activities:**
1. Extract lineage from all YAML files
2. Document Bronze → Silver → Gold mapping for EVERY column
3. Specify transformation type from standard list (DIRECT_COPY, RENAME, CAST, AGGREGATE_SUM, AGGREGATE_SUM_CONDITIONAL, AGGREGATE_COUNT, DERIVED_CALCULATION, HASH_MD5, COALESCE, DATE_TRUNC, GENERATED, LOOKUP)
4. Document transformation logic as executable PySpark/SQL
5. Generate both CSV and Markdown formats

**Use Script:** `scripts/generate_lineage_csv.py`

**Outputs:**
- `gold_layer_design/COLUMN_LINEAGE.csv` (machine-readable, MANDATORY)
- `gold_layer_design/COLUMN_LINEAGE.md` (human-readable)

---

### Phase 6: Business Onboarding Guide (MANDATORY)

**Read:** `references/business-documentation-guide.md`  
**Use Template:** `assets/templates/business-onboarding-template.md`

**Required Sections:**
1. Introduction to Business Domain
2. The Business Lifecycle (Key Stages)
3. Key Business Entities (Players/Actors)
4. The Gold Layer Data Model (Overview)
5. Business Processes & Tracking (with ASCII flow diagrams)
   - 5B. Real-World Scenarios (minimum 3-4 detailed stories)
6. Analytics Use Cases
7. AI & ML Opportunities
8. Self-Service Analytics with Genie
9. Data Quality & Monitoring
10. Getting Started (per role: Engineer, Analyst, Scientist, Business User)

**Critical:** Each story must show source system data → Gold layer updates → analytics impact at each stage.

**Output:** `gold_layer_design/docs/BUSINESS_ONBOARDING_GUIDE.md`

---

### Phase 7: Source Table Mapping (MANDATORY)

**Use Template:** `assets/templates/source-table-mapping-template.csv`

**Activities:**
1. List ALL source tables (included, excluded, planned)
2. Assign status: INCLUDED, EXCLUDED, or PLANNED
3. Provide rationale for EVERY row (required, no exceptions)
4. Map INCLUDED tables to Gold tables
5. Assign domains and implementation phases

**Output:** `gold_layer_design/SOURCE_TABLE_MAPPING.csv`

---

### Phase 8: Design Validation

**MANDATORY: Read this skill using the Read tool BEFORE running design validation:**

1. `.cursor/skills/gold/gold-layer-schema-validation/SKILL.md` — Schema consistency validation, DDL-first workflow, column matching between YAML and ERD

**Also read:** `references/validation-checklists.md`

**Validation Activities:**
1. Consistency check: YAML ↔ ERD ↔ Lineage CSV (all columns match)
2. Validate all ERD columns exist in YAML definitions
3. Validate all YAML columns have lineage metadata
4. Validate PRIMARY KEY definitions match grain type
5. Validate FOREIGN KEY references point to valid tables/columns
6. Run lineage validation script

**Outputs:**
- Validation report (pass/fail for each category)
- List of inconsistencies to fix
- Completed design sign-off checklist

---

### Phase 9: Stakeholder Review

**Activities:**
1. Present ERD hierarchy to business stakeholders
2. Review grain definitions for each fact table
3. Confirm measures are complete for reporting needs
4. Validate naming conventions with data governance
5. Review Business Onboarding Guide stories for accuracy
6. Obtain formal design sign-off

**Output:** Stakeholder approval document

---

## Final File Organization

```
gold_layer_design/
├── README.md                          # Navigation hub
├── erd_master.md                      # Complete ERD (ALWAYS)
├── erd_summary.md                     # Domain overview (20+ tables)
├── erd/                               # Domain ERDs (9+ tables)
│   └── erd_{domain}.md
├── yaml/                              # Domain-organized schemas
│   └── {domain}/
│       └── {table}.yaml
├── docs/
│   └── BUSINESS_ONBOARDING_GUIDE.md   # MANDATORY
├── COLUMN_LINEAGE.csv                 # MANDATORY
├── COLUMN_LINEAGE.md                  # Human-readable
├── SOURCE_TABLE_MAPPING.csv           # MANDATORY
├── DESIGN_SUMMARY.md                  # Design decisions
└── DESIGN_GAP_ANALYSIS.md            # Coverage analysis
```

## Key Design Principles

1. **Schema Extraction Over Generation** - Always extract table/column names from YAML. Never generate from scratch. Prevents hallucinations and schema mismatches.

2. **YAML as Single Source of Truth** - All column names, types, constraints, descriptions defined in YAML first. Implementation reads YAML.

3. **Dual-Purpose Documentation** - ALL descriptions serve both business users and technical users (including LLMs like Genie). Pattern: `[Definition]. Business: [...]. Technical: [...].`

4. **Progressive Disclosure** - Core workflow here in SKILL.md. Detailed patterns in `references/`. Templates in `assets/templates/`.

5. **Dependency Orchestration** - Read and follow dependency skills at the phase indicated. Don't skip dependency skills.

## Common Mistakes to Avoid

| Mistake | Impact | Prevention |
|---------|--------|------------|
| Skipping mandatory docs | 2-3 weeks ramp-up time wasted | Always create all 3 starred deliverables |
| Wrong ERD organization | Unreadable diagrams or unnecessary complexity | Follow table count decision tree |
| Incomplete column lineage | 33% of implementation bugs | Every column needs Bronze → Silver → Gold mapping |
| No grain documentation | Table rewrite required | Document grain in every fact YAML |
| Generic business docs | Slow analytics adoption | Include real-world stories with data flow |

## Time Estimates

| Complexity | Tables | Time |
|-----------|--------|------|
| Small | 1-8 | 3-4 hours |
| Medium | 9-20 | 5-6 hours |
| Large | 20+ | 6-10 hours |

## Next Steps After Design

After completing design and obtaining stakeholder sign-off, **read the implementation orchestrator skill:**

1. `.cursor/skills/gold/gold-layer-implementation/SKILL.md` — End-to-end implementation of tables, merge scripts, FK constraints, and Asset Bundle jobs from the YAML designs created here

That skill will in turn invoke:
- `gold-layer-merge-patterns` — SCD Type 1/2 dimension merges, fact aggregation patterns
- `gold-delta-merge-deduplication` — Mandatory deduplication before MERGE
- All other implementation dependencies

## Reference Files

- **[Dimensional Modeling Guide](references/dimensional-modeling-guide.md)** - Dimensions, facts, measures, relationships, domain assignment
- **[ERD Organization Strategy](references/erd-organization-strategy.md)** - Master/Domain/Summary ERD patterns
- **[YAML Schema Patterns](references/yaml-schema-patterns.md)** - YAML templates for dimensions, facts, date dimensions
- **[Lineage Documentation Guide](references/lineage-documentation-guide.md)** - Column lineage, transformation types, CSV generation
- **[Business Documentation Guide](references/business-documentation-guide.md)** - Business Onboarding Guide and Source Table Mapping
- **[Validation Checklists](references/validation-checklists.md)** - All design validation checklists

## External References

- [Kimball Dimensional Modeling](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)
- [Unity Catalog Constraints](https://docs.databricks.com/data-governance/unity-catalog/constraints.html)
- [Mermaid ERD Syntax](https://mermaid.js.org/syntax/entityRelationshipDiagram.html)
- [AgentSkills.io Specification](https://agentskills.io/specification)
