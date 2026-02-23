# Genie Space Optimization: Skill Feedback Report

**Session:** Revenue & Property Intelligence Genie Space optimization  
**Date:** 2026-02-22  
**Framework:** [self-improvement SKILL.md](../../data_product_accelerator/skills/admin/self-improvement/SKILL.md)  
**Scope:** 18 distinct errors, 4 improvement patterns, targeting 5 worker skills + 1 orchestrator skill

---

## Table of Contents

1. [Error Catalog](#1-error-catalog)
2. [Per-Skill Feedback](#2-per-skill-feedback)
3. [Proposed Skill Updates](#3-proposed-skill-updates)
4. [Architectural Insights](#4-architectural-insights)
5. [Improvement Patterns Discovered](#5-improvement-patterns-discovered)
6. [Appendix: Error-to-Skill Mapping](#appendix-error-to-skill-mapping)
7. [Key Files to Reference](#key-files-to-reference)

---

## 1. Error Catalog

Chronological listing of every error encountered during the optimization session. No recency bias -- errors are ordered by when they appeared, not by severity.

### #1: FileNotFoundError for golden-queries.yaml

| Field | Detail |
|-------|--------|
| **Error** | `FileNotFoundError: [Errno 2] No such file or directory: '/Workspace/src/wanderbricks_semantic/golden-queries.yaml'` |
| **Root Cause** | The evaluator template hardcodes `/Workspace/` as the path prefix for `golden-queries.yaml`. When deployed via Databricks Asset Bundles (DABs), the file lives under the bundle root (e.g., `/Workspace/Users/.../bundle/wanderbricks/dev/files/`), not `/Workspace/`. |
| **Incorrect Assumption** | Notebooks always run from `/Workspace/` root. |
| **Fix Applied** | Made `_bundle_root` a fallback-safe global derived from `dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath()`, then resolved all file paths relative to it. |
| **Target Skill** | Evaluator SKILL.md + template |
| **Prevention** | The evaluator template should use `_bundle_root` for all file resolution. The SKILL.md should document this in a "DABs Deployment" section. |

### #2: Missing LoggedModel

| Field | Detail |
|-------|--------|
| **Error** | Evaluation ran without a `LoggedModel`, disabling config version tracking. No error message -- silent degradation. |
| **Root Cause** | The evaluator template assumes the orchestrator calls `create_genie_model_version()` before triggering evaluation. When evaluation is triggered directly (e.g., via `databricks bundle run`), no LoggedModel exists. |
| **Incorrect Assumption** | Evaluation is always triggered by the orchestrator. |
| **Fix Applied** | Auto-create a LoggedModel in the evaluator template when `model_id` is empty: fetch live Genie config via API, compute config hash, call `mlflow.set_active_model()`, log config as artifact. |
| **Target Skill** | Evaluator SKILL.md (should mandate auto-creation), Orchestrator hard constraint #17 (should note the evaluator fallback) |
| **Prevention** | Add to evaluator Common Mistakes: "Assuming orchestrator always provides `model_id`". |

### #3: LoggedModel Content Quality

| Field | Detail |
|-------|--------|
| **Error** | LoggedModel only stores a config hash + Genie JSON snapshot. Iteration diffs are not meaningful because UC metadata (table comments, column comments, tags) -- which is where most lever changes land -- is not captured. |
| **Root Cause** | The LoggedModel was designed as a version pointer, not a state snapshot. Hard constraint #17 says "LoggedModel MUST be created before every evaluation" but doesn't specify what it should contain beyond the Genie config. |
| **Incorrect Assumption** | The Genie config JSON fully represents the model state. It doesn't -- UC comments (Lever 1), MV definitions (Lever 2), and TVF signatures (Lever 3) all live outside the config. |
| **Fix Proposed** | LoggedModel creation should also query `catalog.information_schema.columns` and `catalog.information_schema.table_tags` for all tables in the space, and store the results as artifacts alongside the Genie config. This enables meaningful iteration diffs. |
| **Target Skill** | Evaluator SKILL.md LoggedModel section, Orchestrator hard constraint #17 |
| **Prevention** | Update hard constraint #17: "LoggedModel MUST capture Genie config + UC metadata (table/column comments, tags) from `information_schema`." |

### #4: MlflowException -- Invalid type for `data`

| Field | Detail |
|-------|--------|
| **Error** | `MlflowException: Invalid type for parameter 'data'. Expected a list of dictionaries, a pandas DataFrame, or a Spark DataFrame. Got: <class 'str'>` |
| **Root Cause** | Cell 7 assigns `eval_data = eval_dataset_uc_name` (a UC table name string) when a UC dataset exists. `mlflow.genai.evaluate()` doesn't accept plain strings -- it needs a DataFrame or list of dicts. |
| **Incorrect Assumption** | UC dataset names can be passed directly to `mlflow.genai.evaluate(data=...)`. |
| **Fix Applied** | Always convert evaluation records to a Pandas DataFrame before passing to `mlflow.genai.evaluate()`, regardless of whether a UC dataset exists. |
| **Target Skill** | Evaluator template Cell 7 |
| **Prevention** | Add to evaluator Common Mistakes: "Passing UC dataset name string to `data` parameter -- always use a DataFrame." |

### #5: Run Lifecycle Conflict

| Field | Detail |
|-------|--------|
| **Error** | `Exception: Run with UUID ... is already active.` |
| **Root Cause** | `mlflow.log_artifact()` (used for LoggedModel config logging) implicitly opens a run. When `register_judge_prompts()` then tries to start another run, it crashes because the first run is still active. |
| **Incorrect Assumption** | `mlflow.log_artifact()` is side-effect-free regarding run state. |
| **Fix Applied** | Wrapped artifact logging inside an explicit `with mlflow.start_run()` context that auto-closes, so no dangling active run exists when prompt registration starts. |
| **Target Skill** | Evaluator template Cell 2 |
| **Prevention** | Add to evaluator Common Mistakes: "Bare `mlflow.log_artifact()` calls open implicit runs -- always wrap in `with mlflow.start_run()`." |

### #6: InstructionsJudge has no `.evaluate()`

| Field | Detail |
|-------|--------|
| **Error** | `'InstructionsJudge' object has no attribute 'evaluate'` |
| **Root Cause** | `make_judge()` returns an `InstructionsJudge` scorer (a callable for `mlflow.genai.evaluate()`), not an object with an `.evaluate()` method. The arbiter tried to call `.evaluate()` for conditional scoring when Layer 1/2 judges disagreed. |
| **Incorrect Assumption** | Scorers returned by `make_judge()` have an `.evaluate()` method for standalone invocation. |
| **Fix Applied** | Refactored the arbiter to call the LLM directly via `_call_llm_for_scoring()` (which uses `w.serving_endpoints.query()`) instead of trying to use `make_judge().evaluate()`. Parses JSON verdict from LLM response. |
| **Target Skill** | Evaluator SKILL.md (should document that `make_judge()` returns a scorer, not an evaluator object), MLflow GenAI skill (should clarify scorer vs evaluator semantics) |
| **Prevention** | Add to evaluator SKILL.md: "`make_judge()` returns a scorer callable -- it has no `.evaluate()` method. For inline/conditional LLM calls, use `_call_llm_for_scoring()` directly." |

### #7: Missing example_question_sqls

| Field | Detail |
|-------|--------|
| **Error** | No `example_question_sqls` were generated for the Revenue & Property Intelligence Genie Space, despite the Unified Monitor space having them. This meant the space lacked SQL routing hints. |
| **Root Cause** | The generator skill doesn't mention `example_question_sqls` at all. The skill that originally created the Genie Space should have added routing hints but this was not part of its output specification. |
| **Incorrect Assumption** | Genie Spaces don't need example SQL for routing -- the instructions and metadata are sufficient. |
| **Fix Applied** | Added 5 targeted `example_question_sqls` to the Genie config, each with a proper 32-hex UUID as the `id`. These serve as strong routing hints for ambiguous questions. |
| **Target Skill** | Generator SKILL.md (should produce routing hints as part of benchmark generation), Applier SKILL.md (should document the `example_question_sqls` format) |
| **Prevention** | Generator output spec should include `example_question_sqls` as an optional output alongside benchmarks. |

### #8: Genie API Sorting Errors

| Field | Detail |
|-------|--------|
| **Error** | `Error: Invalid export proto: data_sources.tables must be sorted by identifier` and `instructions.sql_functions must be sorted by (id, identifier)` |
| **Root Cause** | The Genie Space API PATCH endpoint requires all arrays in the config to be sorted by specific keys. The applier skill documents `sort_genie_config()` but the template code paths don't always call it before PATCH. |
| **Incorrect Assumption** | The API accepts arrays in any order. |
| **Fix Applied** | Called `sort_genie_config()` on the full config before every PATCH request. |
| **Target Skill** | Applier SKILL.md (Common Mistakes table already covers this but the error message format should be documented explicitly) |
| **Prevention** | Add the exact error messages to the applier's Common Mistakes table so agents can pattern-match. |

### #9: Premature Lever 6 Application

| Field | Detail |
|-------|--------|
| **Error** | Agent applied Lever 1 (UC COMMENTs) and Lever 6 (Genie Instructions + `example_question_sqls`) simultaneously in the same iteration, violating hard constraint #14. |
| **Root Cause** | Despite the orchestrator SKILL.md explicitly stating "Proposals MUST be applied in lever priority order (1 -> 6)" and the Common Mistakes table warning "Applying Lever 6 (GEPA) before Levers 1-5 -> Optimization budget wasted on lowest-priority lever," the agent still combined levers. The constraint is written clearly but the Phase 2 pseudocode could be more defensive. |
| **Incorrect Assumption** | Applying multiple levers at once is acceptable for efficiency. |
| **Fix Applied** | Rolled back Lever 6 changes. Re-applied levers sequentially: Lever 1, then Lever 2, then Levers 3-5 (skipped -- no proposals), then Lever 6. Re-evaluated after each lever group. |
| **Target Skill** | Orchestrator SKILL.md Phase 2 pseudocode |
| **Prevention** | The pseudocode already covers this correctly. Consider adding a **bolded, standalone warning** outside the pseudocode block: "NEVER apply multiple levers in the same iteration. Each lever gets its own evaluate-measure-decide cycle." Also add a verification step: "Before applying lever N, confirm that lever N-1's evaluation has been recorded." |

### #10: Job Parameter vs Widget Confusion

| Field | Detail |
|-------|--------|
| **Error** | `Error: the job to run does not define job parameters; specifying job parameters is not allowed` |
| **Root Cause** | `databricks bundle run --params` applies to job parameters (defined via `parameters` block), not notebook widgets (defined via `base_parameters`). The evaluator job uses `base_parameters` + `dbutils.widgets.get()`, so runtime overrides via `--params` don't work. |
| **Incorrect Assumption** | `--params` can override notebook widget values. |
| **Fix Applied** | Modified `genie_evaluation_job.yml` to set `run_repeatability: "true"` directly in `base_parameters`, then redeployed. |
| **Target Skill** | Evaluator SKILL.md (Common Mistakes already warns about `{{job.parameters.X}}` vs `base_parameters` but doesn't explain the `--params` CLI behavior) |
| **Prevention** | Add to evaluator SKILL.md: "To override widget values at runtime, modify `base_parameters` in the job YAML and redeploy. CLI `--params` only works with the `parameters` block (job parameters), not `base_parameters` (notebook widgets)." |

### #11: Cell 9c Column Name Mismatch

| Field | Detail |
|-------|--------|
| **Error** | Cell 9c repeatability check produced 0% results. Every question was skipped by `if not question: continue`. |
| **Root Cause** | Cell 9c references `inputs/question` to extract the question text, but the actual eval DataFrame uses nested dicts: `row["request"]["question"]` for the question and `row["response"]` for the SQL output. The column name convention changed between MLflow GenAI versions. |
| **Incorrect Assumption** | Eval DataFrame columns follow the flat `inputs/question`, `outputs/response` naming convention. |
| **Fix Applied** | Updated Cell 9c to extract question from `row.get("request", {}).get("question")` and SQL from `row.get("response", {})`, with fallbacks to `row.get("inputs", {}).get("question")`. |
| **Target Skill** | Evaluator template Cell 9c |
| **Prevention** | Add to evaluator SKILL.md: "Eval DataFrame column names depend on MLflow GenAI version. Always access via nested dict with fallbacks: `row.get('request', row.get('inputs', {}))`. Test Cell 9c's column access against a real row before looping." |

### #12: ALTER TABLE on Metric View

| Field | Detail |
|-------|--------|
| **Error** | `[EXPECT_TABLE_NOT_VIEW.NO_ALTERNATIVE] 'ALTER TABLE ... ALTER COLUMN' expects a table but booking_analytics_metrics is a view.` |
| **Root Cause** | The Lever 1 application path uses `ALTER TABLE ... ALTER COLUMN ... COMMENT` to update column comments. This fails on Metric Views because they are views, not tables. Metric View column comments must be updated in the MV YAML definition, then the view recreated via `CREATE OR REPLACE VIEW ... WITH METRICS LANGUAGE YAML`. |
| **Incorrect Assumption** | All assets in the Genie Space are tables. |
| **Fix Applied** | Detected that `booking_analytics_metrics` is a Metric View. Updated the YAML definition file (`booking_analytics_metrics.yaml`) with enhanced column comments, then executed `CREATE OR REPLACE VIEW ... WITH METRICS LANGUAGE YAML` to apply. |
| **Target Skill** | Applier SKILL.md Lever 2 section (already documents this for Lever 2 but Lever 1's column comment path doesn't check asset type) |
| **Prevention** | Add to applier SKILL.md Lever 1 section: "Before applying `ALTER TABLE ... ALTER COLUMN`, check if the asset is a view via `DESCRIBE EXTENDED {table}`. If it's a Metric View, route the column comment change to Lever 2 (MV YAML + recreate)." |

### #13: Repeatability Not Visible as a Judge

| Field | Detail |
|-------|--------|
| **Error** | Cell 9c repeatability results only appear in `evaluation/repeatability.json` artifact, not in the MLflow Evaluations UI alongside the other 8 judges. |
| **Root Cause** | Cell 9c writes a JSON artifact but doesn't call `mlflow.log_assessment()` to record per-trace Feedback. The MLflow Evaluations UI only shows judge results that are logged as assessments on individual traces. |
| **Incorrect Assumption** | Artifact logging is sufficient for judge visibility in the UI. |
| **Fix Applied** | Added `mlflow.log_assessment()` calls in Cell 9c for each question's repeatability result, recording it as a per-trace assessment with the same trace ID as the evaluation trace. |
| **Target Skill** | Evaluator SKILL.md (should document that Cell 9c must log assessments, not just artifacts, for UI visibility) |
| **Prevention** | Add to evaluator SKILL.md: "All judge results -- including Cell 9c repeatability -- MUST be logged via `mlflow.log_assessment()` for visibility in the Evaluations UI. Artifact-only logging is invisible to users." |

### #14: Cross-Iteration Repeatability Not Computed

| Field | Detail |
|-------|--------|
| **Error** | After iteration 2, the agent did not compute cross-iteration repeatability despite having both iterations' row data available. The skill describes `_compute_cross_iteration_repeatability()` (v3.8.0) for free SQL hash comparison between iterations, but the agent didn't use it. |
| **Root Cause** | The skill describes two repeatability mechanisms -- (1) cross-iteration SQL hash comparison (free, iteration 2+) and (2) Cell 9c re-query test (expensive, Phase 3b final only) -- but the handoff between them is under-specified. The orchestrator pseudocode calls `_compute_cross_iteration_repeatability()` but it's buried in the Phase 2 loop logic, not highlighted as a mandatory step. |
| **Incorrect Assumption** | Repeatability is only measured by Cell 9c. |
| **Fix Applied** | Manually computed cross-iteration repeatability by comparing SQL hashes from iteration 1 vs 2 row data. Identified rp_001 and rp_010 as oscillating between MV and TVF routing. |
| **Target Skill** | Orchestrator SKILL.md v3.8.0 |
| **Prevention** | Add a **standalone hard constraint** (not buried in pseudocode): "From iteration 2 onward, cross-iteration repeatability MUST be computed before proceeding to the next lever. This is free (no API calls) and mandatory." Add to Common Mistakes: "Skipping cross-iteration repeatability in iteration 2+ -> Repeatability regressions go undetected." |

### #15: serialized_space PATCH Format Error

| Field | Detail |
|-------|--------|
| **Error** | `Error: Could not parse request object: Expected Scalar value for String field 'serialized_space'` |
| **Root Cause** | The PATCH body was constructed with `serialized_space` as a nested JSON object instead of a JSON string. The Genie API requires `serialized_space` to be a string value (the config dict serialized via `json.dumps()`), not a nested object. This means the PATCH body is double-serialized: the outer JSON has `"serialized_space": "<json-string>"`. |
| **Incorrect Assumption** | `serialized_space` accepts a nested JSON object. |
| **Fix Applied** | Constructed PATCH body as `{"serialized_space": json.dumps(config)}` where `config` is the sorted, variable-resolved dict. |
| **Target Skill** | Applier SKILL.md API examples (control-levers.md already shows `json.dumps(config)` but a standalone warning would help) |
| **Prevention** | Add to applier Common Mistakes: "Passing `serialized_space` as nested object instead of JSON string -> Expected Scalar value error. Always use `json.dumps(config)` to serialize." |

### #16: Invalid example_question_sql.id Format

| Field | Detail |
|-------|--------|
| **Error** | `Error: Invalid id for example_question_sql.id: 'ex_rp_001'. Expected lowercase 32-hex UUID without hyphens` |
| **Root Cause** | `example_question_sqls` entries require `id` values to be 32-character lowercase hexadecimal UUIDs without hyphens (e.g., `a1b2c3d4e5f6789012345678abcdef01`), not human-readable IDs like `ex_rp_001`. The applier skill documents the 32-char hex requirement only for `sql_functions`, not for `example_question_sqls`. |
| **Incorrect Assumption** | `example_question_sqls` IDs follow the same `domain_NNN` pattern as benchmark IDs. |
| **Fix Applied** | Generated proper 32-hex UUIDs via `uuid.uuid4().hex` for all `example_question_sqls` entries. |
| **Target Skill** | Applier SKILL.md Lever 6 section, Generator SKILL.md (if it ever generates `example_question_sqls`) |
| **Prevention** | Add to applier SKILL.md: "All Genie Space entity IDs (`example_question_sqls`, `sql_functions`, `data_sources`) must be lowercase 32-hex UUIDs without hyphens. Use `uuid.uuid4().hex` to generate." |

### #17: EXPECT_TABLE_NOT_VIEW on Metric View (Lever 1 Path)

| Field | Detail |
|-------|--------|
| **Error** | `[EXPECT_TABLE_NOT_VIEW.NO_ALTERNATIVE] 'ALTER TABLE ... ALTER COLUMN' expects a table but booking_analytics_metrics is a view.` |
| **Root Cause** | Complementary to #12. The Lever 1 code path for updating column comments assumes all assets are tables and uses `ALTER TABLE`. Metric Views require updating the YAML definition and recreating via `CREATE OR REPLACE VIEW`. |
| **Incorrect Assumption** | Lever 1 (UC table/column COMMENTs) only operates on tables. |
| **Fix Applied** | Same as #12 -- routed the column comment change through Lever 2's MV path. |
| **Target Skill** | Applier SKILL.md Lever 1 section (needs asset type detection before applying DDL) |
| **Prevention** | Add asset type detection to Lever 1: query `DESCRIBE EXTENDED {asset}` and check if it's a `VIEW` or `TABLE`. If VIEW, delegate to Lever 2 path. |

### #18: Unresolved Template Variables in API Payload

| Field | Detail |
|-------|--------|
| **Error** | PATCH payload contained `${catalog}` and `${gold_schema}` DABs template syntax instead of resolved values, causing catalog/schema not found errors. |
| **Root Cause** | The Genie config JSON files in the repository use `${catalog}` and `${gold_schema}` as DABs template variables. When reading these files to construct an API PATCH payload, the variables must be resolved to actual values before serialization. The applier's control-levers.md documents this (lines 249-250: `config_json.replace("${catalog}", CATALOG)`) but it's easy to miss. |
| **Incorrect Assumption** | Config files read from the repo are ready to send to the API without transformation. |
| **Fix Applied** | Added a pre-serialization step: `config_json.replace("${catalog}", catalog).replace("${gold_schema}", gold_schema)` before `json.dumps()`. |
| **Target Skill** | Applier SKILL.md dual-persistence section |
| **Prevention** | Add to applier Common Mistakes (already has "Missing template variables" but the reverse direction is missing): "Sending repo config to API without resolving `${catalog}`/`${gold_schema}` -> Table/catalog not found. Always resolve before API; always re-template before saving to repo." |

---

## 2. Per-Skill Feedback

### Evaluator (02-genie-benchmark-evaluator)

**File:** `data_product_accelerator/skills/semantic-layer/genie-optimization-workers/02-genie-benchmark-evaluator/SKILL.md`  
**Template:** `data_product_accelerator/skills/semantic-layer/genie-optimization-workers/02-genie-benchmark-evaluator/assets/templates/run_genie_evaluation.py`  
**Issues:** 9 (#1, #2, #3, #4, #5, #6, #10, #11, #13)

The evaluator skill and its template are the single biggest source of production errors (9 out of 18). Most errors stem from the gap between what the SKILL.md describes and what the template code actually does.

**Specific issues:**

1. **DABs path resolution (#1):** The SKILL.md never mentions DABs bundle root or `_bundle_root`. The template has the fix (lines 10-16 of `run_genie_evaluation.py`) but the skill should document when and why this matters. Add after the Configuration section (around line 40 of SKILL.md).

2. **LoggedModel auto-creation (#2):** The SKILL.md says `model_id` is an input parameter (line 42 of SKILL.md) but never describes what happens when it's empty. The template should auto-create a LoggedModel as a fallback, and the SKILL.md should document this in the Critical Patterns section (line 182).

3. **LoggedModel content (#3):** Neither the SKILL.md nor the template captures UC metadata (table/column comments, tags) alongside the Genie config. This makes iteration diffs meaningless for Lever 1/2 changes. Update the Critical Patterns section (line 188).

4. **Data type for `mlflow.genai.evaluate()` (#4):** The template passed a UC dataset name string instead of a DataFrame. Add to Common Mistakes table (line 209 of SKILL.md): "The `data` parameter must always be a DataFrame or list of dicts."

5. **Run lifecycle management (#5):** Bare `mlflow.log_artifact()` calls open implicit runs. Add to Common Mistakes table (line 209 of SKILL.md) with explicit warning about implicit run state.

6. **InstructionsJudge API (#6):** The SKILL.md discusses `make_judge()` at hard constraints #9 (line 178) and Common Mistakes (lines 222-229) but never clarifies that it returns a scorer callable, not an object with `.evaluate()`. Add to Critical Patterns (line 182).

7. **Job parameter vs widget (#10):** Common Mistakes (line 218 of SKILL.md) warns about `{{job.parameters.X}}` vs `base_parameters` but doesn't explain the CLI `--params` behavior. Expand that row.

8. **Cell 9c column names (#11):** The template uses `inputs/question` but the actual DataFrame uses `request.question`. Cell 9c is referenced at SKILL.md line 240. Add a column access note to the Cell 9c documentation.

9. **Repeatability as assessment (#13):** Cell 9c logs a JSON artifact but not per-trace assessments. The v3.7.0 changelog (line 257 of SKILL.md) describes Cell 9c but omits `mlflow.log_assessment()`. Mandate it in hard constraint #11 (line 180).

### Orchestrator (05-genie-optimization-orchestrator)

**File:** `data_product_accelerator/skills/semantic-layer/05-genie-optimization-orchestrator/SKILL.md`  
**Issues:** 4 (#3, #9, #14, plus lever-gate enforcement)

1. **Lever sequencing (#9):** Hard constraint #14 (line 140 of SKILL.md) and the Common Mistakes table (line 379) are clear, but the agent still violated them. The Phase 2 pseudocode (lines 202-245) correctly shows the for-loop, but a standalone bolded warning outside the pseudocode block (insert before line 202) would be more prominent: "NEVER apply multiple levers in the same iteration." Also add a new Common Mistakes row at line 379.

2. **Cross-iteration repeatability (#14):** The v3.8.0 changelog (line 390 of SKILL.md) mentions `_compute_cross_iteration_repeatability()` but it's not a hard constraint. Add a new hard constraint #19 after line 144: "Cross-iteration repeatability MUST be computed from iteration 2 onward."

3. **LoggedModel content (#3):** Hard constraint #17 (line 143 of SKILL.md) mandates LoggedModel creation but doesn't specify that it should capture UC metadata alongside the Genie config. Expand line 143.

4. **Lever-gate verification:** The pseudocode (line 203 of SKILL.md) shows `lever_audit[lever].attempted = True` tracking, but there's no verification step that confirms the previous lever's evaluation was recorded before starting the next lever. Add a `VERIFY` step after line 235.

### Generator (01-genie-benchmark-generator)

**File:** `data_product_accelerator/skills/semantic-layer/genie-optimization-workers/01-genie-benchmark-generator/SKILL.md`  
**Issues:** 3 (#7, #16, plus GT validation wiring)

1. **Missing example_question_sqls (#7):** The generator doesn't mention `example_question_sqls` at all. Add an "Optional Outputs" section after the existing Outputs table (around line 100 of SKILL.md). These are powerful routing hints that should be an optional output of benchmark generation.

2. **UUID format (#16):** The generator uses `domain_NNN` format for benchmark IDs (line 87 of SKILL.md). This is fine for benchmarks, but if the generator ever produces `example_question_sqls`, it must use 32-hex UUIDs. Add an "ID Format Requirements" table near line 87.

3. **GT validation wiring:** The generator defines `validate_ground_truth_sql()` and `validate_with_retry()` in `references/gt-validation.md` (lines 15-76), and `benchmark_generator.py` implements them (lines 110-153). But neither the generator SKILL.md (line 80 references gt-validation.md) nor the evaluator SKILL.md explicitly states that the evaluator should call these functions. Add a "Ground Truth Validation Handoff" section after line 170 of generator SKILL.md.

### Applier (04-genie-optimization-applier)

**File:** `data_product_accelerator/skills/semantic-layer/genie-optimization-workers/04-genie-optimization-applier/SKILL.md`  
**Issues:** 5 (#8, #12/#17, #15, #16, #18)

1. **API sorting (#8):** The Common Mistakes table (line 128 of SKILL.md) mentions `sort_genie_config()` but doesn't list the exact error messages. Add the error strings to that row so agents can pattern-match: `"data_sources.tables must be sorted by identifier"`, `"instructions.sql_functions must be sorted by (id, identifier)"`. Also add to a new "API Contract Gotchas" section after line 130.

2. **Metric View asset detection (#12, #17):** Lever 1's column comment path (line 68 of SKILL.md, Lever 2 at line 85) uses `ALTER TABLE` without checking asset type. Lever 2's `CREATE OR REPLACE VIEW` path is documented but the cross-lever routing (Lever 1 detects MV -> delegates to Lever 2) is not. Add an "Asset Type Detection" subsection to the Lever 1 section.

3. **serialized_space format (#15):** `control-levers.md` (lines 254, 319) shows `json.dumps(config)` in code examples, but a prominent warning that `serialized_space` must be a JSON string (not nested object) would prevent this. Add to Common Mistakes table (line 122 of SKILL.md).

4. **UUID format (#16):** The 32-char hex requirement is documented for `sql_functions` in `autonomous-ops-integration.md` (line 155) but not for `example_question_sqls`. Generalize in the new "API Contract Gotchas" section: "All Genie Space entity IDs must be lowercase 32-hex UUIDs without hyphens."

5. **Template variable resolution (#18):** `control-levers.md` (lines 249-275) documents the resolve-before-API/re-template-before-repo pattern, but the Common Mistakes table (line 129 of SKILL.md) only warns about the repo-save direction. Add the reverse direction to that same table row.

### Optimizer (03-genie-metadata-optimizer)

**File:** `data_product_accelerator/skills/semantic-layer/genie-optimization-workers/03-genie-metadata-optimizer/SKILL.md`  
**Issues:** 1 (repeatability-driven routing)

1. **Repeatability-driven optimization:** When `cluster_failures()` (called from the hard constraint in SKILL.md line 49) receives `repeatability_issue` synthetic failures, the skill doesn't specify how to route them. Add a "Repeatability Failure Clustering" section after the existing clustering documentation. The insight from this session: when a question oscillates between two asset types (e.g., MV vs TVF), the root cause is always insufficient disambiguation metadata between those two assets. The optimizer should auto-detect asset-type oscillation in failure clusters and map to the correct lever sequence.

---

## 3. Proposed Skill Updates

Following the self-improvement framework, all proposals are updates to existing skills (no new skills needed).

### Issue-to-Update Mapping

| # | Error | Target Skill | Update Type | Where to Update |
|---|-------|-------------|-------------|-----------------|
| 1 | FileNotFoundError (DABs path) | Evaluator | New section | Add "DABs Deployment" section after line 40 |
| 2 | Missing LoggedModel | Evaluator | Common Mistakes row | Line 209, new row |
| 3 | LoggedModel content quality | Evaluator + Orchestrator | New subsection + expand HC #17 | Evaluator line 182; Orchestrator line 143 |
| 4 | Invalid data type | Evaluator | Common Mistakes row | Line 209, new row |
| 5 | Run lifecycle conflict | Evaluator | Common Mistakes row | Line 209, new row |
| 6 | InstructionsJudge API | Evaluator | Critical Patterns note | Line 182, new subsection |
| 7 | Missing example_question_sqls | Generator + Applier | New output spec | Generator ~line 100; Applier Lever 6 section |
| 8 | API sorting errors | Applier | Expand Common Mistakes row | Line 128, add error strings |
| 9 | Premature Lever 6 | Orchestrator | Standalone warning + Common Mistakes row | Before line 202; line 379 |
| 10 | Job params vs widgets | Evaluator | Expand Common Mistakes row | Line 218 |
| 11 | Cell 9c column mismatch | Evaluator | Common Mistakes row | Line 209, new row |
| 12 | ALTER TABLE on MV | Applier | New subsection | Lever 1 section, after line 68 |
| 13 | Repeatability not visible | Evaluator | Expand HC #11 | Line 180 |
| 14 | Cross-iteration repeatability | Orchestrator | New hard constraint #19 | After line 144 |
| 15 | serialized_space format | Applier | Common Mistakes row + API Gotchas section | Line 122, new row; new section after line 130 |
| 16 | Invalid UUID format | Applier + Generator | API Gotchas section + ID format table | Applier new section; Generator ~line 87 |
| 17 | EXPECT_TABLE_NOT_VIEW | Applier | Asset type detection subsection | Lever 1 section (same as #12) |
| 18 | Unresolved template vars | Applier | Expand Common Mistakes row | Line 129, add reverse direction |

### Evaluator SKILL.md Updates

**Update 1: Add "DABs Deployment" section after the Configuration section**

```markdown
### DABs Bundle Root Path Resolution

When deployed via Databricks Asset Bundles, the notebook runs from the bundle
root (e.g., `/Workspace/Users/<email>/bundle/<project>/dev/files/`), not
`/Workspace/`. All file paths (golden-queries.yaml, genie configs, MV YAML)
must be resolved relative to `_bundle_root`.

The template derives `_bundle_root` from `dbutils.notebook.entry_point`:
- Split notebook path at `/src/` to find bundle root
- Add bundle root to `sys.path` for imports
- Resolve all file paths as `os.path.join(_bundle_root, relative_path)`
```

**Update 2: Add to Common Mistakes table (6 new rows)**

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Hardcoding `/Workspace/` prefix for file paths | `FileNotFoundError` in DABs deployments | Use `_bundle_root` from notebook context |
| Assuming orchestrator always provides `model_id` | No LoggedModel, no config version tracking | Auto-create LoggedModel when `model_id` is empty |
| Passing UC dataset name string to `data` parameter | `MlflowException: Invalid type` | Always convert to DataFrame before `mlflow.genai.evaluate()` |
| Bare `mlflow.log_artifact()` outside run context | `Run already active` error blocks prompt registration | Wrap in `with mlflow.start_run()` |
| Calling `make_judge().evaluate()` for conditional scoring | `AttributeError: no attribute 'evaluate'` | Use `_call_llm_for_scoring()` for inline LLM calls |
| Cell 9c using `inputs/question` column name | Repeatability check produces 0 results | Use `row.get("request", row.get("inputs", {}))` with fallbacks |

**Update 3: Add to Critical Patterns section**

```markdown
### LoggedModel Content Requirements

A LoggedModel MUST capture the full model state, not just the Genie config:
1. Genie Space config JSON (from GET /api/2.0/genie/spaces/{id})
2. UC metadata: table and column comments from
   `catalog.information_schema.columns` for all tables in the space
3. UC tags from `catalog.information_schema.table_tags`
4. Config hash for quick identity comparison

This enables meaningful iteration diffs that show what changed across
Lever 1 (UC comments), Lever 2 (MV definitions), and Lever 6 (instructions).
```

**Update 4: Add note about repeatability assessments**

```markdown
### Repeatability Judge Visibility

Cell 9c MUST log per-trace assessments via `mlflow.log_assessment()` for
each question's repeatability result. Artifact-only logging
(evaluation/repeatability.json) is invisible in the MLflow Evaluations UI.
Use the same trace_id as the original evaluation trace.
```

**Update 5: Add note about job parameter overrides**

```markdown
### Runtime Parameter Overrides

Notebook widget values (`dbutils.widgets.get()`) are set via `base_parameters`
in the job YAML. The CLI `--params` flag only works with `parameters` block
(job parameters), not `base_parameters`. To override a widget value at runtime,
modify `base_parameters` in the job YAML and redeploy via `databricks bundle deploy`.
```

### Orchestrator SKILL.md Updates

**Update 1: Add standalone lever-sequencing warning before Phase 2 pseudocode**

```markdown
> **CRITICAL: NEVER apply multiple levers in the same iteration.**
> Each lever gets its own evaluate-measure-decide cycle. Combining levers
> (e.g., Lever 1 + Lever 6) confounds impact measurement -- you cannot
> determine which lever drove the improvement. This is the most common
> mistake in optimization sessions.
```

**Update 2: Promote cross-iteration repeatability to a hard constraint**

```markdown
19. **Cross-iteration repeatability MUST be computed from iteration 2 onward.**
    Compare per-question SQL hashes between current and previous iteration
    before proceeding to the next lever. This is free (no API calls) and
    mandatory. Questions whose SQL changed AND were previously correct are
    flagged as `repeatability_issue` synthetic failures. See
    `_compute_cross_iteration_repeatability()` in orchestrator.py.
```

**Update 3: Add to Common Mistakes table**

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Skipping cross-iteration repeatability in iteration 2+ | Repeatability regressions go undetected; repeatable failures not fed to optimizer | Compute `_compute_cross_iteration_repeatability()` after every evaluation from iteration 2 |
| Applying Lever 1 + Lever 6 in same iteration | Cannot isolate lever impact; confounded measurements | One lever per iteration, re-evaluate between each |

**Update 4: Expand hard constraint #17**

```markdown
17. **LoggedModel MUST be created before every evaluation and MUST capture
    full model state.** The LoggedModel includes: (a) Genie Space config JSON,
    (b) UC metadata from `information_schema.columns` and
    `information_schema.table_tags` for all tables in the space,
    (c) config hash. If `create_genie_model_version()` returns None, log a
    WARNING and continue with degraded version tracking.
```

### Generator SKILL.md Updates

**Update 1: Add `example_question_sqls` to output specification**

```markdown
### Optional Outputs

| Output | Type | Description |
|--------|------|-------------|
| `example_question_sqls` | list | Routing hints for the Genie Space. For each high-priority benchmark, generate a corresponding entry with `id` (32-hex UUID), `question`, and `sql`. Max 10 entries per space. |
```

**Update 2: Add ID format note**

```markdown
### ID Format Requirements

| Entity | Format | Example |
|--------|--------|---------|
| Benchmark questions | `domain_NNN` | `rp_001`, `ce_015` |
| `example_question_sqls` | 32-hex UUID (no hyphens) | `a1b2c3d4e5f6789012345678abcdef01` |
| `sql_functions` | 32-hex UUID (no hyphens) | `f0e1d2c3b4a5968778695a4b3c2d1e0f` |

Use `uuid.uuid4().hex` to generate UUIDs for Genie Space entities.
```

**Update 3: Add cross-skill GT validation handoff note**

```markdown
### Ground Truth Validation Handoff

This skill defines `validate_ground_truth_sql()` and `validate_with_retry()`
in `references/gt-validation.md`. The evaluator MUST call these functions
in its structural pre-check cell (Cell 3a) before evaluation starts.

Remediation flow when validation fails:
1. Auto-remediate via LLM + `information_schema` schema context
2. If auto-remediation fails, emit `gt_remediation_queue.yaml` for the
   orchestrator to route back to this skill for replacement generation
```

### Applier SKILL.md Updates

**Update 1: Add "API Contract Gotchas" section**

```markdown
### API Contract Gotchas

These Genie API requirements are not documented in the main API reference
but cause immediate failures:

| Requirement | Error if Violated | Fix |
|-------------|-------------------|-----|
| All arrays sorted by key | `data_sources.tables must be sorted by identifier` | Call `sort_genie_config()` before every PATCH |
| `serialized_space` is a JSON string | `Expected Scalar value for String field` | Use `json.dumps(config)`, not nested object |
| All entity IDs are 32-hex UUIDs | `Invalid id: Expected lowercase 32-hex UUID without hyphens` | Use `uuid.uuid4().hex` |
| Template variables must be resolved | `CATALOG_NOT_FOUND` or `TABLE_NOT_FOUND` | Replace `${catalog}`/`${gold_schema}` before API; re-template before repo save |
| MVs cannot use ALTER TABLE | `EXPECT_TABLE_NOT_VIEW` | Check asset type via `DESCRIBE EXTENDED`; route MVs to `CREATE OR REPLACE VIEW` |
```

**Update 2: Add to Common Mistakes table (3 new rows)**

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Passing `serialized_space` as nested object | `Expected Scalar value for String field` error | Use `{"serialized_space": json.dumps(config)}` |
| Using human-readable IDs for `example_question_sqls` | `Invalid id: Expected lowercase 32-hex UUID` | Use `uuid.uuid4().hex` for all Genie entity IDs |
| Sending repo config to API without resolving `${catalog}` | `CATALOG_NOT_FOUND` or `TABLE_NOT_FOUND` | Resolve before API; re-template before repo save |

**Update 3: Add asset type detection to Lever 1 section**

```markdown
### Lever 1: Asset Type Detection

Before applying `ALTER TABLE ... ALTER COLUMN ... COMMENT`:
1. Run `DESCRIBE EXTENDED {fully_qualified_name}`
2. Check if the result shows `Type: VIEW` or `Type: TABLE`
3. If VIEW (especially Metric View): route the column comment change to
   Lever 2 (update MV YAML definition + `CREATE OR REPLACE VIEW`)
4. If TABLE: proceed with `ALTER TABLE`
```

### Optimizer SKILL.md Updates

**Update 1: Add repeatability-driven clustering pattern**

```markdown
### Repeatability Failure Clustering

When `cluster_failures()` receives `repeatability_issue` synthetic failures
(injected by the orchestrator from cross-iteration comparison), apply this
triage pattern:

1. **Detect asset-type oscillation:** If the SQL variants for a question
   reference different asset types (e.g., one uses MV `booking_analytics_metrics`
   and another uses TVF `get_revenue_summary()`), the root cause is insufficient
   disambiguation metadata.

2. **Map to levers:**
   - Lever 1: Add UC COMMENT on the preferred asset with explicit synonym
     phrases that trigger routing to it
   - Lever 2: Add MV measure comments with "Use this MEASURE for X. Do NOT
     use {alternative_asset} for X."
   - Lever 6 (last resort): Add negative routing instruction in Genie
     Instructions: "For questions about X, ALWAYS use {preferred_asset}.
     NEVER use {alternative_asset}."

3. **Verify:** After each lever, re-run the specific question 3x to confirm
   the oscillation is resolved before moving to the next repeatability issue.
```

---

## 4. Architectural Insights

### Insight 1: The Evaluator Template is the Primary Failure Point

9 of 18 errors (50%) originated in the evaluator template or its SKILL.md. The template is the most complex artifact in the system (~500 lines, 15+ cells, 8 scorers), and it runs in a Databricks notebook environment with MLflow state management. The gap between what the SKILL.md describes and what the template code does creates implementation drift.

**Recommendation:** The evaluator SKILL.md should include a "Template Cell Contract" section that specifies, for each cell: inputs, outputs, side effects (MLflow run state changes), and error modes. This would serve as both documentation and a verification checklist.

### Insight 2: Skill Prose vs Template Code Drift

Multiple errors (#4, #5, #6, #11) arose because the SKILL.md described a pattern but the template code implemented it differently (or not at all). The SKILL.md is the authoritative reference, but agents follow the template code when generating implementations.

**Recommendation:** Add a "Template Verification" section to the evaluator SKILL.md that maps each critical pattern to its template cell and expected behavior. Example: "Pattern: `data` parameter must be DataFrame. Verified in: Cell 7, line ~180. If Cell 7 assigns a string, this pattern is violated."

### Insight 3: Ground Truth Validation is Described but Disconnected

The generator skill defines `validate_ground_truth_sql()` and `validate_with_retry()` in `gt-validation.md`. The evaluator skill has Cell 3 for loading benchmarks. But no skill connects them -- there's no "Cell 3a: Validate GT SQL" in the template, and neither skill says "the evaluator calls the generator's validation functions." The validation pipeline exists in pieces but the cross-skill handoff is a gap.

**Recommendation:** Add explicit cross-skill references. The generator SKILL.md should say: "These validation functions are consumed by the evaluator in Cell 3a." The evaluator SKILL.md should say: "Cell 3a calls `validate_ground_truth_sql()` from the generator's `gt-validation.md`."

### Insight 4: Repeatability is Under-Specified Across Skills

The system defines two repeatability mechanisms:
1. **Cross-iteration SQL hash comparison** (free, iteration 2+) -- defined in orchestrator SKILL.md v3.8.0
2. **Cell 9c re-query test** (expensive, Phase 3b final only) -- defined in evaluator template

The handoff between them is unclear. The orchestrator mentions `_compute_cross_iteration_repeatability()` in the changelog but doesn't make it a hard constraint. Cell 9c is gated by `run_repeatability` but doesn't explain its relationship to cross-iteration comparison. The result: the agent missed computing cross-iteration comparison entirely in iteration 2 and treated Cell 9c as the only repeatability mechanism.

**Recommendation:** Create a unified "Repeatability" section in the orchestrator SKILL.md that documents both mechanisms, when each fires, what data each needs, and how they hand off. Make cross-iteration comparison a hard constraint from iteration 2 onward.

### Insight 5: Genie API Contract Details are Scattered

Errors #8, #15, #16, and #18 all relate to Genie API contract requirements that are either undocumented or scattered across reference files. Array sorting is in `control-levers.md`. Template variable resolution is in `control-levers.md`. UUID format is in `autonomous-ops-integration.md` (for `sql_functions` only). `serialized_space` format is implicit in code examples.

**Recommendation:** The applier SKILL.md should have a dedicated "API Contract Gotchas" section (proposed above) that consolidates all non-obvious API requirements in one place with exact error messages.

### Insight 6: LoggedModel is a Checkbox, Not a State Snapshot

Hard constraint #17 says "LoggedModel MUST be created before every evaluation" -- treating it as a binary: exists or doesn't. But the LoggedModel should be a meaningful state snapshot that enables iteration comparison. When most lever changes (UC comments, MV definitions, TVF signatures) live outside the Genie config JSON, logging only the config provides an incomplete picture.

**Recommendation:** Expand the LoggedModel to capture UC metadata from `information_schema`, making it a true "model state" artifact that supports meaningful diffs between iterations.

---

## 5. Improvement Patterns Discovered

These are forward-looking enhancements, not bug fixes. They were discovered during the optimization session and should be codified back into the skills.

### 5a. GT Validation Functions Exist but Are Disconnected

**Current state:** The generator skill's `gt-validation.md` defines `validate_ground_truth_sql()` and `validate_with_retry()`. The evaluator template's Cell 3 loads benchmarks. These are not connected.

**Recommended wiring:**

1. **Cell 3a (structural pre-check):** After loading benchmarks, call `validate_ground_truth_sql()` for each benchmark's `expected_sql` via `spark.sql(sql + " LIMIT 1")`. For passing queries, compute `expected_result_hash`, `expected_result_sample`, and `expected_row_count`. Write enriched fields back to `golden-queries.yaml`.

2. **Remediation flow when structural validation fails (two-pass):**
   - **Pass 1 -- Auto-remediation:** For each failed benchmark, query `information_schema.columns` and `information_schema.tables` to get actual schema context. Send broken SQL + Spark error + schema to an LLM for correction. Validate the corrected SQL with `LIMIT 1`. If it passes, update `golden-queries.yaml` with `source: "auto_corrected_structural"`.
   - **Pass 2 -- Gate and queue:** If auto-remediation fails after N retries, exclude the benchmark. If remaining valid benchmarks < `min_benchmarks`, fail the job. Otherwise, emit `gt_remediation_queue.yaml` for the orchestrator to route to the generator for replacement questions.

3. **Arbiter auto-persistence:** When the arbiter issues `genie_correct` verdicts, automatically update `golden-queries.yaml` with the corrected SQL and set `source: "arbiter_correction"`. The skill spec requires this for 3+ corrections, but single corrections should also be persisted.

**Target skills:** Generator (document validation function handoff), Evaluator (wire Cell 3a), Orchestrator (consume `gt_remediation_queue.yaml`).

### 5b. Benchmark Coverage Minimum Not Enforced

**Current state:** The generator's `benchmark-patterns.md` recommends 20-25 benchmarks per space for large domains (9+ tables), but the initial generation only produced ~8 per space. No guard rail existed in the evaluator.

**Gaps in initial generation:**
- Missing categories: `threshold`, `prediction`, `detail`, edge cases
- Missing patterns: synonym variations, date range variations, ambiguous term tests
- Missing asset coverage: only 2 MV questions per space, no raw TABLE questions
- No `expected_facts`, `required_columns`, or `required_business_logic` fields populated

**Recommended enforcement:**
- Generator SKILL.md: Change coverage recommendations from "should" to "MUST". Add a hard constraint: "Generated benchmarks for large domains MUST meet the minimum question count (20) and category count (8)."
- Evaluator template: Add a pre-evaluation guard in Cell 3 that asserts `len(benchmarks) >= min_benchmarks` for full-scope evaluations. The `min_benchmarks` value should be configurable via a widget (default: 20).

**Target skills:** Generator (enforce coverage rules), Evaluator (add guard rail).

### 5c. Repeatability Variance as a Routing Diagnostic Signal

**Key insight:** When a question shows SIGNIFICANT or CRITICAL variance between two asset types (e.g., MV vs TVF), the root cause is almost always that the disambiguation metadata between those two assets is insufficient. This is a reusable diagnostic pattern.

**The fix mapping:**
1. Identify which two asset types the question oscillates between (from SQL variants)
2. Determine the preferred asset (per the routing priority: MV for aggregations, TVF for parameterized analysis)
3. Apply targeted disambiguation:
   - **Lever 1:** UC COMMENT on the preferred asset with explicit synonym phrases
   - **Lever 2:** MV measure comments with triggering phrases + "Do NOT use {alternative}"
   - **Lever 6 (last resort):** Negative routing instruction in Genie Instructions

**Example from this session:** `rp_001` ("total revenue last quarter") oscillated between `booking_analytics_metrics` (MV) and `get_revenue_summary()` (TVF). Fix: Added "ALWAYS use booking_analytics_metrics MEASURE(total_revenue) for total revenue questions. NEVER get_revenue_summary()." to UC COMMENT (Lever 1), MV measure comment (Lever 2), and Genie Instructions (Lever 6).

**Target skills:** Orchestrator (Phase 2 repeatability handling), Optimizer (auto-detect asset-type oscillation in failure clustering).

### 5d. Optimization Report Template Never Programmatically Used

**Current state:** The applier skill has a comprehensive 15-section report template at `assets/templates/optimization-report.md`. Neither the evaluator nor the applier automates populating it. During this session, the report was generated manually by the assistant from scattered MLflow data, config diffs, and conversation context.

**Recommendation:**
- Report generation should be a mandatory final step in the optimization loop (Phase 4 in the orchestrator).
- Implementation options: (a) a standalone script that reads MLflow experiment data + `golden-queries.yaml` + config files and fills the template, or (b) a final cell in `run_genie_evaluation.py` that generates the report section for that iteration.
- The orchestrator's Phase 4 pseudocode should trigger report generation as a hard constraint, not an optional step.

**Target skills:** Applier (mandate report generation), Orchestrator (Phase 4 hard constraint).

---

## Appendix: Error-to-Skill Mapping

Counts below reflect distinct error IDs touching each skill. Section 2 groups related errors for readability (e.g., #12/#17 are one combined "MV detection" issue; #7 is shared between Generator and Applier). Section 2 also includes unnumbered issues (GT validation wiring, lever-gate enforcement) that don't appear in this table.

| # | Error | Evaluator | Orchestrator | Generator | Applier | Optimizer |
|---|-------|:---------:|:------------:|:---------:|:-------:|:---------:|
| 1 | FileNotFoundError (DABs path) | X | | | | |
| 2 | Missing LoggedModel | X | X | | | |
| 3 | LoggedModel content quality | X | X | | | |
| 4 | Invalid data type | X | | | | |
| 5 | Run lifecycle conflict | X | | | | |
| 6 | InstructionsJudge API | X | | | | |
| 7 | Missing example_question_sqls | | | X | X | |
| 8 | API sorting errors | | | | X | |
| 9 | Premature Lever 6 | | X | | | |
| 10 | Job params vs widgets | X | | | | |
| 11 | Cell 9c column mismatch | X | | | | |
| 12 | ALTER TABLE on MV | | | | X | |
| 13 | Repeatability not visible | X | | | | |
| 14 | Cross-iteration repeatability | | X | | | |
| 15 | serialized_space format | | | | X | |
| 16 | Invalid UUID format | | | X | X | |
| 17 | EXPECT_TABLE_NOT_VIEW | | | | X | |
| 18 | Unresolved template vars | | | | X | |
| -- | Repeatability routing | | | | | X |
| **Total (error IDs)** | | **9** | **4** | **3** | **7** | **1** |

---

## Key Files to Reference

| File | What to Find |
|------|-------------|
| [Orchestrator SKILL.md](../../data_product_accelerator/skills/semantic-layer/05-genie-optimization-orchestrator/SKILL.md) | Hard constraints (lines 117-144), Common Mistakes (line 365), Phase 2 pseudocode (lines 202-245), lever-gate enforcement |
| [Evaluator SKILL.md](../../data_product_accelerator/skills/semantic-layer/genie-optimization-workers/02-genie-benchmark-evaluator/SKILL.md) | Hard constraints (lines 170-180), Common Mistakes (line 209), Critical Patterns (line 182), Cell 9c (line 240) |
| [Evaluator template](../../data_product_accelerator/skills/semantic-layer/genie-optimization-workers/02-genie-benchmark-evaluator/assets/templates/run_genie_evaluation.py) | The actual notebook template; bundle root (lines 10-16), Cell 7 data prep, Cell 9c repeatability |
| [Generator SKILL.md](../../data_product_accelerator/skills/semantic-layer/genie-optimization-workers/01-genie-benchmark-generator/SKILL.md) | Coverage requirements (line 119), Common Mistakes (line 127), ID format (line 87), gt-validation.md reference (line 80) |
| [Applier SKILL.md](../../data_product_accelerator/skills/semantic-layer/genie-optimization-workers/04-genie-optimization-applier/SKILL.md) | Common Mistakes (line 122), Lever 1 (line 68), Lever 2 (line 85), dual persistence (line 74), sort_genie_config reference (line 128) |
| [gt-validation.md](../../data_product_accelerator/skills/semantic-layer/genie-optimization-workers/01-genie-benchmark-generator/references/gt-validation.md) | `validate_ground_truth_sql()` (lines 15-50), `validate_with_retry()` (lines 53-76) -- defined but never wired into the evaluator |
| [control-levers.md](../../data_product_accelerator/skills/semantic-layer/genie-optimization-workers/04-genie-optimization-applier/references/control-levers.md) | Per-lever SQL/API commands, `sort_genie_config()` (lines 328-358), template variable resolution (lines 249-275), serialized_space format (lines 254, 319) |
| [Optimization report template](../../data_product_accelerator/skills/semantic-layer/genie-optimization-workers/04-genie-optimization-applier/assets/templates/optimization-report.md) | 15-section report template -- referenced by applier skill but never programmatically populated |
| [Optimizer SKILL.md](../../data_product_accelerator/skills/semantic-layer/genie-optimization-workers/03-genie-metadata-optimizer/SKILL.md) | Hard constraint (line 49), `cluster_failures()` routing, `target_lever` parameter |
