# Prompt: Improve genai-agents Skills from databricks-skills

## Objective

Analyze the external reference skills in `databricks-skills/model-serving/` and `databricks-skills/mlflow-evaluation/` and use them to improve the existing `skills/genai-agents/` skills. The external skills represent the latest official Databricks patterns (MLflow 3.6.0+, DBR 16.1+) and contain patterns, gotchas, and API details that our genai-agents skills are missing or have outdated.

**Goal:** Merge the new knowledge into existing genai-agents skills by updating reference files. Do NOT create new worker skills unless there is a clearly distinct domain not covered by any existing skill.

---

## Source Files to Analyze

### External: `databricks-skills/model-serving/`

Read ALL files in order:

| File | Key Content |
|------|-------------|
| `SKILL.md` | Overview, Quick Start, MCP tools, common issues |
| `3-genai-agents.md` | ResponsesAgent, LangGraph agent, ChatContext, streaming, testing, logging |
| `4-tools-integration.md` | UCFunctionToolkit, VectorSearchRetrieverTool, custom @tool, resource collection |
| `5-development-testing.md` | MCP workflow, iteration patterns |
| `6-logging-registration.md` | File-based logging, resources for auth, pip_requirements, pre-deployment validation |
| `7-deployment.md` | Job-based async deployment, agents.deploy(), update endpoint, DAB template |
| `8-querying-endpoints.md` | SDK, REST, MCP querying patterns |
| `9-package-requirements.md` | DBR versions, tested package combinations |

### External: `databricks-skills/mlflow-evaluation/`

Read ALL files in order:

| File | Key Content |
|------|-------------|
| `SKILL.md` | Workflow-based navigation, 5 user journeys |
| `references/GOTCHAS.md` | **CRITICAL: 19 common mistakes** - wrong API, data format, predict_fn, scorers |
| `references/CRITICAL-interfaces.md` | Exact API signatures, data schema, built-in scorers, judges API, production monitoring |
| `references/patterns-scorers.md` | 16 scorer patterns including multi-agent, trace-based, factory |
| `references/patterns-evaluation.md` | 12 evaluation patterns: local testing, A/B testing, CI/CD, regression detection |
| `references/patterns-datasets.md` | MLflow-managed datasets, trace-to-dataset conversion |
| `references/patterns-trace-analysis.md` | Trace debugging, span analysis, latency profiling |
| `references/patterns-context-optimization.md` | Token optimization, context management |
| `references/user-journeys.md` | End-to-end workflow guides |

### Target: `skills/genai-agents/`

These are the skills to improve:

| Skill | SKILL.md | References |
|-------|----------|------------|
| `00-genai-agent-implementation` | Orchestrator | references/architecture-overview.md, file-structure.md, implementation-checklist.md, anti-patterns.md |
| `01-responses-agent-patterns` | ResponsesAgent, streaming, OBO, tracing | references/streaming-patterns.md, obo-authentication.md, trace-context-patterns.md, common-mistakes.md, visualization-hints.md |
| `02-mlflow-genai-evaluation` | Evaluation, scorers, threshold checking | references/custom-scorer-patterns.md, built-in-judges.md, threshold-checking.md, evaluation-dataset-patterns.md; scripts/evaluation_helpers.py |
| `06-deployment-automation` | Deployment jobs, promotion, experiments | references/deployment-job-patterns.md, dataset-lineage.md, experiment-organization.md, model-promotion.md |
| `07-production-monitoring` | Registered scorers, trace archival, backfill | references/registered-scorers.md, trace-archival.md, metric-backfill.md, monitoring-dashboard-queries.md |
| `08-mlflow-genai-foundation` | Model signatures, tracing, evaluation basics, prompts | references/model-signatures.md, tracing-patterns.md, evaluation-basics.md, prompt-registry-basics.md |

---

## Gap Analysis: What the External Skills Have That We're Missing

### GAP 1: ResponsesAgent API Updates (HIGH)

**Source:** `model-serving/3-genai-agents.md`
**Target:** `01-responses-agent-patterns/SKILL.md` and `references/streaming-patterns.md`

Missing patterns:
- `ChatContext` for user/conversation info: `request.context.user_id`, `request.context.conversation_id`
- `to_chat_completions_input()` helper for converting ResponsesAgent input to LangGraph messages
- `output_to_responses_items_stream()` helper for converting LangGraph output to stream events
- Stream event type appears as `response.output_item.done` (verify against our `output_item.done`)
- Helper methods beyond `create_text_output_item`: `create_function_call_item(id, call_id, name, arguments)` and `create_function_call_output_item(call_id, output)`
- `mlflow.langchain.autolog()` at module level for automatic tracing (shown in LangGraph pattern)

**Action:** Update `01-responses-agent-patterns/SKILL.md` with ChatContext pattern. Update `references/streaming-patterns.md` with LangGraph streaming helpers. Add tool call output helpers to common patterns.

### GAP 2: Tools Integration (HIGH)

**Source:** `model-serving/4-tools-integration.md`
**Target:** `05-multi-agent-genie-orchestration/` OR new reference in `01-responses-agent-patterns/`

Missing patterns:
- `UCFunctionToolkit` for Unity Catalog SQL/Python functions as tools
- `VectorSearchRetrieverTool` for RAG
- Custom `@tool` decorator with `RunnableConfig` for user context
- `DatabricksFunction` and `DatabricksVectorSearchIndex` resource types
- Wildcard function selection (`catalog.schema.*`)
- Resource collection pattern (iterating tools to build resources list)
- Best practices: limit to 5-10 tools, clear docstrings, error handling

**Decision needed:** This is a distinct concern. Options:
1. Add as `01-responses-agent-patterns/references/tools-integration.md` (since tools are part of agent implementation)
2. Add as `00-genai-agent-implementation/references/tools-integration.md` (orchestrator-level concern)
3. Create new skill `XX-tools-integration/` (if scope warrants it)

**Recommendation:** Option 2 - add to orchestrator since it's a cross-cutting concern used during implementation.

### GAP 3: Model Logging and Registration (MEDIUM)

**Source:** `model-serving/6-logging-registration.md`
**Target:** `06-deployment-automation/references/` and `01-responses-agent-patterns/references/obo-authentication.md`

Missing patterns:
- **File-based logging**: `python_model="agent.py"` instead of `python_model=agent` (class instance)
- **Pre-deployment validation**: `mlflow.models.predict(model_uri, input_data, env_manager="uv")`
- **Resource collection from tools**: Iterate tools to auto-collect DatabricksFunction, VectorSearch resources
- **Exact pip_requirements**: Tested versions (`mlflow==3.6.0`, `langgraph==0.3.4`, `databricks-langchain`)
- **Manual registration**: Separate `mlflow.register_model()` step
- **`code_paths` parameter**: For additional Python dependencies

**Action:** Update `06-deployment-automation/references/deployment-job-patterns.md` with file-based logging and pre-deployment validation. Update `01-responses-agent-patterns/references/obo-authentication.md` to include `DatabricksFunction` and `DatabricksVectorSearchIndex` resource types.

### GAP 4: Evaluation GOTCHAS (CRITICAL)

**Source:** `mlflow-evaluation/references/GOTCHAS.md`
**Target:** `02-mlflow-genai-evaluation/SKILL.md` and references

**19 common mistakes that our evaluation skill doesn't cover:**

1. Wrong API: `mlflow.evaluate()` vs `mlflow.genai.evaluate()`
2. Wrong imports: MLflow 2 vs MLflow 3 GenAI
3. Wrong data format: flat vs nested `{"inputs": {...}}`
4. Wrong predict_fn: receives `**kwargs` not dict
5. Wrong scorer: missing `@scorer` decorator
6. Wrong Feedback return types (can't return dict or tuple)
7. Wrong Guidelines: missing required `name` parameter
8. Wrong trace search syntax (need `attributes.` prefix, single quotes, backticks for dotted names)
9. Wrong Correctness: needs `expectations.expected_facts` or `expected_response`
10. Wrong RetrievalGroundedness: needs RETRIEVER span type
11. Wrong custom scorer imports (must be inline for production monitoring)
12. Wrong type hints in scorers (break serialization)
13. Wrong dataset creation (needs Spark session)
14. Wrong multiple Feedbacks (need unique names)
15. Wrong Guidelines context (use `request`/`response`, not custom variables)
16. Wrong production monitoring (must `register()` then `start()`)
17. Wrong custom judge model format (`databricks:/endpoint` not `databricks:endpoint`)
18. Wrong aggregation values (only min/max/mean/median/variance/p90)
19. Using model serving endpoints for development (import agent locally instead)

**Action:** Create `02-mlflow-genai-evaluation/references/gotchas.md` with all 19 patterns. This is the HIGHEST priority gap - these mistakes cause immediate failures.

### GAP 5: Exact API Interfaces (HIGH)

**Source:** `mlflow-evaluation/references/CRITICAL-interfaces.md`
**Target:** `02-mlflow-genai-evaluation/references/` and `08-mlflow-genai-foundation/references/`

Missing exact signatures:
- `mlflow.genai.evaluate()` parameters and return type
- Data schema: `inputs` (required), `outputs` (optional), `expectations` (optional) with exact field names
- All 6 built-in scorer classes with exact imports: `Guidelines`, `ExpectationsGuidelines`, `Correctness`, `RelevanceToQuery`, `RetrievalGroundedness`, `Safety`
- `Feedback` object: `name`, `value`, `rationale` fields and valid value types
- `Scorer` class-based pattern with Pydantic
- `make_judge()` with template variables `{{ inputs }}`, `{{ outputs }}`, `{{ trace }}`
- Judges API: `meets_guidelines()`, `is_correct()`, `is_safe()`, `is_context_relevant()`, `is_grounded()`
- Trace API: `trace.search_spans(span_type=SpanType.CHAT_MODEL)`, `SpanType` constants
- Production monitoring lifecycle: `register()` -> `start()` -> `update()` -> `stop()` -> `delete_scorer()`
- `ScorerSamplingConfig(sample_rate=0.5)`
- Evaluation Datasets: `mlflow.genai.datasets.create_dataset()`, `merge_records()`

**Action:** Update `02-mlflow-genai-evaluation/references/built-in-judges.md` with exact interfaces. Update `references/custom-scorer-patterns.md` with class-based scorer, make_judge, and Feedback patterns.

### GAP 6: Advanced Scorer Patterns (MEDIUM)

**Source:** `mlflow-evaluation/references/patterns-scorers.md`
**Target:** `02-mlflow-genai-evaluation/references/custom-scorer-patterns.md`

Missing patterns (16 patterns in source, our skill has basics):
- Pattern 7: Custom scorer wrapping LLM judge with `meets_guidelines()` and custom context
- Pattern 8: Trace-based scorer using `trace.search_spans(span_type=SpanType.CHAT_MODEL)`
- Pattern 9: Class-based scorer extending `Scorer` with Pydantic fields
- Pattern 10: Conditional scoring based on input type
- Pattern 11: Scorer aggregations (mean, min, max, median, p90)
- Pattern 12: `make_judge()` with multi-level outcomes
- Pattern 13: Per-stage/component accuracy for multi-agent pipelines
- Pattern 14: Tool selection accuracy scorer
- Pattern 15: Stage latency scorer producing multiple metrics
- Pattern 16: Component accuracy factory

**Action:** Significantly expand `02-mlflow-genai-evaluation/references/custom-scorer-patterns.md`.

### GAP 7: Evaluation Workflows (MEDIUM)

**Source:** `mlflow-evaluation/references/patterns-evaluation.md`
**Target:** `02-mlflow-genai-evaluation/references/evaluation-dataset-patterns.md` and `references/threshold-checking.md`

Missing patterns:
- Pattern 0: Local agent testing (import directly, NOT via endpoint)
- Pattern 2: Pre-computed outputs evaluation (no predict_fn needed)
- Pattern 4: Named runs for comparison
- Pattern 5: Analyzing evaluation results (per-row assessments)
- Pattern 6: Comparing two evaluation runs
- Pattern 7: Regression detection between versions
- Pattern 8: Iterative improvement loop with quality gates
- Pattern 9: Evaluation from production traces
- Pattern 10: A/B testing two prompts
- Pattern 12: CI/CD quality gates with `sys.exit(1)`

**Action:** Expand `02-mlflow-genai-evaluation/references/threshold-checking.md` with comparison and regression patterns. Expand `references/evaluation-dataset-patterns.md` with trace-to-dataset and MLflow-managed dataset patterns.

### GAP 8: Production Monitoring Updates (MEDIUM)

**Source:** `mlflow-evaluation/references/CRITICAL-interfaces.md` (Production Monitoring section)
**Target:** `07-production-monitoring/references/registered-scorers.md`

Missing patterns:
- Exact lifecycle: `register(name=...)` -> `start(sampling_config=...)` -> `update(...)` -> `stop()` -> `delete_scorer(name=...)`
- `ScorerSamplingConfig(sample_rate=0.5)` exact usage
- `list_scorers()`, `get_scorer(name=...)` management functions
- GOTCHA: Must call `start()` after `register()` - registered is NOT running

**Action:** Update `07-production-monitoring/references/registered-scorers.md` with exact lifecycle API.

### GAP 9: Deployment Patterns (LOW)

**Source:** `model-serving/7-deployment.md`
**Target:** `06-deployment-automation/references/deployment-job-patterns.md`

Missing patterns:
- `databricks.agents.deploy(model_name, version, tags={...})` simple deployment
- Job-based async deployment for long-running deploys
- `mlflow.deployments.get_deploy_client("databricks")` for endpoint management
- Update endpoint with new model version and traffic routing
- DAB YAML template for deployment jobs

**Action:** Review and update `06-deployment-automation/references/deployment-job-patterns.md`.

### GAP 10: Package Version Updates (LOW)

**Source:** `model-serving/9-package-requirements.md`
**Target:** All skills referencing pip_requirements

Currently our skills reference `mlflow>=3.0.0`. External skills use tested versions:
- `mlflow==3.6.0`
- `langgraph==0.3.4`
- `databricks-langchain` (not `langchain>=0.3.0`)
- `databricks-agents`
- `pydantic`
- Memory: `databricks-langchain[memory]`

**Action:** Update pip_requirements in relevant reference files to use current tested versions. Note: pin exact versions in examples, use `>=` only when intentional.

---

## Implementation Priority

### Phase 1: Critical (Do First)
1. **GAP 4: Evaluation GOTCHAS** -> Create `02-mlflow-genai-evaluation/references/gotchas.md`
2. **GAP 5: Exact API Interfaces** -> Update `02-mlflow-genai-evaluation/references/built-in-judges.md`
3. **GAP 1: ResponsesAgent API Updates** -> Update `01-responses-agent-patterns/` references

### Phase 2: High Priority
4. **GAP 2: Tools Integration** -> Add `00-genai-agent-implementation/references/tools-integration.md`
5. **GAP 6: Advanced Scorer Patterns** -> Expand `02-mlflow-genai-evaluation/references/custom-scorer-patterns.md`
6. **GAP 3: Model Logging Updates** -> Update `06-deployment-automation/references/`

### Phase 3: Medium Priority
7. **GAP 7: Evaluation Workflows** -> Expand evaluation references
8. **GAP 8: Production Monitoring Updates** -> Update `07-production-monitoring/references/registered-scorers.md`

### Phase 4: Low Priority
9. **GAP 9: Deployment Patterns** -> Update `06-deployment-automation/references/`
10. **GAP 10: Package Versions** -> Update across all relevant files

---

## Rules for Implementation

1. **Merge into existing files** - Do NOT create new worker skills unless clearly warranted
2. **Preserve existing content** - Expand, don't replace. The existing patterns are production-tested
3. **Resolve conflicts carefully** - If external skill contradicts existing skill, investigate which is correct:
   - External skills may be more current (MLflow 3.6.0 vs 3.0.0)
   - Existing skills may have production learnings the external skills lack (e.g., OBO auth)
   - When in doubt, keep BOTH patterns with notes on when each applies
4. **Maintain progressive disclosure** - SKILL.md stays lean (~200 lines max), details go in references/
5. **Update checklists** - Add new validation items to existing checklists in SKILL.md files
6. **Cross-reference** - If content spans multiple skills, put it in one place and link from others
7. **Verify API correctness** - The external skills may have more current APIs. When adding new imports or function signatures, use the external skill as the source of truth for API shape

---

## Verification After Implementation

After making changes, verify:

- [ ] All SKILL.md files are under ~300 lines (progressive disclosure)
- [ ] No duplicate content between skills (single source of truth)
- [ ] All code examples use `mlflow.genai.evaluate()` not `mlflow.evaluate()`
- [ ] All data examples use nested `{"inputs": {...}}` format
- [ ] All scorer examples include `@scorer` decorator
- [ ] ResponsesAgent examples use `input` key not `messages`
- [ ] pip_requirements use tested version numbers
- [ ] Resource declarations include all tool types (GenieSpace, SQLWarehouse, Function, VectorSearch)
- [ ] Production monitoring shows full lifecycle (register -> start -> update -> stop)
- [ ] Skill navigator routing tables are still accurate
