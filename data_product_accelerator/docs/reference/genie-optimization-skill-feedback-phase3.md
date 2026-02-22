# Genie Optimization Skill Feedback — Phase 3: Closed-Loop Optimization Gaps

Self-improvement reflection following the [self-improvement skill](../data_product_accelerator/skills/admin/self-improvement/SKILL.md) framework. This document captures 6 architectural gaps in the optimization orchestrator and worker skills that caused the agent to produce a manually-improvised optimization loop instead of the programmatic closed-loop the skills prescribe.

**Relationship to Phase 1 & 2:** [Phase 1](genie-optimization-skill-feedback.md) documented 9 gaps (5 P0 job-crashers, 4 P1 spec violations) discovered while getting the evaluation job to run. [Phase 2](genie-optimization-skill-feedback-phase2.md) documented 6 gaps (numbered 10-15) in how the agent executed the optimization workflow — skipping workers, half-implementing dual persistence, and defaulting to Lever 6. Phase 3 covers what went wrong on a **second full execution** of the same optimization loop on the same space — after Phase 1 and 2 fixes were applied to the skill specs — revealing that the fixes addressed documentation but not the fundamental data-flow wiring.

**Session:** 2026-02-21
**Space:** Wanderbricks Unified Monitor (`01f10e84df6715e39ea60890ef55ae0f`)
**Baseline Accuracy:** 22.7% (5/22 benchmarks passed — iteration 1)
**Final Accuracy:** 72.7% (16/22 benchmarks — iteration 5, plateau detected)
**Iterations Run:** 5
**Gaps Found:** 6 (numbered 16-21 to continue from Phase 2's 10-15)

---

## Reflection (After Second Optimization Attempt)

> I ran 5 evaluation iterations and improved accuracy from 22.7% to 72.7%, a 50 percentage-point gain. Let me document:
> - **What went wrong:** Despite the skill spec describing a data-driven closed loop — where per-row judge feedback flows into failure clustering, proposal generation, and lever-mapped application — I executed a **manual intuition loop** instead. I looked at aggregate metrics, guessed what was wrong, hand-edited JSON files, and re-evaluated. The evaluation infrastructure worked; the optimization infrastructure was never wired.
> - **What led me astray:** The skills contain two parallel systems that never connect. **System A** (evaluator) produces structured data: `Feedback` objects with ASI metadata, `FAILURE_TAXONOMY` classifications, `blame_set` arrays, and `counterfactual_fix` suggestions. **System B** (optimizer) consumes structured data: `cluster_failures()` reads `feedback/*` columns, `generate_metadata_proposals()` maps clusters to levers, `detect_conflicts_and_batch()` sequences proposals. But **there is no System C** — no code that reads System A's output and feeds it to System B's input. The evaluator notebook emits a JSON summary to `dbutils.notebook.exit()`. The optimizer functions expect a dict with `eval_result` tables or `rows` lists. Nothing bridges them.
> - **Breakthrough insight:** Phase 1 identified **template-checklist divergence** (agents follow concrete code over aspirational checklists). Phase 2 identified the **aspiration-implementation gap** (skills describe WHAT should happen without providing runnable implementations). Phase 3 reveals a third systemic pattern: the **producer-consumer disconnect** — when two systems produce and consume structured data but no integration code connects them, the agent degrades to manual pattern-matching on aggregate statistics.
> - **What would have prevented all 6 gaps:** One structural change: the evaluator notebook must **emit a machine-readable failures artifact** (not just a summary JSON), and the orchestrator must **read that artifact and pass it to `cluster_failures()`** before any optimization decisions are made. The data pipeline must be wired end-to-end, not described in two separate documents.

---

## Gap 16: ASI Metadata Written But Never Read Back

**Priority:** P0 (breaks the entire data-driven optimization loop)

**What went wrong:** The evaluation notebook (`run_genie_evaluation.py`) carefully constructs Actionable Side Information (ASI) metadata for every failed judge verdict — classifying failures by `FAILURE_TAXONOMY`, recording `blame_set` arrays pointing to responsible metadata fields, and including `counterfactual_fix` suggestions. This metadata is attached to MLflow `Feedback` objects. But **no code anywhere in the codebase reads this metadata back** to drive optimization decisions.

The `FAILURE_TAXONOMY` (16 failure types), `ASI_SCHEMA` (12 fields), and `build_asi_metadata()` function are all implemented in `run_genie_evaluation.py` (lines 76-184). Every scorer attaches ASI metadata on failure:

```python
# syntax_validity_scorer (line 726)
metadata=build_asi_metadata(
    failure_type="other", severity="critical", confidence=1.0,
    missing_metadata="Genie returned no SQL",
    counterfactual_fix="Check Genie Space instructions and data asset visibility")

# asset_routing_scorer (line 755)
metadata=build_asi_metadata(
    failure_type="asset_routing_error", severity="major", confidence=0.95,
    expected_value=expected_asset, actual_value=actual_asset,
    blame_set=[f"asset_routing:{expected_asset}"],
    counterfactual_fix=f"Add instruction to prefer {expected_asset} for this query pattern")

# result_correctness (line 792)
metadata=build_asi_metadata(
    failure_type="wrong_aggregation", severity="major", confidence=0.8,
    expected_value=f"rows={cmp.get('gt_rows')}, hash={cmp.get('gt_hash')}",
    actual_value=f"rows={cmp.get('genie_rows')}, hash={cmp.get('genie_hash')}",
    counterfactual_fix="Review Genie metadata for missing joins, filters, or aggregation logic")
```

Meanwhile, the Optimizer worker's `feedback-to-metadata-mapping.md` describes functions that **consume** this metadata:

```python
# cluster_failures() expects eval_result with feedback/* and rationale/* columns
# generate_metadata_proposals() maps clusters to control levers
# detect_conflicts_and_batch() sequences non-conflicting proposals
```

But these functions exist only as code examples in reference documentation. They were never implemented as importable modules, notebook cells, or CLI commands. The orchestrator's v3.4.0 changelog even acknowledges this gap: "Optimizer now receives full iteration result with row-level feedback instead of empty failure ID list." But the fix was applied to the orchestrator *pseudocode*, not to actual executable code.

**Root cause:** The ASI producer (`build_asi_metadata()` in the evaluator) and the ASI consumer (`cluster_failures()` in the optimizer reference docs) are described in two different worker skill files with no integration layer between them. The evaluator attaches metadata to `Feedback` objects inside `mlflow.genai.evaluate()`, but the evaluator notebook's output (line 1073-1089) is a summary JSON with `arbiter_verdicts` counts and `failure_question_ids` — not the per-row feedback table with ASI fields. The optimizer functions expect exactly that per-row data, but the evaluator never emits it.

**What assumption was incorrect:** That describing a data format in one skill (evaluator: "attach ASI to Feedback.metadata") and a consumer in another skill (optimizer: "read ASI from cluster_failures()") would result in the agent wiring the two together. Without explicit code that reads the evaluator's `eval_result.tables["eval_results"]` DataFrame, extracts the `metadata` column from each row, and passes it to `cluster_failures()`, the agent has no bridge to cross.

**What would have prevented this:**

1. Add a **Cell 9: Emit Failures Artifact** to the evaluator notebook template that:
   - Iterates over `eval_result.tables["eval_results"]`
   - Extracts per-row `feedback/*`, `rationale/*`, and `metadata/*` columns
   - Logs a `failures.json` MLflow artifact with the full per-row detail
   - Prints a summary: "Emitted N failures to artifacts/failures.json"

2. Add a **Step 4a: Read Failures Artifact** to the orchestrator loop pseudocode that:
   - Downloads `failures.json` from the latest MLflow run
   - Passes it to `cluster_failures()` and `generate_metadata_proposals()`
   - Makes it a hard constraint: "Do NOT proceed to optimization without reading the failures artifact"

3. Move `cluster_failures()` and `generate_metadata_proposals()` from the optimizer's reference docs into a **runnable script** (`metadata_optimizer.py`) or a **notebook cell template** that the agent can copy directly.

**Files to update:**
- `02-genie-benchmark-evaluator/assets/templates/run_genie_evaluation.py` — Add Cell 9 that emits `failures.json` artifact with per-row ASI data
- `03-genie-metadata-optimizer/SKILL.md` — Add hard constraint: "Optimizer MUST consume the evaluator's failures artifact, not aggregate metrics"
- `03-genie-metadata-optimizer/scripts/metadata_optimizer.py` — Move `cluster_failures()` and `generate_metadata_proposals()` from reference docs into runnable script
- `05-genie-optimization-orchestrator/SKILL.md` — Add Step 4a to loop pseudocode; add hard constraint #15: "Read failures artifact before generating proposals"

---

## Gap 17: Arbiter Verdicts Counted But Not Actioned

**Priority:** P0 (arbiter intelligence wasted; benchmark quality degrades silently)

**What went wrong:** The arbiter scorer produced actionable verdicts across 5 evaluation iterations — `genie_correct` (1 case where Genie was right and the benchmark was wrong), `ground_truth_correct` (4-10 cases where Genie was definitively wrong), `both_correct` and `neither_correct` cases. These verdicts were **counted into a summary dict** (line 1053) and printed (line 1070), but **never routed to any handler**.

The orchestrator's routing table explicitly prescribes:

| Situation | Worker to Load |
|-----------|---------------|
| Arbiter corrected >=3 GTs | `genie-benchmark-generator` |

This threshold was never checked. The `genie_correct` verdict (meaning the benchmark expected SQL was wrong and should be updated) was never fed to `add_benchmark_correction()`. The `ground_truth_correct` verdicts (confirmed Genie failures that should feed `cluster_failures()`) were counted but never classified by root cause.

The relevant code (lines 1052-1067):

```python
failure_ids = []
arbiter_verdicts = {"genie_correct": 0, "ground_truth_correct": 0,
                    "both_correct": 0, "neither_correct": 0, "skipped": 0}
if hasattr(eval_result, "tables") and "eval_results" in eval_result.tables:
    results_df = eval_result.tables["eval_results"]
    for _, row in results_df.iterrows():
        rc = row.get("result_correctness/value", row.get("result_correctness", ""))
        if str(rc).lower() in ("no", "false", "0", "0.0"):
            qid = row.get("inputs/question_id", row.get("inputs", {}).get("question_id", ""))
            if qid:
                failure_ids.append(str(qid))
        av = str(row.get("arbiter/value", row.get("arbiter", "skipped")))
        if av in arbiter_verdicts:
            arbiter_verdicts[av] += 1
        else:
            arbiter_verdicts["skipped"] += 1
```

Two compounding problems:
1. `failure_ids` is always empty because `inputs/question_id` was never set in the eval records (line 940-947 — only `question`, `space_id`, `catalog`, `gold_schema`, `expected_sql` are set in `inputs`, not `question_id`).
2. Even if failure IDs were populated, they would only appear in the output JSON — no code reads them to decide what to do next.

**Root cause:** The arbiter outputs a `Feedback.value` string (`"genie_correct"`, `"ground_truth_correct"`, etc.) but the skill provides no code that bridges from a verdict string to a concrete action. The orchestrator spec says "when arbiter corrects >=3 GTs, load Generator" but the evaluator notebook counts verdicts without checking thresholds, and the orchestrator (running in CLI mode, not notebook mode) receives the counts as a JSON string from `dbutils.notebook.exit()` and never parses the threshold condition.

**What assumption was incorrect:** That documenting the arbiter-to-action routing in the orchestrator's routing table would cause the agent to implement the threshold check and Generator re-invocation. The routing table describes when to invoke workers, but the evaluator — which is the only code that sees per-row arbiter verdicts — doesn't know about the routing table. And the orchestrator, which knows the routing table, only sees aggregate counts.

**What would have prevented this:**

1. Add an **arbiter triage block** to the evaluator notebook (after Cell 8) that:
   ```python
   arbiter_actions = {"corrections": [], "confirmed_failures": []}
   for _, row in results_df.iterrows():
       verdict = row.get("arbiter/value", "skipped")
       if verdict == "genie_correct":
           arbiter_actions["corrections"].append({
               "question": row.get("inputs/question", ""),
               "old_gt": row.get("expectations/expected_response", ""),
               "genie_sql": row.get("outputs/response", ""),
           })
       elif verdict == "ground_truth_correct":
           arbiter_actions["confirmed_failures"].append({
               "question": row.get("inputs/question", ""),
               "genie_sql": row.get("outputs/response", ""),
           })
   mlflow.log_dict(arbiter_actions, "arbiter_actions.json")
   ```

2. Add to the orchestrator loop pseudocode:
   ```
   After evaluation:
     arbiter_actions = download_artifact("arbiter_actions.json")
     if len(arbiter_actions["corrections"]) >= 3:
       load Generator → update benchmarks with corrected GTs
     pass arbiter_actions["confirmed_failures"] to cluster_failures()
   ```

3. Fix `question_id` missing from eval records — add `"question_id": b["id"]` to the `inputs` dict at line 941.

**Files to update:**
- `02-genie-benchmark-evaluator/assets/templates/run_genie_evaluation.py` — Add arbiter triage block after Cell 8; add `question_id` to eval record inputs
- `05-genie-optimization-orchestrator/SKILL.md` — Add explicit arbiter threshold check to loop pseudocode; make it a per-iteration gate
- `01-genie-benchmark-generator/SKILL.md` — Add a "Benchmark Correction" section explaining what happens when the orchestrator passes `corrected_questions`

---

## Gap 18: LoggedModel Lifecycle Entirely Skipped

**Priority:** P1 (no config version tracking; rollback impossible; MLflow Model tab empty)

**What went wrong:** The orchestrator spec requires a LoggedModel before every evaluation — hard constraint #6:

> Every iteration MUST create a LoggedModel via `mlflow.set_active_model()` before evaluation. Pass `model_id` to the Evaluator so `mlflow.genai.evaluate(model_id=...)` links results to the config version.

The loop pseudocode shows this at lines 183 and 213:

```
model_id = create_genie_model_version(space_id, config, 0, domain)
# ...
model_id = create_genie_model_version(space_id, config, lever, domain,
    patch_set=proposals, parent_model_id=prev_model_id)
```

In practice, `model_id` was always `""` (empty string in `genie_evaluation_job.yml` line 46), resolved to `None` in the notebook (lines 215-219), and the `if model_id:` guard (line 346) was never entered. No LoggedModel was created for any of the 5 iterations. Consequences:

1. **No config snapshots** — if iteration 4's accuracy dropped, there was no model artifact to rollback to.
2. **No parent chain** — no way to trace which configuration produced which results.
3. **MLflow Model tab empty** — the GenAI Model version tracking feature was unused.
4. **`promote_best_model()`** could not be called because there was nothing to promote.

**Root cause:** `create_genie_model_version()` is described in the orchestrator's pseudocode but has no implementation anywhere. The orchestrator loop assumes the function exists. The evaluator notebook expects `model_id` as a parameter but doesn't create one — it just checks `if model_id:` and skips when it's `None`. No template code, helper function, or CLI command exists for creating a LoggedModel from a Genie Space configuration.

The gap is: **who creates the model?** The orchestrator says "create before evaluation." The evaluator says "receive model_id as input." Neither provides `create_genie_model_version()`.

**What assumption was incorrect:** That describing the model lifecycle in the orchestrator spec — create, link, chain, promote, rollback — with pseudocode function signatures would be sufficient for the agent to implement the lifecycle. Without a concrete helper function (even a 10-line one), the agent treated `model_id` as optional and skipped it entirely.

**What would have prevented this:**

1. Add a concrete `create_genie_model_version()` implementation to either:
   - The orchestrator's `scripts/orchestrator.py` as a helper function, OR
   - A new reference file `references/logged-model-lifecycle.md` with runnable code

   ```python
   def create_genie_model_version(space_id, space_config, iteration, domain,
                                   patch_set=None, parent_model_id=None):
       """Snapshot Genie Space config as an MLflow LoggedModel."""
       import mlflow
       model = mlflow.create_logged_model(
           name=f"genie-space-{domain}",
           params={
               "space_id": space_id,
               "iteration": str(iteration),
               "domain": domain,
               "config_hash": hashlib.md5(json.dumps(space_config).encode()).hexdigest()[:8],
               "parent_model_id": parent_model_id or "",
           },
       )
       # Log the full space config as an artifact
       with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
           json.dump(space_config, f, indent=2)
           mlflow.log_artifact(f.name, artifact_path="genie_config")
       return model.model_id
   ```

2. Add to the evaluator notebook template: a cell that creates the model if `model_id` is not provided:
   ```python
   if not model_id:
       print("WARNING: No model_id provided. Config version tracking disabled.")
       print("  Pass model_id from orchestrator for full lifecycle tracking.")
   ```

3. Make the evaluation job YAML's `model_id` default something more visible than an empty string — e.g., add a comment: `# REQUIRED for config version tracking. Create via create_genie_model_version() before running.`

**Files to update:**
- `05-genie-optimization-orchestrator/SKILL.md` — Add concrete `create_genie_model_version()` implementation (not just a pseudocode call)
- `05-genie-optimization-orchestrator/references/` — Add `logged-model-lifecycle.md` with `create_genie_model_version()`, `promote_best_model()`, `rollback_to_model()` implementations
- `02-genie-benchmark-evaluator/assets/templates/run_genie_evaluation.py` — Add warning when model_id is None
- `02-genie-benchmark-evaluator/assets/templates/genie-evaluation-job-template.yml` — Add comment to model_id parameter explaining how to create one

---

## Gap 19: Agent Used Only Lever 6 — Lever Priority Ordering Still Not Enforced

**Priority:** P1 (optimization budget burned on lowest-durability lever)

**What went wrong:** Despite Phase 2 Gap 13 identifying this exact issue and the skill being updated to v3.1.0 with hard constraint #14 ("lever-priority ordering 1->6"), the agent once again defaulted to Lever 6 for all 5 iterations. The optimization actions were:

| Iteration | Lever Used | Change |
|-----------|-----------|--------|
| 1→2 | 6 | Deploy config + 12 example_question_sqls |
| 2→3 | 6 | Expand to 21 example_question_sqls, enhance instructions |
| 3→4 | 6 | Add 23 example_question_sqls, UNION ALL pattern |
| 4→5 | 1 (finally) | UC table comments on metric views |

The spec (lines 192-226) prescribes:

```
for lever in [1, 2, 3, 4, 5]:
    load Optimizer → introspect(scores, target_lever=lever) → proposals
    if not proposals:
        continue
    load Applier → apply(proposals, dual_persist=True)
    # ... evaluate, check regression ...
```

The agent never attempted Levers 2 (Metric View metadata), 3 (TVF comments), 4 (Monitoring), or 5 (ML tables) before moving to Lever 6. Hard constraint #14 from v3.1.0 says:

> Proposals must be applied in lever priority order 1->6; re-evaluate after each lever; GEPA (L6) only after Levers 1-5 are exhausted.

But this constraint is in the SKILL.md text — it is not enforced by any code gate.

**Root cause:** The same root cause as Phase 2 Gap 13: Lever 6 (`example_question_sqls`) provides the most immediate, visible impact — exact SQL patterns that Genie can copy. Levers 1-3 (UC comments, metric view metadata, TVF comments) require understanding what's already there, proposing specific metadata changes, and verifying they affect Genie's behavior. The agent rationally optimized for speed: Lever 6 is a few JSON edits, while Lever 1 requires running `ALTER TABLE` SQL and updating YAML files.

Phase 2's fix added hard constraint #14, but the constraint is **descriptive, not prescriptive**. It says "must apply in lever priority order" but doesn't provide:
1. A checker that verifies which levers were attempted
2. A mandatory "lever skip justification" that the agent must provide when skipping a lever
3. A per-lever proposals template showing concretely what a Lever 1, 2, or 3 proposal looks like

**What assumption was incorrect:** That adding a hard constraint to the SKILL.md text would change agent behavior. It did not, for the same reason Phase 2 Gap 10 identified: agents follow concrete code patterns over textual constraints. Without a code-level gate or a mandatory checklist that forces the agent to record "Lever 1: attempted/skipped because X", the constraint is unenforceable.

**What would have prevented this:**

1. Add a **mandatory lever audit log** to the orchestrator output:
   ```
   lever_audit:
     lever_1:
       attempted: true/false
       proposals_generated: N
       proposals_applied: N
       skip_reason: "..." (required if attempted=false)
     lever_2: ...
   ```

2. Add a **per-lever proposal example** to the optimizer skill for each of the 6 levers:
   ```
   Lever 1 example proposal:
     change: "ALTER TABLE booking_analytics_metrics COMMENT 'Use MEASURE() for all metrics...'"
     repo: "src/wanderbricks_semantic/metric_views/booking_analytics_metrics.yaml → update comment field"
     questions_fixed: ["um_001", "um_006", "um_007"]
   
   Lever 2 example proposal:
     change: "Add 'avg_revenue_per_night' measure to booking_analytics_metrics"
     repo: "src/wanderbricks_semantic/metric_views/booking_analytics_metrics.yaml → add measure"
     questions_fixed: ["um_008"]
   ```

3. Add to the loop pseudocode a **lever exhaustion gate**:
   ```
   # Before Phase 3 (GEPA / Lever 6):
   ASSERT lever_audit shows all levers 1-5 were either:
     - attempted with proposals generated, OR
     - skipped with a documented reason
   If assertion fails → STOP and attempt missing levers first
   ```

**Files to update:**
- `05-genie-optimization-orchestrator/SKILL.md` — Add mandatory lever audit log to loop output; add lever exhaustion gate before Phase 3
- `03-genie-metadata-optimizer/SKILL.md` — Add per-lever proposal examples in the Introspective Analysis section
- `03-genie-metadata-optimizer/references/feedback-to-metadata-mapping.md` — Add concrete Lever 1, 2, 3 proposal examples with actual SQL and repo paths

---

## Gap 20: Genie Space State Misdiagnosed — GET API Response Misinterpreted

**Priority:** P1 (incorrect diagnosis cascades into wrong optimization strategy)

**What went wrong:** The agent called `GET /api/2.0/genie/spaces/01f10e84df6715e39ea60890ef55ae0f` and received:

```json
{
  "description": "Comprehensive analytics for...",
  "space_id": "01f10e84df6715e39ea60890ef55ae0f",
  "title": "Wanderbricks Unified Monitor",
  "warehouse_id": "02c1885622661afa"
}
```

The agent concluded the space was "essentially blank — just a title and warehouse" and that "the Genie Space had no configuration deployed." This was incorrect. The space had been fully configured the previous day with 7 trusted tables, 2 metric views, 3 TVFs, text instructions, and benchmarks. The `GET` response omits `serialized_space` unless the query parameter `?include_serialized_space=true` is included.

This misdiagnosis led the agent to:
1. Re-run the `semantic_layer_job` (creating metric views, TVFs, and re-deploying the space) — a 4-minute operation that was unnecessary
2. Attribute the 22.7% → 45.5% accuracy jump to "deploying config to a blank space" rather than to the `example_question_sqls` that were the actual cause
3. Miss the opportunity to diagnose *why* the already-configured space was performing at only 22.7%

The correct API call was documented in the export-import API skill's `api-reference.md` (line 48):

```bash
GET /api/2.0/genie/spaces/{space_id}?include_serialized_space=true
```

The agent used the bare `GET /api/2.0/genie/spaces/{id}` without the query parameter.

**Root cause:** Two contributing factors:

1. The orchestrator skill's Step 0 / Phase 1 does not include a "verify current space state" step that uses the full export API. The pseudocode jumps straight to `snapshot_genie_metadata()` without specifying what API call that function makes or what parameters it requires.

2. The export-import API skill documents `?include_serialized_space=true` in `api-reference.md` but does not flag it as **critical**. The table in `SKILL.md` (line 51) says "Get Space | GET | `/api/2.0/genie/spaces/{space_id}` | Export config, backup" — omitting the query parameter entirely. An agent following the SKILL.md table (not the reference doc) will use the bare URL.

**What assumption was incorrect:** That the standard GET endpoint for a REST resource would return its full state. This is a Databricks Genie API-specific behavior (serialized_space is a potentially large JSON blob and is excluded by default) that the agent had no prior experience with.

**What would have prevented this:**

1. Add to the orchestrator's Phase 1 (before baseline evaluation):
   ```
   Step 0b: Verify Space State
     config = GET /api/2.0/genie/spaces/{id}?include_serialized_space=true
     Log: tables={N}, metric_views={N}, tvfs={N}, instructions={present/absent}
     If serialized_space is empty → space is genuinely unconfigured, deploy first
     If serialized_space has assets → space is configured, proceed to evaluation
   ```

2. Update the export-import API skill's SKILL.md table to include the query parameter:
   ```
   | Get Space | GET | `/api/2.0/genie/spaces/{space_id}?include_serialized_space=true` | Export config |
   ```

3. Add a "Common Mistake" to the export-import API skill:
   ```
   | GET without ?include_serialized_space=true | Space appears empty | Always include query parameter |
   ```

**Files to update:**
- `05-genie-optimization-orchestrator/SKILL.md` — Add Step 0b (verify space state) to Phase 1 pseudocode
- `04-genie-space-export-import-api/SKILL.md` — Add `?include_serialized_space=true` to the API operations table
- `04-genie-space-export-import-api/references/api-reference.md` — Add bold warning that omitting the parameter returns metadata-only

---

## Gap 21: Per-Row Evaluation Data Not Accessible to Optimization Loop

**Priority:** P2 (optimization decisions made on aggregate statistics instead of per-question analysis)

**What went wrong:** Across 5 iterations, the agent only ever saw aggregate metrics:

```
syntax_validity/mean: 1.0
asset_routing/mean: 0.909
result_correctness/mean: 0.727
```

The agent never inspected **which specific questions** failed, **what SQL** Genie generated for them, **what the judge rationale** was, or **what ASI metadata** was attached. Optimization decisions were made by manually reasoning about benchmark categories: "the MV queries probably need more MEASURE() examples" and "the TVF date parameters are probably wrong."

The per-row data exists — `eval_result.tables["eval_results"]` contains a DataFrame with one row per benchmark, including `inputs/question`, `outputs/response`, `feedback/syntax_validity`, `feedback/schema_accuracy`, `rationale/result_correctness`, and so on. But this data is:

1. **Not emitted as an artifact** — the evaluator notebook logs summary metrics but not the per-row DataFrame
2. **Not accessible from the CLI** — the orchestrator (running `databricks bundle run`) receives only the `dbutils.notebook.exit()` JSON, which contains `per_judge` means and `arbiter_verdicts` counts
3. **Not logged to MLflow in a queryable format** — the eval_results table is inside the `EvaluationResult` object during notebook execution but is not persisted as an artifact

Additionally, `failure_question_ids` (line 1052) is always empty because the eval records don't include `question_id` in the `inputs` dict. The code at line 1060 looks for `inputs/question_id`:

```python
qid = row.get("inputs/question_id", row.get("inputs", {}).get("question_id", ""))
```

But the eval records (lines 940-947) only set:

```python
"inputs": {
    "question": b["question"],
    "space_id": space_id,
    "catalog": catalog,
    "gold_schema": gold_schema,
    "expected_sql": b.get("expected_sql", ""),
},
```

No `question_id` key is present, so `failure_ids` is always `[]`.

**Root cause:** The evaluator notebook is designed as a **one-shot job** that runs inside Databricks, produces results within `mlflow.genai.evaluate()`, and exits. The optimization loop runs **outside** the notebook (in the CLI orchestrator or in the agent's conversation). There is no data bridge between the two contexts. The notebook produces rich per-row data during execution but only exports a summary through `dbutils.notebook.exit()`.

**What assumption was incorrect:** That the orchestrator (running in CLI mode) would have access to the evaluator's in-memory `eval_result.tables["eval_results"]` DataFrame. It does not — the notebook runs as a remote Databricks job, and the only output channel is the notebook exit value (a JSON string with a size limit). The assumption that "mlflow.genai.evaluate() populates all MLflow tabs" is true for the UI, but the programmatic consumer (the optimization loop) needs explicit artifact emission.

**What would have prevented this:**

1. Add `question_id` to eval record inputs:
   ```python
   "inputs": {
       "question_id": b["id"],  # <-- add this
       "question": b["question"],
       ...
   }
   ```

2. Add a **Cell 9: Emit Per-Row Results** to the evaluator notebook:
   ```python
   if hasattr(eval_result, "tables") and "eval_results" in eval_result.tables:
       results_df = eval_result.tables["eval_results"]
       results_path = os.path.join(tempfile.gettempdir(), "eval_results.json")
       results_df.to_json(results_path, orient="records")
       mlflow.log_artifact(results_path, artifact_path="evaluation")
       print(f"Logged {len(results_df)} per-row results to artifacts/evaluation/eval_results.json")
   ```

3. Add a **Step 4a: Download Per-Row Results** to the orchestrator:
   ```python
   # After evaluation job completes:
   client = mlflow.tracking.MlflowClient()
   artifact_path = client.download_artifacts(run_id, "evaluation/eval_results.json")
   with open(artifact_path) as f:
       per_row_results = json.load(f)
   # Now pass to cluster_failures() for data-driven optimization
   ```

4. Document in the orchestrator's hard constraints:
   ```
   15. Optimization decisions MUST be based on per-row evaluation data, not aggregate metrics.
       Before generating proposals, the orchestrator MUST download and parse the evaluator's
       per-row results artifact. Generating proposals from aggregate statistics alone is
       prohibited — it produces untargeted, low-confidence changes.
   ```

**Files to update:**
- `02-genie-benchmark-evaluator/assets/templates/run_genie_evaluation.py` — Add `question_id` to inputs; add Cell 9 emitting per-row results artifact
- `05-genie-optimization-orchestrator/SKILL.md` — Add Step 4a (download per-row results); add hard constraint #15
- `03-genie-metadata-optimizer/SKILL.md` — Update input contract to explicitly require per-row data, not summary metrics

---

## Cross-Gap Analysis: The Producer-Consumer Disconnect Pattern

All 6 gaps share a common structural pattern:

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│    EVALUATOR      │     │   (missing wire)  │     │    OPTIMIZER      │
│                   │     │                   │     │                   │
│ Produces:         │ ──X──>                  │ ──X──> Consumes:        │
│ - ASI metadata    │     │  No artifact      │     │ - cluster_failures│
│ - Arbiter verdicts│     │  No artifact      │     │ - proposals       │
│ - Per-row results │     │  Summary JSON only│     │ - lever mapping   │
│ - Failure taxonomy│     │                   │     │ - detect_conflicts│
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

The fix is the same for all: **emit structured artifacts from the evaluator, and require the orchestrator to read them before making optimization decisions.**

Concretely, the evaluator should emit 3 artifacts per run:
1. `evaluation/eval_results.json` — full per-row results with question_id, all feedback, all rationales
2. `evaluation/failures.json` — filtered to failed questions only, with ASI metadata
3. `evaluation/arbiter_actions.json` — arbiter verdicts with question, old GT SQL, Genie SQL

The orchestrator should download all 3 before invoking the optimizer, and the optimizer should consume them via `cluster_failures()` / `generate_metadata_proposals()` / `detect_conflicts_and_batch()`.

---

## Summary of Recommended Skill Changes

| Gap | Priority | Primary File to Change | Change |
|-----|----------|----------------------|--------|
| 16 | P0 | Evaluator template + Optimizer script | Emit failures artifact; move cluster_failures() to runnable script |
| 17 | P0 | Evaluator template + Orchestrator SKILL | Add arbiter triage block; add threshold check to loop |
| 18 | P1 | Orchestrator SKILL + references | Add concrete create_genie_model_version() implementation |
| 19 | P1 | Orchestrator SKILL + Optimizer references | Mandatory lever audit log; per-lever proposal examples |
| 20 | P1 | Orchestrator SKILL + Export-Import API skill | Add space verification step; document ?include_serialized_space=true |
| 21 | P2 | Evaluator template + Orchestrator SKILL | Emit per-row results artifact; add question_id to inputs |

### New Hard Constraints to Add to Orchestrator

```
15. Optimization decisions MUST be based on per-row evaluation data (the evaluator's
    failures artifact), not aggregate metrics. Download and parse the failures artifact
    before generating proposals. Proposals generated from aggregate statistics alone
    (e.g., "result_correctness/mean is low, add more example SQLs") are prohibited.

16. Arbiter verdicts MUST be triaged after every evaluation. If genie_correct >= 3,
    load the Generator to update benchmark expected SQL. All ground_truth_correct
    verdicts must be passed to cluster_failures() as confirmed Genie failures.
```
