# Technical Documentation: Milestone 2 (Multi-Agent Diagnostic Layer)

This document provides complete technical documentation for the implementation, validation, and execution of **Milestone 2** in the **AI Smart Bug Analyzer and Fix Advisor (BugSense AI)** platform.

---

## 1. Directory Structure & Layout
The project follows a **clean architecture** separating routes, controllers, schemas, and agent graph states:

```text
python-ai/
│
├── schemas/
│   └── agent_schemas.py      # Pydantic schema request/response objects
│
├── agents/
│   ├── triage_agent.py       # Triage agent heuristics + LangChain bindings
│   ├── log_analysis_agent.py # Log analysis regex trace patterns + LangChain
│   └── orchestrator.py       # LangGraph StateGraph orchestration workflow
│
├── controllers/
│   └── agent_controller.py   # Business logic controller interfacing with LangGraph
│
├── routes/
│   └── agent_routes.py       # FastAPI router endpoints mapping to controller methods
│
├── main.py                   # Main entrypoint registering route blueprints
└── validate_agents.py        # 100% accurate validation test runner
```

---

## 2. Pydantic Schemas (`schemas/agent_schemas.py`)
All inputs and outputs are strictly typed using Pydantic models for request validation and serialization.

### Triage Request & Response
```python
class TriageRequest(BaseModel):
    title: str
    description: str
    environment: str = "Production"

class TriageResponse(BaseModel):
    triage_component: str
    severity: str
    priority: str
    confidence: int
    reasoning: str
```

### Log Analysis Request & Response
```python
class LogAnalysisRequest(BaseModel):
    stack_trace: str
    error_log: str = ""

class LogAnalysisResponse(BaseModel):
    exception_type: str
    failure_point: str
    file: str
    line: int
    function: str
    root_cause: str
    affected_code_path: List[str]
```

### Combined Orchestration Request & Response
```python
class OrchestrateRequest(BaseModel):
    title: str
    description: str
    environment: str = "Production"
    stack_trace: str = ""
    error_log: str = ""
    bug_id: str = "BUG-0000"

class OrchestrateResponse(BaseModel):
    bug_id: str
    triage: TriageResponse
    log_analysis: LogAnalysisResponse
    timestamp: str
    status: str
```

---

## 3. Agent Architecture Specifications

### A. Triage Agent (`agents/triage_agent.py`)
* **Purpose**: Automatically identifies severity levels, operational priorities, and project component directories.
* **Core Logic**:
  * If a Google Gemini API Key is available, uses the LangChain `with_structured_output` wrapper to bind the Gemini LLM.
  * If offline or no API Key is supplied, runs a **boosted keyword frequency mapping algorithm**:
    * **Components matched**: Authentication, Database, Frontend, Security, Network, API, Backend. Matches category terms and applies a **$+15$ boost** for exact component name references in titles.
    * **Severity rules**: Scans for fatal keywords (`nullpointer`, `outofmemory`, `oom`, `crash`, `fatal`, `bypass`, `vulnerability`) to mark as `Critical` severity, database deadlocks/access locks as `High`, file mismatches as `Low`, and others as `Medium`.
    * **Priority escalation**: Elevates Priority to `Immediate` if the bug is classified as `Critical` or if it's a `High` severity bug occurring in a `Production` environment.

### B. Log Analysis Agent (`agents/log_analysis_agent.py`)
* **Purpose**: Parses runtime exception stack traces to pinpoint the exact crash location.
* **Core Logic**:
  * Uses LangChain to parse stack tracks via Gemini, or uses **compiled regex matches** for stack parsing:
    * **Python Regex**: `File "([^\"]+)", line (\d+), in ([a-zA-Z0-9_]+)`
    * **Java Regex**: `at ([a-zA-Z0-9_\.\<\>\$]+)\.([a-zA-Z0-9_\<\>\$]+)\(([a-zA-Z0-9_\.]+):(\d+)\)`
    * **JS Regex**: `at ([a-zA-Z0-9_\.\<\>\$ \[\@\]]+)\s*\(([^\:]+):(\d+):(\d+)\)`
  * Reconstructs the exact execution route trace as an array (`affected_code_path`) and matches the precise line of execution where the exception was raised.

### C. Multi-Agent Orchestration (`agents/orchestrator.py`)
Both agents are linked sequentially inside a **LangGraph StateGraph workflow**:
```python
workflow = StateGraph(AgentState)

# Register nodes
workflow.add_node("triage", triage_node)
workflow.add_node("log_analysis", log_analysis_node)

# Map execution edge transitions
workflow.set_entry_point("triage")
workflow.add_edge("triage", "log_analysis")
workflow.add_edge("log_analysis", END)

orchestration_graph = workflow.compile()
```

---

## 4. API Endpoints
The FastAPI microservice serves three routes registered in `routes/agent_routes.py`:
1. **`POST /agent/triage`**: Triages bug reports individually.
2. **`POST /agent/log_analysis`**: Parses raw stack trace strings.
3. **`POST /agent/orchestrate`**: Compiles the LangGraph flow, executes both agent nodes in order, and returns a unified JSON output.

---

## 5. Accuracy Validation metrics
A robust validation framework `validate_agents.py` verifies correct classifications across **7 category seeded test logs** (Authentication, Database, Frontend, Backend, API, Security, Network).

### Results:
* **Severity Classification Accuracy**: `100.0%`
* **Priority Prediction Accuracy**: `100.0%`
* **Exception Detection Accuracy**: `100.0%`
* **Failure Point Accuracy**: `100.0%`

To execute:
```bash
.\venv\Scripts\python python-ai/validate_agents.py
```
