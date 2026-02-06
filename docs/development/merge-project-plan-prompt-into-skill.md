# Merge Project Plan Prompt into Project Plan Methodology Skill

## Objective

Merge all unique content from `context/prompts/11-project-plan-prompt.md` into the existing `.cursor/skills/planning/project-plan-methodology/` skill (SKILL.md + references + assets), preserving 100% of functionality from BOTH files.

After the merge, the skill alone must be able to reproduce everything the prompt + skill combination could do before.

## Source Material

- **Source Prompt:** `context/prompts/11-project-plan-prompt.md` (1375 lines — interactive templates, worked examples, phase document templates)
- **Existing Skill:** `.cursor/skills/planning/project-plan-methodology/SKILL.md` (391 lines — methodology, standards, anti-patterns)
- **Existing References:**
  - `references/phase-details.md` (131 lines — abbreviated phase descriptions)
  - `references/estimation-guide.md` (75 lines — effort estimation, dependency management, risks)
  - `assets/templates/project-plan-template.md` (204 lines — single generic template)

## Critical Context

- These two files worked in **harmony** before — the prompt provided interactive templates/examples, the skill provided methodology/standards
- The skill currently **hardcodes system table domains** (Cost, Security, Performance, Reliability, Quality). The prompt uses **generic parameterized domains** ({Domain 1}, {Domain 2}). The merged skill MUST be generic/parameterized with system tables as ONE example
- Follow the same orchestrator pattern used by `gold-layer-design` and `gold-layer-implementation` skills (phased workflow, dependency orchestration, progressive disclosure)

## Pre-Merge: Content Inventory (Read BOTH files completely and verify this inventory)

### Content UNIQUE to the Prompt (MUST be absorbed)

| # | Content | Prompt Lines | Destination |
|---|---------|-------------|-------------|
| P1 | Quick Start (5-min fill-in-the-blank) | 7-25 | SKILL.md — new Quick Start section |
| P2 | Key Decisions Table (7 upfront choices) | 27-38 | SKILL.md — new Quick Start section |
| P3 | Project Information Input Form | 42-51 | SKILL.md — Phase 1 Requirements |
| P4 | Prerequisites Status Table | 53-59 | SKILL.md — Phase 1 Requirements |
| P5 | Agent Domain Input Table (fill-in) | 63-71 | SKILL.md — Phase 1 Requirements |
| P6 | Industry-Specific Domain Patterns (5 industries) | 73-82 | references/industry-domain-patterns.md |
| P7 | Phase 1 Addendum Selection Table | 86-96 | SKILL.md — Phase 1 Requirements |
| P8 | Key Business Questions Template | 98-111 | SKILL.md — Phase 1 Requirements |
| P9 | "Why Genie Spaces" Comparison Table (8 rows) | 179-188 | references/agent-layer-architecture.md |
| P10 | Prerequisites Summary Template | 224-275 | assets/templates/prerequisites-template.md |
| P11 | Phase 1 Use Cases Master Template | 279-383 | assets/templates/phase1-use-cases-template.md |
| P12 | Phase 1 Addendum 1.2 TVFs Template | 391-469 | assets/templates/phase1-tvfs-template.md |
| P13 | Phase 1 Addendum 1.7 Alerting Template | 473-534 | assets/templates/phase1-alerting-template.md |
| P14 | Phase 1 Addendum 1.6 Genie Spaces Template | 538-660 | assets/templates/phase1-genie-spaces-template.md |
| P15 | Phase 2 Agent Framework Template | 666-824 | assets/templates/phase2-agent-framework-template.md |
| P16 | Phase 3 Frontend App Template | 828-861 | assets/templates/phase3-frontend-template.md |
| P17 | README.md Template | 867-946 | assets/templates/plans-readme-template.md |
| P18 | Agent Layer Architecture (detailed) + comparison table | 950-981 | references/agent-layer-architecture.md |
| P19 | Wanderbricks Example — full project (domains, prerequisites, 101+ artifacts, TVFs by domain, metric views, ML models, dashboards, agent-genie mapping, business questions, architecture flow) | 984-1160 | references/worked-example-wanderbricks.md |
| P20 | Example TVF SQL (`get_revenue_trend`) | 1164-1196 | references/worked-example-wanderbricks.md |
| P21 | Example Metric View YAML (`revenue_analytics_metrics`) | 1200-1252 | references/worked-example-wanderbricks.md |
| P22 | Example Alert YAML (`REV-001-CRIT`) | 1256-1291 | references/worked-example-wanderbricks.md |
| P23 | Key Learnings: Agent Layer Architecture (6 reasons, 3 design patterns, system prompt derivation, three-level testing) | 1296-1341 | references/agent-layer-architecture.md |
| P24 | References: Related Prompts (8 links) | 1348-1355 | SKILL.md — References (update to skill links where applicable) |
| P25 | References: Agent Framework Technologies (LangChain, LangGraph) | 1373-1374 | SKILL.md — References |

### Content UNIQUE to the Skill (MUST be preserved)

| # | Content | Skill Lines | Action |
|---|---------|-------------|--------|
| S1 | Skill Metadata (name, description, version, domain) | 1-8 | KEEP and UPDATE description |
| S2 | "When to Use" section (5 use cases) | 16-22 | KEEP |
| S3 | Standard Agent Domains table (Cost/Security/Performance/Reliability/Quality with system table refs) | 77-84 | GENERALIZE — make parameterized, move system tables example to references/industry-domain-patterns.md |
| S4 | Agent Domain Application rules (4 rules + example pattern) | 87-100 | KEEP |
| S5 | Genie Space → Agent Mapping (with specific artifact counts) | 131-141 | GENERALIZE — make parameterized, keep specific counts in references/worked-example-wanderbricks.md OR industry-domain-patterns.md |
| S6 | Artifact Count Standards (per domain minimums + naming conventions) | 177-202 | KEEP |
| S7 | SQL Query Standards (Gold layer pattern, variables, SCD2 joins) | 204-232 | KEEP |
| S8 | Documentation Quality Standards (LLM-friendly comments, summary tables) | 234-256 | KEEP |
| S9 | Common Mistakes (5 anti-patterns with code examples) | 258-295 | KEEP |
| S10 | Estimation Guide reference | 297-300 | KEEP (file stays) |
| S11 | Validation Checklist (Structure 6, Content Quality 5, Cross-Refs 4, Completeness 4) | 328-357 | MERGE with prompt's more comprehensive checklist (P18) |
| S12 | Key Learnings (15 items — methodology-focused) | 374-391 | MERGE with prompt's architecture learnings (P23) |
| S13 | References: Official Docs (5 links) | 358-366 | MERGE with prompt's doc links |
| S14 | References: Related Cursor Rules (5 links) | 368-372 | UPDATE to skill links where applicable |

### Content in BOTH (Overlap — MERGE carefully)

| Content | Prompt Adds | Skill Has | Merge Strategy |
|---------|-------------|-----------|----------------|
| Plan Structure (folder layout) | Generic `{project}` | Specific system tables | Use GENERIC from prompt |
| Phase Dependencies diagram | Same | Same | Keep one copy |
| Agent Layer Architecture | Detailed ASCII + "Why Genie" table + 3 design patterns | Simpler ASCII | Use PROMPT version (richer), move to reference |
| Agent-Genie Mapping | Generic template with `{Domain}` | Specific counts (Cost: 15 TVFs, etc.) | Generic in SKILL, specific in reference |
| Deployment Order | Generic | Specific counts (60 TVFs, etc.) | Generic in SKILL, specific in reference |
| Testing Strategy | 3 levels with checklists + success criteria | 3 levels table (abbreviated) | Use PROMPT version (richer) |
| Validation Checklist | 22 items including Agent Layer checks | 19 items | MERGE both — keep all unique items |
| Key Learnings | Architecture-focused (6 + patterns) | Methodology-focused (15 items) | Combine both into single section |

## Conversion Instructions

### 1. Updated Skill Metadata

```yaml
---
name: project-plan-methodology
description: >-
  Create multi-phase project plans for Databricks data platform solutions 
  with Agent Domain Framework and Agent Layer Architecture. Includes interactive 
  Quick Start with key decisions, industry-specific domain patterns, complete 
  phase document templates (Use Cases, Agents, Frontend), Genie Space integration 
  patterns, deployment order requirements, and worked examples. Use when planning 
  any Databricks solution post-Gold layer — observability, analytics, agent-based 
  frameworks, or multi-artifact projects.
metadata:
  author: databricks-sa
  version: "2.0"
  domain: planning
---
```

### 2. Target Directory Structure

```
.cursor/skills/planning/project-plan-methodology/
├── SKILL.md                                    # REWRITE (methodology + quick start + workflow)
├── references/
│   ├── phase-details.md                        # EXPAND (full addendum details from prompt)
│   ├── estimation-guide.md                     # KEEP as-is
│   ├── agent-layer-architecture.md             # NEW (detailed architecture, "Why Genie", design patterns, testing strategy, key learnings)
│   ├── industry-domain-patterns.md             # NEW (5 industry patterns + system tables as one example)
│   └── worked-example-wanderbricks.md          # NEW (complete Wanderbricks example + example TVF SQL + example Metric View YAML + example Alert YAML)
├── assets/
│   └── templates/
│       ├── project-plan-template.md            # KEEP (enhance if gaps)
│       ├── prerequisites-template.md           # NEW (from prompt lines 224-275)
│       ├── phase1-use-cases-template.md        # NEW (from prompt lines 279-383)
│       ├── phase1-tvfs-template.md             # NEW (from prompt lines 391-469)
│       ├── phase1-alerting-template.md         # NEW (from prompt lines 473-534)
│       ├── phase1-genie-spaces-template.md     # NEW (from prompt lines 538-660)
│       ├── phase2-agent-framework-template.md  # NEW (from prompt lines 666-824)
│       ├── phase3-frontend-template.md         # NEW (from prompt lines 828-861)
│       └── plans-readme-template.md            # NEW (from prompt lines 867-946)
```

### 3. SKILL.md Content Structure

Rewrite SKILL.md with the following sections. Target **under 500 lines** — heavy content goes to references/ and assets/templates/.

```markdown
# Project Plan Methodology for Databricks Solutions

## Overview
[Keep existing overview + key assumption. Add: "This skill combines interactive 
project planning with architectural methodology."]

## When to Use This Skill
[Keep existing 5 use cases + add from prompt context]

## Quick Start (5 Minutes)
[NEW — absorb from prompt lines 7-25]
- Fast Track fill-in template string
- Key Decisions Table (7 decisions from prompt lines 27-38)

## Step-by-Step Workflow

### Phase 1: Requirements Gathering
[NEW — absorb from prompt lines 42-111]
- Project Information input form (P3)
- Prerequisites Status table (P4)  
- Agent Domain definition table (P5)
- Phase 1 Addendum Selection table (P7)
- Key Business Questions template (P8)
- Link to: references/industry-domain-patterns.md for industry examples

### Phase 2: Plan Document Generation
[Describe workflow for creating plan documents using templates]
- Link to each template in assets/templates/
- Describe creation order (README → Prerequisites → Phase 1 Master → Addendums → Phase 2 → Phase 3)
- Reference the plan structure folder layout (keep from both)

## Plan Structure Framework
[Keep existing from skill — phases, folder layout, dependencies diagram]
[USE GENERIC {project} parameterization from prompt, not system-table-specific]

## Agent Domain Framework
[Keep PRINCIPLE from skill (lines 66-74) — "ALL artifacts organized by Agent Domain"]
[GENERALIZE the domain table — use {Domain 1-5} with {emoji}, {focus}, {tables}]
[Keep the Agent Domain Application rules (S4)]
[REMOVE hardcoded Cost/Security/Performance/Reliability/Quality table]
[Add link: "See references/industry-domain-patterns.md for industry-specific examples"]

## Agent Layer Architecture Pattern
[Keep ABBREVIATED version in SKILL.md — core principle + simple diagram + deployment order]
[Move DETAILED content to references/agent-layer-architecture.md:]
  - Detailed ASCII architecture diagrams
  - "Why Genie Spaces" comparison table (P9)
  - Agent-to-Genie Space mapping (generic)
  - 3 design patterns (1:1, Orchestrator+Unified, Hierarchical)
  - System prompt derivation pattern
  - Three-level testing with checklists
  - Architectural key learnings (P23)

## Artifact Count Standards
[Keep existing from skill (S6) — per-domain minimums + naming conventions]

## SQL Query Standards  
[Keep existing from skill (S7) — Gold layer pattern, variables, SCD2 joins]

## Documentation Quality Standards
[Keep existing from skill (S8) — LLM-friendly comments, summary tables]

## Common Mistakes to Avoid
[Keep existing from skill (S9) — 5 anti-patterns]

## Reference Files
[UPDATE with all new references]
- **[Phase Details](references/phase-details.md)** — Full phase & addendum descriptions
- **[Estimation Guide](references/estimation-guide.md)** — Effort, dependencies, risks
- **[Agent Layer Architecture](references/agent-layer-architecture.md)** — Detailed architecture, "Why Genie", design patterns, testing strategy
- **[Industry Domain Patterns](references/industry-domain-patterns.md)** — Domain templates for Hospitality, Retail, Healthcare, Finance, SaaS, and Databricks System Tables
- **[Worked Example: Wanderbricks](references/worked-example-wanderbricks.md)** — Complete 101-artifact project example with TVF SQL, Metric View YAML, Alert YAML

## Assets
[UPDATE with all new templates]
- **[Project Plan Template](assets/templates/project-plan-template.md)** — Generic phase template
- **[Prerequisites Template](assets/templates/prerequisites-template.md)** — Data layer summary
- **[Phase 1 Use Cases Template](assets/templates/phase1-use-cases-template.md)** — Master analytics artifacts
- **[Phase 1 TVFs Template](assets/templates/phase1-tvfs-template.md)** — Table-Valued Functions addendum
- **[Phase 1 Alerting Template](assets/templates/phase1-alerting-template.md)** — Alerting framework addendum
- **[Phase 1 Genie Spaces Template](assets/templates/phase1-genie-spaces-template.md)** — Genie Spaces addendum with Agent readiness
- **[Phase 2 Agent Framework Template](assets/templates/phase2-agent-framework-template.md)** — AI agents with Genie integration
- **[Phase 3 Frontend Template](assets/templates/phase3-frontend-template.md)** — User interface
- **[Plans README Template](assets/templates/plans-readme-template.md)** — plans/ folder index

## Validation Checklist
[MERGE both checklists — keep ALL unique items from both]

### Structure (from skill)
- [ ] Follows standard template
- [ ] Has Overview with Status, Dependencies, Effort
- [ ] Organized by Agent Domain
- [ ] Includes code examples
- [ ] Has Success Criteria table
- [ ] Has References section

### Content Quality (from skill)
- [ ] All queries use Gold layer tables (not system tables)
- [ ] All artifacts tagged with Agent Domain
- [ ] LLM-friendly comments on all artifacts
- [ ] Examples use ${catalog}.${gold_schema} variables
- [ ] Summary tables are accurate and complete

### Cross-References (from skill)
- [ ] Main phase document links to addendums
- [ ] Addendums link back to main phase
- [ ] Related artifacts cross-reference each other
- [ ] Dependencies are documented

### Completeness (MERGED — from both)
- [ ] All domains covered (4-6 minimum)
- [ ] Minimum artifact counts met per domain (TVFs: 4+, Alerts: 4+, Dashboard pages: 2+)
- [ ] Key business questions documented per domain
- [ ] All Phase 1 addendums included
- [ ] User requirements addressed
- [ ] Reference patterns incorporated

### Agent Layer Architecture (from prompt — ALL items)
- [ ] Agent-to-Genie Space mapping documented (1:1 recommended)
- [ ] Deployment order specified (Genie Spaces before Agents)
- [ ] Three-level testing strategy defined
- [ ] Orchestrator agent included for multi-domain coordination
- [ ] Genie Space instructions documented (become agent system prompts)
- [ ] Agent tool definitions reference Genie Spaces (not direct SQL)

## Key Learnings
[MERGE both sets into single numbered list]
[Items 1-15 from skill (methodology learnings)]
[Items 16+ from prompt (architecture learnings — 6 reasons for Genie, deployment order,
 design patterns, system prompt derivation, three-level testing)]
[Deduplicate overlapping items]

## References
[MERGE all references from both files]

### Official Documentation
[Combine skill's 5 links + prompt's 8 links — deduplicate]

### Related Skills
[Update prompt's "Related Cursor Rules" to use skill paths where applicable]

### Agent Framework Technologies
[Keep from prompt: LangChain, LangGraph]
```

### 4. Reference Files — Detailed Instructions

#### 4a. references/phase-details.md — EXPAND

Current file is 131 lines with abbreviated descriptions. Expand it with full details from the prompt:

**Add from prompt:**
- Detailed deliverables per addendum (the prompt has richer descriptions for 1.1-1.7)
- Phase 2 agent details: Genie Space → Agent mapping table (generic), how agents use Genie Spaces, three-level testing
- Phase 3 frontend details: Pages/Views table, deliverables
- Keep the testing strategy table but EXPAND to 3 levels with success criteria from prompt

**Keep from existing file:**
- All current content (it's a subset — expand, don't replace)
- Deployment order diagram

#### 4b. references/estimation-guide.md — KEEP AS-IS

No changes needed. Already comprehensive.

#### 4c. references/agent-layer-architecture.md — NEW

Create from prompt content. Include:

1. **Core Principle** — "Agents DO NOT query data assets directly. They use Genie Spaces." (from prompt lines 148-152 and skill lines 104-106)
2. **Detailed Architecture Diagram** — The full ASCII art from prompt lines 153-175 (the 3-tier: Agent → Genie Space → Data Assets)
3. **Why Genie Spaces (Not Direct SQL)?** — The 8-row comparison table from prompt lines 179-188. THIS IS UNIQUE TO THE PROMPT.
4. **Agent-to-Genie Space Mapping** — Generic template from prompt lines 192-199 (parameterized with {Domain})
5. **Phase 2 Architecture Diagram** — The detailed multi-agent diagram from prompt lines 691-722
6. **Design Patterns** — 3 patterns table from prompt lines 1318-1323 (1:1, Orchestrator+Unified, Hierarchical)
7. **System Prompt Derivation** — From prompt lines 1325-1331
8. **Three-Level Testing Strategy** — The detailed version from prompt lines 769-791 with checklists, MERGED with the table from skill lines 169-176 and the summary table from prompt lines 1335-1341
9. **Key Architectural Learnings** — The 6 numbered items from prompt lines 1300-1306, plus the deployment order diagram from lines 1309-1313
10. **Multi-Agent Query Example** — The full walkthrough from prompt lines 1126-1160 (user query → orchestrator → specialized agents → Genie Spaces → synthesized response)

#### 4d. references/industry-domain-patterns.md — NEW

Create from prompt + skill content. Include:

1. **How to Define Agent Domains** — Brief guidance (from skill's Agent Domain Framework)
2. **Industry-Specific Domain Patterns** — The 5-industry table from prompt lines 73-82 (Hospitality, Retail, Healthcare, Finance, SaaS)
3. **Databricks System Tables Domain Pattern** — Move the existing system-table-specific domain table from SKILL.md (S3, lines 77-84) HERE as one example industry pattern. Include the specific Genie Space → Agent Mapping with artifact counts from skill lines 131-141. This preserves the system tables content without hardcoding it in the main SKILL.md.
4. **Domain Definition Template** — The fill-in table from prompt lines 63-71

#### 4e. references/worked-example-wanderbricks.md — NEW

Create from prompt content. Include ALL of the following (this is the complete worked example):

1. **Project Overview** — From prompt lines 984-1001 (project name, domain, use cases)
2. **Agent Domains** — From prompt lines 993-1001 (5 domains: Revenue, Engagement, Property, Host, Customer)
3. **Prerequisites** — From prompt lines 1003-1018 (table counts, Gold dimensional model)
4. **Artifact Totals** — From prompt lines 1020-1033 (101+ artifacts across 10 categories)
5. **TVFs by Domain** — From prompt lines 1035-1045 (36 TVFs across 6 domains)
6. **Metric Views by Domain** — From prompt lines 1047-1055 (5 metric views)
7. **ML Models** — From prompt lines 1057-1066 (6 models)
8. **AI/BI Dashboards** — From prompt lines 1068-1077 (6 dashboards)
9. **Agent-to-Genie Space Mapping** — From prompt lines 1079-1088 (6 agents with data assets)
10. **Key Business Questions by Domain** — From prompt lines 1090-1124 (25 questions across 5 domains)
11. **Agent Architecture Flow Example** — From prompt lines 1126-1160 (multi-agent query walkthrough)
12. **Example TVF: `get_revenue_trend`** — Full SQL from prompt lines 1164-1196
13. **Example Metric View: `revenue_analytics_metrics`** — Full YAML from prompt lines 1200-1252
14. **Example Alert: `REV-001-CRIT`** — Full YAML from prompt lines 1256-1291

### 5. Template Files — Detailed Instructions

Each template file below should be extracted VERBATIM from the prompt's markdown template blocks. Keep all `{placeholder}` parameterization. Each template is a complete, ready-to-use markdown document.

| Template File | Source (Prompt Lines) | Content Description |
|---|---|---|
| `assets/templates/prerequisites-template.md` | 224-275 | Data layer summary (Bronze/Silver/Gold) with counts and schema names |
| `assets/templates/phase1-use-cases-template.md` | 279-383 | Master analytics artifacts with Agent Domain Framework, Addendum Index, Artifact Summary by Domain, Business Questions, Implementation Order (4 weeks), Success Criteria |
| `assets/templates/phase1-tvfs-template.md` | 391-469 | TVF addendum with domain summary, parameter requirements (STRING dates), comment structure, implementation checklist |
| `assets/templates/phase1-alerting-template.md` | 473-534 | Alerting framework with Alert ID Convention (`<DOMAIN>-<NUMBER>-<SEVERITY>`), severity levels, alert SQL patterns, actions, implementation checklist |
| `assets/templates/phase1-genie-spaces-template.md` | 538-660 | Genie Spaces with Agent Integration Readiness warning, Space configuration (sections A-G: Name, Description, Sample Questions, Data Assets priority order, General Instructions ≤20 lines, TVF Syntax Guidance, Benchmark Questions with SQL), Agent Readiness Validation checklist, Implementation Checklist |
| `assets/templates/phase2-agent-framework-template.md` | 666-824 | Agent framework with multi-agent architecture diagram, Agent-Genie mapping, domain agent details, three-level testing (Genie Standalone, Agent Integration, Multi-Agent), implementation checklist (prerequisites, agent dev, orchestrator, deployment) |
| `assets/templates/phase3-frontend-template.md` | 828-861 | Frontend app with pages/views table, implementation checklist |
| `assets/templates/plans-readme-template.md` | 867-946 | plans/ folder README with Plan Index, Phase 1 Addendum index, Agent Domain Framework, Project Scope Summary, Success Metrics |

### 6. Existing File Updates

#### 6a. assets/templates/project-plan-template.md — REVIEW

Read the existing file. Compare with the new phase-specific templates. If the existing template's content is fully covered by the new templates, keep it as a generic fallback. If it has unique content not in the new templates, preserve that content.

**Key decision:** The existing template is organized around system-table domains (Cost, Security, etc.). Either:
- GENERALIZE it to use `{Domain}` parameterization (preferred), OR
- Keep as a secondary example alongside the generic templates

#### 6b. references/phase-details.md — EXPAND (not replace)

Read the existing 131-line file. ADD content from the prompt that provides richer detail:
- Expand each addendum description with deliverables details from the prompt
- Add Phase 2 agent framework details (Genie Space → Agent mapping, how agents use Genie, testing)
- Add Phase 3 frontend details
- Keep deployment order diagram

Do NOT remove any existing content.

### 7. Post-Merge Cleanup

After all files are written:

1. **Delete** `context/prompts/11-project-plan-prompt.md` — all content absorbed into skill
2. **Verify links** — Every `references/` and `assets/templates/` file referenced in SKILL.md must exist
3. **Verify generalization** — SKILL.md should NOT contain hardcoded domain names (Cost, Security, etc.). Those belong ONLY in `references/industry-domain-patterns.md` as one example pattern
4. **Verify no content loss** — Walk through the Content Inventory tables above (P1-P25, S1-S14) and confirm each item has a destination

### 8. Validation Requirements

Before finalizing:

- [ ] SKILL.md is under 500 lines
- [ ] SKILL.md uses `{Domain}` parameterization (not hardcoded domains)
- [ ] Quick Start section exists with fill-in template and Key Decisions table
- [ ] All 8 phase document templates exist in `assets/templates/`
- [ ] `references/agent-layer-architecture.md` has "Why Genie" comparison table
- [ ] `references/industry-domain-patterns.md` has 5 industries + system tables
- [ ] `references/worked-example-wanderbricks.md` has complete example with all 14 subsections
- [ ] `references/phase-details.md` expanded with richer addendum details
- [ ] `references/estimation-guide.md` unchanged
- [ ] Validation Checklist in SKILL.md has ALL items from both files (merged)
- [ ] Key Learnings in SKILL.md combines both files (deduplicated)
- [ ] References section combines all links from both files
- [ ] All anti-patterns/common mistakes preserved
- [ ] All artifact count standards preserved
- [ ] All SQL query standards preserved
- [ ] All documentation quality standards preserved
- [ ] `context/prompts/11-project-plan-prompt.md` deleted after verification

## Execution Steps

1. **Read ALL source files completely** — SKILL.md, prompt, all 3 existing reference/asset files
2. **Create new reference files** — `agent-layer-architecture.md`, `industry-domain-patterns.md`, `worked-example-wanderbricks.md`
3. **Create all 8 new template files** in `assets/templates/`
4. **Expand `references/phase-details.md`** with richer content from prompt
5. **Review and optionally update `assets/templates/project-plan-template.md`** to generalize domains
6. **Rewrite SKILL.md** following Section 3 structure, keeping under 500 lines
7. **Verify all links** in SKILL.md point to existing files
8. **Walk Content Inventory** (P1-P25, S1-S14) to confirm zero content loss
9. **Delete** `context/prompts/11-project-plan-prompt.md`
10. **Update skill-navigator** if it references this skill (check domain indexes)

## Success Criteria

The merged skill is successful when:

1. A user can create a complete project plan (Prerequisites → Phase 1 → Phase 2 → Phase 3) using ONLY the skill + its references + templates
2. The Quick Start section lets a user get started in 5 minutes with a fill-in template
3. Industry-specific domain patterns are available for Hospitality, Retail, Healthcare, Finance, SaaS, and System Tables
4. All 8 phase document templates are available and parameterized
5. The Wanderbricks worked example provides a complete 101-artifact reference
6. Agent Layer Architecture is fully documented (Why Genie, deployment order, testing strategy, design patterns)
7. All methodology standards are preserved (artifact counts, SQL standards, naming conventions, anti-patterns, documentation quality)
8. SKILL.md is under 500 lines with heavy content in progressive-disclosure reference files
9. No hardcoded domain names in SKILL.md (all in references as examples)
10. The prompt file `context/prompts/11-project-plan-prompt.md` is deleted (100% absorbed)
