from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from schemas.agent_schemas import (
    TriageResponse, LogAnalysisResponse, DuplicateProfile,
    RootCauseResponse, RemediationResponse
)
from agents.triage_agent import triage_agent
from agents.log_analysis_agent import log_analysis_agent
from agents.duplicate_agent import duplicate_agent
from agents.root_cause_agent import root_cause_agent
from agents.remediation_agent import remediation_agent

# Define Graph State
class AgentState(TypedDict):
    title: str
    description: str
    environment: str
    stack_trace: str
    error_log: str
    triage: TriageResponse
    log_analysis: LogAnalysisResponse
    duplicates: List[DuplicateProfile]
    root_cause: RootCauseResponse
    remediation: RemediationResponse

# Node 1: Triage Node
def triage_node(state: AgentState) -> Dict[str, Any]:
    print("[LangGraph Orchestrator] Invoking Triage Agent Node...")
    res = triage_agent.triage(
        title=state["title"],
        description=state["description"],
        environment=state["environment"]
    )
    return {"triage": res}

# Node 2: Log Analysis Node
def log_analysis_node(state: AgentState) -> Dict[str, Any]:
    print("[LangGraph Orchestrator] Invoking Log Analysis Agent Node...")
    res = log_analysis_agent.analyze(
        stack_trace=state["stack_trace"],
        error_log=state["error_log"]
    )
    return {"log_analysis": res}

# Node 3: Duplicate Detection Node
def duplicate_detection_node(state: AgentState) -> Dict[str, Any]:
    print("[LangGraph Orchestrator] Invoking Duplicate Detection Agent Node...")
    res = duplicate_agent.search_duplicates(
        title=state["title"],
        description=state["description"]
    )
    return {"duplicates": res}

# Node 4: Root Cause Node
def root_cause_node(state: AgentState) -> Dict[str, Any]:
    print("[LangGraph Orchestrator] Invoking Root Cause Agent Node...")
    res = root_cause_agent.analyze_root_cause(
        title=state["title"],
        description=state["description"],
        duplicates=state["duplicates"]
    )
    return {"root_cause": res}

# Node 5: Remediation Node
def remediation_node(state: AgentState) -> Dict[str, Any]:
    print("[LangGraph Orchestrator] Invoking Remediation Agent Node...")
    res = remediation_agent.generate_remediation(
        title=state["title"],
        description=state["description"],
        rc=state["root_cause"],
        duplicates=state["duplicates"]
    )
    return {"remediation": res}

# Compile Workflow
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("triage", triage_node)
workflow.add_node("log_analysis", log_analysis_node)
workflow.add_node("duplicate_detection", duplicate_detection_node)
workflow.add_node("root_cause", root_cause_node)
workflow.add_node("remediation", remediation_node)

# Set routing links
workflow.set_entry_point("triage")
workflow.add_edge("triage", "log_analysis")
workflow.add_edge("log_analysis", "duplicate_detection")
workflow.add_edge("duplicate_detection", "root_cause")
workflow.add_edge("root_cause", "remediation")
workflow.add_edge("remediation", END)

orchestration_graph = workflow.compile()
