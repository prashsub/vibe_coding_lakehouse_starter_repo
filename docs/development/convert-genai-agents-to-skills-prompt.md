# Prompt: Convert GenAI Agent Rules to Agent Skills (Orchestrator + Dependencies)

> **Purpose**: Use this prompt in a new Cursor chat session to convert all GenAI agent cursor rules, context prompts, and implementation documentation into a structured set of Agent Skills under `.cursor/skills/genai-agents/`.

---

## Task

Convert the following source materials into a complete set of **Agent Skills** organized as an orchestrator with dependencies, placed in `.cursor/skills/genai-agents/`. Follow the `cursor-rule-to-skill` skill methodology at `.cursor/skills/cursor-rule-to-skill/SKILL.md`.

**IMPORTANT:** Do NOT miss any functionality. Every pattern, anti-pattern, code example, checklist, and production learning from every source file MUST be preserved in the output skills. This is a comprehensive migration, not a summary.

---

## Source Materials (Read ALL before starting)

### Cursor Rules (`.cursor/rules/genai-agents/`)
1. **`30-mlflow-genai-evaluation.mdc`** (~1000 lines) — LLM judges, custom scorers, `_extract_response_text()` helper, `_call_llm_for_scoring()` helper, Databricks SDK for scorers (NOT langchain_databricks), metric aliases for backward compat, 4-6 guidelines best practice, foundation model endpoints, threshold checking, run naming conventions, evaluation dataset patterns
2. **`31-lakebase-memory-patterns.mdc`** (~870 lines) — CheckpointSaver for short-term memory, DatabricksStore for long-term memory, graceful degradation, thread_id resolution, user namespace isolation, LangChain memory tools, setup scripts, lazy loading
3. **`32-prompt-registry-patterns.mdc`** (~675 lines) — Unity Catalog table storage, MLflow artifact versioning, AB testing (champion/challenger), lazy loading in agents, prompt update/promotion workflow, SQL injection prevention
4. **`33-mlflow-tracing-agent-patterns.mdc`** (~1665 lines) — ResponsesAgent (MANDATORY), streaming with `predict_stream()`, MLflow tracing (decorators + manual spans), trace context (tags vs metadata, standard fields), OBO authentication with context detection, Automatic Auth Passthrough (SystemAuthPolicy + UserAuthPolicy), resource declaration (DatabricksGenieSpace, DatabricksSQLWarehouse), multi-agent LangGraph orchestration, Genie tool integration (NO LLM fallback), visualization hints
5. **`34-deployment-automation-patterns.mdc`** (~1280 lines) — Deployment job trigger on MODEL_VERSION_CREATED, dataset linking with `mlflow.log_input()`, evaluation-then-promote workflow, multi-agent Genie config, parallel domain queries, intent classification, MLflow experiment organization (3 separate experiments), run naming conventions, standard tags
6. **`34-genie-space-optimization.mdc`** (~615 lines) — Genie accuracy/repeatability testing, 6 control levers, dual persistence (API + repository), API update pattern with array sorting, rate limiting, asset routing (TVF vs MV), optimization workflow, cross-domain benchmarks
7. **`35-production-monitoring-patterns.mdc`** (~940 lines) — Registered scorers with sampling, on-demand `assess()`, scorer lifecycle (register/start/stop/delete), immutable pattern, trace archival to Unity Catalog, metric backfill, monitoring dashboard queries, production vs dev evaluation, unified scorer definitions, custom heuristic scorers

### Parent MLflow GenAI Rule (`.cursor/rules/ml/`)
8. **`28-mlflow-genai-patterns.mdc`** (~853 lines) — MLflow 3.0 GenAI patterns: ResponsesAgent as MANDATORY (critical section), NO LLM fallback for Genie/tool calls (critical section), model signatures for AI Playground, ResponsesAgent implementation + logging + helper methods, tracing patterns (autolog, decorators, manual spans), evaluation patterns (built-in scorers, custom `@scorer`, production monitoring with `assess()`), prompt registry (log/load/alias), agent logging patterns (ResponsesAgent vs legacy ChatAgent), common mistakes, validation checklists

### Architecture Design Prompt (`context/prompts/`)
9. **`13-agent-architecture-design-prompt.md`** (~700 lines) — Hybrid architecture pattern (Genie + custom orchestrator), orchestrator state definition, intent classification prompt template, response synthesis prompt template, Genie worker agent pattern, utility tools (web search, dashboard linker, alert trigger, runbook RAG), MLflow 3.0 integration (tracing, prompt registry, evaluation with custom judges, agent logging with ChatAgent), Lakebase memory management (short-term + long-term), deployment configuration (model serving endpoint, Databricks App), 8-phase implementation checklist

### Comprehensive Implementation Prompt (`docs/development/`)
10. **`comprehensive-agent-implementation-prompt.md`** (~1321 lines) — Complete production agent template covering: ResponsesAgent class template with streaming, Genie Conversation API pattern (start_conversation_and_wait + get_message_attachment_query_result), OBO authentication with context detection, Lakebase memory (CheckpointSaver + DatabricksStore), cross-domain parallel queries, LLM synthesis, model logging with AuthPolicy (SystemAuthPolicy + UserAuthPolicy), resource declaration, evaluation framework (custom scorers with `_extract_response_text()`), deployment with `databricks.agents.deploy()`, visualization hints, configuration management (AgentSettings dataclass), anti-patterns, file structure, summary checklist

### Index & Summaries (`.cursor/rules/genai-agents/`)
11. **`00-INDEX.md`** (~315 lines) — Complete rule index, pattern coverage matrix, quick start guide, anti-patterns summary, production metrics, learning path

---

## Output Structure

Create the following skill structure under `.cursor/skills/genai-agents/`:

```
.cursor/skills/genai-agents/
├── genai-agent-implementation/                    # ORCHESTRATOR SKILL
│   ├── SKILL.md                                   # Main orchestrator
│   ├── references/
│   │   ├── architecture-overview.md               # From source 9 + 10 architecture sections
│   │   ├── file-structure.md                      # Standard project file structure
│   │   ├── implementation-checklist.md            # Consolidated from all checklists
│   │   └── anti-patterns.md                       # All anti-patterns consolidated
│   ├── assets/
│   │   └── templates/
│   │       ├── agent-class-template.py            # ResponsesAgent template from source 10
│   │       └── agent-settings-template.py         # AgentSettings dataclass from source 10
│   └── scripts/
│       └── validate_agent_config.py               # Pre-deployment validation
│
├── responses-agent-patterns/                      # DEPENDENCY: ResponsesAgent + Streaming + Tracing
│   ├── SKILL.md
│   ├── references/
│   │   ├── streaming-patterns.md                  # predict_stream() patterns from source 4
│   │   ├── trace-context-patterns.md              # Tags vs metadata, standard fields from source 4
│   │   ├── obo-authentication.md                  # OBO + context detection + auth passthrough from source 4
│   │   └── common-mistakes.md                     # All ResponsesAgent mistakes from sources 4, 8
│   └── scripts/
│       └── validate_responses_agent.py            # Check class structure
│
├── mlflow-genai-evaluation/                       # DEPENDENCY: Evaluation Framework
│   ├── SKILL.md
│   ├── references/
│   │   ├── custom-scorer-patterns.md              # @scorer decorator, _extract_response_text, Databricks SDK
│   │   ├── built-in-judges.md                     # Relevance, Safety, Guidelines
│   │   ├── threshold-checking.md                  # Metric aliases, check_thresholds()
│   │   └── evaluation-dataset-patterns.md         # Dataset linking, UC table schema
│   └── scripts/
│       └── evaluation_helpers.py                  # _extract_response_text, _call_llm_for_scoring
│
├── lakebase-memory-patterns/                      # DEPENDENCY: Memory Management
│   ├── SKILL.md
│   ├── references/
│   │   ├── short-term-memory.md                   # CheckpointSaver, thread_id, LangGraph integration
│   │   ├── long-term-memory.md                    # DatabricksStore, semantic search, memory tools
│   │   └── graceful-degradation.md                # Fallback patterns
│   └── scripts/
│       └── setup_lakebase.py                      # Memory table setup
│
├── prompt-registry-patterns/                      # DEPENDENCY: Prompt Management
│   ├── SKILL.md
│   ├── references/
│   │   ├── storage-patterns.md                    # UC table + MLflow dual storage
│   │   ├── ab-testing.md                          # Champion/challenger, variant routing
│   │   └── loading-patterns.md                    # Lazy loading, alias loading, fallback defaults
│   └── scripts/
│       └── register_prompts.py                    # Prompt registration script
│
├── multi-agent-genie-orchestration/               # DEPENDENCY: Multi-Agent + Genie
│   ├── SKILL.md
│   ├── references/
│   │   ├── genie-conversation-api.md              # Full Genie query flow from source 10
│   │   ├── parallel-domain-queries.md             # ThreadPoolExecutor pattern from source 5
│   │   ├── intent-classification.md               # Domain routing, keyword matching from source 5
│   │   ├── cross-domain-synthesis.md              # LLM synthesis from source 10
│   │   └── no-llm-fallback.md                     # CRITICAL anti-pattern from sources 4, 8
│   └── assets/
│       └── templates/
│           └── genie-spaces-config.py             # Centralized Genie Space config
│
├── deployment-automation/                         # DEPENDENCY: Deployment + CI/CD
│   ├── SKILL.md
│   ├── references/
│   │   ├── deployment-job-patterns.md             # Trigger config, evaluation-then-promote
│   │   ├── dataset-lineage.md                     # mlflow.log_input(), from_spark()
│   │   ├── experiment-organization.md             # 3 experiments, run naming, standard tags
│   │   └── model-promotion.md                     # Alias management, champion/production
│   └── assets/
│       └── templates/
│           └── deployment-job.yml                 # Asset Bundle job template
│
├── production-monitoring/                         # DEPENDENCY: Production Ops
│   ├── SKILL.md
│   ├── references/
│   │   ├── registered-scorers.md                  # Register/start/stop, sampling, immutable pattern
│   │   ├── trace-archival.md                      # Unity Catalog Delta tables, archival config
│   │   ├── metric-backfill.md                     # Historical analysis, BackfillScorerConfig
│   │   └── monitoring-dashboard-queries.md        # SQL queries for dashboards
│   └── scripts/
│       └── register_production_scorers.py         # Scorer registration script
│
├── genie-space-optimization/                      # DEPENDENCY: Genie Quality
│   ├── SKILL.md
│   ├── references/
│   │   ├── accuracy-repeatability-testing.md      # Testing methodology, scoring
│   │   ├── six-control-levers.md                  # Priority-ordered optimization levers
│   │   ├── api-update-patterns.md                 # PATCH API, array sorting, dual persistence
│   │   └── asset-routing.md                       # TVF vs MV decision matrix
│   └── scripts/
│       └── test_genie_repeatability.py            # Repeatability testing script
│
└── mlflow-genai-foundation/                       # DEPENDENCY: Core MLflow GenAI (from rule 28)
    ├── SKILL.md
    ├── references/
    │   ├── model-signatures.md                    # Why signatures matter, AI Playground compat
    │   ├── tracing-patterns.md                    # autolog, @mlflow.trace, manual spans, span types
    │   ├── evaluation-basics.md                   # Built-in scorers, @scorer decorator, assess()
    │   └── prompt-registry-basics.md              # log_prompt, load_prompt, aliases
    └── scripts/
        └── validate_agent_logging.py              # Check no manual signature, set_model called
```

---

## Conversion Instructions

### Phase 1: Read the cursor-rule-to-skill Methodology

Read `.cursor/skills/cursor-rule-to-skill/SKILL.md` first. Follow its conversion workflow:
1. Parse frontmatter and body from each `.mdc` file
2. Generate valid skill names (lowercase, hyphens, max 64 chars)
3. Generate descriptions (max 1024 chars, WHAT + WHEN)
4. Transform body content for skill format
5. Use progressive disclosure (references/, scripts/, assets/)
6. Validate against AgentSkills.io spec

### Phase 2: Read ALL Source Materials

Read every source file listed above in full. Do not skip any. Map each pattern to its target skill.

### Phase 3: Create the Orchestrator Skill First

**`genai-agent-implementation/SKILL.md`** is the orchestrator. It must:

1. **Frontmatter:**
   ```yaml
   ---
   name: genai-agent-implementation
   description: >
     End-to-end orchestrator for implementing production-grade Databricks GenAI agents
     using MLflow 3.0 ResponsesAgent, Genie Spaces, Lakebase memory, and comprehensive
     evaluation. Orchestrates mandatory dependencies on genai-agents skills
     (responses-agent-patterns, mlflow-genai-evaluation, lakebase-memory-patterns,
     prompt-registry-patterns, multi-agent-genie-orchestration, deployment-automation,
     production-monitoring, genie-space-optimization, mlflow-genai-foundation).
     Use when implementing AI agents on Databricks, creating multi-agent systems with
     Genie Spaces, setting up agent evaluation pipelines, deploying agents to Model Serving,
     or troubleshooting agent implementation errors.
   license: Apache-2.0
   metadata:
     author: databricks-sa
     version: "1.0.0"
     domain: genai-agents
     dependencies:
       - responses-agent-patterns
       - mlflow-genai-evaluation
       - lakebase-memory-patterns
       - prompt-registry-patterns
       - multi-agent-genie-orchestration
       - deployment-automation
       - production-monitoring
       - genie-space-optimization
       - mlflow-genai-foundation
   ---
   ```

2. **Body structure:**
   - High-level architecture diagram (from sources 9, 10)
   - Technology stack table
   - "When to Use" section
   - Phase-by-phase implementation workflow:
     - Phase 1: Foundation (ResponsesAgent + Tracing) → read `responses-agent-patterns`
     - Phase 2: Data Access (Genie Spaces) → read `multi-agent-genie-orchestration`
     - Phase 3: Memory (Lakebase) → read `lakebase-memory-patterns`
     - Phase 4: Prompt Management → read `prompt-registry-patterns`
     - Phase 5: Evaluation → read `mlflow-genai-evaluation`
     - Phase 6: Deployment → read `deployment-automation`
     - Phase 7: Production Monitoring → read `production-monitoring`
     - Phase 8: Genie Optimization → read `genie-space-optimization`
   - Summary validation checklist (consolidated from all sources)
   - References section (all official documentation links)

3. **Each phase must specify:**
   - Which dependency skill to load
   - What artifacts are produced
   - What to validate before proceeding

### Phase 4: Create Each Dependency Skill

For each dependency skill:

1. **SKILL.md** (under 500 lines):
   - Frontmatter with name, description, license, metadata
   - "When to Use" trigger conditions
   - Core patterns (most critical, commonly needed)
   - Quick reference tables
   - Validation checklist
   - References to sub-files for detailed patterns

2. **references/** (progressive disclosure):
   - Move detailed code examples, long explanations, production learnings
   - Each reference file covers ONE specific pattern area
   - Include complete code examples (don't truncate)
   - Preserve ALL anti-patterns with before/after examples

3. **scripts/** (executable helpers):
   - Extract reusable Python functions from code examples
   - Include `_extract_response_text()`, `_call_llm_for_scoring()`, etc.
   - Setup scripts (lakebase, prompts, scorers)
   - Validation scripts

4. **assets/templates/** (copy-paste starting points):
   - Agent class template
   - Job YAML templates
   - Config file templates

### Phase 5: Content Mapping (CRITICAL - Do Not Miss Anything)

Every piece of content from every source file must appear in exactly one skill. Use this mapping:

| Source Content | Target Skill | Target File |
|---|---|---|
| ResponsesAgent class, predict(), predict_stream() | responses-agent-patterns | SKILL.md + references/streaming-patterns.md |
| Model signatures, AI Playground compatibility | mlflow-genai-foundation | references/model-signatures.md |
| NO manual signature parameter | responses-agent-patterns | SKILL.md (critical warning) |
| Streaming delta events, done events | responses-agent-patterns | references/streaming-patterns.md |
| MLflow tracing (autolog, @mlflow.trace, manual spans) | mlflow-genai-foundation | references/tracing-patterns.md |
| Trace context (tags vs metadata, standard fields) | responses-agent-patterns | references/trace-context-patterns.md |
| Safe trace update helper | responses-agent-patterns | references/trace-context-patterns.md |
| OBO authentication + context detection | responses-agent-patterns | references/obo-authentication.md |
| Automatic Auth Passthrough (SystemAuthPolicy) | responses-agent-patterns | references/obo-authentication.md |
| Resource declaration (GenieSpace, SQLWarehouse) | responses-agent-patterns | references/obo-authentication.md |
| AuthPolicy (system + user) | responses-agent-patterns | references/obo-authentication.md |
| NO LLM fallback for data queries | multi-agent-genie-orchestration | references/no-llm-fallback.md |
| LLM fallback decision table | multi-agent-genie-orchestration | references/no-llm-fallback.md |
| Error message best practices | multi-agent-genie-orchestration | references/no-llm-fallback.md |
| Genie Conversation API (start_conversation_and_wait) | multi-agent-genie-orchestration | references/genie-conversation-api.md |
| get_message_attachment_query_result | multi-agent-genie-orchestration | references/genie-conversation-api.md |
| _format_query_results helper | multi-agent-genie-orchestration | references/genie-conversation-api.md |
| Parallel domain queries (ThreadPoolExecutor) | multi-agent-genie-orchestration | references/parallel-domain-queries.md |
| Intent classification (LLM + keyword) | multi-agent-genie-orchestration | references/intent-classification.md |
| Cross-domain synthesis (LLM) | multi-agent-genie-orchestration | references/cross-domain-synthesis.md |
| LangGraph multi-agent workflow | multi-agent-genie-orchestration | SKILL.md |
| Genie Space configuration registry | multi-agent-genie-orchestration | assets/templates/genie-spaces-config.py |
| Custom scorers with @scorer | mlflow-genai-evaluation | SKILL.md |
| _extract_response_text() helper | mlflow-genai-evaluation | scripts/evaluation_helpers.py |
| _call_llm_for_scoring() helper | mlflow-genai-evaluation | scripts/evaluation_helpers.py |
| Databricks SDK for scorer LLM calls | mlflow-genai-evaluation | references/custom-scorer-patterns.md |
| Built-in judges (Relevance, Safety, Guidelines) | mlflow-genai-evaluation | references/built-in-judges.md |
| Guidelines best practices (4-6, not 8+) | mlflow-genai-evaluation | references/built-in-judges.md |
| Metric aliases (relevance/mean vs relevance_to_query/mean) | mlflow-genai-evaluation | references/threshold-checking.md |
| check_thresholds() function | mlflow-genai-evaluation | scripts/evaluation_helpers.py |
| Evaluation run naming convention | mlflow-genai-evaluation | SKILL.md |
| Foundation model endpoints (cost-effective) | mlflow-genai-evaluation | references/custom-scorer-patterns.md |
| Evaluation dataset UC table schema | mlflow-genai-evaluation | references/evaluation-dataset-patterns.md |
| Dataset linking with mlflow.log_input() | deployment-automation | references/dataset-lineage.md |
| CheckpointSaver for short-term memory | lakebase-memory-patterns | SKILL.md + references/short-term-memory.md |
| DatabricksStore for long-term memory | lakebase-memory-patterns | references/long-term-memory.md |
| Thread ID resolution (custom_inputs > conversation_id > new) | lakebase-memory-patterns | references/short-term-memory.md |
| Graceful degradation (memory optional) | lakebase-memory-patterns | references/graceful-degradation.md |
| LangChain memory tools (get/save/delete) | lakebase-memory-patterns | references/long-term-memory.md |
| Setup Lakebase script | lakebase-memory-patterns | scripts/setup_lakebase.py |
| UC table for prompts (agent_config) | prompt-registry-patterns | SKILL.md |
| MLflow artifact versioning | prompt-registry-patterns | references/storage-patterns.md |
| AB testing (champion/challenger) | prompt-registry-patterns | references/ab-testing.md |
| Lazy loading prompts in agent | prompt-registry-patterns | references/loading-patterns.md |
| Prompt update/promote workflow | prompt-registry-patterns | references/storage-patterns.md |
| SQL injection prevention | prompt-registry-patterns | SKILL.md |
| Deployment job trigger (MODEL_VERSION_CREATED) | deployment-automation | SKILL.md |
| Evaluation-then-promote workflow | deployment-automation | references/deployment-job-patterns.md |
| 3 MLflow experiments (dev, eval, deploy) | deployment-automation | references/experiment-organization.md |
| Run naming conventions | deployment-automation | references/experiment-organization.md |
| Standard tags for runs | deployment-automation | references/experiment-organization.md |
| Model promotion (aliases) | deployment-automation | references/model-promotion.md |
| databricks.agents.deploy() | deployment-automation | references/deployment-job-patterns.md |
| Registered scorers with sampling | production-monitoring | SKILL.md |
| On-demand assess() | production-monitoring | SKILL.md |
| Scorer lifecycle (register/start/stop/delete) | production-monitoring | references/registered-scorers.md |
| Immutable pattern (assign result of .start()) | production-monitoring | references/registered-scorers.md |
| Trace archival to UC Delta tables | production-monitoring | references/trace-archival.md |
| Metric backfill (BackfillScorerConfig) | production-monitoring | references/metric-backfill.md |
| Monitoring dashboard SQL queries | production-monitoring | references/monitoring-dashboard-queries.md |
| Custom heuristic scorers (fast, 100% sampling) | production-monitoring | SKILL.md |
| Production vs dev evaluation comparison | production-monitoring | SKILL.md |
| Unified scorer definitions | production-monitoring | SKILL.md |
| Genie accuracy/repeatability testing | genie-space-optimization | SKILL.md |
| 6 control levers | genie-space-optimization | references/six-control-levers.md |
| Dual persistence (API + repo) | genie-space-optimization | references/api-update-patterns.md |
| PATCH API with array sorting | genie-space-optimization | references/api-update-patterns.md |
| Rate limiting (12+ seconds) | genie-space-optimization | SKILL.md |
| Asset routing (TVF vs MV) | genie-space-optimization | references/asset-routing.md |
| Optimization workflow | genie-space-optimization | SKILL.md |
| sort_genie_config() function | genie-space-optimization | scripts/test_genie_repeatability.py |
| Built-in scorers basics (Relevance, Safety, etc.) | mlflow-genai-foundation | references/evaluation-basics.md |
| @scorer decorator basics | mlflow-genai-foundation | references/evaluation-basics.md |
| Prompt registry basics (log/load/alias) | mlflow-genai-foundation | references/prompt-registry-basics.md |
| Visualization hints pattern | genai-agent-implementation | references/architecture-overview.md |
| AgentSettings dataclass | genai-agent-implementation | assets/templates/agent-settings-template.py |
| Complete agent class template | genai-agent-implementation | assets/templates/agent-class-template.py |
| File structure for agent projects | genai-agent-implementation | references/file-structure.md |
| Consolidated anti-patterns | genai-agent-implementation | references/anti-patterns.md |
| Consolidated validation checklist | genai-agent-implementation | references/implementation-checklist.md |
| Production learnings (Jan 27, 2026 - OBO + Auth Passthrough) | responses-agent-patterns | references/obo-authentication.md |
| Version history from source rules | Each respective SKILL.md footer |

### Phase 6: Quality Validation

After creating all skills, verify:

- [ ] Every source file has been fully consumed (no content dropped)
- [ ] Every code example from source rules exists in output skills
- [ ] Every anti-pattern (❌ WRONG / ✅ CORRECT) is preserved
- [ ] Every validation checklist item appears in output
- [ ] Every production learning is documented
- [ ] Every official documentation reference link is included
- [ ] SKILL.md files are under 500 lines each
- [ ] Detailed content is in references/ (progressive disclosure)
- [ ] Reusable code is in scripts/
- [ ] Templates are in assets/templates/
- [ ] Orchestrator declares all 9 dependencies
- [ ] Each dependency skill has proper frontmatter
- [ ] Skill names match directory names
- [ ] Descriptions include WHAT + WHEN + trigger keywords

---

## Critical Patterns to NEVER Miss

These are the most important patterns that must be prominently featured:

### 1. ResponsesAgent is MANDATORY (not ChatAgent, not PythonModel)
- Automatic signature inference
- `predict()` returns `ResponsesAgentResponse`
- `input` key (NOT `messages`)
- NO `signature` parameter in `log_model()`

### 2. NO LLM Fallback for Data Queries
- LLM fallback = hallucinated fake data
- Return explicit error messages instead
- Include "I will NOT generate fake data" statement
- Decision table: when LLM fallback IS/ISN'T acceptable

### 3. OBO Context Detection (MANDATORY)
- Check `IS_IN_DB_MODEL_SERVING_ENV`, `DATABRICKS_SERVING_ENDPOINT`, `MLFLOW_DEPLOYMENT_FLAVOR_NAME`
- Use OBO only in Model Serving
- Use default auth in notebooks/evaluation/jobs
- Two-part auth: SystemAuthPolicy (resources) + UserAuthPolicy (scopes)

### 4. _extract_response_text() Helper (MANDATORY in all custom scorers)
- `mlflow.genai.evaluate()` serializes `ResponsesAgentResponse` to dict
- Without helper, all custom scorers return 0.0 (silent failure)
- Must handle: string, ResponsesAgentResponse object, serialized dict

### 5. Databricks SDK for Scorer LLM Calls (NOT langchain_databricks)
- `langchain_databricks` fails on serverless compute
- Use `WorkspaceClient().serving_endpoints.query()` instead
- Temperature = 0.0 for deterministic scoring

### 6. Guidelines: 4-6 Sections (NOT 8+)
- 8 guidelines = 0.20 score (too strict)
- 4 guidelines = 0.50+ score (achievable, meaningful)

### 7. Metric Aliases for Backward Compatibility
- MLflow 3.0 uses "relevance/mean"
- MLflow 3.1 uses "relevance_to_query/mean"
- Without aliases, threshold checks silently pass failing agents

### 8. Immutable Scorer Pattern
- `scorer.start(...)` does NOT update the object
- MUST assign: `scorer = scorer.start(...)`

### 9. Genie Dual Persistence
- Every Genie optimization must be applied to BOTH:
  1. Direct API update (effective immediately)
  2. Repository source file (survives redeployment)

### 10. Genie API Array Sorting
- API rejects unsorted arrays
- Must sort: tables, metric_views, sql_functions, text_instructions, example_question_sqls, sample_questions, benchmarks

---

## Execution Order

1. Read `cursor-rule-to-skill/SKILL.md` methodology
2. Read ALL 11 source files completely
3. Create orchestrator: `genai-agent-implementation/SKILL.md` + references + assets
4. Create `responses-agent-patterns/` (largest, most critical)
5. Create `mlflow-genai-evaluation/`
6. Create `lakebase-memory-patterns/`
7. Create `prompt-registry-patterns/`
8. Create `multi-agent-genie-orchestration/`
9. Create `deployment-automation/`
10. Create `production-monitoring/`
11. Create `genie-space-optimization/`
12. Create `mlflow-genai-foundation/`
13. Validate: every pattern from every source exists in output
14. Update `.cursor/skills/skill-navigator/SKILL.md` with new genai-agents domain

---

## Final Reminders

- **Completeness over brevity.** Don't summarize - preserve every pattern, code block, and anti-pattern.
- **Progressive disclosure.** SKILL.md has the essential patterns. references/ has the detailed implementations.
- **Production learnings are gold.** Every "Production Learning" section with dates must be preserved verbatim.
- **Code examples must be complete.** Don't truncate Python functions or YAML configs.
- **Anti-patterns must include BOTH wrong and correct patterns.** The `❌ WRONG` / `✅ CORRECT` format is essential for learning.
- **Official documentation links must be preserved.** Every reference URL from source files goes into the respective skill's References section.
- **Version history from source rules should be preserved** in each skill's footer for traceability.
