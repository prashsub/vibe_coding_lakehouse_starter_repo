---
name: genie-space-patterns
description: Patterns for setting up Databricks Genie Spaces with comprehensive agent instructions, data assets, and benchmark questions. Use when creating Genie Spaces, configuring agent behavior, selecting data assets, or validating benchmark questions. Includes mandatory 7-section deliverable structure, General Instructions (≤20 lines), data asset organization (Metric Views → TVFs → Tables), benchmark questions with exact SQL, testing patterns, and deployment checklists.
metadata:
  author: databricks-sa
  version: "2.0"
  domain: semantic-layer
---

# Genie Space Patterns

## Overview

This skill provides patterns for setting up production-ready Databricks Genie Spaces with natural language analytics capabilities. The quality of Genie responses directly correlates with the depth of business context provided in agent instructions.

**Core Principle:** Business context drives AI quality. Comprehensive agent instructions, properly selected data assets, and validated benchmark questions ensure reliable Genie performance.

---

## When to Use This Skill

Use this skill when:
- Creating new Genie Spaces for natural language analytics
- Configuring agent behavior and instructions
- Selecting and organizing data assets (Metric Views, TVFs, Tables)
- Writing benchmark questions for validation
- Troubleshooting Genie query routing issues
- Optimizing Genie Space performance

---

## Critical Rules

### 1. General Instructions Must Be ≤20 Lines

**⚠️ CRITICAL:** Genie processes General Instructions effectively only when ≤20 lines. Longer instructions get truncated or ignored.

**✅ DO:** Keep General Instructions concise and focused on essential routing rules.

**❌ DON'T:** Exceed 20 lines in General Instructions section.

### 2. Benchmark Questions Must Have Working SQL

**Every benchmark question MUST include copy-paste-ready SQL that actually runs.**

**✅ DO:** Include tested SQL with every benchmark question.

**❌ DON'T:** Provide questions without SQL or untested SQL.

### 3. MEASURE() Uses Column Names, NOT Display Names

**The MEASURE() function requires actual column `name`, NOT `display_name`.**

**❌ WRONG:**
```sql
MEASURE(`Total Revenue`)  -- ❌ FAILS: "Total Revenue" is display_name
```

**✅ CORRECT:**
```sql
MEASURE(total_revenue)  -- ✅ Uses actual column name from YAML
```

### 4. Full UC 3-Part Namespace Required

**All table and function references MUST use full Unity Catalog namespace.**

**❌ WRONG:**
```sql
SELECT * FROM fact_sales;
SELECT * FROM get_revenue_by_period('2024-01-01', '2024-12-31', 'week');
```

**✅ CORRECT:**
```sql
SELECT * FROM ${catalog}.${gold_schema}.fact_sales;
SELECT * FROM ${catalog}.${gold_schema}.get_revenue_by_period('2024-01-01', '2024-12-31', 'week');
```

### 5. Data Asset Hierarchy: Metric Views → TVFs → Tables

**Always add assets in this order:**

1. **Metric Views** (Primary - use first)
   - Pre-aggregated, optimized, rich semantics
   - Best for broad analytical queries

2. **TVFs** (Secondary - use for specific patterns)
   - Parameterized queries, business logic
   - Date-bounded queries, top N rankings

3. **Tables** (Last resort - use sparingly)
   - Only when metric views/TVFs insufficient
   - Reference data, ad-hoc exploration

### 6. Avoid Contradictory Routing Rules

**Issue:** Contradictory rules cause Genie to randomly select wrong assets.

**✅ DO:** Group by question type, not asset
```markdown
Revenue/booking questions:
  - By property → revenue_analytics_metrics
  - By host → get_host_performance TVF (not metric view!)
```

**❌ DON'T:** Create conflicting asset mappings
```markdown
- host_analytics_metrics → for host data
- get_host_performance → for host data  # ❌ CONFLICT!
```

### 7. Define Ambiguous Terms Explicitly

**Common ambiguous terms:** "underperforming", "top performing", "valuable customers", "best hosts"

**✅ DO:** Add explicit definitions
```markdown
## Term Definitions
"underperforming" = properties with revenue below median (use get_underperforming_properties TVF)
"top performing" = highest revenue unless "rated" specified
```

### 8. TVF Syntax Rules

**Common errors to prevent:**

**❌ WRONG:**
```sql
SELECT * FROM TABLE(get_customer_segments(...))  -- ❌ Don't wrap in TABLE()
SELECT * FROM get_customer_segments()            -- ❌ Missing parameters
SELECT * FROM get_customer_segments(...) GROUP BY segment  -- ❌ Unnecessary GROUP BY
```

**✅ CORRECT:**
```sql
SELECT * FROM get_customer_segments('2020-01-01', '2024-12-31')  -- ✅ Direct call with params
```

---

## Quick Reference

### Mandatory 7-Section Structure

Every Genie Space setup MUST produce a document with ALL 7 sections:

| Section | Requirement | Key Constraint |
|---------|-------------|----------------|
| **A. Space Name** | `{Project} {Domain} Analytics Space` | Exact format |
| **B. Space Description** | 2-3 sentences | Business context |
| **C. Sample Questions** | 10-15 questions | Grouped by domain |
| **D. Data Assets** | All tables & metric views | Table format |
| **E. General Instructions** | **≤20 LINES** | **CRITICAL LIMIT** |
| **F. TVFs** | All functions with signatures | Detailed specs |
| **G. Benchmark Questions** | 10-15 with **EXACT SQL** | Working SQL required |

**🔴 Missing any section = INCOMPLETE deliverable. NO EXCEPTIONS.**

---

## Core Setup Pattern

### Step 1: Create Space Document Structure

Follow the mandatory 7-section structure (A-G). Use the [configuration template](assets/templates/genie-space-config.yaml) as a starting point.

### Step 2: Write General Instructions (≤20 Lines)

Use the template from [Agent Instructions Guide](references/agent-instructions.md#general-instructions-mandatory-20-lines):

```markdown
## General Instructions

You are an expert {domain} analyst. Follow these rules:

1. **Primary Data Source:** Always use Metric Views first
2. **Use TVFs:** For common queries, prefer Table-Valued Functions
3. **Date Defaults:** If no date specified, default to last 30 days
4. **Aggregations:** Use SUM for totals, AVG for averages
5. **Sorting:** Sort by primary metric DESC unless specified
6. **Limits:** Return top 10-20 rows for ranking queries
7. **Currency:** Format as USD with 2 decimal places
8. **Percentages:** Show as % with 1 decimal place
9. **Synonyms:** Handle common term equivalents
10. **Context:** Explain results in business terms
11. **Comparisons:** Show absolute values and % difference
12. **Time Periods:** Support today, yesterday, last week, month, quarter, YTD
13. **Null Handling:** Exclude nulls from calculations
14. **Performance:** Never scan raw Bronze/Silver tables
15. **Accuracy:** State assumptions when uncertain
```

### Step 3: Document Data Assets

Add assets in order: Metric Views → TVFs → Tables. Document each with:
- **Metric Views:** Measures, dimensions, use cases
- **TVFs:** Signature, parameters, return schema, use cases
- **Tables:** Purpose, when to use

See [Configuration Guide](references/configuration-guide.md#section-d-data-assets) for detailed patterns.

### Step 4: Write Benchmark Questions

Every question must include:
- Natural language question
- Expected SQL (tested and working)
- Expected result description

See [Configuration Guide](references/configuration-guide.md#section-g-benchmark-questions) for format.

### Step 5: Deploy and Test

1. Create Genie Space via UI or API
2. Add trusted assets in order (Metric Views → TVFs → Tables)
3. Set General Instructions (copy exactly, verify ≤20 lines)
4. Test benchmark questions
5. Validate routing and response quality

See [Configuration Guide](references/configuration-guide.md#deployment-checklist) for complete steps.

---

## Reference Files

Detailed guides are available in the `references/` directory:

### [Configuration Guide](references/configuration-guide.md)
Complete guide for the mandatory 7-section structure:
- Section A-G detailed formats
- Extended space description patterns
- Data asset organization patterns
- Testing and validation procedures
- Deployment checklist
- Success metrics

### [Agent Instructions Guide](references/agent-instructions.md)
Comprehensive patterns for writing effective instructions:
- Extended instructions template (200-500 lines, optional)
- General Instructions consistency patterns
- Ambiguous term definitions
- Metric View vs TVF routing decision table
- TVF syntax guidance
- Professional language standards

### [Troubleshooting Guide](references/troubleshooting.md)
Common issues, debugging steps, and verification procedures:
- Common routing issues and solutions
- MEASURE() function errors
- UC namespace problems
- TVF syntax errors
- Debugging procedures
- Verification checklists

### [Trusted Assets Guide](references/trusted-assets.md)
Complete guide for organizing and documenting data assets:
- Metric View documentation patterns
- TVF documentation patterns
- Asset selection best practices
- Performance considerations
- Asset organization checklist

---

## Assets

### Templates

#### [Genie Space Config Template](assets/templates/genie-space-config.yaml)
Starter YAML template for structuring Genie Space setup documents:
- All 7 sections with placeholders
- Deployment configuration
- Testing and training checklists

---

## Validation Checklist

Before submitting ANY Genie Space document:

| Section | Requirement | Complete? |
|---------|-------------|-----------|
| **A. Space Name** | Exact name in format `{Project} {Domain} Analytics Space` | ☐ |
| **B. Space Description** | 2-3 sentences describing purpose and users | ☐ |
| **C. Sample Questions** | 10-15 questions grouped by domain | ☐ |
| **D. Data Assets** | ALL metric views, dimensions, facts in table format | ☐ |
| **E. General Instructions** | **≤20 lines** of LLM behavior rules | ☐ |
| **F. TVFs** | ALL functions with signatures and examples | ☐ |
| **G. Benchmark Questions** | 10-15 questions with **EXACT working SQL** | ☐ |

### Additional Quality Checks

- [ ] General Instructions are EXACTLY 20 lines or less (not 21+)
- [ ] Every benchmark question has copy-paste-ready SQL
- [ ] SQL in benchmarks actually runs (tested)
- [ ] MEASURE() uses actual column names (not display_name with backticks)
- [ ] All tables/functions have full 3-part UC namespace
- [ ] Metric views documented with measures and dimensions
- [ ] TVFs documented with parameters, returns, and use cases
- [ ] Questions cover all major use cases (revenue, performance, trends)
- [ ] No contradictory routing rules in General Instructions
- [ ] Ambiguous terms explicitly defined

---

## Common Mistakes to Avoid

### ❌ General Instructions > 20 Lines
Genie won't process instructions effectively if they exceed 20 lines.

### ❌ Benchmark Questions Without SQL
Cannot validate Genie responses without working SQL.

### ❌ Using Display Names in MEASURE()
MEASURE() requires actual column names from YAML, not display names.

### ❌ Partial UC Namespaces
Always use full 3-part namespace: `${catalog}.${schema}.{object}`

### ❌ Adding Only Tables as Trusted Assets
Start with Metric Views (pre-aggregated) for better performance.

### ❌ Contradictory Routing Rules
Group by question type, not asset, to avoid conflicts.

### ❌ Undefined Ambiguous Terms
Explicitly define terms like "underperforming", "top performing".

### ❌ Incorrect TVF Syntax
Don't wrap TVFs in TABLE(), include all required parameters, avoid unnecessary GROUP BY.

---

## References

### Official Databricks Documentation
- [Genie Overview](https://docs.databricks.com/genie/)
- [Create a Genie Space](https://docs.databricks.com/genie/create-space.html)
- [Add Trusted Assets](https://docs.databricks.com/genie/trusted-assets.html)
- [Query with Genie](https://docs.databricks.com/genie/query.html)
- [Metric Views Documentation](https://docs.databricks.com/metric-views/)

### Related Skills
- `metric-views-patterns` - Metric view YAML structure
- `databricks-table-valued-functions` - TVF patterns
- `databricks-asset-bundles` - Asset Bundle deployment

---

## Version History

- **v2.0** (Dec 16, 2025) - Genie optimization patterns from production post-mortem
  - Added General Instructions consistency patterns
  - Added ambiguous term definitions
  - Added Metric View vs TVF routing decision table
  - Added TVF syntax guidance
  - Added professional language standards
  - **Key Learning:** Contradictory rules caused 40% of Genie misrouting

- **v1.0** (Jan 2025) - Initial skill based on Genie Space deployment
  - 7-section mandatory structure
  - Benchmark questions with SQL requirement
  - Extended instructions template
