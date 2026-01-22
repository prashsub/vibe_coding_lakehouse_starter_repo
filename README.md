# Vibe Coding Lakehouse Starter Repository

A comprehensive **AI-assisted development framework** for building production-grade Databricks Lakehouse solutions. This repository provides cursor rules and reusable prompts that enable rapid development of complete Medallion Architecture implementations.

> **"Vibe Coding"** - Leverage AI coding assistants to accelerate data platform development from weeks to hours.

---

## 🎯 What's Inside

| Component | Description | Count |
|-----------|-------------|-------|
| **Cursor Rules** | Production-tested patterns for Databricks development | 27 rules (~13,100 lines) |
| **Reusable Prompts** | Templates for AI-assisted code generation | 17 prompts |
| **Context Files** | Schema definitions and example configurations | 2 files |

---

## 🚀 Quick Start

### Prerequisites

- Databricks workspace with Unity Catalog enabled
- [Cursor IDE](https://cursor.sh/) or compatible AI coding assistant
- Databricks CLI installed
- Git for version control

### Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/prashsub/vibe_coding_lakehouse_starter_repo.git
   cd vibe_coding_lakehouse_starter_repo
   ```

2. **Read the framework guides**
   - [Cursor Rules README](.cursor/rules/README.md) - Complete framework overview
   - [Prompts README](context/prompts/README.md) - How to use the prompts

3. **Start building**
   - Use prompts with your AI assistant for code generation
   - Follow cursor rules for best practices enforcement

---

## 📂 Repository Structure

```
.
├── .cursor/rules/              # AI-enforced development patterns
│   ├── common/                 # Foundation & infrastructure (9 rules)
│   ├── bronze/                 # Raw data ingestion (1 rule)
│   ├── silver/                 # Data quality & validation (2 rules)
│   ├── gold/                   # Analytics-ready models (7 rules)
│   ├── semantic-layer/         # Natural language & BI (4 rules)
│   ├── monitoring/             # Observability & dashboards (3 rules)
│   ├── exploration/            # Ad-hoc analysis (1 rule)
│   ├── planning/               # Project methodology (1 rule)
│   └── admin/                  # Meta rules (3 rules)
│
├── context/
│   ├── prompts/                # Reusable AI prompts (17 templates)
│   ├── Wanderbricks_Schema.csv # Example schema definition
│   └── *.lvdash.json           # Example AI/BI dashboard
│
└── Instructions.pdf            # Getting started guide
```

---

## 📚 Framework Components

### Cursor Rules (27 Rules)

Production-tested patterns organized by Medallion Architecture layer:

| Category | Rules | Focus |
|----------|-------|-------|
| **Common** | 9 | Unity Catalog, Asset Bundles, Schema Management |
| **Bronze** | 1 | Faker data generation for testing |
| **Silver** | 2 | DLT expectations, DQX integration |
| **Gold** | 7 | YAML-driven setup, MERGE patterns, validation |
| **Semantic Layer** | 4 | Metric Views, TVFs, Genie Spaces |
| **Monitoring** | 3 | Lakehouse Monitoring, AI/BI Dashboards, Alerting |
| **Exploration** | 1 | Dual-format notebooks |
| **Planning** | 1 | Project methodology |

### Reusable Prompts (17 Templates)

AI-optimized prompts for complete implementations:

| Prompt | Purpose | Time |
|--------|---------|------|
| **01-bronze-layer** | Raw data ingestion with UC compliance | 2-3h |
| **02-silver-layer** | Data quality with DLT | 2-4h |
| **03a/b-gold-layer** | Design + Implementation | 5-7h |
| **04-metric-views** | Semantic layer for Genie | 2h |
| **05-monitoring** | Lakehouse Monitoring setup | 2h |
| **06-genie-space** | Natural language interface | 1-2h |
| **07-dqx-integration** | Advanced DQ diagnostics | 3-4h |
| **08-exploration-notebook** | Ad-hoc analysis | 1h |
| **09-table-valued-functions** | Pre-built queries for Genie | 2-3h |
| **10-aibi-dashboards** | Lakeview visual dashboards | 2-4h |
| **11-project-plan** | Comprehensive planning | 2-4h |
| **12-ml-models** | MLflow pipelines | 6-12h |
| **13-agent-architecture** | Agent system design | 2-4h |
| **14-sql-alerts** | Proactive alerting | 2-3h |
| **15-documentation** | Framework documentation | 1-2h |
| **16-capability-audit** | Feature assessment | 1h |
| **17-figma-interface** | UI/UX design | 2-4h |

---

## 🗺️ Learning Paths

### Rapid Prototyping (8 hours)
```
Foundation → Bronze → Silver → Gold → Validate
```
**Output:** Working Medallion Architecture with test data

### Production Implementation (4 weeks)
```
Week 1: Foundation + Bronze + Silver
Week 2: Gold Layer (complete)
Week 3: Semantic Layer
Week 4: Monitoring + Polish
```
**Output:** Complete data product with semantic layer and monitoring

### Data Quality Focus (2 weeks)
```
Standard DQ → Advanced DQ (DQX) → Monitoring
```
**Output:** Multi-layered data quality strategy

---

## ✅ What You Get

After using this framework:

- ✅ **5-10 Bronze tables** with governance metadata
- ✅ **5-10 Silver tables** with streaming + DQ validation
- ✅ **3-5 Gold tables** as analytics-ready models
- ✅ **20-50 data quality rules** (centralized)
- ✅ **Metric Views** for Genie AI natural language queries
- ✅ **Table-Valued Functions** for pre-built analytics
- ✅ **Lakehouse Monitoring** with custom metrics
- ✅ **AI/BI Dashboards** for visualization
- ✅ **Complete governance** (PII tags, classifications, constraints)

### Time Savings

| Approach | Time | Savings |
|----------|------|---------|
| **Using Framework** | 18-28 hours | - |
| **From Scratch** | 80-120 hours | - |
| **Savings** | - | **4-6x faster** |

---

## 🔧 Key Technologies

- **Databricks Unity Catalog** - Governance & lineage
- **Delta Lake** - ACID transactions & time travel
- **Delta Live Tables (DLT)** - Streaming pipelines
- **Databricks Asset Bundles** - Infrastructure as Code
- **Metric Views** - Semantic layer for AI/BI
- **Genie Spaces** - Natural language queries
- **Lakehouse Monitoring** - Automated observability
- **MLflow** - ML lifecycle management

---

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| [Cursor Rules TOC](.cursor/rules/00_TABLE_OF_CONTENTS.md) | Complete guide with learning paths |
| [Cursor Rules README](.cursor/rules/README.md) | Framework overview |
| [Prompts README](context/prompts/README.md) | Prompt usage guide |

---

## 🌐 Domain Adaptation

These patterns work for any industry:

| Original | Healthcare | Finance | Manufacturing |
|----------|------------|---------|---------------|
| store | hospital | branch | facility |
| product | medication | financial_product | component |
| transaction | encounter | transaction | production_run |
| revenue | reimbursement | interest_income | output_value |

---

## 💡 Pro Tips

1. **Start Small** - Begin with 3-5 tables, not 50
2. **Test with Faker** - Generate sample data before connecting real sources
3. **Use Git** - Version control everything from day 1
4. **Deploy to Dev First** - Test thoroughly before production
5. **Leverage AI** - These prompts are optimized for AI assistants
6. **Read the Docs** - Each prompt links to official Databricks documentation

---

## 📞 Resources

### Official Documentation
- [Databricks Documentation](https://docs.databricks.com/)
- [Unity Catalog](https://docs.databricks.com/unity-catalog/)
- [Delta Lake](https://docs.databricks.com/delta/)
- [DLT Expectations](https://docs.databricks.com/dlt/expectations)
- [Metric Views](https://docs.databricks.com/metric-views/)
- [Lakehouse Monitoring](https://docs.databricks.com/lakehouse-monitoring/)

### Framework Support
- Check cursor rules for inline documentation
- Each prompt has complete examples and common mistakes to avoid
- See self-improvement patterns in `common/21-self-improvement.mdc`

---

## 📋 License

This repository is intended for educational and development purposes. Please review and customize the patterns for your specific use case and compliance requirements.

---

## 🚀 Get Started Now

```bash
# Clone the repository
git clone https://github.com/prashsub/vibe_coding_lakehouse_starter_repo.git

# Open in Cursor IDE
cursor vibe_coding_lakehouse_starter_repo

# Start with the first prompt
# Reference: context/prompts/01-bronze-layer-prompt.md
```

**Time to first deployment: 10-15 hours**  
**Complete framework: 20-30 hours**

Happy Building! 🏗️✨
