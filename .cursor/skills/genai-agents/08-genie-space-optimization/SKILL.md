---
name: genie-space-optimization
description: Interactive Genie Space optimization loop that writes benchmark questions, queries Genie via Conversation API, evaluates accuracy and repeatability, applies changes through six control levers (UC metadata, Metric Views, TVFs, Monitoring tables, ML tables, Genie Instructions), and re-tests until targets are met. Use when optimizing Genie Space accuracy (target 95%+) or repeatability (target 90%+), debugging incorrect SQL generation, improving asset routing, or running automated optimization sessions. Triggers on "optimize Genie", "Genie accuracy", "Genie repeatability", "benchmark questions", "test Genie", "Genie control levers", "Genie optimization loop".
metadata:
  author: prashanth subrahmanyam
  version: "1.0.0"
  domain: genai-agents
  role: worker
  pipeline_stage: 8
  pipeline_stage_name: genai-agents
  called_by:
    - genai-agent-implementation
  standalone: true
---

# Genie Space Optimization

## When to Use

Use this skill when:
- Optimizing Genie Space accuracy (target: 95%+)
- Improving Genie Space repeatability (target: 90%+)
- Debugging incorrect SQL generation from Genie
- Improving asset routing (TVF vs Metric View decisions)
- Running automated optimization sessions
- Testing Genie Space changes before deployment

---

## ⚠️ CRITICAL: Dual Persistence Requirement

**Every optimization MUST be applied in TWO places:**

| Step | Action | Why |
|------|--------|-----|
| **1. Direct Update** | Apply immediately (API, ALTER TABLE) | Effective NOW |
| **2. Repository Update** | Update source files | Future deployments include change |

### Per-Lever Dual Persistence

| Lever | Direct Update | Repository Source File |
|-------|---------------|------------------------|
| UC Tables | `ALTER TABLE ... SET TBLPROPERTIES` | `gold_layer_design/yaml/{domain}/*.yaml` |
| Metric Views | Deploy via script | `src/semantic/metric_views/*.yaml` |
| TVFs | `CREATE OR REPLACE FUNCTION` | `src/semantic/tvfs/*.sql` |
| Lakehouse Monitoring | `ALTER TABLE ... SET TBLPROPERTIES` | `src/monitoring/*.py` (METRIC_DESCRIPTIONS) |
| ML Tables | `ALTER TABLE ... SET TBLPROPERTIES` | `src/ml/config/*.py` |
| **Genie Instructions** | `PATCH /api/2.0/genie/spaces/{id}` | `src/genie/{domain}_genie_export.json` |

---

## ⚠️ CRITICAL: Array Sorting (API Requirement!)

**The Genie API REQUIRES all arrays to be sorted. Unsorted arrays cause API errors.**

Arrays that MUST be sorted:
- `data_sources.tables`
- `data_sources.metric_views`
- `instructions.sql_functions`
- `instructions.text_instructions`
- `instructions.example_question_sqls`
- `config.sample_questions`
- `benchmarks.questions`

**Always call `sort_genie_config()` before API updates.** See [API Update Patterns](references/api-update-patterns.md) for complete implementation.

---

## Rate Limiting

**CRITICAL:** Databricks enforces rate limits on Genie API:
- **5 POST requests/minute/workspace**
- Always wait **12+ seconds** between queries

```python
# Between each test query
time.sleep(12)
```

---

## Six Control Levers (Priority Order)

When Genie returns incorrect or inconsistent results, use these levers in order:

| Priority | Lever | When to Use | Update Method |
|----------|-------|-------------|---------------|
| **1** | UC Tables & Columns | Most issues | `ALTER TABLE ... SET TBLPROPERTIES` |
| **2** | Metric Views | Metric questions | Update metric view YAML |
| **3** | TVFs (Functions) | Complex calculations | Update function COMMENT |
| **4** | Lakehouse Monitoring Tables | Time-series queries | Update table descriptions |
| **5** | ML Model Tables | Prediction queries | Update table descriptions |
| **6** | Genie Instructions | Last resort (~4000 char) | PATCH API update |

### Why This Order?

- **UC metadata** is more durable - survives Genie Space rebuilds
- **Genie instructions** have a ~4000 character limit
- **Lower-priority levers** are less discoverable by Genie

See [Six Control Levers](references/six-control-levers.md) for detailed descriptions.

---

## Quick Repeatability Test Pattern

Test repeatability with 3 iterations per question:

```python
def test_repeatability(question: str, iterations: int = 3) -> dict:
    """Test if a question produces consistent SQL across multiple runs."""
    hashes = []
    assets = []
    
    for i in range(iterations):
        sql = run_genie_query(question).get("sql", "")
        if sql:
            sql_hash = hashlib.md5(sql.lower().encode()).hexdigest()[:8]
            hashes.append(sql_hash)
            assets.append(detect_asset_type(sql))
        time.sleep(12)  # Rate limiting
    
    # Calculate repeatability
    from collections import Counter
    hash_counts = Counter(hashes)
    most_common = hash_counts.most_common(1)[0][1]
    repeatability = (most_common / len(hashes)) * 100
    
    return {
        "question": question,
        "repeatability": repeatability,
        "unique_variants": len(set(hashes)),
        "dominant_asset": Counter(assets).most_common(1)[0][0]
    }
```

### Repeatability Scores

| Score | Classification | Action |
|-------|---------------|--------|
| **100%** | ✅ Identical | No action needed |
| **70-99%** | ⚠️ Minor variance | Usually acceptable |
| **50-69%** | ⚠️ Significant variance | Consider instruction update |
| **<50%** | ❌ Critical variance | Must fix with instructions/sample query |

See [Accuracy & Repeatability Testing](references/accuracy-repeatability-testing.md) for complete implementation.

---

## Asset Routing Overview

### TVF vs Metric View Decision Matrix

| Query Type | Preferred Asset | Reason |
|------------|-----------------|--------|
| **Aggregations** (total, average) | Metric View | Pre-optimized for MEASURE() |
| **Lists** (show me, which, top N) | TVF | Parameterized, returns rows |
| **Time-series with params** | TVF | Date range parameters |
| **Dashboard KPIs** | Metric View | Single-value aggregations |
| **Detail drilldowns** | TVF | Full row data |

**Key Learning:** TVF-first design improves repeatability. Quality domain achieves 100% repeatability by routing most queries to TVFs.

See [Asset Routing](references/asset-routing.md) for detailed decision patterns.

---

## Optimization Workflow

### Standard Optimization Session

```
1. SETUP
   - Identify target Space ID
   - Load test cases from genie_golden_queries.yml
   - Read current Genie export config

2. ACCURACY TESTING
   - Run each test question (respect rate limits)
   - Evaluate SQL correctness
   - Calculate accuracy percentage
   - Identify failure patterns

3. REPEATABILITY TESTING
   - Run key questions 2-3 times each
   - Calculate repeatability scores
   - Identify variance patterns

4. APPLY OPTIMIZATIONS
   - Update instructions with routing rules
   - Apply via API (direct update)
   - Save to repository (dual persistence)

5. VERIFY
   - Wait 30s for propagation
   - Re-run failing/variable questions
   - Measure improvement

6. DOCUMENT
   - Generate report in docs/genie_space_optimizer/
   - Include before/after metrics
   - Document changes applied
```

---

## Cross-Domain Benchmark Results

### Production Results (Feb 2026)

| Domain | SQL Gen | Repeatability (Before → After) |
|--------|---------|-------------------------------|
| **Quality** | 100% | 90% → **100%** (+10%) 🏆 |
| **Reliability** | 100% | 70% → 80% (+10%) |
| **Security** | 96% | 47% → 67% (+20%) |
| **Performance** | 96% | 40% → 47% (+7%) |

### Key Learnings

1. **TVF-first design improves repeatability** - Quality domain achieves 100% by routing most queries to TVFs
2. **MV queries have higher variance** - LLM makes different column/grouping choices
3. **Explicit routing rules help** - "For X queries, ALWAYS use Y" reduces ambiguity
4. **Instructions alone can't fix everything** - LLM non-determinism is inherent

---

## Common Mistakes

### ❌ DON'T: Forget Array Sorting

```python
# ❌ WRONG: Unsorted arrays
payload = {"serialized_space": json.dumps(genie_config)}
# API error: "data_sources.tables must be sorted"

# ✅ CORRECT: Sort all arrays
genie_config = sort_genie_config(genie_config)
payload = {"serialized_space": json.dumps(genie_config)}
```

### ❌ DON'T: Skip Dual Persistence

```python
# ❌ WRONG: Only API update
subprocess.run(["databricks", "api", "patch", ...])
# Change lost on next deployment!

# ✅ CORRECT: Both API and repository
subprocess.run(["databricks", "api", "patch", ...])  # Direct
with open("src/genie/config.json", "w") as f:       # Repository
    json.dump(templated_config, f, indent=2)
```

### ❌ DON'T: Ignore Rate Limits

```python
# ❌ WRONG: Rapid-fire queries
for question in questions:
    run_genie_query(question)
# Rate limited, queries fail

# ✅ CORRECT: Respect rate limits
for question in questions:
    run_genie_query(question)
    time.sleep(12)  # 12+ seconds between queries
```

---

## Validation Checklist

### Before Optimization
- [ ] Correct Space ID identified
- [ ] Test cases loaded from YAML
- [ ] Current config backed up
- [ ] Rate limiting in place (12s between queries)

### During Optimization
- [ ] Accuracy tests run with proper evaluation
- [ ] Repeatability tests run (2-3 iterations)
- [ ] Root causes analyzed for failures
- [ ] Instructions enhanced with routing rules

### API Update
- [ ] All arrays sorted (tables, metric_views, sql_functions, etc.)
- [ ] Variables substituted for deployment
- [ ] PATCH API call succeeds
- [ ] Variables re-templated for repository

### Dual Persistence
- [ ] Direct update applied (API)
- [ ] Repository file updated (`src/genie/{domain}_genie_export.json`)
- [ ] Template variables preserved (`${catalog}`, `${gold_schema}`, etc.)

### Verification
- [ ] Wait 30s for propagation
- [ ] Re-test failing questions
- [ ] Improvement measured
- [ ] Report generated

---

## References

- [Accuracy & Repeatability Testing](references/accuracy-repeatability-testing.md) - Complete testing methodology
- [Six Control Levers](references/six-control-levers.md) - Detailed lever descriptions
- [API Update Patterns](references/api-update-patterns.md) - Array sorting and API calls
- [Asset Routing](references/asset-routing.md) - TVF vs MV decision matrix
- [Test Script](scripts/test_genie_repeatability.py) - Complete Python implementation

### Official Documentation
- [Genie API Reference](https://docs.databricks.com/api/workspace/genie)
- [Genie Space Configuration](https://docs.databricks.com/genie/spaces)
