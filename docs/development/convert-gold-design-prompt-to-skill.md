# Convert Gold Layer Design Prompt to Agent Skill

## Objective

Convert `context/prompts/03a-gold-layer-design-prompt.md` into a properly structured Agent Skill that orchestrates existing Gold layer skills to guide users through the complete Gold layer design process.

## Conversion Instructions

Follow the `cursor-rule-to-skill` methodology to create a new Agent Skill with the following specifications:

### 1. Skill Metadata

```yaml
---
name: gold-layer-design
description: End-to-end orchestrator for designing complete Gold layer schemas with ERDs, YAML files, lineage tracking, and comprehensive business documentation. Guides users through dimensional modeling, ERD creation (master/domain/summary based on table count), YAML schema generation, column-level lineage documentation, business onboarding guide creation, source table mapping, and design validation. Orchestrates mandatory dependencies on Gold skills (mermaid-erd-patterns, yaml-driven-gold-setup, gold-layer-documentation, fact-table-grain-validation, gold-layer-schema-validation, gold-layer-merge-patterns). Use when designing a Gold layer from scratch, creating dimensional models, documenting business processes, or preparing for Gold layer implementation.
license: Apache-2.0
metadata:
  author: databricks-sa
  version: "1.0.0"
  domain: gold-layer
  dependencies:
    - mermaid-erd-patterns
    - yaml-driven-gold-setup
    - gold-layer-documentation
    - fact-table-grain-validation
    - gold-layer-schema-validation
    - gold-layer-merge-patterns
---
```

### 2. Skill Structure

Create the following directory structure:

```
.cursor/skills/gold/gold-layer-design/
├── SKILL.md                                    # Main orchestration workflow
├── references/
│   ├── dimensional-modeling-guide.md          # Extract from Steps 1.1-1.5
│   ├── erd-organization-strategy.md           # Extract from Step 2
│   ├── yaml-schema-patterns.md                # Extract from Step 3
│   ├── lineage-documentation-guide.md         # Extract from Steps 4-5
│   ├── business-documentation-guide.md        # Extract from Steps 7-8
│   └── validation-checklists.md               # Extract validation sections
├── scripts/
│   └── generate_lineage_csv.py                # CSV generation script
└── assets/
    └── templates/
        ├── business-onboarding-template.md    # Section 7 template
        ├── source-table-mapping-template.csv  # Section 8 template
        └── column-lineage-template.csv        # Section 9 template
```

### 3. SKILL.md Content Structure

The main SKILL.md should be structured as follows:

```markdown
# Gold Layer Design Orchestrator

## Overview

This skill orchestrates the complete Gold layer design process, ensuring all mandatory deliverables are created with proper dependencies on specialized Gold layer skills.

## When to Use This Skill

- Designing a Gold layer from scratch
- Creating dimensional models (facts and dimensions)
- Documenting business processes and data lineage
- Preparing for Gold layer implementation
- Generating mandatory documentation (Business Onboarding Guide, Source Table Mapping, Column Lineage CSV)

## Critical Dependencies

This skill orchestrates the following skills (MUST be read and followed):

1. **mermaid-erd-patterns** - ERD creation and organization strategy
2. **yaml-driven-gold-setup** - YAML schema file structure
3. **gold-layer-documentation** - Dual-purpose documentation standards
4. **fact-table-grain-validation** - Grain validation patterns
5. **gold-layer-schema-validation** - Schema consistency validation
6. **gold-layer-merge-patterns** - Future implementation guidance

## Quick Start (4-8 hours)

### Deliverables Checklist

**ERD Organization (based on table count):**
- [ ] Master ERD (erd_master.md) - ALWAYS required
- [ ] Domain ERDs (erd/{domain}.md) - If 9+ tables
- [ ] Summary ERD (erd_summary.md) - If 20+ tables

**YAML Schemas (organized by domain):**
- [ ] gold_layer_design/yaml/{domain}/dim_*.yaml
- [ ] gold_layer_design/yaml/{domain}/fact_*.yaml

**Mandatory Documentation:**
- [ ] ⭐ BUSINESS_ONBOARDING_GUIDE.md - Business processes + stories
- [ ] ⭐ COLUMN_LINEAGE.csv - Machine-readable lineage
- [ ] ⭐ COLUMN_LINEAGE.md - Human-readable lineage
- [ ] ⭐ SOURCE_TABLE_MAPPING.csv - Source table rationale
- [ ] DESIGN_SUMMARY.md - Design decisions
- [ ] DESIGN_GAP_ANALYSIS.md - Coverage analysis
- [ ] README.md - Navigation hub

### ERD Organization Decision

| Tables | Strategy | Required Deliverables |
|--------|----------|----------------------|
| 1-8 | Master only | erd_master.md |
| 9-20 | Master + Domain | erd_master.md + erd/{domain}.md |
| 20+ | Master + Domain + Summary | erd_master.md + erd_summary.md + erd/{domain}.md |

## Step-by-Step Workflow

### Phase 1: Requirements Gathering

**Invoke:** Project context definition

**Collect:**
- Project name and business domain
- Silver schema name
- Gold schema name
- Primary use cases
- Key stakeholders
- Reporting frequency

**Output:** Project requirements document

---

### Phase 2: Dimensional Model Design

**Invoke:** `references/dimensional-modeling-guide.md` patterns

**Activities:**
1. Identify 2-5 dimensions with SCD type decisions
2. Identify 1-3 facts with explicit grain definitions
3. Define measures and metrics with calculation logic
4. Define relationships (FK constraints)
5. Assign tables to domains (Location, Product, Time, Sales, etc.)

**Critical Skill Dependency:** `fact-table-grain-validation`
- Read and apply grain validation patterns
- Document grain type for each fact (transaction, aggregated, snapshot)
- Validate PRIMARY KEY structure matches grain type

**Output:** 
- Dimensions table (with SCD types)
- Facts table (with explicit grains)
- Measures table (with calculation formulas)
- Relationships table (FK mappings)
- Domain assignments table

---

### Phase 3: ERD Creation

**Invoke:** `mermaid-erd-patterns` skill (MANDATORY)

**Read and Follow:** `.cursor/skills/gold/mermaid-erd-patterns/SKILL.md`

**Activities:**
1. Assess table count to determine ERD strategy (1-8, 9-20, 20+)
2. Create Master ERD with all tables grouped by domain
3. Create Domain ERDs (if 9+ tables) with cross-domain references
4. Create Summary ERD (if 20+ tables) showing domain relationships
5. Add Domain Index table to Master ERD

**Critical Rules from mermaid-erd-patterns:**
- Use domain emoji markers (🏪 Location, 📦 Product, 📅 Time, 💰 Sales, 📊 Inventory)
- Use `PK` markers only (no inline descriptions)
- Use `by_{column}` pattern for relationship labels
- Group relationships at the end
- Use bracketed notation for cross-domain references

**Output:**
- `gold_layer_design/erd_master.md` (ALWAYS)
- `gold_layer_design/erd_summary.md` (if 20+ tables)
- `gold_layer_design/erd/erd_{domain}.md` (if 9+ tables)

---

### Phase 4: YAML Schema Generation

**Invoke:** `yaml-driven-gold-setup` skill (MANDATORY)

**Read and Follow:** `.cursor/skills/gold/yaml-driven-gold-setup/SKILL.md`

**Activities:**
1. Create domain-organized YAML directory structure
2. Generate one YAML file per table following the template
3. Include complete column definitions with lineage
4. Document PRIMARY KEY and FOREIGN KEY constraints
5. Apply standard table properties

**Invoke:** `gold-layer-documentation` skill (MANDATORY)

**Read and Follow:** `.cursor/skills/gold/gold-layer-documentation/SKILL.md`

**Critical Rules:**
- Dual-purpose descriptions (business + technical) for ALL columns
- Pattern: `[Definition]. Business: [context]. Technical: [details].`
- Surrogate keys as PRIMARY KEYS (not business keys)
- Include all required TBLPROPERTIES (layer, domain, entity_type, etc.)
- Document grain for facts, SCD type for dimensions

**Output:**
- `gold_layer_design/yaml/{domain}/{table}.yaml` for each table
- Domain-organized folder structure
- Complete lineage metadata in each YAML

---

### Phase 5: Column-Level Lineage Documentation

**Invoke:** `references/lineage-documentation-guide.md`

**Activities:**
1. Extract lineage from all YAML files
2. Document Bronze → Silver → Gold mapping for EVERY column
3. Specify transformation type (DIRECT_COPY, RENAME, AGGREGATE_SUM, etc.)
4. Document transformation logic (executable PySpark/SQL)
5. Generate both CSV and Markdown formats

**Critical Fields:**
- bronze_table, bronze_column
- silver_table, silver_column
- transformation_type (from standard list)
- transformation_logic (explicit expression)
- aggregation_logic (if aggregated)
- groupby_columns (if aggregated)

**Use Script:** `scripts/generate_lineage_csv.py`

**Output:**
- `gold_layer_design/COLUMN_LINEAGE.csv` (machine-readable, MANDATORY)
- `gold_layer_design/COLUMN_LINEAGE.md` (human-readable)

---

### Phase 6: Business Onboarding Guide (MANDATORY)

**Invoke:** `references/business-documentation-guide.md`

**Use Template:** `assets/templates/business-onboarding-template.md`

**Required Sections:**
1. Introduction to Business Domain
2. The Business Lifecycle (Key Stages)
3. Key Business Entities (Players/Actors)
4. The Gold Layer Data Model (Overview)
5. Business Processes & Tracking (DETAILED with ASCII flow diagrams)
   - 5B. Real-World Scenarios: Following the Data (3-4 STORIES)
6. Analytics Use Cases
7. AI & ML Opportunities
8. Self-Service Analytics with Genie
9. Data Quality & Monitoring
10. Getting Started (per role)

**Critical Requirements:**
- Each business process MUST have ASCII flow diagram
- Each process MUST show Source Tables → Gold Tables mapping
- Section 5B MUST include 3-4 detailed stories with:
  - Business context
  - 4-6 chapters (stages)
  - Source system data examples
  - Gold layer updates at each stage
  - Analytics impact
  - Timeline visualization

**Output:**
- `gold_layer_design/docs/BUSINESS_ONBOARDING_GUIDE.md` (MANDATORY)

---

### Phase 7: Source Table Mapping (MANDATORY)

**Use Template:** `assets/templates/source-table-mapping-template.csv`

**Activities:**
1. List ALL source tables (included, excluded, planned)
2. Document status for each (INCLUDED, EXCLUDED, PLANNED)
3. Provide rationale for EVERY inclusion/exclusion decision
4. Map included tables to Gold tables
5. Assign domains and phases

**Required Fields:**
- source_table, source_description
- status (INCLUDED, EXCLUDED, PLANNED)
- gold_table (or N/A if excluded)
- domain, entity_type
- rationale (REQUIRED for all)
- phase, priority

**Standard Exclusion Rationales:**
- "System/audit table - no business value"
- "Historical archive - superseded by {table}"
- "Duplicate data available in {table}"
- "Out of scope for {project} phase {N}"

**Output:**
- `gold_layer_design/SOURCE_TABLE_MAPPING.csv` (MANDATORY)

---

### Phase 8: Design Validation

**Invoke:** `gold-layer-schema-validation` skill

**Read and Follow:** `.cursor/skills/gold/gold-layer-schema-validation/SKILL.md`

**Validation Activities:**
1. Consistency check: YAML ↔ ERD ↔ Lineage CSV
2. Validate all columns in ERD exist in YAML
3. Validate all YAML columns have lineage metadata
4. Validate PRIMARY KEY definitions
5. Validate FOREIGN KEY references
6. Run validation script

**Invoke:** Complete validation checklist from prompt

**Validation Categories:**
- [ ] Dimensional Model (dimensions, facts, SCD, grain, measures, relationships, domains)
- [ ] ERD Organization (table count, Master/Domain/Summary ERDs, Domain Index)
- [ ] YAML Schemas (domain-organized, complete columns, PKs, FKs, lineage)
- [ ] Column Lineage (Bronze → Silver → Gold mapping, transformation types)
- [ ] Mandatory Documentation (Business Onboarding, Source Mapping, Lineage CSV)

**Output:**
- Validation report
- List of inconsistencies to fix
- Design sign-off checklist

---

### Phase 9: Stakeholder Review

**Activities:**
1. Present ERD hierarchy to stakeholders
2. Review grain definitions for each fact
3. Confirm measures are complete
4. Validate naming conventions
5. Review Business Onboarding Guide stories
6. Obtain design sign-off

**Output:**
- Stakeholder approval document
- Design sign-off record

---

## Mandatory Deliverables Summary

### ERD Deliverables (Based on Table Count)

| Tables | Required Files |
|--------|----------------|
| 1-8 | erd_master.md |
| 9-20 | erd_master.md + erd/{domain}.md |
| 20+ | erd_master.md + erd_summary.md + erd/{domain}.md |

### Schema Deliverables

- YAML Schema Files (domain-organized)

### Lineage & Mapping (ALL MANDATORY)

- ⭐ COLUMN_LINEAGE.csv (machine-readable)
- COLUMN_LINEAGE.md (human-readable)
- ⭐ SOURCE_TABLE_MAPPING.csv (rationale for all tables)

### Business Documentation (ALL MANDATORY)

- ⭐ BUSINESS_ONBOARDING_GUIDE.md (processes + stories)
- DESIGN_SUMMARY.md (design decisions)
- DESIGN_GAP_ANALYSIS.md (coverage analysis)
- README.md (navigation hub)

### Final File Organization

```
gold_layer_design/
├── README.md                                   # ⭐ Navigation hub
├── erd_master.md                               # ⭐ Complete ERD (ALWAYS)
├── erd_summary.md                              # Domain overview (20+ tables)
├── erd/                                        # Domain ERDs (9+ tables)
│   └── erd_{domain}.md
├── yaml/                                       # Domain-organized schemas
│   └── {domain}/
│       └── {table}.yaml
├── docs/
│   └── BUSINESS_ONBOARDING_GUIDE.md            # ⭐ MANDATORY
├── COLUMN_LINEAGE.csv                          # ⭐ MANDATORY
├── COLUMN_LINEAGE.md                           # Human-readable
├── SOURCE_TABLE_MAPPING.csv                    # ⭐ MANDATORY
├── DESIGN_SUMMARY.md                           # Design decisions
└── DESIGN_GAP_ANALYSIS.md                      # Coverage analysis
```

## Key Design Principles

### 1. Schema Extraction Over Generation

**Critical:** Always extract table/column names from existing YAML schemas. NEVER generate from scratch.

**Why:** Prevents hallucinations, schema mismatches, and broken references.

**Pattern:**
```python
# ✅ CORRECT: Extract from YAML
with open("gold_layer_design/yaml/billing/dim_sku.yaml") as f:
    schema = yaml.safe_load(f)
    columns = [col['name'] for col in schema['columns']]

# ❌ WRONG: Generate/guess
columns = ["sku_name", "sku_type"]  # Might be wrong!
```

### 2. YAML as Single Source of Truth

All column names, types, constraints, and descriptions MUST be defined in YAML first. Implementation scripts read from YAML.

### 3. Dual-Purpose Documentation

ALL descriptions serve both business users and technical users (including LLMs like Genie). No "LLM:" prefix needed.

### 4. Progressive Disclosure

Core workflow in SKILL.md (under 500 lines). Detailed patterns in references/. Templates in assets/.

### 5. Dependency Orchestration

This skill orchestrates specialized skills. Always read and follow dependency skills:
- mermaid-erd-patterns (ERD syntax, organization)
- yaml-driven-gold-setup (YAML structure)
- gold-layer-documentation (description standards)
- fact-table-grain-validation (grain patterns)
- gold-layer-schema-validation (validation patterns)
- gold-layer-merge-patterns (future implementation guidance)

## Common Mistakes to Avoid

### ❌ Mistake 1: Skipping Mandatory Documentation

All three are MANDATORY:
- BUSINESS_ONBOARDING_GUIDE.md
- SOURCE_TABLE_MAPPING.csv
- COLUMN_LINEAGE.csv

**Impact:** 2-3 weeks ramp-up time, scope creep, 33% implementation bugs.

### ❌ Mistake 2: Wrong ERD Organization

Don't create Domain ERDs for simple models (1-8 tables). Don't skip Summary ERD for large models (20+ tables).

### ❌ Mistake 3: Incomplete Column Lineage

Every column MUST have Bronze → Silver → Gold mapping with transformation type and logic.

### ❌ Mistake 4: No Grain Documentation

Every fact table MUST have explicit grain documented in YAML and validated.

### ❌ Mistake 5: Generic Business Documentation

Business Onboarding Guide MUST include real-world stories showing actual data flow through source systems to Gold tables.

## Time Estimates

- 3-4 hours for 1-8 tables (Master ERD only)
- 5-6 hours for 9-20 tables (Master + Domain ERDs)
- 6-10 hours for 20+ tables (Full ERD hierarchy + comprehensive documentation)

**Breakdown (20+ tables):**
- ERDs + YAML schemas: 3-4 hours
- Business Onboarding Guide: 2-3 hours
- Source Table Mapping: 1-2 hours
- Column Lineage CSV: 1-2 hours
- Review & validation: 1 hour

## Next Steps

After completing design and obtaining stakeholder sign-off:
1. Deploy YAML schemas to Databricks workspace
2. Use `yaml-driven-gold-setup` to create tables
3. Use `gold-layer-merge-patterns` to implement merge scripts
4. Use `gold-layer-schema-validation` to validate merge DataFrames

## References

- [AgentSkills.io Specification](https://agentskills.io/specification)
- [Kimball Dimensional Modeling](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)
- [Unity Catalog Constraints](https://docs.databricks.com/data-governance/unity-catalog/constraints.html)
- [Mermaid ERD Syntax](https://mermaid.js.org/syntax/entityRelationshipDiagram.html)
```

### 4. Reference Files to Extract

Create the following reference files by extracting and organizing content from the original prompt:

1. **references/dimensional-modeling-guide.md** - Extract Steps 1.1-1.5 (Dimensions, Facts, Measures, Relationships, Domains)
2. **references/erd-organization-strategy.md** - Extract Step 2 (ERD organization patterns)
3. **references/yaml-schema-patterns.md** - Extract Step 3 (YAML structure and examples)
4. **references/lineage-documentation-guide.md** - Extract Steps 4-5 (Column lineage patterns and CSV generation)
5. **references/business-documentation-guide.md** - Extract Steps 7-8 (Business Onboarding Guide and Source Table Mapping)
6. **references/validation-checklists.md** - Extract all validation checklists

### 5. Scripts to Create

Create `scripts/generate_lineage_csv.py` by extracting the Python code from Step 5.3 of the original prompt.

### 6. Assets/Templates to Create

1. **assets/templates/business-onboarding-template.md** - Template structure from Step 7.2
2. **assets/templates/source-table-mapping-template.csv** - CSV template from Step 8.2
3. **assets/templates/column-lineage-template.csv** - CSV template from Step 9.2

### 7. Validation Requirements

Before finalizing the skill:

- [ ] `name` is lowercase with hyphens: `gold-layer-design`
- [ ] `description` is under 1024 chars and includes WHAT and WHEN
- [ ] SKILL.md body is under 500 lines (detailed content in references/)
- [ ] All 6 dependency skills are explicitly referenced
- [ ] Progressive disclosure pattern used (main workflow in SKILL, details in references)
- [ ] All mandatory deliverables clearly identified with ⭐ markers
- [ ] ERD organization decision tree is prominent
- [ ] Schema extraction principle is emphasized
- [ ] Validation checklist references other skills
- [ ] File organization structure is complete

## Execution Steps

1. **Read the cursor-rule-to-skill skill** to understand conversion methodology
2. **Create the skill directory structure** as specified above
3. **Write the main SKILL.md** following the structure provided
4. **Extract content to reference files** from the original prompt
5. **Create template files** in assets/templates/
6. **Create the Python script** in scripts/
7. **Validate the skill** using the checklist above
8. **Test the skill** by having a user attempt to design a small Gold layer

## Success Criteria

The converted skill is successful when:
- A user can follow it to complete an entire Gold layer design
- All mandatory deliverables are created (3 starred items)
- ERD organization adapts to table count (1-8, 9-20, 20+)
- All dependency skills are properly orchestrated
- YAML schemas become the single source of truth
- Column lineage prevents implementation bugs
- Business Onboarding Guide enables quick team onboarding
