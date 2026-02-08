# Comprehensive Databricks Agent Implementation Prompt

> **Purpose**: This is a complete, generalized prompt to implement a production-grade AI Agent on Databricks using MLflow 3.0, ResponsesAgent, Genie Spaces, Lakebase Memory, and comprehensive evaluation. This prompt is designed to be adaptable to any domain while maintaining the architectural patterns proven in production.

---

## Your Task

You are implementing a production-grade AI agent on Databricks. The agent will:
1. **Accept natural language queries** from users via a conversational interface
2. **Route queries** to domain-specific data sources (Genie Spaces)
3. **Support cross-domain queries** that synthesize insights from multiple data sources
4. **Maintain conversation context** using short-term memory (Lakebase CheckpointSaver)
5. **Learn user preferences** using long-term memory (Lakebase DatabricksStore)
6. **Stream responses** in real-time for better user experience
7. **Provide visualization hints** for frontend rendering of tabular data
8. **Be comprehensively evaluated** using LLM-as-judge scorers before deployment
9. **Be deployed** to Databricks Model Serving with On-Behalf-Of (OBO) authentication
10. **Be monitored** using MLflow tracing and production monitoring

---

## Part 1: Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AGENT DEPLOYMENT FLOW                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [User Query] → [Model Serving Endpoint] → [ResponsesAgent]                 │
│                          │                       │                          │
│                          │                       ▼                          │
│                     OBO Auth        ┌─────────────────────────┐             │
│                          │          │  Domain Classification   │             │
│                          │          └───────────┬─────────────┘             │
│                          │                      │                           │
│                          │         ┌────────────┴────────────┐              │
│                          │         │                          │             │
│                          ▼         ▼                          ▼             │
│                    ┌─────────┐ ┌─────────┐            ┌─────────────┐       │
│                    │ Genie   │ │ Genie   │    ...     │ Cross-Domain│       │
│                    │ Space 1 │ │ Space 2 │            │  Synthesis  │       │
│                    └────┬────┘ └────┬────┘            └──────┬──────┘       │
│                         │           │                        │              │
│                         └───────────┼────────────────────────┘              │
│                                     ▼                                       │
│                          ┌─────────────────────┐                            │
│                          │  Response + Memory  │                            │
│                          │  + Visualization    │                            │
│                          └─────────────────────┘                            │
│                                     │                                       │
│                                     ▼                                       │
│                          [Streamed Response to User]                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Agent Interface** | MLflow ResponsesAgent | AI Playground compatibility, streaming, automatic signatures |
| **Data Access** | Databricks Genie Spaces | Natural language → SQL → Results |
| **Short-term Memory** | Lakebase CheckpointSaver | Conversation context within sessions |
| **Long-term Memory** | Lakebase DatabricksStore | User preferences across sessions |
| **LLM** | Databricks Foundation Models | Response synthesis, analysis generation |
| **Authentication** | OBO (On-Behalf-Of) | User-level data access controls |
| **Evaluation** | MLflow GenAI Evaluation | LLM-as-judge scoring |
| **Tracing** | MLflow Tracing | Observability and debugging |
| **Deployment** | Databricks Model Serving | Scalable, managed inference |
| **Configuration** | Databricks Asset Bundles | Infrastructure-as-code |

---

## Part 2: ResponsesAgent Implementation

### Why ResponsesAgent (NOT ChatAgent or PythonModel)

ResponsesAgent is **MANDATORY** for Databricks AI Playground compatibility:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  INTERFACE        │  STREAMING     │  AI PLAYGROUND  │  RECOMMENDED     │
├───────────────────┼────────────────┼─────────────────┼──────────────────┤
│  ChatAgent        │  ❌ No         │  ✅ Yes         │  Simple agents   │
│  ResponsesAgent   │  ✅ Yes        │  ✅ Yes         │  Production ✓    │
│  PythonModel      │  ❌ Manual     │  ⚠️ Risky       │  Not recommended │
└───────────────────┴────────────────┴─────────────────┴──────────────────┘
```

**Key Advantages**:
1. **Automatic signature inference** - No manual schema definition
2. **Streaming support** - Real-time response delivery via `predict_stream()`
3. **AI Playground compatible** - Works out-of-the-box
4. **MLflow tracing integration** - Automatic observability

### Agent Class Template

```python
import mlflow
import mlflow.pyfunc
from mlflow.pyfunc import ResponsesAgent
from mlflow.types.responses import (
    ResponsesAgentRequest,
    ResponsesAgentResponse,
    ResponsesAgentStreamEvent
)
from typing import List, Dict, Any, Generator, Optional
import os
import uuid

class YourDomainAgent(mlflow.pyfunc.ResponsesAgent):
    """
    Production Agent implementing MLflow 3.0 ResponsesAgent pattern.
    
    Key Features:
    - Streaming via predict_stream()
    - Multiple domain support with Genie Spaces
    - Cross-domain query synthesis
    - Short-term and long-term memory
    - Visualization hints for frontend
    
    References:
    - https://mlflow.org/docs/latest/genai/serving/responses-agent
    - https://learn.microsoft.com/en-us/azure/databricks/generative-ai/agent-framework/author-agent
    """
    
    # ================================================================
    # DOMAIN CONFIGURATION
    # ================================================================
    # Define your domain keywords for query classification
    # Each domain maps to a Genie Space
    DOMAIN_KEYWORDS = {
        "domain1": ["keyword1", "keyword2", "keyword3"],
        "domain2": ["keyword4", "keyword5", "keyword6"],
        # Add more domains as needed
    }
    
    # Patterns indicating cross-domain queries
    CROSS_DOMAIN_INDICATORS = [
        "and", "vs", "versus", "compared to", "correlation",
        "overall", "comprehensive", "all", "everything",
        "why", "root cause", "impact", "relationship",
    ]
    
    def __init__(self):
        """Initialize agent - called when model is loaded."""
        super().__init__()
        
        # LLM configuration (from environment)
        self.llm_endpoint = os.environ.get("LLM_ENDPOINT", "databricks-claude-sonnet-4-5")
        
        # Genie Space IDs (from environment - set by serving endpoint)
        self.genie_spaces = {
            "domain1": os.environ.get("DOMAIN1_GENIE_SPACE_ID", ""),
            "domain2": os.environ.get("DOMAIN2_GENIE_SPACE_ID", ""),
            # Add more domains
        }
        
        # Lakebase memory configuration
        self.lakebase_instance_name = os.environ.get("LAKEBASE_INSTANCE_NAME", "")
        self.embedding_endpoint = os.environ.get("EMBEDDING_ENDPOINT", "databricks-gte-large-en")
        
        # Memory availability flags (assume available until proven otherwise)
        self._short_term_memory_available = True
        self._long_term_memory_available = True
        
        print(f"Agent initialized. LLM: {self.llm_endpoint}")
    
    def load_context(self, context):
        """Initialize agent with serving context (called by MLflow)."""
        # Re-initialize from environment (same as __init__)
        self.llm_endpoint = os.environ.get("LLM_ENDPOINT", "databricks-claude-sonnet-4-5")
        self.genie_spaces = {
            "domain1": os.environ.get("DOMAIN1_GENIE_SPACE_ID", ""),
            "domain2": os.environ.get("DOMAIN2_GENIE_SPACE_ID", ""),
        }
        self.lakebase_instance_name = os.environ.get("LAKEBASE_INSTANCE_NAME", "")
        self._short_term_memory_available = True
        self._long_term_memory_available = True
    
    # ================================================================
    # MAIN PREDICTION METHOD (Non-Streaming)
    # ================================================================
    
    @mlflow.trace(name="agent_predict", span_type="AGENT")
    def predict(self, request: ResponsesAgentRequest) -> ResponsesAgentResponse:
        """
        Handle inference requests using ResponsesAgent interface.
        
        Input format: {"input": [{"role": "user", "content": "..."}]}
        Output format: ResponsesAgentResponse with output items
        
        IMPORTANT: Load prompts inside this traced function to link
        them to traces in MLflow UI.
        """
        # ================================================================
        # STEP 1: Parse Request
        # ================================================================
        query, input_messages = self._parse_request(request)
        if not query:
            return self._error_response("No query provided.")
        
        # Extract custom inputs (user_id, session_id, etc.)
        custom_inputs = self._extract_custom_inputs(request)
        user_id = custom_inputs.get("user_id", "anonymous")
        session_id = custom_inputs.get("session_id", str(uuid.uuid4()))
        thread_id = custom_inputs.get("thread_id", str(uuid.uuid4()))
        genie_conversation_ids = custom_inputs.get("genie_conversation_ids", {})
        
        # ================================================================
        # STEP 2: Update Trace Context
        # ================================================================
        self._safe_update_trace(
            metadata={
                "mlflow.trace.user": user_id,
                "mlflow.trace.session": session_id,
            },
            tags={
                "user_id": user_id,
                "thread_id": thread_id,
            }
        )
        
        # ================================================================
        # STEP 3: Load Memory Context
        # ================================================================
        conversation_history = self._get_conversation_history(thread_id)
        user_preferences = self._get_user_preferences(user_id, query)
        
        # ================================================================
        # STEP 4: Classify Domain(s)
        # ================================================================
        with mlflow.start_span(name="classify_domain", span_type="CLASSIFIER") as span:
            domains = self._classify_domains(query)
            is_cross_domain = len(domains) > 1
            domain = domains[0]
            
            span.set_outputs({
                "domain": domain,
                "all_domains": domains,
                "is_cross_domain": is_cross_domain
            })
        
        # ================================================================
        # STEP 5: Execute Query (Cross-Domain or Single-Domain)
        # ================================================================
        if is_cross_domain:
            response_text, updated_conv_ids, visualization_hint, data = \
                self._handle_cross_domain_query(
                    domains, query, session_id, genie_conversation_ids
                )
        else:
            response_text, updated_conv_ids, visualization_hint, data = \
                self._handle_single_domain_query(
                    domain, query, session_id, genie_conversation_ids
                )
        
        # ================================================================
        # STEP 6: Save to Memory
        # ================================================================
        self._save_to_short_term_memory(thread_id, query, response_text, domain)
        self._extract_and_save_insights(user_id, query, response_text, domain)
        
        # ================================================================
        # STEP 7: Return Response
        # ================================================================
        return ResponsesAgentResponse(
            id=f"resp_{uuid.uuid4().hex[:12]}",
            output=[self.create_text_output_item(
                text=response_text,
                id=str(uuid.uuid4())
            )],
            custom_outputs={
                "domain": domain if not is_cross_domain else "cross_domain",
                "domains": domains,
                "source": "genie",
                "thread_id": thread_id,
                "genie_conversation_ids": updated_conv_ids,
                "memory_status": "saved",
                "visualization_hint": visualization_hint,
                "data": data,
            }
        )
    
    # ================================================================
    # STREAMING PREDICTION METHOD
    # ================================================================
    
    def predict_stream(self, request) -> Generator:
        """
        Streaming inference for real-time responses.
        
        Yields ResponsesAgentStreamEvent objects:
        - output_item.delta: Text chunks
        - output_item.done: Completion signal
        
        Reference: https://learn.microsoft.com/en-us/azure/databricks/generative-ai/agent-framework/author-agent#streaming-responses
        """
        # Parse request
        query, input_messages = self._parse_request(request)
        if not query:
            yield self._stream_error("No query provided.")
            return
        
        custom_inputs = self._extract_custom_inputs(request)
        session_id = custom_inputs.get("session_id", "single-turn")
        thread_id = custom_inputs.get("thread_id", str(uuid.uuid4()))
        genie_conversation_ids = custom_inputs.get("genie_conversation_ids", {})
        
        # Classify domain
        domains = self._classify_domains(query)
        is_cross_domain = len(domains) > 1
        domain = domains[0]
        
        item_id = str(uuid.uuid4())
        
        # ================================================================
        # Stream Response
        # ================================================================
        if is_cross_domain:
            # Stream cross-domain progress
            yield self.create_text_delta(
                delta=f"🔀 Analyzing across: {', '.join([d.title() for d in domains])}...\n\n",
                item_id=item_id
            )
            
            # Query multiple domains
            multi_result = self._query_multiple_genie_spaces(
                domains, query, session_id, genie_conversation_ids
            )
            
            # Stream progress for each domain
            for d in multi_result["results"].keys():
                yield self.create_text_delta(delta=f"✓ {d.title()} retrieved\n", item_id=item_id)
            
            # Synthesize
            yield self.create_text_delta(delta="\n🧠 Synthesizing...\n\n", item_id=item_id)
            
            response_text = self._synthesize_cross_domain_results(
                query, multi_result["results"], multi_result["errors"]
            )
        else:
            # Stream single-domain query
            yield self.create_text_delta(
                delta=f"🔍 Querying {domain.title()}...\n\n",
                item_id=item_id
            )
            
            response_text, new_conv_id = self._query_genie(
                domain, query, session_id, genie_conversation_ids.get(domain)
            )
        
        # Stream response in chunks
        if response_text:
            chunks = response_text.split('\n\n')
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    text = chunk + ('\n\n' if i < len(chunks) - 1 else '')
                    yield self.create_text_delta(delta=text, item_id=item_id)
        
        # Final done event (REQUIRED)
        full_response = response_text or "No results."
        yield ResponsesAgentStreamEvent(
            type="response.output_item.done",
            item=self.create_text_output_item(text=full_response, id=item_id)
        )
    
    # ================================================================
    # HELPER METHODS (Implement these)
    # ================================================================
    
    def _parse_request(self, request) -> tuple:
        """Extract query and messages from request."""
        # Implementation: Parse ResponsesAgentRequest format
        pass
    
    def _extract_custom_inputs(self, request) -> dict:
        """Extract custom_inputs from request."""
        # Implementation: Handle various custom_inputs formats
        pass
    
    def _safe_update_trace(self, metadata=None, tags=None):
        """Safely update trace without warnings during evaluation."""
        try:
            if mlflow.get_current_active_span():
                mlflow.update_current_trace(metadata=metadata, tags=tags)
        except:
            pass
    
    def _classify_domains(self, query: str) -> list:
        """Classify query to one or more domains."""
        # Implementation: Keyword matching + cross-domain detection
        pass
    
    def _is_cross_domain_query(self, query: str, domains: list) -> bool:
        """Check if query requires cross-domain analysis."""
        # Implementation: Check for cross-domain indicators
        pass
    
    def _query_genie(self, domain: str, query: str, session_id: str, 
                     conversation_id: str = None) -> tuple:
        """Query single Genie Space."""
        # Implementation: Genie API with OBO auth
        pass
    
    def _query_multiple_genie_spaces(self, domains: list, query: str,
                                      session_id: str, conv_ids: dict) -> dict:
        """Query multiple Genie Spaces in parallel."""
        # Implementation: ThreadPoolExecutor for parallel queries
        pass
    
    def _synthesize_cross_domain_results(self, query: str, 
                                          results: dict, errors: dict) -> str:
        """Synthesize results from multiple domains using LLM."""
        # Implementation: LLM synthesis prompt
        pass
    
    def _get_conversation_history(self, thread_id: str) -> list:
        """Get conversation history from short-term memory."""
        # Implementation: Lakebase CheckpointSaver
        pass
    
    def _save_to_short_term_memory(self, thread_id: str, user_msg: str,
                                    assistant_msg: str, domain: str):
        """Save conversation to short-term memory."""
        # Implementation: Lakebase CheckpointSaver
        pass
    
    def _get_user_preferences(self, user_id: str, query: str) -> dict:
        """Get user preferences from long-term memory."""
        # Implementation: Lakebase DatabricksStore with semantic search
        pass
    
    def _extract_and_save_insights(self, user_id: str, query: str,
                                    response: str, domain: str):
        """Extract and save insights to long-term memory."""
        # Implementation: Lakebase DatabricksStore
        pass
    
    def _suggest_visualization(self, data: list, query: str, domain: str) -> dict:
        """Suggest appropriate visualization for data."""
        # Implementation: Rule-based visualization hints
        pass
```

---

## Part 3: Genie Space Integration

### Genie Conversation API Pattern

Genie Spaces provide natural language → SQL → Results:

```python
def _query_genie(self, domain: str, query: str, session_id: str,
                 conversation_id: str = None) -> tuple:
    """
    Query Genie Space using Databricks SDK.
    
    Implements the full Genie conversation flow:
    1. start_conversation_and_wait() - Sends query, waits for SQL generation
    2. get_message_attachment_query_result() - Gets EXECUTED query results
    
    CRITICAL: Without step 2, you only get the SQL, not the results!
    
    References:
    - https://learn.microsoft.com/en-us/azure/databricks/genie/conversation-api
    - https://docs.databricks.com/api/workspace/genie
    
    IMPORTANT (Model Serving Statelessness):
    - Replicas don't share state
    - conversation_id must be passed via custom_inputs for follow-ups
    - Returns (response_text, conversation_id) for client tracking
    """
    space_id = self.genie_spaces.get(domain)
    if not space_id:
        raise ValueError(f"No Genie Space configured for: {domain}")
    
    client = self._get_genie_client(domain)
    
    # Follow-up or new conversation?
    if conversation_id:
        # Use existing conversation
        response = client.genie.create_message_and_wait(
            space_id=space_id,
            conversation_id=conversation_id,
            content=query
        )
    else:
        # Start new conversation
        response = client.genie.start_conversation_and_wait(
            space_id=space_id,
            content=query
        )
    
    new_conversation_id = getattr(response, 'conversation_id', None)
    message_id = getattr(response, 'id', None)
    
    # Extract attachments (text, SQL, query results)
    result_text = ""
    query_results = ""
    
    for attachment in (response.attachments or []):
        attachment_id = getattr(attachment, 'id', None)
        
        # Extract text content
        if hasattr(attachment, 'text') and attachment.text:
            result_text += attachment.text.content + "\n"
        
        # Extract query results (THE ACTUAL DATA!)
        if hasattr(attachment, 'query') and attachment.query:
            if new_conversation_id and message_id and attachment_id:
                try:
                    query_result = client.genie.get_message_attachment_query_result(
                        space_id=space_id,
                        conversation_id=new_conversation_id,
                        message_id=message_id,
                        attachment_id=attachment_id
                    )
                    query_results = self._format_query_results(query_result)
                except Exception as e:
                    query_results = f"(Query execution error: {str(e)[:100]})"
    
    # Build final response
    final_response = ""
    if result_text:
        final_response += f"**Analysis:**\n{result_text}\n\n"
    if query_results:
        final_response += f"**Results:**\n{query_results}\n"
    
    return (final_response.strip(), new_conversation_id)
```

### On-Behalf-Of (OBO) Authentication

OBO enables the agent to query data using the calling user's permissions:

```python
def _get_genie_client(self, domain: str):
    """
    Get WorkspaceClient with appropriate auth strategy.
    
    CRITICAL: OBO only works in Model Serving context.
    Outside Model Serving (notebooks, jobs, evaluation), use default auth.
    
    Environment Detection:
    - IS_IN_DB_MODEL_SERVING_ENV=true
    - DATABRICKS_SERVING_ENDPOINT
    - MLFLOW_DEPLOYMENT_FLAVOR_NAME=databricks
    """
    from databricks.sdk import WorkspaceClient
    import os
    
    # Detect Model Serving environment
    is_model_serving = (
        os.environ.get("IS_IN_DB_MODEL_SERVING_ENV") == "true" or
        os.environ.get("DATABRICKS_SERVING_ENDPOINT") is not None or
        os.environ.get("MLFLOW_DEPLOYMENT_FLAVOR_NAME") == "databricks"
    )
    
    if is_model_serving:
        # Use OBO authentication
        try:
            from databricks_ai_bridge import ModelServingUserCredentials
            return WorkspaceClient(credentials_strategy=ModelServingUserCredentials())
        except:
            return WorkspaceClient()
    else:
        # Use default auth (notebooks, evaluation, jobs)
        return WorkspaceClient()
```

---

## Part 4: Memory Management (Lakebase)

### Short-Term Memory (CheckpointSaver)

Conversation context within sessions:

```python
def _get_conversation_history(self, thread_id: str) -> list:
    """Retrieve conversation history from CheckpointSaver."""
    if not self._short_term_memory_available:
        return []
    
    try:
        from databricks_langchain import CheckpointSaver
        
        with CheckpointSaver(instance_name=self.lakebase_instance_name) as saver:
            config = {"configurable": {"thread_id": thread_id}}
            checkpoint = saver.get_tuple(config)
            
            if checkpoint and checkpoint.checkpoint:
                messages = checkpoint.checkpoint.get("channel_values", {}).get("messages", [])
                return [{"role": m.type, "content": m.content} for m in messages]
        
    except Exception as e:
        if "does not exist" in str(e):
            self._short_term_memory_available = False
        return []
    
    return []

def _save_to_short_term_memory(self, thread_id: str, user_msg: str,
                                assistant_msg: str, domain: str):
    """Save conversation turn to CheckpointSaver."""
    if not self._short_term_memory_available:
        return
    
    try:
        from databricks_langchain import CheckpointSaver
        from langchain_core.messages import HumanMessage, AIMessage
        
        with CheckpointSaver(instance_name=self.lakebase_instance_name) as saver:
            config = {"configurable": {"thread_id": thread_id}}
            
            # Get existing messages
            existing = []
            checkpoint = saver.get_tuple(config)
            if checkpoint and checkpoint.checkpoint:
                existing = checkpoint.checkpoint.get("channel_values", {}).get("messages", [])
            
            # Add new messages
            messages = existing + [
                HumanMessage(content=user_msg),
                AIMessage(content=assistant_msg)
            ]
            
            # Save checkpoint
            saver.put(
                config={"configurable": {
                    "thread_id": thread_id,
                    "checkpoint_id": str(uuid.uuid4())
                }},
                checkpoint={"v": 1, "channel_values": {"messages": messages}},
                metadata={"domain": domain}
            )
    except Exception as e:
        if "does not exist" in str(e):
            self._short_term_memory_available = False
```

### Long-Term Memory (DatabricksStore)

User preferences and insights across sessions:

```python
def _get_user_preferences(self, user_id: str, query: str) -> dict:
    """Retrieve user preferences using semantic search."""
    if not self._long_term_memory_available:
        return {}
    
    try:
        from databricks_langchain import DatabricksStore
        
        store = DatabricksStore(
            instance_name=self.lakebase_instance_name,
            embedding_endpoint=self.embedding_endpoint
        )
        
        namespace = self._get_user_namespace(user_id)
        results = store.search(namespace, query=query, limit=5)
        
        # Parse results into preferences
        preferences = {}
        for item in results:
            # Process based on key prefix (preference_, domain_, threshold_, etc.)
            pass
        
        return preferences
        
    except Exception as e:
        if "does not exist" in str(e):
            self._long_term_memory_available = False
        return {}
```

---

## Part 5: Cross-Domain Query Handling

### Parallel Genie Queries

```python
def _query_multiple_genie_spaces(self, domains: list, query: str,
                                  session_id: str, conv_ids: dict) -> dict:
    """
    Query multiple Genie Spaces in parallel for cross-domain analysis.
    
    Returns:
    {
        "results": {"domain1": {"response": "...", "data": [...]}},
        "errors": {"domain2": "Error message"},
        "updated_conversation_ids": {"domain1": "conv_abc"}
    }
    """
    import concurrent.futures
    
    results = {}
    errors = {}
    updated_ids = dict(conv_ids)
    
    def query_domain(domain: str):
        try:
            space_id = self.genie_spaces.get(domain)
            if not space_id:
                return (domain, None, f"No Genie Space for {domain}")
            
            response, conv_id = self._query_genie(
                domain, query, session_id, conv_ids.get(domain)
            )
            data = self._extract_tabular_data(response)
            
            return (domain, {"response": response, "data": data, "conv_id": conv_id}, None)
        except Exception as e:
            return (domain, None, str(e))
    
    with mlflow.start_span(name="parallel_genie_queries", span_type="TOOL"):
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(domains)) as executor:
            futures = {executor.submit(query_domain, d): d for d in domains}
            
            for future in concurrent.futures.as_completed(futures, timeout=120):
                domain, result, error = future.result()
                if error:
                    errors[domain] = error
                else:
                    results[domain] = result
                    if result.get("conv_id"):
                        updated_ids[domain] = result["conv_id"]
    
    return {"results": results, "errors": errors, "updated_conversation_ids": updated_ids}
```

### LLM Synthesis

```python
def _synthesize_cross_domain_results(self, query: str, 
                                      results: dict, errors: dict) -> str:
    """
    Synthesize results from multiple Genie Spaces using LLM.
    
    The LLM:
    1. Identifies correlations across domains
    2. Highlights cross-domain impacts
    3. Provides actionable recommendations
    4. Presents a coherent narrative
    """
    from databricks_langchain import ChatDatabricks
    
    # Build context from all results
    summaries = []
    for domain, result in results.items():
        summaries.append(f"## {domain.upper()}:\n{result['response'][:2000]}")
    
    synthesis_prompt = f"""You are synthesizing insights from multiple data domains.

User Question: {query}

Data from Multiple Domains:
{chr(10).join(summaries)}

{f"Note: {', '.join(errors.keys())} domains failed" if errors else ""}

Synthesize into a coherent response that:
1. Answers the question directly
2. Identifies cross-domain patterns and correlations
3. Provides actionable recommendations
4. Highlights key metrics

Response:"""
    
    with mlflow.start_span(name="synthesize", span_type="LLM"):
        llm = ChatDatabricks(endpoint=self.llm_endpoint, temperature=0.3)
        response = llm.invoke(synthesis_prompt)
        return response.content
```

---

## Part 6: Model Logging and Authentication

### Resource Declaration

```python
def get_mlflow_resources():
    """
    Declare ALL resources for Automatic Authentication Passthrough.
    
    CRITICAL: Without these, evaluation/notebook contexts cannot access Genie!
    
    Resources:
    - DatabricksServingEndpoint: LLM endpoint
    - DatabricksLakebase: Memory storage
    - DatabricksGenieSpace: Each Genie Space
    - DatabricksSQLWarehouse: For Genie query execution
    """
    from mlflow.models.resources import (
        DatabricksServingEndpoint,
        DatabricksLakebase,
        DatabricksGenieSpace,
        DatabricksSQLWarehouse
    )
    
    resources = []
    
    # LLM endpoint
    resources.append(DatabricksServingEndpoint(endpoint_name=LLM_ENDPOINT))
    
    # Lakebase
    if LAKEBASE_INSTANCE:
        resources.append(DatabricksLakebase(database_instance_name=LAKEBASE_INSTANCE))
    
    # ALL Genie Spaces (CRITICAL!)
    for domain, space_id in GENIE_SPACES.items():
        if space_id:
            resources.append(DatabricksGenieSpace(genie_space_id=space_id))
    
    # SQL Warehouse for Genie
    resources.append(DatabricksSQLWarehouse(warehouse_id=WAREHOUSE_ID))
    
    return resources


def get_auth_policy():
    """
    Create AuthPolicy with BOTH System and User authentication.
    
    SystemAuthPolicy: For evaluation/notebooks (service principal)
    UserAuthPolicy: For Model Serving (OBO with end-user credentials)
    """
    from mlflow.models.auth_policy import AuthPolicy, SystemAuthPolicy, UserAuthPolicy
    
    # System policy: Resources for automatic passthrough
    system_policy = SystemAuthPolicy(resources=get_mlflow_resources())
    
    # User policy: API scopes for OBO
    user_policy = UserAuthPolicy(api_scopes=[
        "dashboards.genie",
        "sql.warehouses",
        "sql.statement-execution",
        "serving.serving-endpoints",
    ])
    
    return AuthPolicy(system_auth_policy=system_policy, user_auth_policy=user_policy)
```

### Model Logging

```python
def log_agent():
    """
    Log agent to MLflow with proper authentication.
    
    CRITICAL: DO NOT pass signature parameter!
    ResponsesAgent automatically infers the correct signature.
    """
    agent = YourDomainAgent()
    
    # Set model for MLflow
    mlflow.models.set_model(agent)
    
    # Input example (ResponsesAgent format - uses 'input', not 'messages')
    input_example = {
        "input": [{"role": "user", "content": "Sample query?"}]
    }
    
    with mlflow.start_run(run_name="agent_registration"):
        mlflow.set_tags({"run_type": "model_logging", "agent_version": "1.0"})
        
        logged_model = mlflow.pyfunc.log_model(
            artifact_path="agent",
            python_model=agent,
            input_example=input_example,
            # NO signature parameter! Auto-inferred by ResponsesAgent
            registered_model_name=f"{CATALOG}.{SCHEMA}.your_agent",
            auth_policy=get_auth_policy(),  # OBO + System auth
            pip_requirements=[
                "mlflow>=3.0.0",
                "databricks-sdk>=0.28.0",
                "databricks-langchain[memory]",
                "databricks-agents>=1.2.0",
                "databricks-ai-bridge",
            ],
        )
    
    return logged_model
```

---

## Part 7: Evaluation Framework

### LLM-as-Judge Scorers

```python
from mlflow.genai.scorers import scorer
from mlflow.entities import Feedback

@scorer
def domain_accuracy_scorer(*, inputs: dict, outputs: Any, **kwargs) -> Feedback:
    """
    Custom LLM judge for domain-specific accuracy.
    
    CRITICAL: Use _extract_response_text() helper!
    mlflow.genai.evaluate() serializes outputs differently.
    """
    # Extract response text properly
    response_text = _extract_response_text(outputs)
    query = inputs.get("request", "")
    
    # Build evaluation prompt
    prompt = f"""Evaluate this response for accuracy.

Query: {query}
Response: {response_text}

Score (0-1) based on:
1. Specific numbers and data referenced
2. Correct interpretation of the data
3. Actionable insights provided

Return JSON: {{"value": "yes|no|partial", "score": 0.0-1.0, "rationale": "..."}}"""
    
    result = _call_llm_for_scoring(prompt)
    
    return Feedback(
        value=result.get("value", "partial"),
        score=result.get("score", 0.5),
        rationale=result.get("rationale", ""),
        name="domain_accuracy"
    )


def _extract_response_text(outputs) -> str:
    """
    Extract response text from various output formats.
    
    CRITICAL: mlflow.genai.evaluate() serializes outputs differently.
    Without this helper, all scorers return 0.0!
    """
    if isinstance(outputs, str):
        return outputs
    
    if hasattr(outputs, 'output'):
        if outputs.output and len(outputs.output) > 0:
            item = outputs.output[0]
            if hasattr(item, 'content') and item.content:
                return item.content[0].text
    
    if isinstance(outputs, dict):
        if 'output' in outputs:
            output_list = outputs['output']
            if output_list and 'content' in output_list[0]:
                return output_list[0]['content'][0].get('text', '')
    
    return ""
```

### Evaluation Execution

```python
def run_evaluation(model_uri: str, eval_dataset: pd.DataFrame) -> dict:
    """
    Run comprehensive agent evaluation.
    
    Reference: https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/
    """
    from mlflow.genai.scorers import RelevanceToQuery, Safety, Guidelines
    
    # Define guidelines
    guidelines = Guidelines(guidelines=[
        "Response must include specific data values",
        "Response must be relevant to the query",
        "Response must not fabricate data",
        "Response must provide actionable insights",
    ])
    
    # Run evaluation
    results = mlflow.genai.evaluate(
        model=model_uri,
        data=eval_dataset,
        model_type="databricks-agent",
        evaluators=[
            RelevanceToQuery(),
            Safety(),
            guidelines,
            domain_accuracy_scorer,  # Custom scorer
        ],
        evaluator_config={
            "col_mapping": {"inputs": "request", "output": "response"}
        }
    )
    
    # Check thresholds
    thresholds = {
        "relevance/mean": 0.4,
        "safety/mean": 0.7,
        "guidelines/mean": 0.5,
        "domain_accuracy/mean": 0.6,
    }
    
    passed = all(
        results.metrics.get(k, 0) >= v 
        for k, v in thresholds.items()
    )
    
    return {"passed": passed, "metrics": results.metrics}
```

---

## Part 8: Deployment

### Using databricks-agents SDK

```python
from databricks import agents

def deploy_agent(model_uri: str, model_version: str):
    """
    Deploy agent using databricks.agents.deploy().
    
    This handles:
    - Endpoint creation/update
    - AI Gateway configuration
    - Inference table setup
    - OBO authentication
    
    Reference: https://docs.databricks.com/aws/en/generative-ai/agent-framework/deploy-agent
    """
    # Set experiment for tracing
    mlflow.set_experiment(EXPERIMENT_EVALUATION)
    
    endpoint_name = f"your_agent_{ENVIRONMENT}"
    
    deployment = agents.deploy(
        model_uri=model_uri,
        model_version=model_version,
        endpoint_name=endpoint_name,
        scale_to_zero=True,
        environment_vars={
            "LLM_ENDPOINT": LLM_ENDPOINT,
            "LAKEBASE_INSTANCE_NAME": LAKEBASE_INSTANCE,
            "DOMAIN1_GENIE_SPACE_ID": GENIE_SPACES["domain1"],
            # Add all environment variables
        }
    )
    
    return deployment
```

---

## Part 9: Visualization Hints

### Hint Generation

```python
def _suggest_visualization(self, data: list, query: str, domain: str) -> dict:
    """
    Suggest appropriate visualization for tabular data.
    
    Returns hint for frontend rendering:
    {
        "type": "bar_chart|line_chart|pie_chart|table|text",
        "x_axis": "column_name",
        "y_axis": ["metric1", "metric2"],
        "title": "Chart Title",
        "domain_preferences": {...}
    }
    """
    if not data:
        return {"type": "text", "reason": "No data"}
    
    headers = list(data[0].keys())
    numeric_cols = [c for c in headers if self._is_numeric(data[0].get(c))]
    datetime_cols = [c for c in headers if self._is_datetime(data[0].get(c))]
    categorical_cols = [c for c in headers if c not in numeric_cols + datetime_cols]
    
    # Time series: datetime + numeric
    if datetime_cols and numeric_cols:
        return {
            "type": "line_chart",
            "x_axis": datetime_cols[0],
            "y_axis": numeric_cols[:3],
            "title": f"{numeric_cols[0]} Over Time",
        }
    
    # Top N: categorical + numeric with <= 20 rows
    if categorical_cols and numeric_cols and len(data) <= 20:
        return {
            "type": "bar_chart",
            "x_axis": categorical_cols[0],
            "y_axis": numeric_cols[0],
            "title": f"Top {len(data)} by {numeric_cols[0]}",
        }
    
    # Distribution: categorical + numeric with <= 10 rows
    if categorical_cols and numeric_cols and len(data) <= 10:
        if any(word in query.lower() for word in ["breakdown", "distribution", "%"]):
            return {
                "type": "pie_chart",
                "label": categorical_cols[0],
                "value": numeric_cols[0],
            }
    
    # Default: table
    return {"type": "table", "columns": headers}
```

---

## Part 10: Configuration Management

### Centralized Settings Pattern

```python
# src/agents/config/settings.py

import os
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class AgentSettings:
    """Centralized configuration with environment overrides."""
    
    # Databricks connection
    databricks_host: str = field(
        default_factory=lambda: os.environ.get("DATABRICKS_HOST", "")
    )
    
    # LLM configuration
    llm_endpoint: str = field(
        default_factory=lambda: os.environ.get("LLM_ENDPOINT", "databricks-claude-sonnet-4-5")
    )
    
    # Genie Space IDs
    @property
    def domain1_genie_space_id(self) -> str:
        return os.environ.get("DOMAIN1_GENIE_SPACE_ID", "")
    
    # Lakebase memory
    lakebase_instance_name: str = field(
        default_factory=lambda: os.environ.get("LAKEBASE_INSTANCE_NAME", "")
    )
    
    # Unity Catalog
    catalog: str = field(
        default_factory=lambda: os.environ.get("CATALOG", "")
    )
    agent_schema: str = field(
        default_factory=lambda: os.environ.get("AGENT_SCHEMA", "")
    )
    
    def validate(self) -> list:
        """Validate required settings."""
        errors = []
        if not self.databricks_host:
            errors.append("DATABRICKS_HOST not set")
        if not self.lakebase_instance_name:
            errors.append("LAKEBASE_INSTANCE_NAME not set")
        return errors


# Global settings instance
settings = AgentSettings()
```

---

## Part 11: Key Learnings and Anti-Patterns

### NEVER Do These

1. **NO LLM Fallback for Data Queries**
   ```python
   # ❌ BAD: Causes hallucination of fake data
   try:
       result = genie.query(q)
   except:
       result = llm.invoke(q)  # ❌ HALLUCINATED DATA!
   
   # ✅ GOOD: Explicit error message
   try:
       result = genie.query(q)
   except Exception as e:
       result = f"**Error:** Could not retrieve data. {e}"
   ```

2. **NO Manual Signatures for ResponsesAgent**
   ```python
   # ❌ BAD: Breaks AI Playground
   mlflow.pyfunc.log_model(
       python_model=agent,
       signature=my_signature,  # ❌ NEVER!
   )
   
   # ✅ GOOD: Let MLflow infer
   mlflow.pyfunc.log_model(
       python_model=agent,
       # NO signature parameter
   )
   ```

3. **NO OBO in Non-Serving Contexts**
   ```python
   # ❌ BAD: OBO fails outside Model Serving
   client = WorkspaceClient(credentials_strategy=ModelServingUserCredentials())
   
   # ✅ GOOD: Detect context first
   if is_model_serving:
       client = WorkspaceClient(credentials_strategy=ModelServingUserCredentials())
   else:
       client = WorkspaceClient()  # Default auth
   ```

4. **NO Missing Resource Declarations**
   ```python
   # ❌ BAD: Evaluation fails without resources
   mlflow.pyfunc.log_model(python_model=agent)
   
   # ✅ GOOD: Declare all resources
   mlflow.pyfunc.log_model(
       python_model=agent,
       auth_policy=AuthPolicy(
           system_auth_policy=SystemAuthPolicy(resources=[
               DatabricksGenieSpace(genie_space_id=SPACE_ID),
               DatabricksSQLWarehouse(warehouse_id=WH_ID),
           ])
       )
   )
   ```

---

## Part 12: File Structure

```
your_project/
├── databricks.yml                    # Asset Bundle configuration
├── src/
│   └── agents/
│       ├── config/
│       │   ├── settings.py           # Centralized configuration
│       │   └── genie_spaces.py       # Genie Space registry
│       ├── setup/
│       │   ├── log_agent_model.py    # Agent class + logging
│       │   ├── deployment_job.py     # Evaluation + deployment
│       │   ├── register_prompts.py   # Prompt registry
│       │   └── register_scorers.py   # Custom scorers
│       ├── notebooks/
│       │   └── setup_lakebase.py     # Memory table setup
│       └── monitoring/
│           └── production_monitor.py # Production monitoring
├── resources/
│   └── agents/
│       ├── agent_setup_job.yml       # Setup workflow
│       └── agent_deployment_job.yml  # Deployment workflow
├── context/
│   └── prompts/
│       └── agents/                   # Domain prompts
└── docs/
    └── agent-framework-design/       # Architecture docs
```

---

## Summary Checklist

Before deploying your agent:

### ResponsesAgent
- [ ] Inherits from `mlflow.pyfunc.ResponsesAgent`
- [ ] `predict()` returns `ResponsesAgentResponse`
- [ ] `predict_stream()` implemented with proper events
- [ ] NO manual signature parameter

### Authentication
- [ ] OBO context detection implemented
- [ ] ALL Genie Spaces in resources
- [ ] SQL Warehouse in resources
- [ ] auth_policy with SystemAuthPolicy + UserAuthPolicy

### Memory
- [ ] Lakebase instance configured
- [ ] Short-term memory (CheckpointSaver)
- [ ] Long-term memory (DatabricksStore)
- [ ] Graceful degradation when unavailable

### Evaluation
- [ ] Custom scorers with proper response extraction
- [ ] Built-in scorers (Relevance, Safety, Guidelines)
- [ ] Threshold checking before deployment

### Deployment
- [ ] Environment variables for Genie Space IDs
- [ ] agents.deploy() for endpoint management
- [ ] Inference tables configured
- [ ] Tracing enabled

---

## References

### Official Documentation
- [MLflow ResponsesAgent](https://mlflow.org/docs/latest/genai/serving/responses-agent)
- [Databricks Agent Framework](https://learn.microsoft.com/en-us/azure/databricks/generative-ai/agent-framework/)
- [Genie Conversation API](https://learn.microsoft.com/en-us/azure/databricks/genie/conversation-api)
- [Agent Authentication](https://docs.databricks.com/aws/en/generative-ai/agent-framework/agent-authentication)
- [MLflow GenAI Evaluation](https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/)
- [Lakebase Memory](https://learn.microsoft.com/en-us/azure/databricks/generative-ai/agent-framework/stateful-agents)

---

*This prompt was generated from a production implementation. Adapt the domain-specific sections to your use case while maintaining the architectural patterns.*
