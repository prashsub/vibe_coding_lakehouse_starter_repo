# 11: Project Plan Prompt

**Create a comprehensive phased project plan for Databricks solutions (starting from Use Cases after Gold layer is complete)**

---

## 🚀 Quick Start (5 Minutes)

### Fast Track: Create Your Project Plan

```bash
# 1. Verify prerequisites are complete:
#    - Bronze ingestion ✅
#    - Silver DLT streaming ✅
#    - Gold dimensional model ✅

# 2. Run this prompt with your project info:
"Create a phased project plan for {project_name} with:
- Gold tables: {n} tables ({d} dimensions + {f} facts)
- Use cases: {revenue analysis, marketing, operations, etc.}
- Target audience: {executives, analysts, data scientists}
- Agent domains: {cost, security, performance, reliability, quality}"

# 3. Output: Complete plan structure in plans/ folder
```

### Key Decisions (Answer These First)

| Decision | Options | Your Choice |
|----------|---------|-------------|
| Agent Domains | Define 4-6 business domains | __________ |
| Phase 1 Addendums | TVFs, Metric Views, Dashboards, Monitoring, Genie, Alerts, ML | __________ |
| Phase 2 Scope | AI Agents (optional) or skip | __________ |
| Phase 3 Scope | Frontend App (optional) or skip | __________ |
| Artifact Counts | Min per domain: TVFs (4+), Alerts (4+), etc. | __________ |
| Agent Architecture | Agents use Genie Spaces (recommended) or Direct SQL | __________ |
| Agent-Genie Mapping | 1:1 (recommended) or Many-to-1 | __________ |

---

## 📋 Your Requirements (Fill These In First)

### Project Information

| Field | Your Value |
|-------|------------|
| Project Name | {project_name} |
| Business Domain | {hospitality, retail, healthcare, finance, etc.} |
| Primary Use Cases | {revenue tracking, customer analytics, operations, etc.} |
| Target Stakeholders | {executives, analysts, data scientists, operations} |

### Prerequisites (Must Be Complete)

| Layer | Count | Status |
|-------|-------|--------|
| Bronze Tables | {n} | ✅ Complete |
| Silver Tables | {m} | ✅ Complete |
| Gold Dimensions | {d} | ✅ Complete |
| Gold Facts | {f} | ✅ Complete |

### Agent Domain Framework

Define your business domains (typically 4-6):

| Domain | Icon | Focus Area | Key Gold Tables |
|--------|------|------------|-----------------|
| {Domain 1} | {emoji} | {focus} | {tables} |
| {Domain 2} | {emoji} | {focus} | {tables} |
| {Domain 3} | {emoji} | {focus} | {tables} |
| {Domain 4} | {emoji} | {focus} | {tables} |
| {Domain 5} | {emoji} | {focus} | {tables} |

**Common Domain Patterns:**

| Industry | Domains |
|----------|---------|
| Hospitality | 💰 Revenue, 📊 Engagement, 🏠 Property, 👤 Host, 🎯 Customer |
| Retail | 💰 Sales, 📦 Inventory, 🏪 Store, 👤 Customer, 📊 Marketing |
| Healthcare | 👨‍⚕️ Clinical, 💰 Financial, 📊 Operations, 🏥 Facility, 👤 Patient |
| Finance | 💰 Revenue, 🔒 Risk, 📊 Compliance, 👤 Customer, ⚡ Operations |
| SaaS | 💰 Revenue, 📊 Product, 👤 Customer, ⚡ Performance, 🔒 Security |

### Phase 1 Addendum Selection

Select which addendums to include:

| # | Addendum | Include? | Artifact Count |
|---|----------|----------|----------------|
| 1.1 | ML Models | {Yes/No} | {count} |
| 1.2 | Table-Valued Functions | {Yes/No} | {count} |
| 1.3 | Metric Views | {Yes/No} | {count} |
| 1.4 | Lakehouse Monitoring | {Yes/No} | {count} |
| 1.5 | AI/BI Dashboards | {Yes/No} | {count} |
| 1.6 | Genie Spaces | {Yes/No} | {count} |
| 1.7 | Alerting Framework | {Yes/No} | {count} |

### Key Business Questions by Domain

List 5-10 key questions per domain that the solution must answer:

**{Domain 1}:**
1. {Question 1}
2. {Question 2}
3. {Question 3}
4. {Question 4}
5. {Question 5}

**{Domain 2}:**
1. {Question 1}
2. {Question 2}
...

---

## 📚 Full Implementation Guide

### Plan Structure Overview

A complete project plan follows this structure:

```
plans/
├── README.md                              # Index and overview
├── prerequisites.md                       # Bronze/Silver/Gold summary (optional)
├── phase1-use-cases.md                    # Analytics artifacts (master)
│   ├── phase1-addendum-1.1-ml-models.md
│   ├── phase1-addendum-1.2-tvfs.md
│   ├── phase1-addendum-1.3-metric-views.md
│   ├── phase1-addendum-1.4-lakehouse-monitoring.md
│   ├── phase1-addendum-1.5-aibi-dashboards.md
│   ├── phase1-addendum-1.6-genie-spaces.md
│   └── phase1-addendum-1.7-alerting.md
├── phase2-agent-framework.md              # AI agent framework
└── phase3-frontend-app.md                 # User interface (optional)
```

### Phase Dependencies

```
Prerequisites (Bronze → Silver → Gold) → Phase 1 (Use Cases) → Phase 2 (Agents) → Phase 3 (Frontend)
         [COMPLETE]                               ↓
                                           All Addendums
```

---

## 🏗️ Agent Layer Architecture (Critical for Phase 2)

### Core Principle: Agents Use Genie Spaces as Query Interface

**AI Agents DO NOT query data assets directly.** Instead, they use Genie Spaces as their natural language query interface. Genie Spaces translate natural language to SQL and route to appropriate tools (TVFs, Metric Views, ML Models).

```
┌───────────────────────────┐
│     AI AGENT (Phase 2)    │
│ (e.g., {Domain} Agent)    │
│   - System Prompt         │
│   - Tools (Genie Spaces)  │
└───────────┬───────────────┘
            │ Natural Language Query
            ▼
┌───────────────────────────┐
│   GENIE SPACE (Phase 1.6) │
│ (e.g., {Domain} Intel)    │
│   - Instructions          │
│   - Data Assets           │
└───────────┬───────────────┘
            │ SQL Query
            ▼
┌───────────────────────────┐
│   DATA ASSETS (Phase 1)   │
│ (TVFs, Metric Views,      │
│  ML Models, Gold Tables)  │
└───────────────────────────┘
```

### Why Genie Spaces (Not Direct SQL)?

| Without Genie Spaces | With Genie Spaces |
|---------------------|-------------------|
| Agents must write SQL | Agents use natural language |
| High SQL complexity for agents | Abstraction layer for agents |
| Direct data asset coupling | Decoupled agent from data schema |
| Manual SQL optimization | Genie handles query optimization |
| Limited natural language understanding | Enhanced NL-to-SQL capabilities |
| Hard to maintain agent prompts | Genie instructions act as agent context |
| No built-in guardrails | Genie provides query guardrails |
| No benchmark testing framework | Genie has built-in benchmark testing |

### Agent-to-Genie Space Mapping

**Each specialized agent has a dedicated Genie Space (1:1 correspondence):**

| Agent | Dedicated Genie Space | Purpose |
|-------|----------------------|---------|
| {Domain 1} Agent | {Domain 1} Intelligence | {domain 1} analysis, {use cases} |
| {Domain 2} Agent | {Domain 2} Intelligence | {domain 2} analysis, {use cases} |
| Orchestrator Agent | Unified {Project} Monitor | Intent classification, multi-agent coordination |

### Deployment Order (Critical!)

**Genie Spaces MUST be deployed BEFORE agents can use them:**

```
Phase 1 Addendums (Deploy First)
├── 1.1: ML Models
├── 1.2: TVFs
├── 1.3: Metric Views
├── 1.4: Lakehouse Monitors
├── 1.5: AI/BI Dashboards
├── 1.6: Genie Spaces ← CRITICAL: Agents depend on this
└── 1.7: Alerting

Phase 2 (Deploy After Phase 1.6)
├── Specialized agents (1 per domain)
├── Orchestrator agent
└── Agent deployment to Model Serving
```

---

## Phase Document Templates

### Prerequisites Summary Template (Optional)

```markdown
# Prerequisites: Data Layer Summary

## Overview

**Status:** ✅ Complete
**Description:** Summary of completed Bronze, Silver, and Gold layers

---

## Bronze Layer

**Schema:** `{project}_bronze`
**Tables:** {n}

| Category | Tables |
|----------|--------|
| {Category 1} | {table_1}, {table_2} |
| {Category 2} | {table_3} |

---

## Silver Layer

**Schema:** `{project}_silver`
**Tables:** {m} streaming tables

| Type | Tables |
|------|--------|
| Dimensions | silver_{entity}_dim |
| Facts | silver_{entity} |

---

## Gold Layer

**Schema:** `{project}_gold`
**Tables:** {n} ({d} dimensions + {f} facts)

| Type | Tables |
|------|--------|
| Dimensions | dim_{entity} |
| Facts | fact_{entity} |

---

## Next Phase

**→ [Phase 1: Use Cases](./phase1-use-cases.md)**
```

### Phase 1: Use Cases Master Template

```markdown
# Phase 1: Use Cases - Analytics Artifacts

## Overview

**Status:** {status}
**Dependencies:** Prerequisites (Gold Layer) ✅ Complete
**Estimated Effort:** {weeks}

---

## Purpose

{Explain TVFs, Metric Views, Dashboards, Monitoring, Genie, Alerts}

---

## Agent Domain Framework

| Domain | Icon | Focus Area | Primary Tables |
|--------|------|------------|----------------|
| {Domain 1} | {emoji} | {focus} | {tables} |

---

## Addendum Index

| # | Addendum | Status | Artifacts |
|---|----------|--------|-----------|
| 1.1 | ML Models | {status} | {count} |
| 1.2 | TVFs | {status} | {count} |
| 1.3 | Metric Views | {status} | {count} |
| 1.4 | Lakehouse Monitoring | {status} | {count} |
| 1.5 | AI/BI Dashboards | {status} | {count} |
| 1.6 | Genie Spaces | {status} | {count} |
| 1.7 | Alerting | {status} | {count} |

---

## Artifact Summary by Domain

### {Domain 1}

| Artifact Type | Count | Examples |
|--------------|-------|----------|
| TVFs | {n} | `get_{metric}_by_{dimension}` |
| Metric Views | {n} | `{domain}_analytics_metrics` |
| Dashboards | {n} | {Domain} Performance Dashboard |
| Monitors | {n} | {Domain} Data Quality Monitor |
| Alerts | {n} | {metric} drop, {anomaly} |
| ML Models | {n} | {Type} Predictor/Forecaster |
| Genie Space | 1 | {Domain} Intelligence |

---

## Key Business Questions by Domain

### {Domain 1}

1. {Question 1}?
2. {Question 2}?
...

---

## Implementation Order

### Week 1: Foundation
1. Create TVFs (all domains)
2. Create Metric Views

### Week 2: Monitoring
3. Setup Lakehouse Monitors
4. Create Alerting Framework
5. Validate data quality baselines

### Week 3: Visualization
6. Build AI/BI Dashboards
7. Configure Genie Spaces
8. Document business usage guides

### Week 4: Intelligence
9. Train ML Models
10. Deploy model endpoints
11. Integrate predictions

---

## Success Criteria

| Metric | Target |
|--------|--------|
| TVFs deployed and functional | {count} |
| Metric Views queryable | {count} |
| Dashboards published | {count} |
| Monitors with baselines | {count} |
| Alerts configured | {count} |
| Genie Spaces responding | {count} |

---

## Next Phase

**→ [Phase 2: Agent Framework](./phase2-agent-framework.md)**
```

---

## Addendum Templates

### Phase 1 Addendum 1.2: TVFs Template

```markdown
# Phase 1 Addendum 1.2: Table-Valued Functions (TVFs)

## Overview

**Status:** {status}
**Dependencies:** Prerequisites (Gold Layer) ✅ Complete
**Artifact Count:** {n} TVFs

---

## TVF Summary by Domain

| Domain | Icon | TVF Count | Primary Tables |
|--------|------|-----------|----------------|
| {Domain 1} | {emoji} | {n} | {tables} |

---

## {Domain 1} TVFs

### 1. get_{metric}_by_{dimension}

**Purpose:** {description}

```sql
CREATE OR REPLACE FUNCTION ${catalog}.${gold_schema}.get_{metric}_by_{dimension}(
    start_date STRING COMMENT 'Start date in YYYY-MM-DD format',
    end_date STRING COMMENT 'End date in YYYY-MM-DD format',
    filter_param {TYPE} DEFAULT NULL COMMENT 'Optional filter'
)
RETURNS TABLE (
    {column_1} {TYPE},
    {column_2} {TYPE},
    {measure_1} {TYPE}
)
COMMENT 'LLM: {Description for Genie}.
Use for: {use cases}.
Example questions: "{Question 1}" "{Question 2}"'
RETURN
    SELECT 
        ...
    FROM ${catalog}.${gold_schema}.{fact_table}
    WHERE {date_column} BETWEEN CAST(start_date AS DATE) AND CAST(end_date AS DATE)
    GROUP BY ...
    ORDER BY ...;
```

---

## TVF Design Standards

### Parameter Requirements

```sql
-- ✅ CORRECT: STRING dates for Genie compatibility
start_date STRING COMMENT 'Start date in YYYY-MM-DD format'

-- ❌ WRONG: DATE type breaks Genie
start_date DATE
```

### Comment Structure

```sql
COMMENT 'LLM: [One-line description].
Use for: [Use cases separated by commas].
Example questions: "[Question 1]" "[Question 2]"'
```

---

## Implementation Checklist

### {Domain 1} TVFs
- [ ] get_{metric1}_by_{dimension}
- [ ] get_{metric2}_by_{dimension}
- [ ] get_top_{entities}_by_{metric}
```

### Phase 1 Addendum 1.7: Alerting Template

```markdown
# Phase 1 Addendum 1.7: Alerting Framework

## Overview

**Status:** {status}
**Dependencies:** Prerequisites (Gold Layer), 1.4 (Lakehouse Monitoring)
**Artifact Count:** {n} SQL Alerts

---

## Alert Summary by Domain

| Domain | Icon | Alert Count | Critical | Warning | Info |
|--------|------|-------------|----------|---------|------|
| {Domain 1} | {emoji} | {n} | {c} | {w} | {i} |

---

## Alert ID Convention

```
<DOMAIN>-<NUMBER>-<SEVERITY>
```

Examples:
- `{DOM}-001-CRIT` - {Domain} critical alert #1
- `{DOM}-002-WARN` - {Domain} warning alert #2

---

## {Domain 1} Alerts

### {DOM}-001-CRIT: {Alert Name}

**Severity:** 🔴 Critical
**Frequency:** {Daily/Hourly/Weekly}
**Condition:** {Description}

```sql
SELECT 
    CURRENT_DATE() as alert_date,
    {metric} as current_value,
    {threshold} as threshold,
    '{message}' as alert_message
FROM ${catalog}.${gold_schema}.{table}
WHERE {condition}
```

**Actions:**
- Email: {recipients}
- Slack: #{channel}

---

## Implementation Checklist

### {Domain 1} Alerts
- [ ] {DOM}-001-CRIT: {Alert Name}
- [ ] {DOM}-002-WARN: {Alert Name}
- [ ] {DOM}-003-INFO: {Alert Name}
```

### Phase 1 Addendum 1.6: Genie Spaces Template

```markdown
# Phase 1 Addendum 1.6: Genie Spaces

## Overview

**Status:** {status}
**Dependencies:** Prerequisites (Gold Layer), 1.2 (TVFs), 1.3 (Metric Views), 1.1 (ML Models)
**Artifact Count:** {n} Genie Spaces ({n-1} domain-specific + 1 unified)

---

## Critical: Agent Integration Readiness

⚠️ **Genie Spaces serve as the natural language query interface for Phase 2 AI Agents.**

Each Genie Space will become a "tool" for its corresponding AI agent:
- Genie Space `instructions` → Agent system prompt
- Genie Space data assets → Agent query capabilities
- Genie Space benchmark questions → Agent testing framework

---

## Genie Space Summary

| Domain | Icon | Genie Space Name | Agent Integration |
|--------|------|------------------|-------------------|
| {Domain 1} | {emoji} | {Domain 1} Intelligence | → {Domain 1} Agent tool |
| {Domain 2} | {emoji} | {Domain 2} Intelligence | → {Domain 2} Agent tool |
| Unified | 🌐 | {Project} Monitor | → Orchestrator Agent tool |

---

## {Domain 1} Intelligence Genie Space

### A. Space Name
`{Domain 1} Intelligence`

### B. Description (2-3 sentences)
{Description optimized for LLM understanding. Include primary use cases.}

### C. Sample Questions (5-7 examples)
1. {Question 1}
2. {Question 2}
3. {Question 3}
4. {Question 4}
5. {Question 5}

### D. Data Assets

**Priority Order:** Metric Views → TVFs → ML Prediction Tables → Gold Tables

| Type | Asset | Purpose |
|------|-------|---------|
| Metric View | `{domain}_analytics_metrics` | Broad aggregations |
| TVF | `get_{metric}_by_{dimension}` | Parameterized queries |
| ML Model | `{model}_predictions` | ML-enhanced insights |
| Gold Table | `fact_{entity}` | Direct access (rare) |

### E. General Instructions (≤20 lines)
```
You are {Domain 1} Intelligence, helping users analyze {domain focus}.

DATA ASSET SELECTION:
- Use Metric Views for: {use cases}
- Use TVFs for: {use cases}
- Use ML tables for: {use cases}

QUERY PATTERNS:
- Always use MEASURE() syntax for Metric View aggregations
- TVF parameters use STRING dates (YYYY-MM-DD format)
- Use 3-part namespace: catalog.schema.table

{Additional domain-specific rules}
```

### F. TVF Syntax Guidance
```sql
-- {Domain 1} TVFs require STRING date parameters
SELECT * FROM TABLE(get_{metric}_by_{dimension}('2024-01-01', '2024-12-31'))
```

### G. Benchmark Questions with Exact SQL
1. **{Question 1}**
   ```sql
   SELECT ... FROM TABLE(get_{metric}_by_{dimension}(...))
   ```

2. **{Question 2}**
   ```sql
   SELECT MEASURE(`{measure}`) FROM {metric_view} WHERE ...
   ```

---

## Agent Readiness Validation

After deployment, validate each Genie Space is ready for agent integration:

- [ ] All benchmark questions return correct results
- [ ] Query latency < 10 seconds for typical queries
- [ ] >80% accuracy on domain-specific natural language questions
- [ ] Instructions are concise (≤20 lines) and clear for LLM
- [ ] All data assets are accessible and queryable

---

## Implementation Checklist

### {Domain 1} Intelligence
- [ ] Create Genie Space in Databricks workspace
- [ ] Configure data assets (prioritize Metric Views)
- [ ] Write general instructions (≤20 lines)
- [ ] Add benchmark questions with working SQL
- [ ] Test natural language queries
- [ ] Validate for Phase 2 agent integration

### Unified {Project} Monitor
- [ ] Create unified Genie Space
- [ ] Include all domain data assets
- [ ] Write multi-domain routing instructions
- [ ] Test cross-domain queries
- [ ] Prepare for Orchestrator Agent
```

---

### Phase 2: Agent Framework Template

```markdown
# Phase 2: Agent Framework - AI Agents

## Overview

**Status:** {status}
**Dependencies:** Phase 1 (Use Cases) - especially 1.6 Genie Spaces ✅
**Estimated Effort:** {weeks}

---

## Purpose

AI agents provide natural language interfaces to data assets. Agents use Genie Spaces
as their query interface - they do NOT write SQL directly. This architecture provides:

- Natural language understanding via Genie Spaces
- Abstraction from underlying data schema changes
- Built-in query guardrails and optimization
- Benchmark testing framework from Genie Spaces

---

## Agent Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    USER / FRONTEND APPLICATION                       │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR AGENT                                │
│  Purpose: Intent classification, multi-domain query coordination     │
│  Genie Space: Unified {Project} Monitor                             │
│  Capabilities: Route to specialized agents, synthesize responses     │
└─────────────────────────────────────────────────────────────────────┘
                    │               │               │
        ┌───────────┘               │               └───────────┐
        ▼                           ▼                           ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│  {Domain 1} Agent │   │  {Domain 2} Agent │   │  {Domain N} Agent │
│  Genie: {D1} Int  │   │  Genie: {D2} Int  │   │  Genie: {DN} Int  │
└───────────────────┘   └───────────────────┘   └───────────────────┘
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────────────────────────────────────────────────────────────┐
│                         GENIE SPACES (Phase 1.6)                       │
│  Each agent uses its dedicated Genie Space as the query interface      │
└───────────────────────────────────────────────────────────────────────┘
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────────────────────────────────────────────────────────────┐
│                    DATA ASSETS (Phase 1.1-1.5, 1.7)                    │
│  TVFs | Metric Views | ML Models | Lakehouse Monitors | Gold Tables   │
└───────────────────────────────────────────────────────────────────────┘
```

---

## Agent-to-Genie Space Mapping

| Agent | Dedicated Genie Space | Purpose |
|-------|----------------------|---------|
| {Domain 1} Agent | {Domain 1} Intelligence | {domain 1} queries via NL |
| {Domain 2} Agent | {Domain 2} Intelligence | {domain 2} queries via NL |
| Orchestrator Agent | Unified {Project} Monitor | Intent classification |

---

## Agent Summary by Domain

| Domain | Icon | Agent Name | Genie Space | Capabilities |
|--------|------|------------|-------------|--------------|
| {Domain 1} | {emoji} | {Domain 1} Agent | {Domain 1} Intelligence | {capabilities} |
| {Domain 2} | {emoji} | {Domain 2} Agent | {Domain 2} Intelligence | {capabilities} |
| Unified | 🌐 | Orchestrator Agent | Unified Monitor | Multi-domain coordination |

---

## {Domain 1} Agent

**Name:** {Domain 1} Intelligence Agent
**Focus:** {focus area}
**Genie Space:** {Domain 1} Intelligence ← Agent's primary tool
**System Prompt Source:** Genie Space instructions

**How Agent Uses Genie Space:**
1. Agent receives natural language query from user/orchestrator
2. Agent sends query to Genie Space via tool call
3. Genie Space translates NL to SQL and executes
4. Agent receives results and synthesizes response

**Capabilities (via Genie Space):**
- Answer {domain}-related questions using Genie Space NL interface
- Access {domain} TVFs indirectly (Genie routes to correct TVF)
- Retrieve {domain} ML predictions (Genie accesses prediction tables)
- Generate {domain} insights from Metric Views

---

## Three-Level Testing Strategy

### Level 1: Genie Space Standalone (Phase 1.6)

Validate Genie Spaces work before agent integration:
- [ ] All benchmark questions return correct results
- [ ] Query latency < 10 seconds
- [ ] >80% accuracy on domain-specific questions

### Level 2: Agent Integration (Phase 2)

Validate agents correctly use Genie Spaces:
- [ ] Agent correctly routes queries to Genie Space tool
- [ ] Agent interprets Genie Space results accurately
- [ ] >90% intent classification accuracy
- [ ] Correct tool usage patterns

### Level 3: Multi-Agent Workflow (Phase 2)

Validate Orchestrator coordinates specialized agents:
- [ ] Orchestrator correctly classifies multi-domain intent
- [ ] Sub-queries routed to correct specialized agents
- [ ] Responses synthesized coherently
- [ ] >85% multi-intent classification accuracy

---

## Implementation Checklist

### Prerequisites (Must Complete First)
- [ ] All Genie Spaces deployed and responding (Phase 1.6 complete)
- [ ] Genie Space benchmark questions validated
- [ ] Genie Space instructions finalized (become agent system prompts)

### Agent Development
- [ ] Define agent system prompts (derived from Genie Space instructions)
- [ ] Configure Genie Space as agent tool (LangChain/LangGraph)
- [ ] Implement agent response synthesis logic
- [ ] Test agent-to-Genie Space integration

### Orchestrator Development
- [ ] Define orchestrator routing logic
- [ ] Map intents to specialized agents
- [ ] Implement multi-agent coordination
- [ ] Test multi-domain query handling

### Deployment
- [ ] Deploy agents to Model Serving
- [ ] Configure API endpoints
- [ ] Set up monitoring and logging
- [ ] Validate end-to-end workflows

---

## Next Phase

**→ [Phase 3: Frontend App](./phase3-frontend-app.md)**
```

### Phase 3: Frontend App Template

```markdown
# Phase 3: Frontend App - User Interface

## Overview

**Status:** {status}
**Dependencies:** Phase 2 (Agent Framework)
**Estimated Effort:** {weeks}

---

## Purpose

{Explain frontend application, user interface, self-service analytics}

---

## Application Architecture

### Pages/Views

| Page | Purpose | Agents Used |
|------|---------|-------------|
| {Page 1} | {purpose} | {agents} |

---

## Implementation Checklist

- [ ] Design UI mockups
- [ ] Implement frontend framework
- [ ] Integrate with agents
- [ ] Deploy application
```

---

## README.md Template

```markdown
# {Project Name} Project Plans

**Complete phased implementation plan for {Project Description}**

---

## 📋 Plan Index

### Prerequisites (Complete)

| Layer | Document | Status | Description |
|-------|----------|--------|-------------|
| Bronze | [Prerequisites](./prerequisites.md) | ✅ Complete | Raw data ingestion ({n} tables) |
| Silver | [Prerequisites](./prerequisites.md) | ✅ Complete | DLT streaming with DQ |
| Gold | [Prerequisites](./prerequisites.md) | ✅ Complete | Dimensional model ({n} tables) |

### Project Phases

| Phase | Document | Status | Description |
|-------|----------|--------|-------------|
| 1 | [Phase 1: Use Cases](./phase1-use-cases.md) | {status} | Analytics artifacts |
| 2 | [Phase 2: Agent Framework](./phase2-agent-framework.md) | {status} | AI agents |
| 3 | [Phase 3: Frontend App](./phase3-frontend-app.md) | {status} | User interface |

### Phase 1 Addendums

| # | Addendum | Status | Artifacts |
|---|----------|--------|-----------|
| 1.1 | [ML Models](./phase1-addendum-1.1-ml-models.md) | {status} | {count} |
| 1.2 | [TVFs](./phase1-addendum-1.2-tvfs.md) | {status} | {count} |
| 1.3 | [Metric Views](./phase1-addendum-1.3-metric-views.md) | {status} | {count} |
| 1.4 | [Lakehouse Monitoring](./phase1-addendum-1.4-lakehouse-monitoring.md) | {status} | {count} |
| 1.5 | [AI/BI Dashboards](./phase1-addendum-1.5-aibi-dashboards.md) | {status} | {count} |
| 1.6 | [Genie Spaces](./phase1-addendum-1.6-genie-spaces.md) | {status} | {count} |
| 1.7 | [Alerting](./phase1-addendum-1.7-alerting.md) | {status} | {count} |

---

## 🎯 Agent Domain Framework

| Domain | Icon | Focus Area | Key Gold Tables |
|--------|------|------------|-----------------|
| {Domain 1} | {emoji} | {focus} | {tables} |

---

## 📊 Project Scope Summary

### Prerequisites (Data Layers)

| Layer | Schema | Tables | Status |
|-------|--------|--------|--------|
| Bronze | `{schema}` | {n} | ✅ Complete |
| Silver | `{schema}` | {n} | ✅ Complete |
| Gold | `{schema}` | {n} | ✅ Complete |

### Phase 1 (Use Cases)

| Artifact Type | Count |
|---------------|-------|
| TVFs | {n}+ |
| Metric Views | {n} |
| Dashboards | {n} |
| Monitors | {n} |
| Alerts | {n} |
| ML Models | {n} |
| Genie Spaces | {n} |

---

## 📈 Success Metrics

| Phase | Criteria | Target |
|-------|----------|--------|
| Use Cases | TVFs deployed | {n}+ |
| Use Cases | Dashboards created | {n}+ |
| Agents | Agents responding | {n}+ |
| Frontend | App deployed | 1 |
```

---

## ✅ Validation Checklist

### Plan Structure
- [ ] README.md with index and overview
- [ ] Prerequisites section documents completed layers
- [ ] Phase 1-3 documents created
- [ ] All Phase 1 addendums included
- [ ] Cross-references between documents

### Content Quality
- [ ] Agent Domains defined consistently
- [ ] All artifacts tagged with domain
- [ ] Business questions documented per domain
- [ ] Implementation checklists in each phase
- [ ] Success criteria tables included

### Completeness
- [ ] All domains covered (4-6 minimum)
- [ ] Minimum artifact counts per domain:
  - [ ] TVFs: 4+ per domain
  - [ ] Alerts: 4+ per domain  
  - [ ] Dashboard pages: 2+ per domain
- [ ] Key business questions answered

### Agent Layer Architecture (If Phase 2 Included)
- [ ] Agent-to-Genie Space mapping documented (1:1 recommended)
- [ ] Deployment order specified (Genie Spaces before Agents)
- [ ] Three-level testing strategy defined
- [ ] Orchestrator agent included for multi-domain coordination
- [ ] Genie Space instructions documented (become agent system prompts)
- [ ] Agent tool definitions reference Genie Spaces (not direct SQL)

---

## 🎯 Example: Hospitality (Wanderbricks)

### Agent Domains

| Domain | Icon | Focus Area | Key Tables |
|--------|------|------------|------------|
| Revenue | 💰 | Booking revenue, payments | fact_booking_daily, fact_booking_detail |
| Engagement | 📊 | Views, clicks, conversions | fact_property_engagement |
| Property | 🏠 | Listings, pricing | dim_property |
| Host | 👤 | Host performance | dim_host |
| Customer | 🎯 | User behavior, CLV | dim_user |

### Agent-to-Genie Space Mapping (Example)

| Agent | Genie Space | Primary Use Cases |
|-------|-------------|-------------------|
| 💰 Revenue Agent | Revenue Intelligence | Booking analysis, payment tracking |
| 📊 Engagement Agent | Engagement Analytics | Funnel analysis, conversion rates |
| 🏠 Property Agent | Property Intelligence | Listing performance, pricing |
| 👤 Host Agent | Host Intelligence | Host earnings, performance |
| 🎯 Customer Agent | Customer Intelligence | CLV analysis, user behavior |
| 🌐 Orchestrator | Wanderbricks Health Monitor | Multi-domain coordination |

### Artifact Totals

| Artifact Type | Count |
|--------------|-------|
| Gold Tables (Prerequisite) | 8 |
| TVFs | 25+ |
| Metric Views | 5 |
| Dashboards | 5 |
| Monitors | 5 |
| Alerts | 21 |
| ML Models | 5 |
| Genie Spaces | 6 (5 domain + 1 unified) |
| AI Agents | 6 (5 domain + 1 orchestrator) |
| **Total** | **87+** |

### Agent Architecture Flow (Example)

```
User: "What was last month's revenue and which hosts performed best?"
                    │
                    ▼
        ┌───────────────────────────────┐
        │     Orchestrator Agent        │
        │ Uses: Wanderbricks Monitor    │
        │ Intent: Multi-domain (Rev+Host)│
        └───────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌───────────────────┐   ┌───────────────────┐
│  Revenue Agent    │   │   Host Agent      │
│  Uses: Revenue    │   │   Uses: Host      │
│  Intelligence     │   │   Intelligence    │
└───────────────────┘   └───────────────────┘
        │                       │
        ▼                       ▼
    Genie Space             Genie Space
        │                       │
        ▼                       ▼
    Revenue TVFs            Host TVFs
    Metric Views           Metric Views
                    │
                    ▼
        Synthesized Response:
        "Last month's revenue was $2.4M.
         Top hosts: [Host A], [Host B]..."
```

---

## 💡 Key Learnings: Agent Layer Architecture

### Why Agents Should Use Genie Spaces (Not Direct SQL)

1. **Abstraction Layer:** Agents don't need to know SQL syntax or schema details
2. **Schema Evolution:** Data model changes don't break agent implementations
3. **Query Optimization:** Genie Spaces handle SQL optimization automatically
4. **Natural Language:** Genie Spaces are designed for NL-to-SQL translation
5. **Guardrails:** Genie Spaces provide built-in query safety checks
6. **Testing Framework:** Benchmark questions test both Genie and Agent accuracy

### Critical Deployment Order

```
Phase 1.1-1.5 (Data Assets) → Phase 1.6 (Genie Spaces) → Phase 2 (Agents)
         ↓                            ↓                        ↓
   Build foundation          Create NL interface        Consume interface
```

**⚠️ Agents CANNOT be developed until Genie Spaces are deployed and validated.**

### Agent-to-Genie Space Design Patterns

| Pattern | Description | When to Use |
|---------|-------------|-------------|
| 1:1 Mapping | Each agent has dedicated Genie Space | Domain-specific agents |
| Orchestrator + Unified | Orchestrator uses unified Genie Space | Multi-domain coordination |
| Hierarchical | Orchestrator routes to specialized agents | Complex multi-intent queries |

### System Prompt Derivation

**Genie Space `instructions` become agent system prompts:**
- Keep instructions ≤20 lines (LLM context efficiency)
- Include data asset selection guidance
- Document query patterns and syntax rules
- Add domain-specific business rules

### Three-Level Testing (Critical for Quality)

| Level | What to Test | Success Criteria |
|-------|--------------|------------------|
| 1. Genie Standalone | Genie Space accuracy | >80% benchmark accuracy |
| 2. Agent Integration | Agent uses Genie correctly | >90% tool usage accuracy |
| 3. Multi-Agent | Orchestrator coordination | >85% intent classification |

**Test each level before proceeding to the next.** Do not skip levels.

---

## 📚 References

### Related Prompts
- [01-bronze-layer-prompt.md](./01-bronze-layer-prompt.md) - Bronze implementation
- [02-silver-layer-prompt.md](./02-silver-layer-prompt.md) - Silver implementation
- [03a-gold-layer-design-prompt.md](./03a-gold-layer-design-prompt.md) - Gold design
- [03b-gold-layer-implementation-prompt.md](./03b-gold-layer-implementation-prompt.md) - Gold implementation
- [04-metric-views-prompt.md](./04-metric-views-prompt.md) - Metric Views
- [05-monitoring-prompt.md](./05-monitoring-prompt.md) - Lakehouse Monitoring
- [09-table-valued-functions-prompt.md](./09-table-valued-functions-prompt.md) - TVFs
- [10-aibi-dashboards-prompt.md](./10-aibi-dashboards-prompt.md) - Dashboards

### Cursor Rules
- [26-project-plan-methodology.mdc](../.cursor/rules/planning/26-project-plan-methodology.mdc) - Full methodology (includes Agent Layer Architecture)
- [16-genie-space-patterns.mdc](../.cursor/rules/semantic-layer/16-genie-space-patterns.mdc) - Genie Space structure and patterns
- [15-databricks-table-valued-functions.mdc](../.cursor/rules/semantic-layer/15-databricks-table-valued-functions.mdc) - TVF patterns for Genie

### Official Documentation
- [Databricks Docs](https://docs.databricks.com/)
- [Unity Catalog](https://docs.databricks.com/unity-catalog/)
- [Delta Live Tables](https://docs.databricks.com/dlt/)
- [Lakehouse Monitoring](https://docs.databricks.com/lakehouse-monitoring/)
- [Metric Views](https://docs.databricks.com/metric-views/)
- [Genie Spaces](https://docs.databricks.com/genie/)
- [Model Serving](https://docs.databricks.com/machine-learning/model-serving/)
- [Foundation Models (DBRX)](https://docs.databricks.com/machine-learning/foundation-models/)

### Agent Framework Technologies
- [LangChain](https://python.langchain.com/) - Agent framework
- [LangGraph](https://langchain-ai.github.io/langgraph/) - Multi-agent workflows
