---
name: project-plan-methodology
description: Create multi-phase project plans for Databricks data platform solutions with Agent Domain Framework and Agent Layer Architecture. Use when planning observability solutions, multi-artifact projects, or agent-based frameworks. Includes 3-phase structure (Use Cases → Agents → Frontend), Genie Space integration patterns, and deployment order requirements.
metadata:
  author: databricks-sa
  version: "1.0"
  domain: planning
---

# Project Plan Methodology for Databricks Solutions

## Overview

Comprehensive methodology for creating multi-phase project plans for Databricks data platform solutions. The methodology was discovered and refined during the Databricks Health Monitor project planning process.

**Key Assumption:** Planning starts AFTER Bronze ingestion and Gold layer design are complete. These are prerequisites, not phases.

## When to Use This Skill

Use this skill when:
- Creating architectural plans for Databricks data platform projects
- Building observability/monitoring solutions using system tables
- Planning multi-artifact solutions (TVFs, Metric Views, Dashboards, etc.)
- Developing agent-based frameworks for platform management
- Creating frontend applications for data platform interaction

## Plan Structure Framework

### Prerequisites (Not Numbered Phases)

Before planning begins, these must be complete:

| Prerequisite | Description | Status |
|--------------|-------------|--------|
| Bronze Layer | Raw data ingestion from source systems | ✅ Complete |
| Silver Layer | DLT streaming with data quality | ✅ Complete |
| Gold Layer | Dimensional model (star schema) | ✅ Complete |

### Standard Project Phases

```
plans/
├── README.md                              # Index and overview
├── prerequisites.md                       # Bronze/Silver/Gold summary (optional)
├── phase1-use-cases.md                    # Analytics artifacts (master)
│   ├── phase1-addendum-1.1-ml-models.md   # Machine Learning
│   ├── phase1-addendum-1.2-tvfs.md        # Table-Valued Functions
│   ├── phase1-addendum-1.3-metric-views.md # UC Metric Views
│   ├── phase1-addendum-1.4-lakehouse-monitoring.md # Monitoring
│   ├── phase1-addendum-1.5-ai-bi-dashboards.md # Dashboards
│   ├── phase1-addendum-1.6-genie-spaces.md # Natural Language
│   └── phase1-addendum-1.7-alerting-framework.md # Alerting
├── phase2-agent-framework.md              # AI Agents
└── phase3-frontend-app.md                 # User Interface
```

### Phase Dependencies

```
Prerequisites (Bronze → Silver → Gold) → Phase 1 (Use Cases) → Phase 2 (Agents) → Phase 3 (Frontend)
         [COMPLETE]                               ↓
                                           All Addendums
```

## Agent Domain Framework

### Core Principle

**ALL artifacts across ALL phases MUST be organized by Agent Domain.** This ensures:
- Consistent categorization across 100+ artifacts
- Clear ownership by future AI agents
- Easy discoverability for users
- Aligned tooling for each domain

### Standard Agent Domains

| Domain | Icon | Focus Area | Key Gold Tables |
|--------|------|------------|-----------------|
| **Cost** | 💰 | FinOps, budgets, chargeback | `fact_usage`, `dim_sku`, `commit_configurations` |
| **Security** | 🔒 | Access audit, compliance | `fact_audit_events`, `fact_table_lineage` |
| **Performance** | ⚡ | Query optimization, capacity | `fact_query_history`, `fact_node_timeline` |
| **Reliability** | 🔄 | Job health, SLAs | `fact_job_run_timeline`, `dim_job` |
| **Quality** | ✅ | Data quality, governance | `fact_data_quality_monitoring_table_results` |

### Agent Domain Application

Every artifact (TVF, Metric View, Dashboard, Alert, ML Model, Monitor, Genie Space) must:
1. Be tagged with its Agent Domain
2. Use the domain's Gold tables
3. Answer domain-specific questions
4. Be grouped with related domain artifacts in documentation

**Example Pattern:**
```markdown
## 💰 Cost Agent: get_top_cost_contributors

**Agent Domain:** 💰 Cost
**Gold Tables:** `fact_usage`, `dim_workspace`
**Business Questions:** "What are the top cost drivers?"
```

## Agent Layer Architecture Pattern

### Core Principle: Agents Use Genie Spaces as Query Interface

**AI Agents DO NOT query data assets directly.** Instead, they use Genie Spaces as their natural language query interface. Genie Spaces translate natural language to SQL and route to appropriate tools (TVFs, Metric Views, ML Models).

```
USERS (Natural Language)
    ↓
PHASE 2: AI AGENT LAYER (LangChain/LangGraph)
    ├── Orchestrator Agent (intent classification)
    └── Specialized Agents (Cost, Security, Performance, etc.)
            ↓
PHASE 1.6: GENIE SPACES (NL Query Execution)
    ├── Cost Intelligence Genie Space
    ├── Security Auditor Genie Space
    └── Performance Analyzer Genie Space
            ↓
PHASE 1: DATA ASSETS (Agent Tools)
    ├── Metric Views (pre-aggregated - use FIRST)
    ├── TVFs (parameterized queries)
    ├── ML Predictions (ML-powered insights)
    └── Lakehouse Monitors (drift detection)
            ↓
PREREQUISITES: GOLD LAYER (Foundation)
```

### Genie Space → Agent Mapping

Each specialized agent has a corresponding Genie Space that serves as its query interface:

| Agent | Genie Space | Tools (via Genie) |
|-------|-------------|-------------------|
| 💰 **Cost Agent** | Cost Intelligence | 15 TVFs, 2 MVs, 6 ML |
| 🔒 **Security Agent** | Security Auditor | 10 TVFs, 2 MVs, 4 ML |
| ⚡ **Performance Agent** | Performance Analyzer | 16 TVFs, 3 MVs, 7 ML |
| 🔄 **Reliability Agent** | Job Health Monitor | 12 TVFs, 1 MV, 5 ML |
| ✅ **Data Quality Agent** | Data Quality Monitor | 7 TVFs, 2 MVs, 3 ML |
| 🌐 **Orchestrator Agent** | Unified Health Monitor | All 60 TVFs, 10 MVs, 25 ML |

### Deployment Order (Critical!)

**Genie Spaces MUST be deployed BEFORE agents can use them.**

```
Phase 0: Prerequisites (Complete)
    └── Bronze → Silver → Gold Layer

Phase 1: Data Assets (Deploy First)
    ├── 1.1: ML Models (25 models → prediction tables)
    ├── 1.2: TVFs (60 functions)
    ├── 1.3: Metric Views (10 views)
    ├── 1.4: Lakehouse Monitors (8 monitors)
    ├── 1.5: AI/BI Dashboards (11 dashboards)
    ├── 1.6: Genie Spaces (7 spaces) ← Critical for agents
    └── 1.7: Alerting (40 alerts)

Phase 2: Agent Framework (Deploy After Genie Spaces)
    ├── 2.1: Agent framework setup (LangChain/LangGraph)
    ├── 2.2: Specialized agents (6 agents)
    ├── 2.3: Orchestrator agent
    └── 2.4: Deployment to Model Serving

Phase 3: Frontend (Deploy Last)
    └── Unified UI consuming agents
```

### Testing Strategy

| Level | What to Test | When to Test |
|-------|--------------|--------------|
| **L1: Genie Standalone** | Genie Space returns correct results for benchmark questions | After Genie deployment |
| **L2: Agent Integration** | Agent successfully uses Genie and formats response | After agent deployment |
| **L3: Multi-Agent** | Orchestrator coordinates multiple agents for complex queries | After all agents deployed |

## Artifact Count Standards

### Minimum Artifacts Per Domain

| Artifact Type | Per Domain | Total (5 domains) |
|---------------|------------|-------------------|
| TVFs | 4-8 | 20-40 |
| Metric Views | 1-2 | 5-10 |
| Dashboard Pages | 2-4 | 10-20 |
| Alerts | 4-8 | 20-40 |
| ML Models | 3-5 | 15-25 |
| Lakehouse Monitors | 1-2 | 5-10 |
| Genie Spaces | 1-2 | 5-10 |

### Artifact Naming Conventions

| Artifact | Pattern | Example |
|----------|---------|---------|
| TVF | `get_<domain>_<metric>` | `get_cost_by_tag` |
| Metric View | `<domain>_analytics_metrics` | `cost_analytics_metrics` |
| Dashboard | `<Domain> <Purpose> Dashboard` | `Cost Attribution Dashboard` |
| Alert | `<DOMAIN>-NNN` | `COST-001` |
| ML Model | `<Purpose> <Type>` | `Budget Forecaster` |
| Monitor | `<table> Monitor` | `Cost Data Quality Monitor` |
| Genie Space | `<Domain> <Purpose>` | `Cost Intelligence` |
| AI Agent | `<Domain> Agent` | `Cost Agent` |

## SQL Query Standards

### Gold Layer Reference Pattern

**ALWAYS use Gold layer tables, NEVER system tables directly.**

```sql
-- ❌ WRONG: Direct system table reference
FROM system.billing.usage

-- ✅ CORRECT: Gold layer reference with variables
FROM ${catalog}.${gold_schema}.fact_usage
```

### Standard Variable References

```sql
-- Catalog and schema (from parameters)
${catalog}.${gold_schema}.table_name

-- Date parameters (STRING type for Genie compatibility)
WHERE usage_date BETWEEN CAST(start_date AS DATE) AND CAST(end_date AS DATE)

-- SCD Type 2 dimension joins
LEFT JOIN dim_workspace w 
    ON f.workspace_id = w.workspace_id 
    AND w.is_current = TRUE
```

## Documentation Quality Standards

### LLM-Friendly Comments

All artifacts must have comments that help LLMs (Genie, AI/BI) understand:
- What the artifact does
- When to use it
- Example questions it answers

```sql
COMMENT 'LLM: Returns top N cost contributors by workspace and SKU for a date range.
Use this for cost optimization, chargeback analysis, and identifying spending hotspots.
Parameters: start_date, end_date (YYYY-MM-DD format), optional top_n (default 10).
Example questions: "What are the top 10 cost drivers?" or "Which workspace spent most?"'
```

### Summary Tables

Every addendum must include:
1. **Overview table** - All artifacts with agent domain, dependencies, status
2. **By-domain sections** - Artifacts grouped by agent domain
3. **Count summary** - Total artifacts by type and domain
4. **Success criteria** - Measurable targets

## Common Mistakes to Avoid

### ❌ DON'T: Mix system tables and Gold tables

```sql
-- BAD: Direct system table
FROM system.billing.usage u
JOIN ${catalog}.${gold_schema}.dim_workspace w ...
```

### ❌ DON'T: Forget Agent Domain classification

```markdown
## get_slow_queries (BAD - no domain)

## ⚡ Performance Agent: get_slow_queries (GOOD)
```

### ❌ DON'T: Create artifacts without cross-addendum updates

When adding a TVF, also consider:
- Does it need a Metric View counterpart?
- Should there be an Alert?
- Is it Dashboard-worthy?

### ❌ DON'T: Use DATE parameters in TVFs (Genie incompatible)

```sql
-- BAD
start_date DATE

-- GOOD
start_date STRING COMMENT 'Format: YYYY-MM-DD'
```

### ❌ DON'T: Deploy agents before Genie Spaces

**Genie Spaces MUST be deployed BEFORE agents can use them.**

## Reference Files

### [phase-details.md](references/phase-details.md)
Detailed phase descriptions including:
- Prerequisites and dependencies
- Phase 1 addendums (1.1-1.7) with deliverables
- Phase 2 agent architecture and mapping
- Phase 3 frontend application
- Success criteria by phase
- Deployment order and testing strategy

### [estimation-guide.md](references/estimation-guide.md)
Effort estimation and dependency management:
- Effort estimation guidelines by phase
- Dependency management patterns
- Risk management strategies
- Progress tracking templates
- Resource allocation recommendations

## Assets

### [project-plan-template.md](assets/templates/project-plan-template.md)
Starter template for creating project plan documents:
- Standard structure for each phase
- Agent domain organization patterns
- SQL query standards
- Summary table templates
- Success criteria format

**Usage:** Copy template, customize for your phase, follow Agent Domain Framework.

## Validation Checklist

Before finalizing any plan document:

### Structure
- [ ] Follows standard template
- [ ] Has Overview with Status, Dependencies, Effort
- [ ] Organized by Agent Domain
- [ ] Includes code examples
- [ ] Has Success Criteria table
- [ ] Has References section

### Content Quality
- [ ] All queries use Gold layer tables (not system tables)
- [ ] All artifacts tagged with Agent Domain
- [ ] LLM-friendly comments on all artifacts
- [ ] Examples use `${catalog}.${gold_schema}` variables
- [ ] Summary tables are accurate and complete

### Cross-References
- [ ] Main phase document links to addendums
- [ ] Addendums link back to main phase
- [ ] Related artifacts cross-reference each other
- [ ] Dependencies are documented

### Completeness
- [ ] All 5 agent domains covered
- [ ] Minimum artifact counts met
- [ ] User requirements addressed
- [ ] Reference patterns incorporated

## References

### Official Documentation
- [Databricks System Tables](https://docs.databricks.com/administration-guide/system-tables/)
- [Databricks SQL Alerts](https://docs.databricks.com/sql/user/alerts/)
- [Lakehouse Monitoring](https://docs.databricks.com/lakehouse-monitoring/)
- [Metric Views](https://docs.databricks.com/metric-views/)
- [Table-Valued Functions](https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-create-sql-function.html)

### Related Cursor Rules
- [15-databricks-table-valued-functions.mdc](.cursor/rules/semantic-layer/15-databricks-table-valued-functions.mdc)
- [14-metric-views-patterns.mdc](.cursor/rules/semantic-layer/14-metric-views-patterns.mdc)
- [17-lakehouse-monitoring-comprehensive.mdc](.cursor/rules/monitoring/17-lakehouse-monitoring-comprehensive.mdc)
- [18-databricks-aibi-dashboards.mdc](.cursor/rules/monitoring/18-databricks-aibi-dashboards.mdc)
- [16-genie-space-patterns.mdc](.cursor/rules/semantic-layer/16-genie-space-patterns.mdc) - **Genie Space setup for agents**

## Key Learnings

1. Agent Domain framework provides consistent organization across all artifacts
2. Gold layer references (not system tables) ensure consistency
3. User requirements often span multiple addendums - update all
4. Dashboard JSON files are rich sources of SQL patterns
5. LLM-friendly comments are critical for Genie/AI/BI integration
6. Summary tables help maintain accuracy across large plans
7. Planning starts after data layers are complete - focus on consumption artifacts
8. **Agents should NOT write SQL directly - use Genie Spaces as abstraction**
9. **Genie Spaces provide natural language understanding that agents leverage**
10. **Each specialized agent has a dedicated Genie Space (1:1 mapping)**
11. **Orchestrator agent uses Unified Genie Space for intent classification**
12. **Genie Spaces must be deployed BEFORE agents can be developed**
13. **Multi-agent workflows require correlation and synthesis in Orchestrator**
14. **Three-level testing ensures each layer works before next is built**
15. **General Instructions in Genie Spaces become agent system prompts**
