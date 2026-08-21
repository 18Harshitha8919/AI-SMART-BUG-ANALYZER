from fastapi import APIRouter, HTTPException
from schemas.agent_schemas import (
    TriageRequest, TriageResponse,
    LogAnalysisRequest, LogAnalysisResponse,
    OrchestrateRequest, OrchestrateResponse
)
from controllers.agent_controller import agent_controller

router = APIRouter(prefix="/agent", tags=["Agents"])

@router.post("/triage", response_model=TriageResponse)
def triage_endpoint(req: TriageRequest):
    try:
        return agent_controller.triage(req.title, req.description, req.environment)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/log_analysis", response_model=LogAnalysisResponse)
def log_analysis_endpoint(req: LogAnalysisRequest):
    try:
        return agent_controller.log_analysis(req.stack_trace, req.error_log)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/orchestrate", response_model=OrchestrateResponse)
def orchestrate_endpoint(req: OrchestrateRequest):
    try:
        return agent_controller.orchestrate(
            title=req.title,
            description=req.description,
            environment=req.environment,
            stack_trace=req.stack_trace,
            error_log=req.error_log,
            bug_id=req.bug_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
