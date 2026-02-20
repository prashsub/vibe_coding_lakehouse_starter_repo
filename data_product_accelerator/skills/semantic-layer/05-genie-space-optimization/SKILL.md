---
name: genie-space-optimization
description: Interactive Genie Space optimization loop that writes benchmark questions, queries Genie via Conversation API, evaluates accuracy and repeatability, applies changes through six control levers (UC metadata, Metric Views, TVFs, Monitoring tables, ML tables, Genie Instructions), and re-tests until targets are met. Use when optimizing Genie Space accuracy (target 95%+) or repeatability (target 90%+), debugging incorrect SQL generation, improving asset routing, or running automated optimization sessions. Triggers on "optimize Genie", "Genie accuracy", "Genie repeatability", "benchmark questions", "test Genie", "Genie control levers", "Genie optimization loop".
metadata:
  author: prashanth subrahmanyam
  version: "1.2.0"
  domain: semantic-layer
  role: worker
  pipeline_stage: 6
  pipeline_stage_name: semantic-layer
  called_by:
    - semantic-layer-setup
  common_dependencies:
    - databricks-autonomous-operations
    - genie-space-export-import-api
  standalone: true
  source: 34-genie-space-optimization.mdc
  last_verified: "2026-02-20"
  volatility: high
  upstream_sources:
    - name: "ai-dev-kit"
      repo: "databricks-solutions/ai-dev-kit"
      paths:
        - "databricks-skills/databricks-genie/SKILL.md"
      relationship: "extended"
      last_synced: "2026-02-19"
      sync_commit: "97a3637"
---

# Genie Space Optimization

Interactive, agent-driven optimization loop that improves Genie Space quality through systematic benchmark testing, evaluation, and iterative control lever adjustments.

## When to Use This Skill

- Optimizing Genie Space accuracy or repeatability scores
- Writing benchmark questions for a new or existing Genie Space
- Accepting and validating user-submitted benchmark questions against a live Genie Space
- Generating synthetic benchmark questions from Genie Space asset metadata
- Debugging incorrect SQL generation from Genie
- Improving asset routing (TVF vs Metric View selection)
- Running automated optimization sessions against live Genie Spaces
- Updating Genie Space configurations via API after testing
- Managing Genie export JSON files with dual persistence

### Hand Off to Related Skills

| User Says / Task Involves | Load Instead |
|---|---|
| "create Genie Space from scratch" | `genie-space-patterns` |
| "deploy Genie Space via API" | `genie-space-export-import-api` |
| "create metric view" | `metric-views-patterns` |
| "create TVF" | `databricks-table-valued-functions` |

**This skill** covers the *optimization loop*: test → evaluate → adjust → re-test.
Other skills cover *creation* and *deployment* of individual assets.

---

## Quality Dimensions

| Dimension | Target | Definition |
|-----------|--------|------------|
| **Accuracy** | 95%+ | Does Genie return correct SQL/answers for benchmark questions? |
| **Repeatability** | 90%+ | Does the same question produce the same SQL across multiple runs? |

---

## Core Optimization Loop

```
┌──────────────────────────────────────────────────────┐
│  0. IDENTIFY GENIE SPACE                              │
│     Get Space ID from user or discover via API        │
├──────────────────────────────────────────────────────┤
│  1. WRITE BENCHMARKS                                  │
│     Generate domain-relevant benchmark questions      │
│     with expected SQL answers                         │
├──────────────────────────────────────────────────────┤
│  2. QUERY GENIE                                       │
│     Run benchmarks via Conversation API               │
│     (respect 12s rate limit between queries)          │
├──────────────────────────────────────────────────────┤
│  3. EVALUATE                                          │
│     Compare generated SQL to expected SQL             │
│     Measure accuracy + repeatability                  │
├──────────────────────────────────────────────────────┤
│  4. DIAGNOSE                                          │
│     Identify failure patterns:                        │
│     - Wrong asset selected (TVF vs MV vs Table)       │
│     - Wrong columns/aggregations                      │
│     - Missing routing context                         │
├──────────────────────────────────────────────────────┤
│  5. APPLY CONTROL LEVERS                              │
│     Fix issues using 6 levers (priority order)        │
│     Apply via BOTH API + repository (dual persist)    │
├──────────────────────────────────────────────────────┤
│  6. RE-TEST (max 3 iterations)                        │
│     Wait 30s → re-run failing questions               │
│     Measure improvement                               │
│     Loop back to step 4 if targets not met            │
├──────────────────────────────────────────────────────┤
│  7. DEPLOY BUNDLE + TRIGGER GENIE JOB                 │
│     bundle deploy → run genie_spaces_deployment_job   │
│     Rebuilds Genie Space from bundle (source of truth)│
├──────────────────────────────────────────────────────┤
│  8. FINAL RE-ASSESS + DOCUMENT                        │
│     Confirm bundle-deployed state matches API-tested  │
│     Generate optimization report with metrics         │
└──────────────────────────────────────────────────────┘
```

---

## Step 0: Identify Genie Space

Before optimization can begin, identify the target Genie Space ID.

**If the user provides a Space ID**, use it directly.

**If the Space ID is unknown**, either ask the user or discover deployed spaces. See `references/optimization-code-patterns.md` for SDK and CLI discovery code. For domain-specific projects, maintain a `DOMAIN_SPACES` dict mapping domain names to Space IDs.

See `genie-space-export-import-api` for full List Spaces API details.

---

## Step 1: Write Benchmark Questions (Interactive Intake)

**Always prompt the user for benchmark questions before generating synthetic ones.** User-provided questions reflect real business needs and catch domain-specific edge cases.

### Three-Path Workflow

| User Provides | Action |
|--------------|--------|
| **10+ questions** | Validate each against live Genie Space assets. Report any that can't be answered (missing trusted asset, ambiguous terms, need more info). Proceed with valid set. |
| **1-9 questions** | Validate provided questions. Report issues. Augment with synthetic benchmarks to reach 10-15 total. Show augmentation report. |
| **No questions** | Inspect live Genie Space assets via API. Generate 10-15 synthetic benchmarks from metric view measures, TVF signatures, and table schemas. Show to user for review. |

### Prompting the User

Before generating or starting the loop, ask:

```markdown
I need benchmark questions to test and optimize this Genie Space.
These questions will measure accuracy (target 95%+) and repeatability (target 90%+).

Options:
1. Provide your own questions (I'll validate each against the live space)
2. Let me generate them from the space's assets
3. Provide a few key ones, I'll augment to reach the 10-15 minimum

Format: natural language question, optionally with expected SQL and asset type.
```

### Validating User-Submitted Questions

For each submitted question, validate against the **live Genie Space**:

| Check | What to Verify | If Failed, Tell the User |
|-------|---------------|--------------------------|
| **Trusted asset match** | At least one trusted asset in the space can answer it | "No trusted asset can answer '{question}'. Available assets: {list}. Add the required table or rephrase." |
| **SQL object references** | SQL only references objects trusted in the space | "'{table}' isn't a trusted asset in this space. Add it first, or rewrite SQL." |
| **MEASURE() columns** | Column names match actual metric view columns | "MEASURE({col}) not found. Available measures: {list}." |
| **Ambiguous terms** | Terms like "underperforming" are defined in Genie Instructions | "'{term}' is ambiguous and not defined in instructions. How should it be interpreted?" |
| **Category coverage** | Overall set covers 4+ categories | "Your questions only cover aggregation. Need ranking, time-series, or comparison questions too." |

**If a question cannot be answered**, do NOT silently drop it. Inform the user with the specific reason and suggest alternatives based on available trusted assets.

**If a question needs clarification**, present the specific issue (e.g., "What does 'underperforming' mean — cost above median? Job failure rate above threshold?") and offer to define it in Genie Instructions as part of the optimization.

See [Benchmark Intake Workflow](references/benchmark-intake-workflow.md) for the full validation pipeline and user feedback templates.

### Synthetic Generation (When User Provides None or Few)

Generate benchmarks from the live Genie Space's trusted assets:
1. **From Metric Views** — one aggregation question per measure, one comparison question per view
2. **From TVFs** — one question per function matching its use case
3. **From Tables** — list/detail questions for dimension tables (only if needed)
4. **Ensure category coverage** — at least 4 categories: aggregation, ranking, time-series, comparison, list

After generation, **always show synthetic benchmarks to the user** for review before proceeding to Step 2.

### Augmentation (When User Provides Partial Set)

When augmenting user-provided questions:
1. **User questions always take priority** — never replaced or reworded
2. **Fill category gaps first** — if user only has aggregation, add ranking/time-series/list
3. **Fill asset type gaps** — if user only tests MVs, add TVF questions
4. **Add synonym/date variations** — test "total spend" vs "how much spent" vs "total costs"
5. **Show augmentation report** — let user review before proceeding

### Required Fields Per Benchmark

Each question must have:

1. **Natural language question** (what a user would ask)
2. **Expected SQL** (tested, working SQL)
3. **Expected asset** (MV, TVF, or TABLE)
4. **Category** (aggregation, list, time-series, comparison, etc.)
5. **Source** (user, synthetic, or augmented — for tracking)

### Asset Routing Rules for Benchmarks

| Question Type | Expected Asset | Example |
|--------------|----------------|---------|
| Total/average/overall | Metric View | "What is total spend?" |
| Top N / list / show me | TVF | "Show top 10 costliest jobs" |
| Date-range analysis | TVF | "Daily costs for last month" |
| KPI / single value | Metric View | "Average job duration" |
| Drill-down / detail | TVF | "Details for workspace X" |

See [Benchmark Patterns](references/benchmark-patterns.md) for complete question-writing guide.

### Quick Benchmark Template

```yaml
benchmarks:
  - id: "cost_001"
    question: "What is total spend this month?"
    expected_sql: "SELECT MEASURE(total_cost) FROM ${catalog}.${schema}.mv_cost_analytics WHERE ..."
    expected_asset: "MV"
    category: "aggregation"
    source: "user"  # or "synthetic" or "augmented"

  - id: "cost_002"
    question: "Show top 10 costliest workspaces"
    expected_sql: "SELECT * FROM ${catalog}.${schema}.get_top_cost_contributors('7', 'workspace')"
    expected_asset: "TVF"
    category: "list"
    source: "user"
```

See [Golden Queries Template](assets/templates/golden-queries.yaml) for the full YAML format.

---

## Step 2: Query Genie via API

### Core Query Function

`run_genie_query(space_id, question, max_wait=120) -> dict` — starts a Genie conversation, polls for completion with exponential backoff (3s initial, max 10s), extracts SQL from response attachments. Returns `{"status": ..., "sql": ...}`.

**MANDATORY:** Read `references/optimization-code-patterns.md` for the full implementation.

### Rate Limiting (CRITICAL)

Databricks enforces **5 POST requests/minute/workspace**. Always wait **12+ seconds** between queries:

```python
time.sleep(12)  # MANDATORY between every Genie API call
```

---

## Step 3: Evaluate Results

### Accuracy Evaluation

`evaluate_accuracy(result, expected) -> dict` — compares generated SQL against expected SQL. Detects asset routing by checking for `mv_`/`measure(` (Metric View) vs `get_` (TVF) prefixes. Returns `{"question", "sql_generated", "correct_asset", "actual_asset", "expected_asset"}`.

### Repeatability Testing

`test_repeatability(space_id, question, iterations=3) -> dict` — runs the same question N times (with 12s spacing), MD5-hashes each result, measures consistency. Returns `{"question", "repeatability_pct", "unique_variants"}`.

**MANDATORY:** Read `references/optimization-code-patterns.md` for full implementations of both functions.

### Score Thresholds

| Score | Classification | Action Required |
|-------|---------------|-----------------|
| **100%** | Identical | No action needed |
| **70-99%** | Minor variance | Usually acceptable |
| **50-69%** | Significant variance | Update instructions or add sample query |
| **<50%** | Critical variance | Must fix with explicit routing rules |

---

## Step 4: Diagnose Failures

Common failure patterns and their root causes:

| Symptom | Root Cause | Lever to Fix |
|---------|-----------|--------------|
| Wrong asset selected (MV vs TVF) | Ambiguous routing | Genie Instructions (lever 6) |
| Wrong columns in query | Poor column descriptions | UC Table/Column comments (lever 1) |
| Missing aggregation | Metric view not discoverable | Metric View metadata (lever 2) |
| Wrong parameters to TVF | TVF comment unclear | TVF COMMENT (lever 3) |
| Inconsistent SQL across runs | Ambiguous question mapping | Genie Instructions + sample query |
| Query returns no data | Wrong date range defaults | Genie Instructions (time defaults) |

---

## Step 5: Apply Control Levers (Priority Order)

Six levers to fix Genie behavior, applied **in priority order**:

| Priority | Lever | Durability | Char Limit | When to Use |
|----------|-------|------------|------------|-------------|
| **1** | UC Tables & Columns | Highest | Unlimited | Column misunderstanding, wrong tables |
| **2** | Metric Views | High | N/A | Metric/aggregation questions wrong |
| **3** | TVFs (Functions) | High | N/A | Complex calculation errors |
| **4** | Monitoring Tables | Medium | Unlimited | Time-series queries wrong |
| **5** | ML Model Tables | Medium | Unlimited | Prediction queries wrong |
| **6** | Genie Instructions | Lowest | ~4000 chars | Asset routing, last resort |

**Why this order?** UC metadata survives Genie Space rebuilds. Genie Instructions have a ~4000 char limit and are the least durable.

### Dual Persistence (CRITICAL)

**Every optimization MUST be applied in TWO places:**

| Step | Action | Why |
|------|--------|-----|
| **1. Direct Update** | API call or ALTER TABLE | Effective immediately |
| **2. Repository Update** | Update source files | Persists across deployments |

See [Control Levers Reference](references/control-levers.md) for detailed per-lever update patterns.

### Three-Phase Deployment Model

Every optimization uses a **three-phase deployment model** integrated with `databricks-autonomous-operations`:

| Phase | When | What | Purpose |
|-------|------|------|---------|
| **A** | During loop | Direct API/SQL (`ALTER TABLE`, `PATCH`, `CREATE OR REPLACE`) | Immediate testing — changes take effect in seconds |
| **A** | During loop | Update bundle repository files simultaneously | Keep bundle in sync for final deploy |
| **B** | End of loop | `databricks bundle deploy -t <target>` | Persist all repository changes to workspace |
| **C** | End of loop | `databricks bundle run -t <target> genie_spaces_deployment_job` | Rebuild Genie Space from bundle JSON, overwriting API patches |

**Phase A** happens during each iteration. **Phases B + C** happen once after the loop converges (or at max iterations).

The deployment job in Phase C reads `src/genie/*_genie_export.json` from the bundle and recreates the Genie Space via API. Any API-only patches NOT captured in bundle files will be lost — this is intentional. The bundle is the **single source of truth**.

See [Autonomous Ops Integration](references/autonomous-ops-integration.md) for detailed patterns.

---

## Step 6: Re-Test and Iterate (Max 3 Iterations)

After applying control lever changes (Phase A — direct API/SQL + repository update):

1. **Wait 30 seconds** for propagation
2. **Re-run only failing/variable questions** (not full suite)
3. **Measure improvement** (compare before/after)
4. **Loop back to Step 4** if targets not met

Re-test pattern: `time.sleep(30)` → loop over `failing_questions` → call `run_genie_query` + `evaluate_accuracy` → `time.sleep(12)` between each. See `references/optimization-code-patterns.md` for the re-test loop code.

### Iteration Limits and Escalation

**Maximum 3 optimization iterations.** Track each iteration's error and fix.

| Condition | Action |
|-----------|--------|
| Accuracy >= 95% AND Repeatability >= 90% | Proceed to Step 7 (deploy bundle) |
| Accuracy >= 90% after 3 iterations | Acceptable — proceed to Step 7, document remaining issues |
| No improvement after 2 iterations | Root cause may be LLM limitation — proceed to Step 7, document |
| Repeatability < 50% on specific question | May need TVF redesign or question rewording |

**If escalating after 3 iterations**, present to the user:
1. All errors encountered with question IDs
2. All fixes attempted (which levers, what changed)
3. Root cause hypothesis
4. Current accuracy/repeatability scores
5. Recommendation for next steps

This matches the escalation pattern in `databricks-autonomous-operations` Section 7.

---

## Step 7: Deploy Bundle and Trigger Genie Space Job

After the optimization loop converges (or at max iterations), finalize by deploying the bundle and rebuilding the Genie Space from bundle state.

Read `common/databricks-autonomous-operations/SKILL.md` and follow the deploy-run-fix cycle:

### Phase B: Bundle Deploy

```bash
databricks bundle validate -t <target>
databricks bundle deploy -t <target>
```

If deploy fails, follow `databricks-autonomous-operations` Section 5: diagnose, fix, redeploy (max 3 attempts).

### Phase C: Trigger Genie Space Deployment Job

```bash
databricks bundle run -t <target> genie_spaces_deployment_job
```

This job reads the Genie Space JSON configs (`src/genie/*_genie_export.json`) from the bundle and creates/updates Genie Spaces via the API. It **overwrites any direct API patches** from Phase A, ensuring the live Genie Space matches the bundle.

Poll the job for completion using the autonomous-ops polling pattern (30s → 60s → 120s backoff).

---

## Step 8: Final Re-Assessment and Document Results

After the Genie Space deployment job completes:

1. **Re-run benchmark questions** one final time against the bundle-deployed Genie Space
2. **Compare results** to the API-patched results from Step 6
3. If results match or improve — optimization is complete
4. If discrepancy found — a change was applied via API but NOT captured in bundle files. Fix the missing file, repeat Steps 7-8.

Generate an optimization report using the [Report Template](assets/templates/optimization-report.md).

Key sections:
- Executive summary with before/after metrics
- Per-question test results
- Optimizations applied (which levers, what changed)
- Dual persistence confirmation
- Bundle deployment status (Phase B + C)
- Post-deploy vs in-loop result comparison
- Files updated

---

## Scripts

### [genie_optimizer.py](scripts/genie_optimizer.py)
Complete optimization loop: discover spaces → load benchmarks → query Genie → evaluate → report → deploy bundle + trigger Genie job.

```bash
# Discover available Genie Spaces
python scripts/genie_optimizer.py --discover

# Run assessment only
python scripts/genie_optimizer.py --space-id <ID> --benchmarks golden-queries.yaml

# Run assessment + deploy bundle + trigger Genie Space deployment job
python scripts/genie_optimizer.py --space-id <ID> --benchmarks golden-queries.yaml --deploy-target dev
```

### [repeatability_tester.py](scripts/repeatability_tester.py)
Standalone repeatability testing with configurable iterations.

```bash
python scripts/repeatability_tester.py --space-id <ID> --iterations 3
```

---

## Optimization Notes to Carry Forward

After each optimization session, persist the following for future sessions or handoff:

| Note | What to Record | Example |
|------|---------------|---------|
| **Space ID** | Target Genie Space identifier | `01ef...abc` |
| **Baseline Scores** | Accuracy % and Repeatability % before changes | Acc: 72%, Rep: 60% |
| **Final Scores** | Accuracy % and Repeatability % after all iterations | Acc: 96%, Rep: 92% |
| **Iterations Used** | How many of the 3 max iterations were needed | 2 of 3 |
| **Levers Applied** | Which control levers were changed and what was modified | Lever 1: added column comments to `mv_cost_analytics`; Lever 6: added TVF routing rule |
| **Unresolved Questions** | Benchmark questions still failing after max iterations | `cost_007` — TVF parameter ambiguity |
| **Bundle Deploy Status** | Phase B + C success/failure | Deploy: success; Genie job: success |
| **Post-Deploy Match** | Did bundle-deployed results match API-tested results? | Yes / No (if no, which questions diverged) |
| **Files Modified** | All repository files changed during dual persistence | `src/genie/cost_genie_export.json`, `ALTER TABLE` on `gold.mv_cost_analytics` |

**When resuming**: Load these notes first, then re-run only unresolved questions (skip the full benchmark suite).

## Reference Files

- **[Benchmark Intake Workflow](references/benchmark-intake-workflow.md)**: Interactive workflow for accepting, validating, and augmenting benchmark questions — three-path intake (full/partial/none), per-question validation against live Genie Space, synthetic generation from trusted assets, augmentation strategy, user feedback templates
- **[Control Levers](references/control-levers.md)**: Detailed per-lever update patterns, SQL commands, API calls, and repository file mappings for dual persistence
- **[Optimization Workflow](references/optimization-workflow.md)**: Extended step-by-step workflow with decision trees, failure pattern analysis, and advanced techniques
- **[Benchmark Patterns](references/benchmark-patterns.md)**: Complete guide to writing effective benchmark questions including category coverage, SQL templates, and domain-specific patterns
- **[Autonomous Ops Integration](references/autonomous-ops-integration.md)**: Three-phase deployment model, per-lever bundle file mapping, self-healing deploy + job pattern, post-deploy verification
- **[Optimization Code Patterns](references/optimization-code-patterns.md)**: Python implementations for `run_genie_query`, `evaluate_accuracy`, `test_repeatability`, space discovery, and re-test loop

---

## Validation Checklist

### Before Optimization
- [ ] Correct Space ID identified (Step 0 — ask user or discover via API)
- [ ] User prompted for benchmark questions before synthetic generation
- [ ] User-submitted questions validated against live Genie Space trusted assets
- [ ] Invalid/needs-info questions reported to user with specific reasons (not silently dropped)
- [ ] Benchmark suite has 10-15 questions with 4+ categories covered
- [ ] Benchmark questions loaded with expected SQL
- [ ] Current Genie export config backed up
- [ ] Rate limiting in place (12s between queries)

### During Optimization
- [ ] Accuracy tests run for all benchmark questions
- [ ] Repeatability tests run (2-3 iterations per question)
- [ ] Root causes identified for each failure
- [ ] Control levers applied in priority order (1-6)
- [ ] Every direct change also written to bundle repository files (dual persistence)

### After Optimization
- [ ] Direct update applied (API/ALTER TABLE)
- [ ] Repository file updated (dual persistence)
- [ ] Template variables preserved (`${catalog}`, `${gold_schema}`)
- [ ] All arrays sorted in Genie export JSON
- [ ] Wait 30s, then re-test failing questions
- [ ] Improvement measured and documented
- [ ] All control lever changes reflected in bundle repository files
- [ ] `databricks bundle validate -t <target>` passes
- [ ] `databricks bundle deploy -t <target>` succeeds
- [ ] `genie_spaces_deployment_job` triggered and succeeds (rebuilds Genie Space from bundle JSON)
- [ ] Final re-assessment confirms bundle-deployed Genie Space matches API-tested results
- [ ] Optimization report generated

---

## Common Mistakes

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Unsorted arrays in API payload | `data_sources.tables must be sorted` error | Call `sort_genie_config(config)` before `json.dumps` |
| API-only update (no repo file) | Changes lost on next `bundle deploy` | Always write to both API and `src/genie/*.json` |
| No delay between Genie queries | Queries fail silently (5 POST/min limit) | `time.sleep(12)` between every API call |
| Everything in Genie Instructions | Exceeds ~4000 char limit | Use levers 1-3 first; instructions only for routing rules |

---

## Related Skills

- **`genie-space-patterns`** - Initial Genie Space creation and setup
- **`genie-space-export-import-api`** - List Spaces API for Space ID discovery; Genie PATCH/Create API patterns; `import_genie_space.py` script
- **`metric-views-patterns`** - Metric view creation and validation
- **`databricks-table-valued-functions`** - TVF creation for Genie
- **`databricks-autonomous-operations`** - Deploy-run-fix loop for bundle deployment after optimization; self-healing deploy cycle; escalation patterns

---

## References

### Official Databricks Documentation
- [Genie API Reference](https://docs.databricks.com/api/workspace/genie)
- [Genie Space Configuration](https://docs.databricks.com/genie/spaces)
- [Genie Conversation API](https://docs.databricks.com/api/workspace/genie/startconversation)

---

## Version History

- **v1.2** (Feb 20, 2026) - Interactive benchmark question intake
  - Added three-path benchmark intake workflow to Step 1 (full, partial, none)
  - Added per-question validation against live Genie Space trusted assets
  - Added user feedback for invalid/needs-info questions (never silently dropped)
  - Added synthetic benchmark generation from live space assets
  - Added augmentation strategy for partial submissions with category/asset coverage
  - Added benchmark re-intake after failed optimization (rewording, replacing questions)
  - New reference: `benchmark-intake-workflow.md`
  - Updated validation checklist with benchmark intake checks
  - **Key Learning:** User-provided questions catch domain-specific edge cases; always ask first, validate against live space, then generate/augment

- **v1.1** (Feb 2026) - Autonomous operations integration and closed-loop deployment
  - Step 0: Genie Space ID discovery via SDK/API (Gap 1)
  - Three-phase deployment model: direct API during loop, bundle deploy at end, trigger `genie_spaces_deployment_job` to rebuild from bundle (Gap 2, 5)
  - Integration with `databricks-autonomous-operations` for deploy-run-fix cycle (Gap 2)
  - Max 3 optimization iterations with escalation pattern (Gap 4)
  - Post-deploy re-assessment to confirm bundle-deployed state matches API-tested results (Gap 3)
  - Cross-reference to `genie-space-export-import-api` for PATCH operations (Gap 6)
  - New reference: `autonomous-ops-integration.md`
  - Updated validation checklist with bundle deployment items
- **v1.0** (Feb 2026) - Initial skill converted from `34-genie-space-optimization.mdc`
  - Interactive optimization loop (write → query → evaluate → adjust → re-test)
  - Six control levers with priority ordering
  - Dual persistence requirement for all changes
  - Repeatability testing methodology
  - Benchmark question writing patterns
  - Domain-specific Space ID reference
  - Rate limiting enforcement (12s between queries)
  - Benchmarked results: Quality 100%, Reliability 80%, Security 67%, Performance 47%
  - Key discovery: TVF-first routing improves repeatability
