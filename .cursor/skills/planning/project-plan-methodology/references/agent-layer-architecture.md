# Agent Layer Architecture — Detailed Reference

## Core Principle: Agents Use Genie Spaces as Query Interface

**AI Agents DO NOT query data assets directly.** Instead, they use Genie Spaces as their natural language query interface. Genie Spaces translate natural language to SQL and route to appropriate tools (TVFs, Metric Views, ML Models).

## Architecture Diagram (3-Tier)

```
┌───────────────────────────┐
│     AI AGENT (Phase 2)    │
│ (e.g., {Domain} Agent)    │
│   - System Prompt         │
│   - Tools (Genie Spaces)  │
└───────────┬───────────────┘
            │ Natural Language Query
            ▼
┌───────────────────────────┐
│   GENIE SPACE (Phase 1.6) │
│ (e.g., {Domain} Intel)    │
│   - Instructions          │
│   - Data Assets           │
└───────────┬───────────────┘
            │ SQL Query
            ▼
┌───────────────────────────┐
│   DATA ASSETS (Phase 1)   │
│ (TVFs, Metric Views,      │
│  ML Models, Gold Tables)  │
└───────────────────────────┘
```

## Why Genie Spaces (Not Direct SQL)?

| Without Genie Spaces | With Genie Spaces |
|---------------------|-------------------|
| Agents must write SQL | Agents use natural language |
| High SQL complexity for agents | Abstraction layer for agents |
| Direct data asset coupling | Decoupled agent from data schema |
| Manual SQL optimization | Genie handles query optimization |
| Limited natural language understanding | Enhanced NL-to-SQL capabilities |
| Hard to maintain agent prompts | Genie instructions act as agent context |
| No built-in guardrails | Genie provides query guardrails |
| No benchmark testing framework | Genie has built-in benchmark testing |

### Why Agents Should Use Genie Spaces — Summary

1. **Abstraction Layer:** Agents don't need to know SQL syntax or schema details
2. **Schema Evolution:** Data model changes don't break agent implementations
3. **Query Optimization:** Genie Spaces handle SQL optimization automatically
4. **Natural Language:** Genie Spaces are designed for NL-to-SQL translation
5. **Guardrails:** Genie Spaces provide built-in query safety checks
6. **Testing Framework:** Benchmark questions test both Genie and Agent accuracy

## Agent-to-Genie Space Mapping (Generic Template)

**Each specialized agent has a dedicated Genie Space (1:1 correspondence):**

| Agent | Dedicated Genie Space | Purpose |
|-------|----------------------|---------|
| {Domain 1} Agent | {Domain 1} Intelligence | {domain 1} analysis, {use cases} |
| {Domain 2} Agent | {Domain 2} Intelligence | {domain 2} analysis, {use cases} |
| {Domain N} Agent | {Domain N} Intelligence | {domain N} analysis, {use cases} |
| Orchestrator Agent | Unified {Project} Monitor | Intent classification, multi-agent coordination |

## Multi-Agent Architecture Diagram (Phase 2)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    USER / FRONTEND APPLICATION                       │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR AGENT                                │
│  Purpose: Intent classification, multi-domain query coordination     │
│  Genie Space: Unified {Project} Monitor                             │
│  Capabilities: Route to specialized agents, synthesize responses     │
└─────────────────────────────────────────────────────────────────────┘
                    │               │               │
        ┌───────────┘               │               └───────────┐
        ▼                           ▼                           ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│  {Domain 1} Agent │   │  {Domain 2} Agent │   │  {Domain N} Agent │
│  Genie: {D1} Int  │   │  Genie: {D2} Int  │   │  Genie: {DN} Int  │
└───────────────────┘   └───────────────────┘   └───────────────────┘
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────────────────────────────────────────────────────────────┐
│                         GENIE SPACES (Phase 1.6)                       │
│  Each agent uses its dedicated Genie Space as the query interface      │
└───────────────────────────────────────────────────────────────────────┘
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────────────────────────────────────────────────────────────┐
│                    DATA ASSETS (Phase 1.1-1.5, 1.7)                    │
│  TVFs | Metric Views | ML Models | Lakehouse Monitors | Gold Tables   │
└───────────────────────────────────────────────────────────────────────┘
```

## Agent-to-Genie Space Design Patterns

| Pattern | Description | When to Use |
|---------|-------------|-------------|
| 1:1 Mapping | Each agent has dedicated Genie Space | Domain-specific agents |
| Orchestrator + Unified | Orchestrator uses unified Genie Space | Multi-domain coordination |
| Hierarchical | Orchestrator routes to specialized agents | Complex multi-intent queries |

## System Prompt Derivation

**Genie Space `instructions` become agent system prompts:**
- Keep instructions ≤20 lines (LLM context efficiency)
- Include data asset selection guidance
- Document query patterns and syntax rules
- Add domain-specific business rules

## Three-Level Testing Strategy

### Level 1: Genie Space Standalone (Phase 1.6)

Validate Genie Spaces work before agent integration:
- [ ] All benchmark questions return correct results
- [ ] Query latency < 10 seconds
- [ ] >80% accuracy on domain-specific questions

### Level 2: Agent Integration (Phase 2)

Validate agents correctly use Genie Spaces:
- [ ] Agent correctly routes queries to Genie Space tool
- [ ] Agent interprets Genie Space results accurately
- [ ] >90% intent classification accuracy
- [ ] Correct tool usage patterns

### Level 3: Multi-Agent Workflow (Phase 2)

Validate Orchestrator coordinates specialized agents:
- [ ] Orchestrator correctly classifies multi-domain intent
- [ ] Sub-queries routed to correct specialized agents
- [ ] Responses synthesized coherently
- [ ] >85% multi-intent classification accuracy

### Testing Summary

| Level | What to Test | Success Criteria |
|-------|--------------|------------------|
| 1. Genie Standalone | Genie Space accuracy | >80% benchmark accuracy |
| 2. Agent Integration | Agent uses Genie correctly | >90% tool usage accuracy |
| 3. Multi-Agent | Orchestrator coordination | >85% intent classification |

**Test each level before proceeding to the next.** Do not skip levels.

## Critical Deployment Order

```
Phase 1.1-1.5 (Data Assets) → Phase 1.6 (Genie Spaces) → Phase 2 (Agents)
         ↓                            ↓                        ↓
   Build foundation          Create NL interface        Consume interface
```

**Agents CANNOT be developed until Genie Spaces are deployed and validated.**

## Multi-Agent Query Example (Generic)

```
User: "What was last month's {metric_A} and which {entities_B} performed best?"
                    │
                    ▼
        ┌──────────────────────────────────────┐
        │        Orchestrator Agent            │
        │ Uses: Unified {Project} Monitor      │
        │ Intent: Multi-domain ({D1} + {D2})   │
        └──────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌───────────────────┐   ┌───────────────────┐
│  {Domain 1} Agent │   │  {Domain 2} Agent │
│  Uses: {D1}       │   │  Uses: {D2}       │
│  Intelligence     │   │  Intelligence     │
└───────────────────┘   └───────────────────┘
        │                       │
        ▼                       ▼
    Genie Space             Genie Space
        │                       │
        ├── get_{d1}_trend      ├── get_{d2}_performance
        ├── {d1}_analytics      ├── {d2}_analytics
        └── {d1}_forecasts      └── get_{d2}_rankings
                    │
                    ▼
        Synthesized Response:
        "{Domain 1} summary + {Domain 2} summary
         combined into a coherent answer"
```

For a concrete worked example with real domain names and data, see [Worked Example: Wanderbricks](worked-example-wanderbricks.md).
