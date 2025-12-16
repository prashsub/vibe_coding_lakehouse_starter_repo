# Phase 3: Frontend App - User Interface

## Overview

**Status:** 📋 Planned  
**Dependencies:** Phase 2 (Agent Framework)  
**Estimated Effort:** 4-6 weeks  
**Reference:** [Databricks Apps](https://docs.databricks.com/apps/)

---

## Purpose

Phase 3 creates a user-friendly frontend application that:
1. **Provides conversational interface** - Chat with AI agents for analytics
2. **Displays dashboards** - Embedded visualizations and KPIs
3. **Enables self-service** - Natural language queries without SQL
4. **Centralizes access** - Single entry point for all Wanderbricks analytics

---

## Application Architecture

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | React / Streamlit / Gradio | User interface |
| Backend | Databricks Apps / FastAPI | API layer |
| AI | Agent Framework | Natural language processing |
| Data | Unity Catalog | Data access |
| Auth | Databricks OAuth | Authentication |

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Application                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │   Chat   │  │Dashboard │  │  Query   │  │  Admin   │    │
│  │ Interface│  │  Viewer  │  │ Builder  │  │  Panel   │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                     Backend API Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │    Agent     │  │   Dashboard  │  │    Query     │       │
│  │   Gateway    │  │     API      │  │   Executor   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│                   Databricks Platform                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │   AI     │  │ Lakeview │  │   SQL    │  │  Unity   │    │
│  │  Agents  │  │Dashboards│  │Warehouse │  │ Catalog  │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## Application Features

### 1. Chat Interface

**Purpose:** Conversational analytics with AI agents

| Feature | Description |
|---------|-------------|
| Natural Language Queries | Ask questions in plain English |
| Agent Selection | Choose specific domain agent or auto-route |
| Conversation History | Maintain context across questions |
| Data Visualization | Display charts and tables inline |
| Export Results | Download query results as CSV/Excel |

**User Flow:**
```
User → Asks question → Orchestrator routes → Domain agent processes → 
Response with data/charts → User follow-up or new question
```

**Example Interface:**
```
┌─────────────────────────────────────────────────────────┐
│  🏠 Wanderbricks Analytics                        ⚙️ 👤  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 💬 How was revenue last month?                   │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 🤖 Revenue Agent                                 │   │
│  │                                                   │   │
│  │ Last month's revenue was **$1.2M**, up 15%       │   │
│  │ from the previous month.                         │   │
│  │                                                   │   │
│  │ ┌──────────────────────────────────────────┐    │   │
│  │ │ [Revenue Trend Chart]                     │    │   │
│  │ └──────────────────────────────────────────┘    │   │
│  │                                                   │   │
│  │ Top destinations: Paris ($180K), Rome ($145K)   │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Type your question...                       📤   │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 2. Dashboard Viewer

**Purpose:** Display embedded Lakeview dashboards

| Feature | Description |
|---------|-------------|
| Dashboard Gallery | Browse available dashboards |
| Embedded Dashboards | View Lakeview dashboards inline |
| Filter Controls | Interact with dashboard filters |
| Refresh | Update dashboard data |
| Full Screen | Expand to full-screen mode |

**Available Dashboards:**
- 💰 Revenue Performance Dashboard
- 📊 Engagement & Conversion Dashboard
- 🏠 Property Portfolio Dashboard
- 👤 Host Performance Dashboard
- 🎯 Customer Analytics Dashboard

### 3. Query Builder

**Purpose:** Visual SQL query construction

| Feature | Description |
|---------|-------------|
| Table Browser | Browse available Gold tables |
| Column Selector | Select columns to include |
| Filter Builder | Add conditions visually |
| Aggregation | Group by and aggregate |
| Preview | See results before saving |
| Save Query | Save for reuse |

### 4. Admin Panel

**Purpose:** Configuration and monitoring (for admins)

| Feature | Description |
|---------|-------------|
| User Management | Manage access permissions |
| Agent Configuration | Adjust agent settings |
| Query History | View past queries and usage |
| System Health | Monitor agent and data status |
| Alert Configuration | Set up custom alerts |

---

## Pages/Views

### Page Structure

| Page | URL | Purpose | Components |
|------|-----|---------|------------|
| Home | `/` | Landing with quick actions | KPI cards, quick links |
| Chat | `/chat` | Conversational analytics | Chat interface |
| Dashboards | `/dashboards` | Dashboard gallery and viewer | Dashboard list, embedded views |
| Query | `/query` | Ad-hoc query builder | Query builder, results |
| Reports | `/reports` | Scheduled reports | Report list, scheduler |
| Admin | `/admin` | System administration | Config panels |

### Navigation Flow

```
                    ┌─────────┐
                    │  Home   │
                    └────┬────┘
                         │
    ┌────────────────────┼────────────────────┐
    │                    │                    │
    ▼                    ▼                    ▼
┌───────┐          ┌──────────┐         ┌───────┐
│ Chat  │◄────────►│Dashboards│◄───────►│ Query │
└───┬───┘          └────┬─────┘         └───┬───┘
    │                   │                   │
    │                   ▼                   │
    │              ┌─────────┐              │
    └─────────────►│ Reports │◄─────────────┘
                   └─────────┘
```

---

## User Personas & Workflows

### Executive (Leadership)

**Needs:** High-level KPIs, trends, strategic insights

**Primary Workflow:**
1. Login → Home (see KPI summary)
2. Navigate to Revenue Dashboard
3. Ask "What were the highlights last quarter?"
4. Export executive summary

### Analyst (Marketing/Operations)

**Needs:** Detailed data, custom queries, drill-downs

**Primary Workflow:**
1. Login → Chat interface
2. Ask detailed questions across domains
3. Build custom query for specific analysis
4. Save and schedule report

### Data Scientist (ML Team)

**Needs:** Model outputs, predictions, feature data

**Primary Workflow:**
1. Login → Chat interface
2. Query ML model predictions
3. Access Feature Store data
4. Validate model accuracy

---

## Deployment Options

### Option 1: Databricks Apps (Recommended)

```python
# app.py - Databricks App using Streamlit
import streamlit as st
from databricks.agents import get_agent

st.title("🏠 Wanderbricks Analytics")

# Initialize agents
orchestrator = get_agent("wanderbricks-orchestrator")

# Chat interface
user_query = st.chat_input("Ask a question...")

if user_query:
    with st.chat_message("user"):
        st.write(user_query)
    
    with st.chat_message("assistant"):
        response = orchestrator.answer(user_query)
        st.write(response.text)
        
        if response.chart:
            st.plotly_chart(response.chart)
```

### Option 2: External Web App

```python
# main.py - FastAPI backend
from fastapi import FastAPI
from databricks.sdk import WorkspaceClient

app = FastAPI()
w = WorkspaceClient()

@app.post("/api/chat")
async def chat(query: str):
    # Call agent endpoint
    response = w.serving_endpoints.query(
        name="wanderbricks-orchestrator",
        dataframe_records=[{"query": query}]
    )
    return {"response": response}
```

### Option 3: Gradio Interface

```python
# app.py - Gradio interface
import gradio as gr

def answer_query(query, history):
    response = orchestrator.answer(query)
    return response.text

demo = gr.ChatInterface(
    answer_query,
    title="Wanderbricks Analytics",
    examples=[
        "What was revenue last month?",
        "Show me the conversion funnel",
        "Who are our top hosts?"
    ]
)

demo.launch()
```

---

## Implementation Plan

### Week 1-2: Foundation

| Task | Description | Status |
|------|-------------|--------|
| Setup project structure | Create app scaffolding | 📋 |
| Authentication | Implement Databricks OAuth | 📋 |
| Agent integration | Connect to agent endpoints | 📋 |
| Basic chat UI | Text-based chat interface | 📋 |

### Week 3-4: Features

| Task | Description | Status |
|------|-------------|--------|
| Dashboard embedding | Embed Lakeview dashboards | 📋 |
| Visualization rendering | Display charts in chat | 📋 |
| Query builder | Visual query construction | 📋 |
| Conversation memory | Multi-turn conversations | 📋 |

### Week 5-6: Polish & Deploy

| Task | Description | Status |
|------|-------------|--------|
| UI/UX refinement | Design polish | 📋 |
| Mobile responsiveness | Support mobile devices | 📋 |
| Performance optimization | Caching, lazy loading | 📋 |
| Production deployment | Deploy to Databricks Apps | 📋 |

---

## Implementation Checklist

### Core Infrastructure
- [ ] Set up project with chosen framework (Streamlit/Gradio/React)
- [ ] Configure Databricks OAuth authentication
- [ ] Create agent endpoint connections
- [ ] Implement error handling and logging

### Chat Interface
- [ ] Build conversational UI component
- [ ] Implement message history management
- [ ] Add typing indicators and loading states
- [ ] Support multi-turn conversations
- [ ] Render charts and tables inline
- [ ] Add export functionality (CSV, Excel, PDF)

### Dashboard Integration
- [ ] Create dashboard gallery view
- [ ] Implement dashboard embedding
- [ ] Add filter synchronization
- [ ] Enable full-screen mode
- [ ] Support refresh and auto-update

### Query Builder
- [ ] Build table/column browser
- [ ] Implement visual filter builder
- [ ] Add aggregation controls
- [ ] Create results preview
- [ ] Save and share queries

### Admin Panel
- [ ] User management interface
- [ ] Agent configuration settings
- [ ] Query history and analytics
- [ ] System health monitoring

### Deployment
- [ ] Create deployment configuration
- [ ] Set up CI/CD pipeline
- [ ] Configure production environment
- [ ] Document deployment process

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Page load time | <2 seconds |
| Chat response time | <5 seconds |
| User adoption | >50% of target users |
| User satisfaction | >4.0/5.0 rating |
| Feature usage | >3 features/user/session |
| Mobile usability | >80% satisfaction |

---

## Technical Specifications

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/chat` | POST | Send query to agent |
| `/api/dashboards` | GET | List available dashboards |
| `/api/dashboards/{id}` | GET | Get dashboard embed URL |
| `/api/query` | POST | Execute ad-hoc query |
| `/api/history` | GET | Get conversation history |

### Data Models

```python
# Chat message model
class ChatMessage:
    id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    agent: str  # Which agent responded
    visualizations: List[Visualization]

# Dashboard model
class Dashboard:
    id: str
    name: str
    description: str
    domain: str  # Revenue, Engagement, etc.
    embed_url: str
    thumbnail: str
```

---

## Security Considerations

| Aspect | Implementation |
|--------|----------------|
| Authentication | Databricks OAuth 2.0 |
| Authorization | Unity Catalog permissions |
| Data Access | Row-level security via TVFs |
| Audit Logging | Track all queries |
| Rate Limiting | Prevent abuse |
| Input Validation | Sanitize user inputs |

---

## References

- [Databricks Apps](https://docs.databricks.com/apps/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Gradio Documentation](https://gradio.app/docs/)
- [Databricks OAuth](https://docs.databricks.com/dev-tools/auth.html)
- [Agent Framework](https://docs.databricks.com/generative-ai/agent-framework.html)


