from datetime import datetime
from agents.triage_agent import triage_agent
from agents.log_analysis_agent import log_analysis_agent
from agents.orchestrator import orchestration_graph
from schemas.agent_schemas import TriageResponse, LogAnalysisResponse, OrchestrateResponse

class AgentController:
    @staticmethod
    def triage(title: str, description: str, environment: str = "Production") -> TriageResponse:
        return triage_agent.triage(title, description, environment)

    @staticmethod
    def log_analysis(stack_trace: str, error_log: str = "") -> LogAnalysisResponse:
        return log_analysis_agent.analyze(stack_trace, error_log)

    @staticmethod
    def orchestrate(
        title: str, 
        description: str, 
        environment: str, 
        stack_trace: str, 
        error_log: str,
        bug_id: str = "BUG-0000"
    ) -> OrchestrateResponse:
        # Run LangGraph State Graph Workflow
        initial_state = {
            "title": title,
            "description": description,
            "environment": environment,
            "stack_trace": stack_trace,
            "error_log": error_log,
            "triage": None,
            "log_analysis": None,
            "duplicates": None,
            "root_cause": None,
            "remediation": None
        }
        
        # Execute graph
        final_state = orchestration_graph.invoke(initial_state)
        
        # Compile response matching requested schema format
        triage_data = final_state["triage"]
        log_data = final_state["log_analysis"]
        rc_data = final_state["root_cause"]
        dup_data = final_state["duplicates"]
        rem_data = final_state["remediation"]
        
        return OrchestrateResponse(
            bug_id=bug_id,
            triage=triage_data,
            log_analysis=log_data,
            root_cause=rc_data,
            duplicates=dup_data,
            remediation=rem_data,
            timestamp=datetime.utcnow().isoformat() + "Z",
            status="completed"
        )

agent_controller = AgentController()
