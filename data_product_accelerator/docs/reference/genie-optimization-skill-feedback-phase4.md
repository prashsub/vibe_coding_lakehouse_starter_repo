# Genie Optimization Skill Feedback — Phase 4: Runtime Errors in Evaluation Pipeline

Self-improvement reflection following the [self-improvement skill](../data_product_accelerator/skills/admin/self-improvement/SKILL.md) framework. This document captures 4 concrete runtime errors encountered during the Feb 21 optimization session that each required multiple fix-deploy-retry cycles to resolve.

**Relationship to prior phases:**
- [Phase 1](genie-optimization-skill-feedback.md) — 9 gaps getting the evaluation job to run (CLI profile, DABs params, experiment path, template vars, multi-statement SQL, mlflow.genai.evaluate, traces, datasets, judge registration)
- [Phase 2](genie-optimization-skill-feedback-phase2.md) — 6 gaps in the optimization workflow (bypassed optimizer, GEPA non-functional, half-dual-persistence, lever priority, undocumented API error, no multi-lever strategy)
- [Phase 3](genie-optimization-skill-feedback-phase3.md) — 6 gaps in the closed-loop data flow (ASI never read, arbiter not actioned, LoggedModel skipped, lever ordering, GET API misinterpreted, per-row data inaccessible)
- **Phase 4 (this document)** — 4 runtime errors that occurred during the Feb 21 re-execution after Phase 1-3 skill updates, each revealing a gap between what the skill templates contain and what MLflow/Genie APIs actually accept

**Session:** 2026-02-21
**Space:** Wanderbricks Unified Monitor (`01f10e84df6715e39ea60890ef55ae0f`)
**Errors Found:** 4 (numbered 22-25 to continue from Phase 3's 16-21)
**Fix Attempts per Error:** 2-4 (cascading fix pattern — each fix exposed the next constraint)

---

## Reflection (After Debugging 4 Cascading Errors)

> I spent significant time debugging. Let me document:
> - **What went wrong:** Four distinct runtime errors crashed the evaluation job, each requiring 2-4 fix-deploy-retry cycles. The errors cascaded — fixing Error 22 (custom template variables) exposed Error 23 (missing required variables), and fixing Error 23 exposed Error 24 (predict_fn signature). Error 25 (sorted arrays) occurred during the Genie Space PATCH deployment.
> - **What led me astray:** The skill templates — specifically `JUDGE_PROMPTS` in `judge-definitions.md` (lines 818-853) and `run_genie_evaluation.py` template (lines 525-559) — use `{{question}}`, `{{expected_sql}}`, `{{genie_sql}}` as template variables in `make_judge()` instructions. These look correct because they follow Jinja2/Mustache conventions and are documented in the skill as the prescribed pattern. But `make_judge()` has a strict allowlist of only 5 variables: `inputs`, `outputs`, `trace`, `expectations`, `conversation`. This constraint is not documented anywhere in the skill tree.
> - **Breakthrough insight:** The skill templates are the only code the agent sees before generating the evaluation notebook. When the templates use `{{question}}` and the reference docs say "use `{{double_brace}}` syntax," the agent has no signal that these specific variable names will be rejected. The constraint lives in MLflow's source code, not in the skill documentation. **Every template variable in every `make_judge()` instruction must be validated against MLflow's allowlist before the skill ships.**
> - **What would have prevented all 4 errors:** (1) Fix the JUDGE_PROMPTS in both the template file and the reference docs to use only `{{ inputs }}`, `{{ outputs }}`, `{{ expectations }}`. (2) Document the `make_judge()` variable allowlist as a hard constraint. (3) Document that `predict_fn` receives unpacked keyword arguments from the `inputs` dict. (4) Document that Genie PATCH requires sorted arrays.

---

## Error 22: `make_judge()` Rejects Custom Template Variables

**Priority:** P0 (crashes the evaluation job before any benchmark runs)

**Error message:**
```
MlflowException: Instructions template contains unsupported variables:
{'question', 'expected_sql', 'genie_sql'}. Only the following variables
are allowed: inputs, outputs, trace, expectations, conversation
```

**Traceback location:** `run_genie_evaluation.py`, Cell 5 (judge creation), during `make_judge(name="schema_accuracy", instructions=...)` call.

**What went wrong:** The `JUDGE_PROMPTS` dict in the evaluator template uses custom template variables:

```python
# FROM: judge-definitions.md lines 822-823 AND run_genie_evaluation.py template lines 528-529
"schema_accuracy": (
    "You are a SQL schema expert evaluating SQL for a Databricks Genie Space.\n"
    "Determine if the GENERATED SQL references the correct tables, columns, and joins.\n\n"
    "Question: {{question}}\nExpected SQL: {{expected_sql}}\nGenerated SQL: {{genie_sql}}\n\n"
    'Respond with JSON: {"score": "yes" or "no", "rationale": "explanation"}'
),
```

All 5 judge prompts (`schema_accuracy`, `logical_accuracy`, `semantic_equivalence`, `completeness`, `arbiter`) use `{{question}}`, `{{expected_sql}}`, and `{{genie_sql}}` (plus `{{gt_sql}}` and `{{comparison}}` in the arbiter). MLflow's `make_judge()` validates all `{{variable}}` tokens against a strict allowlist and raises `MlflowException` for any not in `{inputs, outputs, trace, expectations, conversation}`.

**Root cause:** The skill's reference file `judge-definitions.md` (line 815) says:

> **IMPORTANT:** All templates use `{{double_brace}}` syntax (`{{variable}}`), NOT Python `{single_brace}` format strings. The MLflow Prompt Registry requires this for its `.format()` method.

This is correct for the Prompt Registry — you can register prompts with any variable names. But it's **incorrect for `make_judge()`**, which has the strict allowlist. The skill conflates two different template systems:

| System | Variable Names | Validation |
|--------|---------------|------------|
| MLflow Prompt Registry (`register_prompt()`) | Any `{{variable}}` | No validation — any name accepted |
| MLflow `make_judge(instructions=...)` | Only `{{ inputs }}`, `{{ outputs }}`, `{{ trace }}`, `{{ expectations }}`, `{{ conversation }}` | Strict — raises `MlflowException` on unknown variables |

The templates pass through both systems: first registered to the Prompt Registry (where `{{question}}` is fine), then loaded and passed to `make_judge()` (where `{{question}}` crashes).

**How I fixed it:** Rewrote all `JUDGE_PROMPTS` to use only the allowed variables:

```python
# AFTER FIX: run_genie_evaluation.py lines 525-564 (current state)
"schema_accuracy": (
    "You are a SQL schema expert evaluating SQL for a Databricks Genie Space.\n"
    "Determine if the GENERATED SQL references the correct tables, columns, and joins.\n\n"
    "User question: {{ inputs }}\n"
    "Generated SQL: {{ outputs }}\n"
    "Expected SQL: {{ expectations }}\n\n"
    "Respond with yes if the generated SQL references the correct tables, columns, "
    "and joins for the question, or no if it does not."
),
```

Also added a `_sanitize_prompt_for_make_judge()` helper (lines 622-645) that strips custom variables and ensures at least one allowed variable is present.

**What assumption was incorrect:** That `{{variable}}` syntax is universally compatible across MLflow's prompt ecosystem. The Prompt Registry and `make_judge()` have different validation rules for the same template syntax.

**What would have prevented this:**

1. **Fix the templates:** Replace all `{{question}}`, `{{expected_sql}}`, `{{genie_sql}}` with `{{ inputs }}`, `{{ outputs }}`, `{{ expectations }}` in:
   - `02-genie-benchmark-evaluator/references/judge-definitions.md` lines 818-853
   - `02-genie-benchmark-evaluator/assets/templates/run_genie_evaluation.py` lines 525-559

2. **Add a hard constraint** to the evaluator SKILL.md:
   ```
   9. make_judge() instructions MUST only use these template variables:
      {{ inputs }}, {{ outputs }}, {{ trace }}, {{ expectations }}, {{ conversation }}.
      Custom variables like {{question}}, {{genie_sql}} will raise MlflowException.
      The Prompt Registry accepts any variable names, but make_judge() does not.
   ```

3. **Add to the `02-mlflow-genai-evaluation` skill's Common Mistakes:**
   ```
   | Custom template variables in make_judge() | MlflowException: unsupported variables |
   | Use only {{ inputs }}, {{ outputs }}, {{ expectations }} |
   ```

4. **Add a template validation step** to `register_judge_prompts()` that checks all variables against the allowlist before registration.

**Files to update:**
- `02-genie-benchmark-evaluator/references/judge-definitions.md` — Fix JUDGE_PROMPTS section (lines 818-853) to use only allowed variables
- `02-genie-benchmark-evaluator/assets/templates/run_genie_evaluation.py` — Fix JUDGE_PROMPTS dict to use only allowed variables
- `02-genie-benchmark-evaluator/SKILL.md` — Add hard constraint #9: make_judge() variable allowlist
- `genai-agents/02-mlflow-genai-evaluation/SKILL.md` — Add make_judge() template variable constraint to Critical Patterns section

---

## Error 23: `make_judge()` Requires At Least One Template Variable

**Priority:** P0 (crashes the evaluation job — exposed after fixing Error 22)

**Error message:**
```
MlflowException: Instructions template must contain at least one variable
(e.g., {{ inputs }}, {{ outputs }}, ...)
```

**What went wrong:** After fixing Error 22 by removing the custom variables (`{{question}}`, `{{genie_sql}}`, etc.), the resulting prompts were plain text with zero template variables. This exposed a second constraint: `make_judge()` requires at least one of the allowed variables to be present.

The intermediate (broken) state looked like:

```python
"schema_accuracy": (
    "You are a SQL schema expert evaluating SQL for a Databricks Genie Space.\n"
    "Determine if the GENERATED SQL references the correct tables, columns, and joins.\n\n"
    "Respond with yes if the generated SQL references correct tables, columns, "
    "and joins for the question, or no if it does not."
),
# ^ No {{variable}} at all — make_judge() rejects this too
```

**How I fixed it:** Added `{{ inputs }}`, `{{ outputs }}`, and `{{ expectations }}` explicitly to every prompt:

```python
"User question: {{ inputs }}\n"
"Generated SQL: {{ outputs }}\n"
"Expected SQL: {{ expectations }}\n\n"
```

Also added a guard in `_sanitize_prompt_for_make_judge()` (lines 638-644) that appends the required variables if none are present after stripping:

```python
remaining_vars = set(re.findall(r'\{\{\s*(\w+)\s*\}\}', cleaned))
if not remaining_vars & allowed:
    cleaned += (
        "\n\nUser question: {{ inputs }}\n"
        "Generated SQL: {{ outputs }}\n"
        "Expected SQL: {{ expectations }}"
    )
```

**Root cause:** Error 22 and Error 23 are two halves of the same constraint:
1. Error 22: `make_judge()` rejects variables NOT in the allowlist
2. Error 23: `make_judge()` also rejects prompts with NO variables at all

A naive fix for Error 22 (strip custom variables) immediately triggers Error 23. The correct fix is: **replace custom variables with allowed ones** (not strip them).

**What assumption was incorrect:** That removing the custom variables was sufficient. The constraint is bidirectional: prompts must contain ONLY allowed variables AND must contain AT LEAST ONE.

**What would have prevented this:**

1. **Document both constraints together** — never document one without the other:
   ```
   make_judge() instructions template rules:
   - MUST contain at least one of: {{ inputs }}, {{ outputs }}, {{ trace }}, {{ expectations }}, {{ conversation }}
   - MUST NOT contain any other {{ variable }} names
   - Plain text without any variables is rejected
   ```

2. **Include the `_sanitize_prompt_for_make_judge()` helper** in the evaluator template as a safety net for prompts loaded from the Prompt Registry (which may contain custom variables from older versions).

**Files to update:**
- Same files as Error 22 — the fix is the same: use allowed variables in templates, add sanitizer helper
- `02-genie-benchmark-evaluator/references/judge-definitions.md` — Add "Template Variable Rules" section before the JUDGE_PROMPTS section

---

## Error 24: `predict_fn` Receives Unpacked Keyword Arguments, Not a Dict

**Priority:** P0 (crashes the evaluation job — exposed after fixing Errors 22-23)

**Error message:**
```
MlflowException: The `inputs` column must be a dictionary with the parameter
names of the `predict_fn` as keys.
```

**What went wrong:** The evaluation data has:

```python
# run_genie_evaluation.py lines 940-952
eval_records.append({
    "inputs": {
        "question": b["question"],
        "space_id": space_id,
        "catalog": catalog,
        "gold_schema": gold_schema,
        "expected_sql": b.get("expected_sql", ""),
    },
    "expectations": {
        "expected_response": b.get("expected_sql", ""),
        "expected_asset": b.get("expected_asset", "TABLE"),
    },
})
```

And the predict function was:

```python
# BEFORE FIX
@mlflow.trace
def genie_predict_fn(inputs: dict) -> dict:
    question = inputs.get("question", "")
    expected_sql = inputs.get("expected_sql", "")
    ...
```

`mlflow.genai.evaluate()` **unpacks** the `inputs` dict as keyword arguments when calling `predict_fn`. So instead of calling `genie_predict_fn({"question": "...", "space_id": "..."})`, it calls `genie_predict_fn(question="...", space_id="...", catalog="...", gold_schema="...", expected_sql="...")`. The function signature must match the keys in the `inputs` dict.

**How I fixed it:**

```python
# AFTER FIX: run_genie_evaluation.py line 458
@mlflow.trace
def genie_predict_fn(question: str, expected_sql: str = "", **kwargs) -> dict:
    ...
```

The `**kwargs` catches the additional keys (`space_id`, `catalog`, `gold_schema`) that the function doesn't need directly (they're captured from the outer scope via closure).

**Root cause:** The skill's reference code in `judge-definitions.md` (lines 386-426) shows:

```python
def genie_predict_fn(inputs: dict) -> dict:
    question = inputs["question"]
    ...
```

This is the `dict` signature pattern, which works when calling the function directly but NOT when `mlflow.genai.evaluate()` unpacks the inputs. The reference code contradicts how `mlflow.genai.evaluate()` actually invokes the predict function.

The `02-mlflow-genai-evaluation` skill (line 65) documents:
> Data format: `{"inputs": {"query": "..."}}` (nested structure required)

But it doesn't document that the `inputs` dict's keys become the predict function's keyword arguments.

**What assumption was incorrect:** That `predict_fn(inputs: dict)` would receive the entire `inputs` dict as a single argument. In reality, `mlflow.genai.evaluate()` performs `predict_fn(**inputs_dict)` — destructuring the dict into keyword arguments.

**What would have prevented this:**

1. **Fix the predict function template** in both:
   - `02-genie-benchmark-evaluator/references/judge-definitions.md` — Change `genie_predict_fn(inputs: dict)` to `genie_predict_fn(question: str, expected_sql: str = "", **kwargs)`
   - `02-genie-benchmark-evaluator/assets/templates/run_genie_evaluation.py` — Same fix

2. **Add to the `02-mlflow-genai-evaluation` skill:**
   ```
   CRITICAL: predict_fn signature must match inputs dict keys.
   
   mlflow.genai.evaluate() UNPACKS the inputs dict as keyword arguments:
     inputs = {"question": "...", "space_id": "..."}
     → predict_fn(question="...", space_id="...")
   
   ❌ def predict_fn(inputs: dict):       # WRONG — receives keywords, not dict
   ✅ def predict_fn(question: str, **kwargs):  # CORRECT — matches input keys
   ```

3. **Add to the evaluator SKILL.md Common Mistakes table:**
   ```
   | predict_fn(inputs: dict) signature | MlflowException: inputs column must be a dictionary |
   | Use keyword args matching inputs keys: predict_fn(question: str, **kwargs) |
   ```

**Files to update:**
- `02-genie-benchmark-evaluator/references/judge-definitions.md` — Fix `genie_predict_fn` signature
- `02-genie-benchmark-evaluator/assets/templates/run_genie_evaluation.py` — Fix `genie_predict_fn` signature (already fixed in deployed version)
- `02-genie-benchmark-evaluator/SKILL.md` — Add to Common Mistakes and Hard Constraints
- `genai-agents/02-mlflow-genai-evaluation/SKILL.md` — Add predict_fn keyword argument documentation

---

## Error 25: Genie PATCH API Requires Arrays Sorted by Identifier

**Priority:** P1 (crashes Genie Space deployment — separate from evaluation pipeline)

**Error message:**
```
Error: Invalid export proto: data_sources.tables must be sorted by identifier
```

**What went wrong:** When PATCHing the Genie Space configuration with updated `example_question_sqls`, `sql_functions`, and instructions, the API rejected the payload because the `data_sources.tables` array was not sorted alphabetically by the `identifier` field.

The PATCH payload contained:

```json
{
  "serialized_space": "{\"data_sources\": {\"tables\": [{\"identifier\": \"catalog.schema.fact_booking\"}, {\"identifier\": \"catalog.schema.dim_customer\"}, ...]}, ...}"
}
```

The Genie API requires `data_sources.tables`, `data_sources.metric_views`, `instructions.sql_functions`, and `config.example_question_sqls` to be sorted by their respective identifier/id fields.

**How I fixed it:** Added pre-PATCH sorting:

```python
import json

config = json.loads(serialized_space)

if "data_sources" in config:
    if "tables" in config["data_sources"]:
        config["data_sources"]["tables"].sort(key=lambda t: t.get("identifier", ""))
    if "metric_views" in config["data_sources"]:
        config["data_sources"]["metric_views"].sort(key=lambda m: m.get("identifier", ""))
if "instructions" in config:
    if "sql_functions" in config["instructions"]:
        config["instructions"]["sql_functions"].sort(key=lambda f: f.get("identifier", ""))

serialized_space = json.dumps(config)
```

**Root cause:** The `04-genie-space-export-import-api` skill documents array format requirements (section "Array Format Requirements") and ID generation rules, but does NOT document the sorting requirement. The `sort_genie_config()` function in the applier's `control-levers.md` exists but was not referenced in the export-import API skill, and the evaluator/optimizer workflow that generates the PATCH payload doesn't call it.

The export-import API skill's troubleshooting section (Common Errors table, lines 218-225) lists 5 errors but omits this one — despite it being the first error any agent will encounter when building PATCH payloads from scratch.

**What assumption was incorrect:** That REST API PATCH payloads don't have ordering constraints on array fields. Most REST APIs are order-agnostic for arrays. The Genie Space API's protobuf-based serialization requires deterministic ordering.

**What would have prevented this:**

1. **Add to the export-import API skill's Common Errors table:**
   ```
   | `Invalid export proto: data_sources.tables must be sorted by identifier` |
   | Arrays not sorted | Sort all arrays by identifier/id before PATCH |
   ```

2. **Add a "CRITICAL: Array Sorting" section** to the export-import API SKILL.md:
   ```
   CRITICAL: Before any PATCH request, sort these arrays:
   - data_sources.tables → sort by "identifier"
   - data_sources.metric_views → sort by "identifier"
   - instructions.sql_functions → sort by "identifier"
   - config.example_question_sqls → sort by "id"
   - instructions.text_instructions → sort by "id"
   
   The Genie API uses protobuf serialization which requires deterministic ordering.
   ```

3. **Include a `sort_genie_config()` helper** directly in the export-import API skill (not just in the applier's control-levers.md):
   ```python
   def sort_genie_config(config: dict) -> dict:
       """Sort all arrays required by the Genie PATCH API."""
       if "data_sources" in config:
           for key in ["tables", "metric_views"]:
               if key in config["data_sources"]:
                   config["data_sources"][key].sort(
                       key=lambda x: x.get("identifier", ""))
       if "instructions" in config:
           for key in ["sql_functions", "text_instructions", "join_specs"]:
               if key in config["instructions"]:
                   config["instructions"][key].sort(
                       key=lambda x: x.get("identifier", x.get("id", "")))
       if "config" in config:
           if "example_question_sqls" in config["config"]:
               config["config"]["example_question_sqls"].sort(
                   key=lambda x: x.get("id", ""))
       return config
   ```

**Files to update:**
- `04-genie-space-export-import-api/SKILL.md` — Add "Array Sorting" section; add to Common Errors table
- `04-genie-space-export-import-api/references/troubleshooting.md` — Add sorted arrays requirement with helper function
- `04-genie-space-export-import-api/references/workflow-patterns.md` — Add `sort_genie_config()` to the deployment workflow
- `04-genie-optimization-applier/SKILL.md` — Add to Common Mistakes: "Unsorted arrays in PATCH payload | `Invalid export proto` | Call `sort_genie_config()` before every PATCH"

---

## Cross-Error Analysis: The Cascading Fix Pattern

Errors 22, 23, and 24 form a **cascade** — each fix exposed the next error:

```
Error 22: make_judge() rejects {{question}}, {{genie_sql}}, {{expected_sql}}
    ↓ Fix: Strip custom variables
Error 23: make_judge() requires at least one variable — plain text rejected
    ↓ Fix: Add {{ inputs }}, {{ outputs }}, {{ expectations }}
Error 24: predict_fn(inputs: dict) doesn't match unpacked keyword arguments
    ↓ Fix: Change signature to predict_fn(question: str, **kwargs)
    ✓ Evaluation finally runs
```

Error 25 is independent (Genie PATCH API, not MLflow evaluation) but follows the same pattern: **an undocumented API constraint that is not surfaced until runtime.**

The cascade pattern means:
1. Each fix attempt requires a full redeploy cycle (`databricks bundle deploy` + `databricks bundle run` = ~5 minutes)
2. The agent discovers constraints sequentially, not all at once
3. Total debugging time: ~25 minutes for 4 errors that could have been prevented by 4 lines of documentation

---

## Self-Improvement Analysis: Which Existing Skills to Update

Following the [self-improvement skill](../data_product_accelerator/skills/admin/self-improvement/SKILL.md) Step 2 (Search Existing Skills):

**Skills searched:** All 59 skills in `data_product_accelerator/skills/` were listed. Keyword searches performed for: `make_judge`, `template variable`, `predict_fn`, `sorted`, `PATCH`, `genie api`.

**Decision matrix (all 4 errors → update existing skills):**

| Error | Existing Skill to Update | Update Type |
|-------|------------------------|-------------|
| 22 (custom variables) | `02-genie-benchmark-evaluator` + `02-mlflow-genai-evaluation` | Fix templates + add hard constraint |
| 23 (required variables) | `02-genie-benchmark-evaluator` + `02-mlflow-genai-evaluation` | Add both halves of constraint together |
| 24 (predict_fn signature) | `02-genie-benchmark-evaluator` + `02-mlflow-genai-evaluation` | Fix template + add documentation |
| 25 (sorted arrays) | `04-genie-space-export-import-api` + `04-genie-optimization-applier` | Add sorting requirement + helper |

**No new skills needed.** All 4 errors are sub-cases of existing skills. Each error maps to a specific section that should be updated.

---

## Summary of Recommended Changes

### `02-genie-benchmark-evaluator/references/judge-definitions.md`

1. **JUDGE_PROMPTS section (lines 818-853):** Replace ALL instances of `{{question}}`, `{{expected_sql}}`, `{{genie_sql}}`, `{{gt_sql}}`, `{{comparison}}` with `{{ inputs }}`, `{{ outputs }}`, `{{ expectations }}`
2. **Add "Template Variable Rules" section** before JUDGE_PROMPTS:
   ```
   make_judge() instructions rules:
   - MUST contain at least one of: {{ inputs }}, {{ outputs }}, {{ trace }}, {{ expectations }}, {{ conversation }}
   - MUST NOT contain any other {{ variable }} names
   - Plain text without any variables is rejected
   - The Prompt Registry accepts any variable names, but make_judge() does NOT
   ```
3. **Fix `genie_predict_fn` signature** (line ~387): Change `def genie_predict_fn(inputs: dict)` to `def genie_predict_fn(question: str, expected_sql: str = "", **kwargs)`

### `02-genie-benchmark-evaluator/assets/templates/run_genie_evaluation.py`

1. **Fix JUDGE_PROMPTS** (lines 525-559): Same variable replacement as judge-definitions.md
2. **Fix genie_predict_fn** signature: Already fixed in deployed version, ensure template matches

### `02-genie-benchmark-evaluator/SKILL.md`

1. **Add Hard Constraint #9:** `make_judge()` instructions MUST only use allowed template variables
2. **Add to Common Mistakes table:**
   - `Custom template variables in make_judge()` → `MlflowException: unsupported variables` → `Use only {{ inputs }}, {{ outputs }}, {{ expectations }}`
   - `Plain text instructions without variables` → `MlflowException: must contain at least one variable` → `Include at least one of {{ inputs }}, {{ outputs }}, {{ expectations }}`
   - `predict_fn(inputs: dict) signature` → `MlflowException: inputs column must be a dictionary` → `Use keyword args: predict_fn(question: str, **kwargs)`

### `genai-agents/02-mlflow-genai-evaluation/SKILL.md`

1. **Add "make_judge() Template Variable Constraints" section** after the existing `@scorer` pattern:
   ```
   CRITICAL: make_judge() only allows 5 template variables:
   {{ inputs }}, {{ outputs }}, {{ trace }}, {{ expectations }}, {{ conversation }}
   Custom variables like {{question}} are rejected. Plain text is also rejected.
   ```
2. **Add predict_fn signature documentation:**
   ```
   CRITICAL: mlflow.genai.evaluate() unpacks inputs as keyword arguments:
   ❌ def predict_fn(inputs: dict)
   ✅ def predict_fn(query: str, **kwargs)
   ```

### `04-genie-space-export-import-api/SKILL.md`

1. **Add "Array Sorting Requirement" section** after "Array Format Requirements":
   ```
   CRITICAL: All arrays in serialized_space must be sorted before PATCH:
   - data_sources.tables → sort by "identifier"
   - data_sources.metric_views → sort by "identifier"
   - instructions.sql_functions → sort by "identifier"
   - config.example_question_sqls → sort by "id"
   ```
2. **Add to Common Errors table:** `Invalid export proto: must be sorted by identifier`

### `04-genie-space-export-import-api/references/troubleshooting.md`

1. **Add `sort_genie_config()` helper function** with sorting for all arrays

---

## Generalized Principles

> **Key Insight 1:** When a skill template uses a third-party API (MLflow, Genie), every constraint of that API must be documented in the skill — even constraints that seem "obvious" to API designers. Agents have no prior experience with undocumented constraints and will reproduce template code verbatim.

> **Key Insight 2:** Cascading errors cost disproportionate debugging time because each fix requires a full redeploy cycle. Skills should document ALL constraints for a given API call together, not force agents to discover them sequentially.

> **Key Insight 3:** Two different MLflow systems (`register_prompt()` and `make_judge()`) use the same `{{ }}` template syntax but have different validation rules. Skills must explicitly document where systems diverge, especially when the same syntax has different semantics.

> **Key Insight 4:** API constraints that exist in source code but not in documentation will be discovered at runtime. Skills should include a "Known Constraints" section for each API call, sourced from testing, not from official docs alone.
