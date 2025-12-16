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

### Phase 2: Agent Framework Template

```markdown
# Phase 2: Agent Framework - AI Agents

## Overview

**Status:** {status}
**Dependencies:** Phase 1 (Use Cases)
**Estimated Effort:** {weeks}

---

## Purpose

{Explain AI agents, natural language interfaces, automated workflows}

---

## Agent Summary by Domain

| Domain | Icon | Agent Name | Capabilities |
|--------|------|------------|--------------|
| {Domain 1} | {emoji} | {Domain} Agent | {capabilities} |

---

## Agent Architecture

### {Domain 1} Agent

**Name:** {Domain} Intelligence Agent
**Focus:** {focus area}
**Gold Tables:** {tables}
**TVFs Used:** `get_{metric}_by_{dimension}`, ...
**Genie Space:** {Domain} Intelligence

**Capabilities:**
- Answer {domain}-related questions
- Execute {domain} TVFs
- Generate {domain} insights
- Create {domain} reports

---

## Implementation Checklist

- [ ] Define agent capabilities
- [ ] Configure agent tools (TVFs)
- [ ] Test natural language queries
- [ ] Deploy to production

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
| Genie Spaces | 5 |
| AI Agents | 6 |
| **Total** | **85+** |

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
- [26-project-plan-methodology.mdc](../.cursor/rules/planning/26-project-plan-methodology.mdc) - Full methodology

### Official Documentation
- [Databricks Docs](https://docs.databricks.com/)
- [Unity Catalog](https://docs.databricks.com/unity-catalog/)
- [Delta Live Tables](https://docs.databricks.com/dlt/)
- [Lakehouse Monitoring](https://docs.databricks.com/lakehouse-monitoring/)
- [Metric Views](https://docs.databricks.com/metric-views/)
- [Genie Spaces](https://docs.databricks.com/genie/)
