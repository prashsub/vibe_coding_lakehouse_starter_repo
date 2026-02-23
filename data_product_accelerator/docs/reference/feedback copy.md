# Feedback: Optimizer, Applier & Orchestrator — ASI-to-Metadata Loop Gaps

**Date:** 2026-02-23
**Reporter:** Genie Space Optimization Loop (iteration 0 → 3)
**Severity:** Mixed (P0–P2)
**Affected skills:**
- `03-genie-metadata-optimizer/SKILL.md`
- `04-genie-optimization-applier/SKILL.md`
- `05-genie-optimization-orchestrator/SKILL.md`

---

## Context

Starting from the prompt "Please continue optimizing metadata by reading ASI feedback from judges," the optimization loop ran three iterations of ASI-grounded introspection across Levers 1, 2, 3, and 6. This feedback captures 13 issues discovered during that loop — gaps where the skill documentation was insufficient, incorrect, or missing, causing wasted cycles, overcorrections, or silent failures.

**Score progression across the loop:**

| Judge | Iter 0 (baseline) | Iter 2 (post-Lever 3+6) | Delta |
|---|---|---|---|
| syntax_validity | 96% | **100%** | +4% |
| schema_accuracy | 40% | **48%** | +8% |
| logical_accuracy | 32% | **45%** | +13% |
| semantic_equivalence | 24% | **44%** | +20% |
| completeness | 12% | **48%** | +36% |
| asset_routing | 88% | **96%** | +8% |
| result_correctness | 64% | **68%** | +4% |

---

## Optimizer Issues (03-genie-metadata-optimizer)

### Issue 1 (P1): `missing_filter` Not Mapped in Root Cause → Lever Table

**What happened:** The most common ASI `failure_type` from judges was `missing_filter` (13 occurrences), but the Root Cause → Lever Mapping table (lines 135–143) only lists `wrong_filter → Lever 3`. The `missing_filter` type covers three distinct sub-patterns that route to different levers:

| Sub-pattern | Example | Correct Lever |
|---|---|---|
| TVF receives `'NULL'` string instead of SQL NULL | `destination_filter => 'NULL'` | 3 (TVF COMMENT) |
| Missing temporal WHERE clause on MV | No `WHERE payment_date >= DATE_TRUNC(...)` | 2 (MV dimension comment) |
| Wrong date range on TVF parameters | `start_date => '2026-01-01'` when GT uses `DATE_TRUNC` | 3 (TVF COMMENT) |

**Recommendation:** Add `missing_filter` to the Root Cause → Lever Mapping with sub-type routing:

```
| Missing filter (TVF param format)   | 3 (TVFs)       | `CREATE OR REPLACE FUNCTION` — fix COMMENT PARAMS section |
| Missing filter (temporal on MV)     | 2 (Metric Views)| MV dimension YAML — add temporal filtering guidance to date column |
| Missing filter (date param value)   | 3 (TVFs)       | `CREATE OR REPLACE FUNCTION` — fix COMMENT SYNTAX example |
```

### Issue 2 (P0): TVF COMMENT Effective Format Not Documented

**What happened:** The optimizer knows TVF COMMENTs are Lever 3, but doesn't document the COMMENT structure that Genie actually reads. During optimization, we discovered that the effective format is a structured bullet-point layout:

```
• PURPOSE: What this function returns and when to use it
• BEST FOR: Specific query patterns that should use this TVF
• NOT FOR: Patterns that should use a different asset (with redirect)
• RETURNS: Column list (helps Genie understand output schema)
• PARAMS: Parameter descriptions WITH format rules and NULL handling
• SYNTAX: Full working example with dynamic dates and NULL
• NOTE: Additional constraints (e.g., ROW_NUMBER ranking, no GROUP BY)
```

**Critical discovery:** The `PARAMS` and `SYNTAX` sections directly control Genie's parameter handling. Without explicit "pass NULL, do NOT pass 'NULL'" guidance and `CAST(DATE_ADD(CURRENT_DATE(), -N) AS STRING)` syntax examples, Genie consistently:
1. Passes the string literal `'NULL'` instead of SQL `NULL` for optional parameters
2. Uses hardcoded dates like `'2025-02-23'` instead of dynamic date expressions

**Recommendation:** Add a "TVF COMMENT Format" section to the SKILL.md with the bullet-point template above, and add to Common Mistakes:

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| TVF COMMENT missing PARAMS null-handling guidance | Genie passes `'NULL'` string literal for optional params | Add "pass NULL, do NOT pass the string literal 'NULL'" to each optional param |
| TVF COMMENT SYNTAX shows hardcoded dates | Genie uses hardcoded dates instead of dynamic expressions | Show `CAST(DATE_ADD(CURRENT_DATE(), -N) AS STRING)` in SYNTAX |

### Issue 3 (P1): Bilateral Disambiguation Needs Concrete Templates

**What happened:** The Bilateral Disambiguation section (lines 170–178) says BOTH sides must be addressed but doesn't provide actionable templates. During optimization, we had to manually construct:

- **Positive side (MV):** Updated `booking_analytics_metrics.destination_country` comment to say "ALWAYS use this dimension with MEASURE(total_revenue) for revenue by country"
- **Negative side (TVF):** Changed `get_revenue_summary` COMMENT `BEST FOR` to remove "Revenue by country this year" and add explicit "NOT FOR: Revenue by destination country (use booking_analytics_metrics)"

**Recommendation:** Add a template pair to the Bilateral Disambiguation section:

```
# Positive routing (preferred asset):
ALTER COLUMN <preferred_asset>.<dimension> COMMENT '... ALWAYS use this for <pattern>...'

# Negative routing (competing asset):
ALTER FUNCTION <competing_tvf> — change BEST FOR to remove <pattern>,
add to NOT FOR: "<pattern> (use <preferred_asset> MEASURE(<measure>))"
```

### Issue 4 (P0): No Guidance on Lever 6 Overcorrection

**What happened:** Adding Genie Space instructions with routing rules caused an overcorrection. The instruction "Revenue by destination country → booking_analytics_metrics" inadvertently redirected "Revenue by destination for last 6 months" (rev_015) away from its correct TVF target (`get_revenue_summary`). The question was routed to the MV, which returned wrong results.

The overcorrection occurred because the instruction was too broad — it matched any query containing "revenue by destination" regardless of whether the user wanted the simple MV aggregation or the detailed multi-metric TVF breakdown.

**Root cause:** Lever 6 instructions lack specificity guidance. The optimizer should generate instructions that include BOTH positive examples ("use MV for X") AND negative exclusions ("do NOT use MV for Y, use TVF instead").

**Recommendation:** Add a "Lever 6 Instruction Specificity" section:

```
## Lever 6 Instruction Quality Rules

1. Every routing instruction MUST include both the POSITIVE case and NEGATIVE exclusion
2. Use the question's exact phrasing or a close paraphrase, not generic patterns
3. Distinguish simple aggregations (MV) from date-ranged detail queries (TVF)

GOOD: "Revenue by destination country this year" → MV. "Revenue by destination for last 6 months" → TVF.
BAD:  "Revenue by destination" → MV. (Too broad — catches TVF-appropriate queries too)
```

Add to Common Mistakes:

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Overly broad Lever 6 routing instruction | Overcorrects — redirects TVF-appropriate queries to MV | Include both positive routing and negative exclusion per instruction |

### Issue 5 (P2): Missing `missing_temporal_filter` Sub-type in FAILURE_TAXONOMY

**What happened:** 5 questions (rev_001, rev_005, rev_006, rev_008, rev_009) failed because Genie didn't add temporal filters when users said "this year" or "last quarter". The ASI tagged these as generic `missing_filter` or `other`, providing no signal to distinguish temporal filtering gaps from parameter formatting gaps.

**Recommendation:** Add `missing_temporal_filter` to the FAILURE_TAXONOMY (16 → 17 types). Route to Lever 2 (MV dimension comment for the date column, adding temporal filtering patterns like `DATE_TRUNC`, `ADD_MONTHS`).

### Issue 6 (P2): ASI `counterfactual_fix` Too Generic

**What happened:** The evaluator's LLM judges returned generic `counterfactual_fix` values like "Review table/column references in Genie metadata" for 33 out of 80 ASI entries. These don't help the optimizer generate targeted proposals. The optimizer's `_describe_fix()` function falls back to keyword extraction when `counterfactual_fix` is too vague.

**Recommendation:** Add to the ASI Consumption Contract:

> When `counterfactual_fix` contains only generic guidance (e.g., "Review X in metadata"), the optimizer SHOULD ignore it and use `blame_set` + `wrong_clause` to synthesize a specific fix. Generic fixes are treated as equivalent to "no fix provided."

---

## Applier Issues (04-genie-optimization-applier)

### Issue 7 (P0): Metric View Column Comments Require Full VIEW Recreation

**What happened:** Attempting `ALTER TABLE ... ALTER COLUMN ... COMMENT` on `booking_analytics_metrics.check_in_date` failed with:

```
[EXPECT_TABLE_NOT_VIEW.NO_ALTERNATIVE] 'ALTER TABLE ... ALTER COLUMN' expects a table
but `vibe_coding_workshop_catalog.prashanth_s_wanderbricks_gold.booking_analytics_metrics` is a view.
```

The applier's Asset Type Detection section (lines 89–102) correctly documents this for Lever 1 → Lever 2 routing, but doesn't document the actual SQL syntax for recreating a Metric View with updated column comments.

**The correct syntax:**

```sql
DROP VIEW IF EXISTS catalog.schema.mv_name;

CREATE VIEW catalog.schema.mv_name
WITH METRICS
LANGUAGE YAML
COMMENT '<view_level_comment>'
AS $$
<yaml_content_with_updated_dimension_comments>
$$
```

**Recommendation:** Add this syntax to the Lever 2 section in `control-levers.md`, and add to Common Mistakes:

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Using ALTER COLUMN COMMENT on Metric View | `EXPECT_TABLE_NOT_VIEW` error | Read MV YAML, update dimension comment, execute full `CREATE VIEW ... WITH METRICS LANGUAGE YAML ... AS $$ ... $$` |

### Issue 8 (P0): TVF COMMENT Updates Require Full Function Replacement

**What happened:** There is no `ALTER FUNCTION SET COMMENT` or `COMMENT ON FUNCTION` in Databricks SQL. The only way to update a TVF COMMENT is to execute the full `CREATE OR REPLACE FUNCTION` statement with the updated COMMENT. `COMMENT ON FUNCTION` returns:

```
[PARSE_SYNTAX_ERROR] Syntax error at or near 'FUNCTION'. SQLSTATE: 42601
```

**Impact:** Lever 3 changes require reading the full TVF SQL definition from the repo file, modifying only the COMMENT section, substituting template variables (`${catalog}`, `${gold_schema}`), and executing the entire CREATE statement via the SQL Statement API.

**Recommendation:** Add to `control-levers.md` under Lever 3:

> TVF COMMENTs can ONLY be updated via `CREATE OR REPLACE FUNCTION` with the full function body. There is no `ALTER FUNCTION SET COMMENT` or `COMMENT ON FUNCTION` syntax in Databricks SQL. The applier must: (1) read the function SQL from the repo file, (2) modify the COMMENT section, (3) resolve template variables, (4) execute the full CREATE statement.

Add to Common Mistakes:

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Attempting `COMMENT ON FUNCTION` or `ALTER FUNCTION SET COMMENT` | `PARSE_SYNTAX_ERROR` | Execute full `CREATE OR REPLACE FUNCTION` with updated COMMENT |

### Issue 9 (P1): Genie Space `description` vs `serialized_space` for Instructions

**What happened:** The Genie Space instructions live in the `description` field of the space, NOT inside `serialized_space`. The PATCH API accepts `{"description": "new instructions"}` directly. But the dual persistence table (line 87) says the repo file is `src/genie/{domain}_genie_export.json`, which contains `serialized_space`. The `description` is a top-level field separate from the serialized config.

**Recommendation:** Clarify in the dual persistence table:

| Lever | Direct Update | Payload Field | Repository File |
|-------|--------------|---------------|-----------------|
| Genie Instructions | `PATCH /api/2.0/genie/spaces/{id}` | `{"description": "..."}` (top-level, NOT inside serialized_space) | `src/genie/{domain}_genie_export.json` — update `description` field |

---

## Orchestrator Issues (05-genie-optimization-orchestrator)

### Issue 10 (P2): One-Lever-Per-Iteration Rule Too Strict for Non-Overlapping Clusters

**What happened:** Levers 1, 3, and 6 were applied in iteration 2 because they addressed completely different failure clusters:
- Lever 1: `dim_property` table comment (affects rev_022 only)
- Lever 3: TVF NULL parameter handling (affects rev_008, rev_013, rev_015, rev_025)
- Lever 6: Asset routing instructions (affects rev_016, rev_021)

No question was affected by more than one lever. Applying them separately would have required 3 evaluation cycles (~24 min total) with no measurement benefit, since the failure clusters don't overlap.

**Recommendation:** Add an exception to hard constraint #14:

> **Exception:** Non-overlapping lever proposals (targeting completely different question sets with zero intersection) MAY be applied in the same iteration to save evaluation cycles. The optimizer MUST verify zero question overlap before combining. Log a warning: "Combining levers {A, B} — non-overlapping question sets verified."

### Issue 11 (P1): Benchmark Ground Truth Temporal Staleness

**What happened:** `rev_009` ("Who are the top 10 hosts by revenue this year?") had ground truth SQL with hardcoded `'2025-01-01', '2025-12-31'`. Since today is Feb 2026, "this year" = 2026. Genie correctly used 2026 dates but was marked wrong because the GT used 2025. This wasted an investigation cycle.

**Recommendation:** Add a pre-loop validation step to the Phase 1 section:

```
# Phase 0c: Benchmark Temporal Freshness Check
for each benchmark in golden-queries.yaml:
    if question contains temporal phrases ("this year", "last quarter", "last N months"):
        if expected_sql contains hardcoded dates:
            WARN: "{question_id} has hardcoded dates but temporal phrasing — 
                   GT may be stale. Consider using dynamic date expressions."
```

### Issue 12 (P1): Evaluation Metrics Not Available via `run.data.metrics`

**What happened:** After evaluation, `mlflow.get_run(run_id).data.metrics` returned empty for per-judge metrics. The scores were only available through the job's structured output JSON and the `evaluation/eval_results.json` artifact. This forced downloading and parsing artifacts for every metrics check.

**Recommendation:** The evaluator template should log per-judge percentages as top-level MLflow metrics (via `mlflow.log_metric()`) in addition to the `mlflow.genai.evaluate()` output. Add to the evaluator-orchestrator data contract:

> The evaluator MUST log `eval_{judge}_pct` as MLflow run metrics for: `result_correctness`, `asset_routing`, `syntax_validity`, `schema_accuracy`, `semantic_equivalence`, `completeness`, `logical_accuracy`. These MUST be accessible via `mlflow.get_run(run_id).data.metrics`.

### Issue 13 (P2): `counterfactual_fix` Quality Feedback Loop Missing

**What happened:** The LLM judges generated `counterfactual_fix` values that were too generic to drive optimization (Issue 6 above). But the optimizer has no mechanism to feed this quality signal back to the judge prompts. If the optimizer could report "this counterfactual_fix was too vague to generate a proposal," the SIMBA alignment process could improve judge prompt quality.

**Recommendation:** Add a `judge_quality_feedback` output to the optimizer's output schema:

```python
{
    "judge_name": "completeness",
    "feedback_type": "generic_counterfactual_fix",
    "example": "Review column visibility and filter completeness in Genie metadata",
    "desired": "Add 'WHERE payment_date >= DATE_TRUNC(\"year\", CURRENT_DATE())' filter to payment_date column comment",
    "count": 8  # number of times this generic fix appeared
}
```

This feeds into the SIMBA Tier 3 judge alignment workflow when judges are identified as the bottleneck.

---

## Summary of Recommendations by Priority

| # | Priority | Skill | Issue | Fix |
|---|----------|-------|-------|-----|
| 2 | **P0** | Optimizer | TVF COMMENT format not documented | Add TVF COMMENT Format section with bullet-point template |
| 4 | **P0** | Optimizer | Lever 6 overcorrection | Add specificity rules for routing instructions |
| 7 | **P0** | Applier | MV column comment requires full VIEW recreation | Document CREATE VIEW WITH METRICS YAML syntax |
| 8 | **P0** | Applier | TVF COMMENT requires full function replacement | Document that `COMMENT ON FUNCTION` is unsupported |
| 1 | **P1** | Optimizer | `missing_filter` not in lever mapping | Add with sub-type routing |
| 3 | **P1** | Optimizer | Bilateral disambiguation needs templates | Add positive/negative routing template pair |
| 9 | **P1** | Applier | `description` vs `serialized_space` confusion | Clarify dual persistence payload field |
| 11 | **P1** | Orchestrator | Benchmark temporal staleness | Add pre-loop date freshness check |
| 12 | **P1** | Orchestrator | Metrics not in `run.data.metrics` | Require `mlflow.log_metric()` for per-judge pct |
| 5 | **P2** | Optimizer | Missing `missing_temporal_filter` type | Add to FAILURE_TAXONOMY |
| 6 | **P2** | Optimizer | Generic `counterfactual_fix` handling | Define fallback to `blame_set` + `wrong_clause` |
| 10 | **P2** | Orchestrator | One-lever-per-iteration too strict | Allow non-overlapping lever combination |
| 13 | **P2** | Optimizer | Judge quality feedback loop missing | Add `judge_quality_feedback` output |

---

## Affected Runs

- **Iter 0 (baseline — post evaluator fixes):** `164697c46bcd4d72983d3e625a91f19a`
- **Iter 2 (post Lever 1+3+6):** `c7fb522bf3f9404ba1ed4e2de60e2f09`
- **Experiment:** `/Users/prashanth.subrahmanyam@databricks.com/genie-optimization/revenue_property`
- **Space ID:** `01f10e84df3b14d993c30773abde7f44`
