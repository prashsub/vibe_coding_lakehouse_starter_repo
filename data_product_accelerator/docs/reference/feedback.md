# Feedback: Evaluator Template Bugs — UC Dataset Data Path & LLM Judge Resilience

**Date:** 2026-02-23
**Reporter:** Genie Space Optimization Loop (automated run)
**Severity:** Critical (renders evaluation meaningless)
**Affected file:** `assets/templates/run_genie_evaluation.py`
**Affected SKILL:** `02-genie-benchmark-evaluator/SKILL.md`

---

## Summary

Two bugs in the evaluator template caused a baseline evaluation to produce **zero usable judge scores**: `result_correctness` was 0/25 due to missing ground truth SQL, and all four LLM judges (`schema_accuracy`, `logical_accuracy`, `semantic_equivalence`, `completeness`) returned "unknown" due to unretried transient failures. Only `syntax_validity` and `asset_routing` (both code-based, not LLM-based) produced meaningful results.

---

## Bug 1: UC Dataset `inputs` Dict Missing Critical Fields

### What Happened

When `dataset_mode=uc` and the UC evaluation dataset is successfully created, `mlflow.genai.evaluate()` receives the UC dataset object instead of the DataFrame. The UC dataset's `inputs` dict contains only `{question_id, question, space_id}`, missing `expected_sql`, `catalog`, and `gold_schema`. The predict function receives `expected_sql=""` and cannot compute the comparison dict. Every benchmark gets `comparison.error = "Missing SQL for comparison"`, and `result_correctness` scores 0%.

### Root Cause

There are **two** independent issues that combine to cause this:

**Issue A — Inconsistent `inputs` schemas between the two data paths:**

The UC dataset path (Cell 5, lines 693–705) builds `inputs` with only 3 fields:

```python
# Cell 5: UC dataset path — MISSING expected_sql, catalog, gold_schema
"inputs": {
    "question_id": b.get("id", ""),
    "question": b["question"],
    "space_id": space_id,
}
```

While the DataFrame path (Cell 7, lines 1369–1381) correctly includes all 6 fields:

```python
# Cell 7: DataFrame path — correct
"inputs": {
    "question_id": b.get("id", ""),
    "question": b["question"],
    "space_id": space_id,
    "catalog": catalog,
    "gold_schema": gold_schema,
    "expected_sql": b.get("expected_sql", ""),
}
```

**Issue B — UC dataset object passed to `data` parameter instead of DataFrame:**

Cell 8 (line 1433) prefers the UC dataset object over the DataFrame:

```python
"data": eval_dataset if eval_dataset is not None else eval_data,
```

This contradicts the SKILL.md's own documented constraint at line 355:

> | Passing UC dataset name string to `data` parameter | `MlflowException` | **Always convert to DataFrame before `mlflow.genai.evaluate()`; UC dataset is still created for Datasets tab** |

And the Template Verification table at line 401:

> | `data` param must be DataFrame | Cell 7 | `eval_data` always assigned as `pd.DataFrame` |

When UC creation succeeds on the Databricks cluster (which it does — the API works there even though it fails locally with different `mlflow` versions), the incomplete UC dataset overrides the correct DataFrame.

### Evidence

Query of the UC table `vibe_coding_workshop_catalog.prashanth_s_wanderbricks_gold.genie_benchmarks_revenue_property`:

```
inputs: {"question_id": "rev_019", "question": "Payment analysis for the last quarter", "space_id": "01f10e84df3b14d993c30773abde7f44"}
```

No `expected_sql`. No `catalog`. No `gold_schema`.

MLflow trace for every row:

```
request.expected_sql: ''
comparison.error: "Missing SQL for comparison"
result_correctness/value: "no"
```

### Fix (Applied to `src/wanderbricks_semantic/run_genie_evaluation.py`)

**Fix A:** Add missing fields to UC dataset `inputs`:

```python
"inputs": {
    "question_id": b.get("id", ""),
    "question": b["question"],
    "space_id": space_id,
    "expected_sql": b.get("expected_sql", ""),
    "catalog": catalog,
    "gold_schema": gold_schema,
}
```

**Fix B:** Always use the DataFrame for `data`, keep UC dataset for Datasets tab only:

```python
"data": eval_data,  # ALWAYS DataFrame — UC dataset populates Datasets tab separately
```

**Fix C (defense-in-depth):** Predict function fallback lookup when `expected_sql` is empty:

```python
_eff_sql = expected_sql
if not _eff_sql:
    _qid = kwargs.get("question_id", "")
    if _qid:
        _match = next((b for b in benchmarks if b.get("id") == _qid), None)
        if _match:
            _eff_sql = _match.get("expected_sql", "")
```

### Recommendation for Template

1. **Keep UC dataset and DataFrame `inputs` schemas identical** — extract a shared helper function:

    ```python
    def _build_inputs(b):
        return {
            "question_id": b.get("id", ""),
            "question": b["question"],
            "space_id": space_id,
            "expected_sql": b.get("expected_sql", ""),
            "catalog": catalog,
            "gold_schema": gold_schema,
        }
    ```

    Use `_build_inputs(b)` in both the UC dataset records (Cell 5) and eval_records (Cell 7).

2. **Always pass DataFrame to `data`** — enforce the constraint already documented in SKILL.md lines 355 and 401. Change Cell 8 line 1433 to:

    ```python
    "data": eval_data,
    ```

3. **Add a template verification test** — a Cell 7.5 assertion that catches this class of bug before evaluation runs:

    ```python
    _sample = eval_records[0]["inputs"]
    assert "expected_sql" in _sample and _sample["expected_sql"], \
        "expected_sql missing from inputs — result_correctness will score 0%"
    assert "catalog" in _sample, "catalog missing from inputs — SQL templates won't resolve"
    ```

---

## Bug 2: `_call_llm_for_scoring()` Has No Retry Logic

### What Happened

All four LLM judges returned `value="unknown"` with `rationale="LLM call failed: Expecting value: line 1 column 1 (char 0)"` for most benchmarks. The `schema_accuracy`, `logical_accuracy`, `semantic_equivalence`, and `completeness` scores were effectively meaningless.

### Root Cause

`_call_llm_for_scoring()` (line 1019–1026) makes a single attempt with no retry:

```python
def _call_llm_for_scoring(prompt: str) -> dict:
    response = w.serving_endpoints.query(
        name=LLM_ENDPOINT,
        messages=[ChatMessage(role=ChatMessageRole.USER, content=prompt)],
        temperature=0,
    )
    return json.loads(response.choices[0].message.content)
```

When the serving endpoint returns an empty response (transient rate-limiting, cold-start latency, or platform hiccup), `json.loads("")` raises `JSONDecodeError`, the scorer catches it, and returns `value="unknown"`. There is:

- No retry with backoff
- No empty-response validation before JSON parsing
- No markdown code fence stripping (some LLMs wrap JSON in ` ```json ... ``` `)

With 25 benchmarks × 4 LLM judges = 100 LLM calls, even a 10% transient failure rate produces ~10 "unknown" verdicts, and since the 8-judge evaluation runs sequentially per benchmark, a burst of endpoint issues can cascade across multiple judges for the same row.

### Fix (Applied to `src/wanderbricks_semantic/run_genie_evaluation.py`)

```python
def _call_llm_for_scoring(prompt: str, max_retries: int = 3) -> dict:
    import time as _time
    last_err = None
    for attempt in range(max_retries):
        try:
            response = w.serving_endpoints.query(
                name=LLM_ENDPOINT,
                messages=[ChatMessage(role=ChatMessageRole.USER, content=prompt)],
                temperature=0,
            )
            content = response.choices[0].message.content
            if not content or not content.strip():
                raise ValueError(f"Empty LLM response on attempt {attempt + 1}")
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1] if "\n" in content else content[3:]
                content = content.rsplit("```", 1)[0]
            return json.loads(content)
        except Exception as e:
            last_err = e
            if attempt < max_retries - 1:
                _time.sleep(2 ** attempt)
    raise last_err
```

### Recommendation for Template

1. **Add retry with exponential backoff** — 3 retries with 1s/2s/4s backoff covers most transient failures.
2. **Validate response content before JSON parsing** — raise explicitly on empty content so the retry loop catches it.
3. **Strip markdown code fences** — some model versions wrap JSON responses in ` ```json ... ``` ` blocks.
4. **Document the retry behavior in SKILL.md** — add to the Hard Constraints section:

    > `_call_llm_for_scoring()` MUST retry transient failures with exponential backoff (default: 3 attempts). Empty or non-JSON responses MUST be retried, not silently degraded to "unknown".

5. **Add to Common Mistakes table:**

    | Mistake | Consequence | Fix |
    |---------|-------------|-----|
    | `_call_llm_for_scoring()` with no retry | Transient empty responses cascade to "unknown" verdicts across all LLM judges | Add 3-retry exponential backoff with empty-response validation |

---

## Meta: SKILL.md Documents the Constraint But Template Violates It

The most concerning aspect of Bug 1 is that the SKILL.md *already knows about this failure mode*:

- **Line 348**: "Missing `expected_sql` in eval_records `inputs`" → Fix: "Add expected_sql to inputs dict"
- **Line 355**: "Passing UC dataset name string to `data` parameter" → Fix: "Always convert to DataFrame"
- **Line 401**: "`data` param must be DataFrame" (Template Verification table)

Despite these three separate warnings, the template code at Cell 5 (lines 693–705) and Cell 8 (line 1433) violates all of them. This suggests the Common Mistakes table was written *after* encountering the DataFrame-path bug, but the UC-dataset-path code was added later without cross-checking against the documented constraints.

### Recommendation

Add a **Template Self-Consistency Check** section to the SKILL.md that explicitly maps each Common Mistake to the template line(s) that must enforce it, with a machine-verifiable assertion. This would catch future regressions where documentation and code diverge.

---

## Bug 3: LoggedModel Not Tagged on Evaluation Runs

### What Happened

The user reported "I don't see LoggedModels for the latest evaluation runs." Investigation showed that while `mlflow.set_active_model(model_id=...)` correctly links traces (trace metadata has `mlflow.modelId`) and metrics (model has per-run metrics), the evaluation **run itself has no model-related tags**. This means the MLflow UI's Evaluation Runs tab may not show the LoggedModel association.

Additionally, the job YAML hardcodes `model_id: "m-7d3b61ec0b164702813db392f39e7f6b"` (the iter0 model). After applying Lever 1+2 metadata changes, a new LoggedModel should have been created to snapshot the updated configuration, but the same iter0 model was reused for all subsequent evaluations.

### Root Cause

Two issues:

1. **Hardcoded `model_id` in job YAML**: The `base_parameters.model_id` is set once and never updated between iterations. After applying levers, the Genie Space config changes but no new LoggedModel captures these changes.

2. **`set_active_model()` called outside run context**: Cell 2 calls `mlflow.set_active_model(model_id=model_id)` before `with mlflow.start_run()` in Cell 8. While this correctly links traces via metadata, the run itself doesn't get a `mlflow.loggedModelId` tag.

### Fix Applied

Changed `model_id` in job YAML from the hardcoded value to `""` (empty string). This triggers Cell 0b's auto-creation logic, which:
1. Fetches the LIVE Genie Space config (including lever changes)
2. Snapshots UC columns, tags, and routines
3. Creates a new LoggedModel with a content-hash name
4. Links the evaluation to the fresh model

### Recommendation for Template

1. **Never hardcode `model_id` in job YAML** — either pass it dynamically from the orchestrator or leave it empty for auto-creation.
2. **Call `set_active_model()` INSIDE the `with mlflow.start_run()` block** — move the call from Cell 2 into Cell 8 to ensure the run is tagged.
3. **Add to Common Mistakes table:**

    | Mistake | Consequence | Fix |
    |---------|-------------|-----|
    | Hardcoded `model_id` in job YAML across iterations | All eval runs link to stale iter0 model, lever changes not captured | Leave `model_id` empty for auto-creation, or update dynamically per iteration |

---

## Bug 4: LLM Judge `unknown` Path Missing ASI Metadata

### What Happened

Hard constraint #13 states: "ALL judges MUST return structured ASI metadata via `Feedback(metadata=build_asi_metadata(...))` on failure verdicts." However, when LLM judges fail after exhausting retries, the `except` handler returns `value="unknown"` with **no ASI metadata**:

```python
# Lines 1158, 1198, 1238, 1278 — all 4 LLM judges + arbiter
except Exception as e:
    return Feedback(name="schema_accuracy", value="unknown",
                    rationale=f"LLM call failed: {e}", source=LLM_SOURCE)
    # ^^^ NO metadata=build_asi_metadata(...)
```

This means the optimizer receives no structured guidance for 5 assessments in the latest run. An `unknown` verdict IS a failure (the system couldn't judge), so ASI should be emitted.

### Fix Applied

Added `metadata=build_asi_metadata(failure_type="other", severity="info", confidence=0.0, counterfactual_fix="LLM judge unavailable — retry or check endpoint")` to all 5 `unknown` return paths (4 LLM judges + arbiter).

### Recommendation for Template

1. **Add ASI to ALL failure/unknown paths** — audit every `Feedback()` return that isn't `value="yes"` or `value="skipped"` and ensure it has `metadata=build_asi_metadata(...)`.
2. **Add to Common Mistakes table:**

    | Mistake | Consequence | Fix |
    |---------|-------------|-----|
    | `unknown` verdict with no ASI metadata | Optimizer receives no structured guidance for failed LLM judges | Add `build_asi_metadata()` to all `except` handlers in LLM judge scorers |

---

## Validation: Fixes Confirmed Working

After deploying all three fixes (UC inputs, LLM retry, DataFrame-only data path), the re-run showed dramatic improvement:

| Judge | Before (broken) | After (fixed) | Delta |
|---|---|---|---|
| syntax_validity | 96% | 96% | — |
| schema_accuracy | **0%** | **40%** | +40% |
| logical_accuracy | **28%** | **43%** | +15% |
| semantic_equivalence | **16%** | **37.5%** | +21.5% |
| completeness | **4%** | **40%** | +36% |
| asset_routing | 88% | 92% | +4% |
| result_correctness | **0%** | **64%** | +64% |

ASI structured metadata is now present on **75 assessments** (up from ~0). LLM judges reduced from dozens of "unknown" verdicts to just **5**.

Example ASI from LLM judge (schema_accuracy on rev_001):
```json
{
  "failure_type": "wrong_column",
  "blame_set": ["check_in_date"],
  "wrong_clause": "WHERE booking_status = 'confirmed' GROUP BY ALL ORDER BY quarter_start DESC LIMIT 1",
  "counterfactual_fix": "Review table/column references in Genie metadata",
  "severity": "major",
  "confidence": 0.85
}
```

---

## Affected Runs

- **Pre-fix baseline (MLflow Run ID):** `7f8e958fbf2a47f6ae2899474df727f6`
- **Post-fix validation (MLflow Run ID):** `164697c46bcd4d72983d3e625a91f19a`
- **Experiment:** `/Users/prashanth.subrahmanyam@databricks.com/genie-optimization/revenue_property`
- **UC Dataset:** `vibe_coding_workshop_catalog.prashanth_s_wanderbricks_gold.genie_benchmarks_revenue_property`
