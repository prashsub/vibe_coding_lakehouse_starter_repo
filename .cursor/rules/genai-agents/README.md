# GenAI Agents Cursor Rules

Comprehensive cursor rules for building production-grade GenAI agents with MLflow 3.0+, Databricks Agent Framework, and LangGraph. Based on actual implementation of Databricks Health Monitor Agent.

## Overview

These rules capture best practices, patterns, and anti-patterns discovered during production implementation of a multi-agent system with:
- 5 domain specialists (Cost, Security, Performance, Reliability, Quality)
- Genie Space integration for real data access
- Multi-turn conversation support with Lakebase memory
- Comprehensive LLM-based evaluation with custom judges
- Streaming responses and AI Playground compatibility

---

## Rule Index

### Core Agent Patterns

| Rule | File | Description | Key Learnings |
|---|---|---|---|
| **30** | [mlflow-genai-evaluation.mdc](30-mlflow-genai-evaluation.mdc) | MLflow evaluation with LLM judges and custom scorers | Guidelines: 4-6 sections (not 8+), use foundation model endpoints, consistent run naming |
| **31** | [lakebase-memory-patterns.mdc](31-lakebase-memory-patterns.mdc) | Short-term (CheckpointSaver) and long-term (DatabricksStore) memory | Graceful degradation if tables don't exist, thread_id tracking, user namespace isolation |
| **32** | [prompt-registry-patterns.mdc](32-prompt-registry-patterns.mdc) | Unity Catalog + MLflow prompt versioning | Dual storage, AB testing with champion/challenger, lazy loading |
| **33** | [mlflow-tracing-agent-patterns.mdc](33-mlflow-tracing-agent-patterns.mdc) | MLflow 3.0 tracing, ResponsesAgent, streaming, OBO auth, **trace context** | ResponsesAgent is MANDATORY for AI Playground, no LLM fallback for data queries, **standard metadata fields (mlflow.trace.user/session)** |
| **34** | [deployment-automation-patterns.mdc](34-deployment-automation-patterns.mdc) | Deployment jobs, dataset linking, multi-agent with Genie | Auto-trigger on model versions, dataset lineage with mlflow.log_input(), parallel Genie queries |
| **35** | [production-monitoring-patterns.mdc](35-production-monitoring-patterns.mdc) | Production monitoring with registered scorers and sampling | Continuous monitoring, scorer lifecycle, trace archival, metric backfill, assess() for real-time checks |

---

## Quick Reference: Critical Patterns

### 1. ResponsesAgent (MANDATORY for AI Playground)

**Without `ResponsesAgent`, your agent will NOT work in AI Playground.**

```python
from mlflow.pyfunc import ResponsesAgent

class MyAgent(ResponsesAgent):
    def predict(self, request):
        # Input: request.input (not messages!)
        query = request.input[-1].get("content", "")
        
        # Process...
        response_text = self._process(query)
        
        # Output: ResponsesAgentResponse (not dict!)
        return ResponsesAgentResponse(
            output=[self.create_text_output_item(text=response_text, id=str(uuid.uuid4()))]
        )

# Logging: NO signature parameter!
mlflow.pyfunc.log_model(
    python_model=agent,
    input_example={"input": [{"role": "user", "content": "..."}]},
    # ❌ NEVER: signature=...
)
```

### 2. No LLM Fallback for Data Queries (Prevents Hallucination)

**When Genie fails, return explicit error - NEVER fall back to LLM.**

```python
# ❌ WRONG: LLM fallback generates FAKE DATA
try:
    result = genie.invoke(query)
    return result
except:
    return llm.invoke(query)  # ❌ Hallucinated data!

# ✅ CORRECT: Explicit error
try:
    result = genie.invoke(query)
    return result
except Exception as e:
    return f"""## Genie Query Failed
**Error:** {e}
I will NOT generate fake data."""
```

### 3. Evaluation with 4-6 Essential Guidelines

**Too many guidelines = low scores. Keep it focused.**

```python
# ❌ 8 comprehensive guidelines = 0.20 score
guidelines = [
    "200-word section 1",
    "180-word section 2",
    # ... 6 more sections ...
]

# ✅ 4 focused guidelines = 0.5+ score
guidelines = [
    """Data Accuracy: MUST include specific numbers with time context""",
    """No Fabrication: MUST NEVER guess at numbers""",
    """Actionability: MUST provide specific next steps""",
    """Professional Tone: MUST use proper formatting""",
]
```

### 4. Memory Graceful Degradation

**Agent must work without Lakebase tables.**

```python
def _get_short_term_memory(self):
    if self._short_term_memory_available:
        try:
            memory = ShortTermMemory()
            with memory.get_checkpointer():
                pass  # Test if tables exist
            return memory
        except:
            self._short_term_memory_available = False
    
    return None  # Graceful fallback to stateless
```

### 5. Streaming Responses

```python
def predict_stream(self, request):
    """Stream ResponsesAgent events."""
    query = request.input[-1].get("content", "")
    
    # Stream text chunks
    item_id = str(uuid.uuid4())
    for chunk in self._process_streaming(query):
        yield ResponsesAgentStreamEvent(
            type="output_item.delta",
            delta=ResponsesAgentStreamEventDelta(
                type="message_delta",
                delta=ResponsesAgentMessageContentDelta(
                    type="text",
                    text=chunk
                )
            ),
            item_id=item_id
        )
    
    # Final done event
    yield ResponsesAgentStreamEvent(
        type="output_item.done",
        item_id=item_id
    )
```

---

## Project Structure

```
src/agents/
├── __init__.py
├── config/
│   ├── settings.py              # Centralized config
│   └── genie_spaces.py          # Genie Space IDs
├── memory/
│   ├── short_term.py            # CheckpointSaver for conversations
│   └── long_term.py             # DatabricksStore for user preferences
├── prompts/
│   ├── registry.py              # Prompt definitions
│   ├── manager.py               # Load/update functions
│   └── ab_testing.py            # Champion/challenger logic
├── evaluation/
│   ├── judges.py                # Custom LLM judges
│   ├── evaluator.py             # Evaluation orchestration
│   └── production_monitor.py    # Live monitoring
├── orchestrator/
│   ├── agent.py                 # Main orchestrator (ResponsesAgent)
│   ├── graph.py                 # LangGraph workflow
│   ├── intent_classifier.py    # Domain routing
│   └── synthesizer.py           # Multi-domain response synthesis
├── workers/
│   ├── base.py                  # Base worker class
│   ├── cost_agent.py            # Cost domain specialist
│   ├── security_agent.py        # Security domain specialist
│   ├── performance_agent.py     # Performance domain specialist
│   ├── reliability_agent.py     # Reliability domain specialist
│   └── quality_agent.py         # Quality domain specialist
├── tools/
│   ├── genie_tool.py            # Genie Space integration
│   ├── web_search.py            # Web search tool
│   └── dashboard_linker.py      # Link to dashboards
└── setup/
    ├── log_agent_model.py       # Log agent to MLflow
    ├── register_prompts.py      # Register prompts to UC + MLflow
    ├── run_evaluation.py        # Run comprehensive evaluation
    ├── deployment_job.py        # Eval + deploy with thresholds
    └── configure_trace_storage.py  # Unity Catalog trace setup
```

---

## Key Implementation Files

### Agent Entry Point

**File:** `src/agents/setup/log_agent_model.py`
- Implements `ResponsesAgent` with streaming support
- Lazy-loads memory (graceful degradation)
- Integrates Genie tools
- On-behalf-of authentication pattern

### Evaluation System

**File:** `src/agents/setup/deployment_job.py`
- Registers 10+ LLM judges (built-in + custom)
- Defines deployment thresholds per judge
- Links evaluation dataset
- Checks thresholds before deployment approval

### Memory Management

**Files:** `src/agents/memory/{short_term,long_term}.py`
- Short-term: LangGraph CheckpointSaver for conversation continuity
- Long-term: Vector-based DatabricksStore for user preferences
- Both support graceful degradation

### Prompt System

**Files:** `src/agents/prompts/{registry,manager}.py`
- 8 prompts (orchestrator, 5 domains, intent classifier, synthesizer)
- Stored in Unity Catalog `agent_config` table
- Versioned in MLflow for rollback
- AB testing with champion/challenger aliases

---

## Common Mistakes (from Production Experience)

### 1. ❌ Guidelines Judge Too Strict

**Problem:** 8 comprehensive guideline sections → 0.20 score  
**Solution:** 4 focused, essential guidelines → 0.5+ score  
**Learning:** Evaluation judges should be achievable, not aspirational

### 2. ❌ LLM Fallback for Data Queries

**Problem:** Genie fails → LLM generates fake job names → user acts on fake data  
**Solution:** Return explicit error instead of hallucinating  
**Learning:** Data accuracy > response availability

### 3. ❌ Manual Signatures for ResponsesAgent

**Problem:** Agent doesn't load in AI Playground  
**Solution:** Never pass `signature` parameter - auto-inference required  
**Learning:** Follow ResponsesAgent pattern exactly per docs

### 4. ❌ Assuming Memory Tables Exist

**Problem:** Agent crashes if Lakebase not set up  
**Solution:** Lazy loading with try/except and graceful fallback  
**Learning:** Memory is optional enhancement, not requirement

### 5. ❌ Not Returning thread_id

**Problem:** Client can't continue multi-turn conversations  
**Solution:** Return `thread_id` in `custom_outputs`  
**Learning:** State management requires client-server coordination

---

## Testing & Validation

### Pre-Deployment Checklist

- [ ] Agent uses `ResponsesAgent` (not `PythonModel`)
- [ ] No `signature` parameter in `log_model()`
- [ ] Input example uses `input` key (not `messages`)
- [ ] Output returns `ResponsesAgentResponse` (not dict)
- [ ] Evaluation dataset linked to MLflow run
- [ ] 4-6 focused guidelines (not 8+)
- [ ] Custom judges use `@mlflow.trace` and `@scorer`
- [ ] Foundation model endpoints for judges (not pay-per-token)
- [ ] No LLM fallback for Genie/tool calls
- [ ] Memory graceful degradation implemented
- [ ] thread_id returned in custom_outputs
- [ ] Streaming implemented via `predict_stream()`
- [ ] On-behalf-of auth configured for serving
- [ ] Tracing enabled and visible in MLflow UI

### Evaluation Commands

```bash
# Run evaluation
databricks bundle run -t dev agent_evaluation_job

# Check latest results
python scripts/check_latest_evaluation.py

# View in MLflow UI
# Navigate to: /Shared/health_monitor_agent_evaluation
# Look for runs with prefix: eval_pre_deploy_*
```

---

## References

### Official Documentation

**MLflow & Agents:**
- [MLflow GenAI](https://mlflow.org/docs/latest/llms/genai/index.html)
- [ResponsesAgent](https://mlflow.org/docs/latest/genai/serving/responses-agent)
- [Databricks Agent Framework](https://docs.databricks.com/en/generative-ai/agent-framework/)
- [Agent Evaluation](https://docs.databricks.com/en/generative-ai/agent-evaluation/)

**Memory & State:**
- [Stateful Agents Guide](https://learn.microsoft.com/en-us/azure/databricks/generative-ai/agent-framework/stateful-agents)
- [Short-Term Memory](https://docs.databricks.com/aws/en/notebooks/source/generative-ai/short-term-memory-agent-lakebase.html)
- [Long-Term Memory](https://docs.databricks.com/aws/en/notebooks/source/generative-ai/long-term-memory-agent-lakebase.html)

**Tracing & Monitoring:**
- [MLflow Tracing](https://mlflow.org/docs/latest/llms/tracing/index.html)
- [Unity Catalog Trace Storage](https://docs.databricks.com/aws/en/mlflow3/genai/tracing/storage)

### Related Databricks Rules

- [28-mlflow-genai-patterns.mdc](../ml/28-mlflow-genai-patterns.mdc) - MLflow 3.0 GenAI comprehensive patterns
- [09-databricks-python-imports.mdc](../common/09-databricks-python-imports.mdc) - Asset Bundle import patterns

---

## Contributing

When adding new patterns to these rules:

1. **Ground in actual implementation** - No theoretical patterns
2. **Document mistakes** - What didn't work and why
3. **Include references** - Official docs, not blog posts
4. **Show before/after** - Bad pattern → Good pattern
5. **Quantify impact** - Time saved, errors prevented, etc.

Example:
```
### Pattern: X

❌ WRONG: [code that causes problem]
Problem: [what fails and why]

✅ CORRECT: [code that works]
Why: [explanation with official doc reference]

Impact: Prevented 10+ deployment failures, saved 2 hours per deployment
```

---

## Version History

- **v1.0** (Jan 14, 2026) - Initial rules from Health Monitor Agent implementation
  - MLflow Evaluation with custom judges
  - Lakebase memory patterns
  - Prompt Registry with AB testing
  - ResponsesAgent + Streaming patterns
  - On-behalf-of authentication
  - Key learnings: Guidelines simplification (8→4 sections), no LLM fallback, graceful degradation

---

**Last Updated:** January 14, 2026  
**Project:** Databricks Health Monitor Agent  
**Implementation:** `src/agents/`
