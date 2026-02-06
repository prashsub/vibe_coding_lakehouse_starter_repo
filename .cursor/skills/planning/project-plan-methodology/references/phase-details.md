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
- **Deliverables:** 15-25 models across 5 agent domains
- **Dependencies:** Gold layer tables
- **Output:** Prediction tables for consumption

#### 1.2: Table-Valued Functions (TVFs)
- **Purpose:** Parameterized SQL queries for Genie Spaces
- **Deliverables:** 20-40 TVFs (4-8 per domain)
- **Dependencies:** Gold layer tables
- **Requirements:** STRING parameters (not DATE) for Genie compatibility

#### 1.3: Metric Views
- **Purpose:** Pre-aggregated metrics for fast queries
- **Deliverables:** 5-10 metric views (1-2 per domain)
- **Dependencies:** Gold layer tables
- **Priority:** Use FIRST before TVFs (faster queries)

#### 1.4: Lakehouse Monitoring
- **Purpose:** Data quality and drift detection
- **Deliverables:** 5-10 monitors (1-2 per domain)
- **Dependencies:** Gold layer tables
- **Custom Metrics:** Table-level business KPIs

#### 1.5: AI/BI Dashboards
- **Purpose:** Visual analytics for users
- **Deliverables:** 10-20 dashboard pages (2-4 per domain)
- **Dependencies:** Gold layer tables, Metric Views, TVFs
- **Format:** Lakeview dashboard JSON

#### 1.6: Genie Spaces (CRITICAL)
- **Purpose:** Natural language query interface for agents
- **Deliverables:** 5-10 Genie Spaces (1-2 per domain)
- **Dependencies:** All Phase 1 artifacts (TVFs, Metric Views, ML Models)
- **Critical:** Must be deployed BEFORE Phase 2 agents

#### 1.7: Alerting Framework
- **Purpose:** Proactive notifications for issues
- **Deliverables:** 20-40 alerts (4-8 per domain)
- **Dependencies:** Gold layer tables
- **Format:** SQL alerts with config-driven deployment

## Phase 2: Agent Framework

### Overview

Phase 2 creates AI agents that use Genie Spaces as their query interface. Agents do NOT write SQL directly - they use Genie Spaces for natural language understanding.

### Genie Space → Agent Mapping

Each specialized agent has a corresponding Genie Space:

| Agent | Genie Space | Tools (via Genie) |
|-------|-------------|-------------------|
| 💰 **Cost Agent** | Cost Intelligence | 15 TVFs, 2 MVs, 6 ML |
| 🔒 **Security Agent** | Security Auditor | 10 TVFs, 2 MVs, 4 ML |
| ⚡ **Performance Agent** | Performance Analyzer | 16 TVFs, 3 MVs, 7 ML |
| 🔄 **Reliability Agent** | Job Health Monitor | 12 TVFs, 1 MV, 5 ML |
| ✅ **Data Quality Agent** | Data Quality Monitor | 7 TVFs, 2 MVs, 3 ML |
| 🌐 **Orchestrator Agent** | Unified Health Monitor | All 60 TVFs, 10 MVs, 25 ML |

### Testing Strategy

| Level | What to Test | When to Test |
|-------|--------------|--------------|
| **L1: Genie Standalone** | Genie Space returns correct results for benchmark questions | After Genie deployment |
| **L2: Agent Integration** | Agent successfully uses Genie and formats response | After agent deployment |
| **L3: Multi-Agent** | Orchestrator coordinates multiple agents for complex queries | After all agents deployed |

## Phase 3: Frontend Application

### Overview

Phase 3 creates a unified user interface that consumes AI agents from Phase 2.

### Deliverables

- **Chat Interface:** Natural language interaction with agents
- **Dashboard Views:** Visual analytics from Phase 1.5 dashboards
- **Alert Management:** View and manage alerts from Phase 1.7
- **Unified Experience:** Single UI for all agent domains

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
