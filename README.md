# Vibe Coding Lakehouse Starter Repository

A comprehensive **AI-assisted development framework** for building production-grade Databricks Lakehouse solutions. This repository provides Agent Skills that encode domain expertise directly into your AI coding assistant, enabling rapid development of complete Medallion Architecture implementations — from a raw schema CSV to production GenAI agents.

> **"Vibe Coding"** — Leverage AI coding assistants to accelerate data platform development from weeks to hours.

---

## What's Inside

| Component | Description | Count |
|-----------|-------------|-------|
| **Agent Skills** | Structured knowledge packages for AI-assisted Databricks development | 50+ skills across 12 domains |
| **Cursor Rules** | Lightweight always-on routing rules that direct the agent to skills | 2 rules |
| **Context Files** | Customer schema CSV (the starting input for the pipeline) | 1 file |

---

## Quick Start

### Prerequisites

- Databricks workspace with Unity Catalog enabled
- [Cursor IDE](https://cursor.sh/) with Agent mode enabled
- Databricks CLI v0.200+ installed and configured
- Git for version control

### Getting Started

1. **Clone the repository**

```bash
git clone https://github.com/prashsub/vibe_coding_lakehouse_starter_repo.git
cd vibe_coding_lakehouse_starter_repo
```

2. **Place your schema CSV** in the `context/` directory

3. **Open in Cursor IDE** and start with the first prompt:

```
I have a customer schema at @context/Wanderbricks_Schema.csv.
Please design the Gold layer using @.cursor/skills/gold/00-gold-layer-design/SKILL.md
```

4. **Follow the [QUICKSTART guide](QUICKSTART.md)** for all 9 stages

---

## How It Works

The framework uses a **skills-first architecture**: 2 lightweight routing rules point the AI assistant to 50+ Agent Skills organized by domain. Each skill contains production-tested patterns, reference documentation, executable scripts, and starter templates.

### Design-First Pipeline (9 Stages)

One prompt per stage. One new Cursor Agent conversation per stage.

```
context/*.csv
  → Gold Design (1)      — dimensional model, ERDs, YAML schemas
  → Bronze (2)           — source tables + test data
  → Silver (3)           — DLT pipelines + data quality
  → Gold Impl (4)        — tables, merges, constraints
  → Planning (5)         — phase plans + manifest contracts
  → Semantic (6)         — Metric Views, TVFs, Genie Spaces
  → Observability (7)    — monitors, dashboards, alerts
  → ML (8)               — experiments, training, inference
  → GenAI Agents (9)     — agents, evaluation, deployment
```

### Key Principle: Design-First

Design the target Gold dimensional model **first** (from the customer's schema CSV), then build the data layers (Bronze → Silver) to feed it. This is the opposite of the traditional bottom-up approach.

---

## Repository Structure

```
.
├── .cursor/
│   ├── rules/                          # 2 always-on routing rules
│   │   ├── skill-navigator.mdc         #   Routes tasks to orchestrator skills
│   │   └── common-skills-reference.mdc #   Indexes 8 shared common skills
│   └── skills/                         # 50+ Agent Skills
│       ├── admin/                      #   Skill creation, auditing, docs (6)
│       ├── bronze/                     #   Bronze layer + Faker data (2)
│       ├── common/                     #   Cross-cutting shared skills (8)
│       ├── exploration/                #   Ad-hoc notebooks (1)
│       ├── genai-agents/               #   GenAI agent patterns (10+)
│       ├── gold/                       #   Gold design + implementation (9)
│       ├── ml/                         #   MLflow pipelines (1)
│       ├── monitoring/                 #   Monitors, dashboards, alerts (5)
│       ├── planning/                   #   Project planning (2)
│       ├── semantic-layer/             #   Metric Views, TVFs, Genie (6)
│       ├── silver/                     #   DLT pipelines, DQ rules (4)
│       └── skill-navigator/            #   Master routing system (1)
│
├── context/
│   └── Wanderbricks_Schema.csv         # Customer schema input
│
├── docs/                               # Framework documentation
│   └── vibe-coding-framework-design/   #   Complete design documentation
│
├── QUICKSTART.md                       # One-prompt-per-stage guide
└── README.md                           # This file
```

---

## Agent Skills by Domain

Skills follow an **orchestrator/worker** pattern: orchestrators (prefixed `00-`) manage end-to-end workflows, workers (prefixed `01-`, `02-`, etc.) handle specific patterns.

| Domain | Orchestrator | Workers | Focus |
|--------|-------------|---------|-------|
| **Gold (Design)** | `00-gold-layer-design` | 7 | ERDs, YAML schemas, dimensional modeling |
| **Bronze** | `00-bronze-layer-setup` | 1 | Table DDLs, Faker data, source copy |
| **Silver** | `00-silver-layer-setup` | 2 | DLT expectations, DQX diagnostics |
| **Gold (Impl)** | `01-gold-layer-setup` | shared | MERGE scripts, FK constraints |
| **Planning** | `00-project-planning` | 0 | Phase plans, YAML manifest contracts |
| **Semantic** | `00-semantic-layer-setup` | 5 | Metric Views, TVFs, Genie Spaces |
| **Monitoring** | `00-observability-setup` | 4 | Monitors, dashboards, SQL alerts |
| **ML** | `00-ml-pipeline-setup` | 0 | MLflow, Feature Store, inference |
| **GenAI** | `00-genai-agents-setup` | 8+ | ResponsesAgent, evaluation, deployment |
| **Common** | — | 8 | Asset Bundles, naming, constraints, imports |

---

## What You Get

After using this framework:

- **Complete Medallion Architecture** — Bronze, Silver, and Gold tables with governance
- **Data Quality** — DLT expectations with quarantine patterns, stored in Unity Catalog
- **Dimensional Model** — Fact and dimension tables with PK/FK constraints
- **Semantic Layer** — Metric Views and TVFs for Genie natural language queries
- **Observability** — Lakehouse Monitors, AI/BI Dashboards, and SQL Alerts
- **ML Pipelines** — MLflow experiments, model training, and batch inference
- **GenAI Agents** — ResponsesAgent with multi-agent Genie orchestration
- **Governance** — PII tags, data classification, rich comments, full lineage

### Time Savings

| Approach | Time | Savings |
|----------|------|---------|
| **Using Framework (core)** | 17-28 hours | — |
| **Using Framework (full stack)** | 31-56 hours | — |
| **From Scratch** | 80-120 hours | — |
| **Savings** | — | **4-6x faster** |

---

## Key Technologies

- **Databricks Unity Catalog** — Governance, lineage, and data classification
- **Delta Lake** — ACID transactions, time travel, and Change Data Feed
- **Delta Live Tables (DLT)** — Streaming pipelines with data quality expectations
- **Databricks Asset Bundles** — Infrastructure as Code for all resources
- **Metric Views** — Semantic metadata layer for AI/BI and Genie
- **Genie Spaces** — Natural language query interface
- **Lakehouse Monitoring** — Data profiling with custom business metrics
- **MLflow** — ML experiment tracking, model registry, and GenAI agents

---

## Documentation

| Document | Purpose |
|----------|---------|
| [QUICKSTART.md](QUICKSTART.md) | One-prompt-per-stage guide (start here) |
| [Framework Design Docs](docs/vibe-coding-framework-design/00-index.md) | Complete architecture and design documentation |
| [Skill Navigator](.cursor/skills/skill-navigator/SKILL.md) | Master skill routing system |

---

## Domain Adaptation

These patterns work for any industry:

| Original | Healthcare | Finance | Manufacturing |
|----------|------------|---------|---------------|
| store | hospital | branch | facility |
| product | medication | financial_product | component |
| transaction | encounter | transaction | production_run |
| revenue | reimbursement | interest_income | output_value |

---

## Pro Tips

1. **One prompt per stage** — Each orchestrator skill handles the full workflow
2. **New conversation per stage** — Start fresh to keep context clean
3. **Start with Gold Design** — Design the target model before building Bronze/Silver
4. **Let the skill do the thinking** — The orchestrator loads its workers and common skills automatically
5. **Test with Faker** — Generate synthetic data before connecting real sources
6. **Deploy to dev first** — Use `databricks bundle deploy -t dev`
7. **If something fails** — The autonomous operations skill handles troubleshooting

---

## Resources

### Official Documentation

- [Databricks Documentation](https://docs.databricks.com/)
- [Unity Catalog](https://docs.databricks.com/unity-catalog/)
- [Delta Lake](https://docs.databricks.com/delta/)
- [DLT Expectations](https://docs.databricks.com/dlt/expectations)
- [Metric Views](https://docs.databricks.com/metric-views/)
- [Lakehouse Monitoring](https://docs.databricks.com/lakehouse-monitoring/)
- [MLflow](https://mlflow.org/docs/latest/)

### Framework Support

- See the [Skill Navigator](.cursor/skills/skill-navigator/SKILL.md) for routing to the right skill
- Run `@.cursor/skills/admin/self-improvement/SKILL.md` to capture learnings from errors
- Run `@.cursor/skills/admin/skill-freshness-audit/SKILL.md` to verify skills are current

---

## License

This repository is intended for educational and development purposes. Please review and customize the patterns for your specific use case and compliance requirements.

---

## Get Started Now

```bash
# Clone the repository
git clone https://github.com/prashsub/vibe_coding_lakehouse_starter_repo.git

# Open in Cursor IDE
cursor vibe_coding_lakehouse_starter_repo

# Follow the QUICKSTART guide
# → QUICKSTART.md
```

**Core platform (stages 1-7): 17-28 hours**
**Full stack with ML and GenAI (stages 1-9): 31-56 hours**
