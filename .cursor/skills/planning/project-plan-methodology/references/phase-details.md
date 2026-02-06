# Phase Details - Project Plan Methodology

## Prerequisites (Not Numbered Phases)

Before planning begins, these must be complete:

| Prerequisite | Description | Status |
|--------------|-------------|--------|
| Bronze Layer | Raw data ingestion from source systems | ✅ Complete |
| Silver Layer | DLT streaming with data quality | ✅ Complete |
| Gold Layer | Dimensional model (star schema) | ✅ Complete |

**Key Assumption:** Planning starts AFTER Bronze ingestion and Gold layer design are complete. These are prerequisites, not phases.

## Phase 1: Use Cases (Analytics Artifacts)

### Overview

Phase 1 creates all data consumption artifacts organized by Agent Domain. These artifacts serve as tools for AI agents in Phase 2.

### Phase 1 Addendums

#### 1.1: ML Models
- **Purpose:** ML-powered predictions and insights
- **Deliverables:** 15-25 models across all agent domains
- **Dependencies:** Gold layer tables
- **Output:** Prediction tables for consumption by TVFs, Genie Spaces, and Dashboards
- **Key Artifacts:** {metric} predictors, {metric} optimizers, {entity} classifiers, {entity} LTV models, segmentation models, {metric} forecasters

#### 1.2: Table-Valued Functions (TVFs)
- **Purpose:** Parameterized SQL queries for Genie Spaces
- **Deliverables:** 20-40 TVFs (4-8 per domain)
- **Dependencies:** Gold layer tables
- **Requirements:** STRING parameters (not DATE) for Genie compatibility
- **Comment Format:** `LLM: [Description]. Use for: [use cases]. Example questions: "[Q1]" "[Q2]"`
- **Template:** See `assets/templates/phase1-tvfs-template.md`

#### 1.3: Metric Views
- **Purpose:** Pre-aggregated metrics for fast queries
- **Deliverables:** 5-10 metric views (1-2 per domain)
- **Dependencies:** Gold layer tables
- **Priority:** Use FIRST before TVFs (faster queries)
- **Format:** YAML with `WITH METRICS LANGUAGE YAML` syntax

#### 1.4: Lakehouse Monitoring
- **Purpose:** Data quality and drift detection
- **Deliverables:** 5-10 monitors (1-2 per domain)
- **Dependencies:** Gold layer tables
- **Custom Metrics:** Table-level business KPIs using `input_columns=[":table"]`

#### 1.5: AI/BI Dashboards
- **Purpose:** Visual analytics for users
- **Deliverables:** 10-20 dashboard pages (2-4 per domain)
- **Dependencies:** Gold layer tables, Metric Views, TVFs
- **Format:** Lakeview dashboard JSON
- **Key Dashboards:** One per domain + one Lakehouse Monitoring dashboard

#### 1.6: Genie Spaces (CRITICAL)
- **Purpose:** Natural language query interface for agents
- **Deliverables:** 5-10 Genie Spaces (1-2 per domain + 1 unified)
- **Dependencies:** All Phase 1 artifacts (TVFs, Metric Views, ML Models)
- **Critical:** Must be deployed BEFORE Phase 2 agents
- **Data Asset Priority:** Metric Views → TVFs → ML Prediction Tables → Gold Tables
- **Instructions:** ≤20 lines per space (become agent system prompts)
- **Benchmark Questions:** 5-7 per space with exact SQL
- **Agent Readiness:** Each space validated for >80% NL accuracy
- **Template:** See `assets/templates/phase1-genie-spaces-template.md`

#### 1.7: Alerting Framework
- **Purpose:** Proactive notifications for issues
- **Deliverables:** 20-40 alerts (4-8 per domain)
- **Dependencies:** Gold layer tables, 1.4 (Lakehouse Monitoring)
- **Format:** SQL alerts with config-driven deployment
- **Alert ID Convention:** `<DOMAIN>-<NUMBER>-<SEVERITY>` (e.g., `REV-001-CRIT`)
- **Severity Levels:** CRITICAL, WARNING, INFO
- **Template:** See `assets/templates/phase1-alerting-template.md`

### Implementation Order

| Week | Activities |
|------|-----------|
| Week 1: Foundation | Create TVFs (all domains), Create Metric Views |
| Week 2: Monitoring | Setup Lakehouse Monitors, Create Alerting Framework, Validate data quality baselines |
| Week 3: Visualization | Build AI/BI Dashboards, Configure Genie Spaces, Document business usage guides |
| Week 4: Intelligence | Train ML Models, Deploy model endpoints, Integrate predictions |

## Phase 2: Agent Framework

### Overview

Phase 2 creates AI agents that use Genie Spaces as their query interface. Agents do NOT write SQL directly - they use Genie Spaces for natural language understanding.

### Genie Space → Agent Mapping

Each specialized agent has a corresponding Genie Space (1:1 recommended):

| Agent | Dedicated Genie Space | Purpose |
|-------|----------------------|---------|
| {Domain 1} Agent | {Domain 1} Intelligence | {domain 1} queries via NL |
| {Domain 2} Agent | {Domain 2} Intelligence | {domain 2} queries via NL |
| Orchestrator Agent | Unified {Project} Monitor | Intent classification, multi-agent coordination |

### How Agents Use Genie Spaces

1. Agent receives natural language query from user/orchestrator
2. Agent sends query to Genie Space via tool call
3. Genie Space translates NL to SQL and executes
4. Agent receives results and synthesizes response

### Agent Capabilities (via Genie Space)

- Answer domain-related questions using Genie Space NL interface
- Access domain TVFs indirectly (Genie routes to correct TVF)
- Retrieve domain ML predictions (Genie accesses prediction tables)
- Generate domain insights from Metric Views

### Testing Strategy

| Level | What to Test | When to Test | Success Criteria |
|-------|--------------|--------------|------------------|
| **L1: Genie Standalone** | Genie Space returns correct results for benchmark questions | After Genie deployment | >80% benchmark accuracy |
| **L2: Agent Integration** | Agent successfully uses Genie and formats response | After agent deployment | >90% tool usage accuracy |
| **L3: Multi-Agent** | Orchestrator coordinates multiple agents for complex queries | After all agents deployed | >85% intent classification |

**Test each level before proceeding to the next.** Do not skip levels.

### Implementation Phases

1. **Agent framework setup** — LangChain/LangGraph configuration
2. **Specialized agents** — One per domain, each with dedicated Genie Space
3. **Orchestrator agent** — Multi-domain coordination and intent classification
4. **Deployment** — Deploy to Model Serving, configure API endpoints

### Template

See `assets/templates/phase2-agent-framework-template.md`

## Phase 3: Frontend Application

### Overview

Phase 3 creates a unified user interface that consumes AI agents from Phase 2.

### Deliverables

- **Chat Interface:** Natural language interaction with agents
- **Dashboard Views:** Visual analytics from Phase 1.5 dashboards
- **Alert Management:** View and manage alerts from Phase 1.7
- **Unified Experience:** Single UI for all agent domains

### Pages/Views

| Page | Purpose | Agents Used |
|------|---------|-------------|
| Chat | Natural language queries | All agents via Orchestrator |
| Dashboards | Visual analytics | Phase 1.5 dashboard embedding |
| Alerts | Alert management | Phase 1.7 alert monitoring |
| Settings | Configuration | Admin functions |

### Template

See `assets/templates/phase3-frontend-template.md`

## Deployment Order (Critical!)

**Genie Spaces MUST be deployed BEFORE agents can use them.**

```
Phase 0: Prerequisites (Complete)
    └── Bronze → Silver → Gold Layer

Phase 1: Data Assets (Deploy First)
    ├── 1.1: ML Models
    ├── 1.2: TVFs
    ├── 1.3: Metric Views
    ├── 1.4: Lakehouse Monitors
    ├── 1.5: AI/BI Dashboards
    ├── 1.6: Genie Spaces ← Critical for agents
    └── 1.7: Alerting

Phase 2: Agent Framework (Deploy After Genie Spaces)
    ├── 2.1: Agent framework setup
    ├── 2.2: Specialized agents
    ├── 2.3: Orchestrator agent
    └── 2.4: Deployment to Model Serving

Phase 3: Frontend (Deploy Last)
    └── Unified UI consuming agents
```

## Success Criteria by Phase

### Phase 1

| Metric | Target |
|--------|--------|
| TVFs deployed and functional | {count}+ per domain |
| Metric Views queryable | {count} |
| Dashboards published | {count} |
| Monitors with baselines | {count} |
| Alerts configured | {count} |
| Genie Spaces responding | {count} |
| ML Models deployed | {count} |

### Phase 2

| Metric | Target |
|--------|--------|
| Specialized agents responding | 1 per domain |
| Orchestrator classifying intents | >85% accuracy |
| Agent-to-Genie integration | >90% tool usage accuracy |
| End-to-end query latency | < 15 seconds |

### Phase 3

| Metric | Target |
|--------|--------|
| App deployed | 1 |
| Chat interface functional | All agents accessible |
| Dashboard embedding working | All Phase 1.5 dashboards |
