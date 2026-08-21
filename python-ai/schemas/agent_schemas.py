from pydantic import BaseModel
from typing import List

class TriageRequest(BaseModel):
    title: str
    description: str
    environment: str = "Production"

class TriageResponse(BaseModel):
    triage_component: str
    severity: str
    priority: str  # P1, P2, P3, P4
    confidence: int
    reasoning: str
    severity_reason: str
    priority_reason: str

class LogAnalysisRequest(BaseModel):
    stack_trace: str
    error_log: str = ""

class LogAnalysisResponse(BaseModel):
    exception_type: str
    error_message: str
    failed_class: str
    failed_method: str
    timestamp: str
    failure_reason: str
    file: str
    line: int
    function: str
    root_cause: str
    affected_code_path: List[str]

class DuplicateProfile(BaseModel):
    bug_id: str
    similarity: int  # percentage 0-100
    summary: str
    resolution: str

class RootCauseResponse(BaseModel):
    root_cause: str
    confidence: int
    supporting_evidence: List[str]
    explanation: str

class RemediationResponse(BaseModel):
    immediate_fix: str
    long_term: str
    best_practices: List[str]

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
    root_cause: RootCauseResponse
    duplicates: List[DuplicateProfile]
    remediation: RemediationResponse
    timestamp: str
    status: str
