"""OpsOracle Models Package - Pydantic Models"""

from pydantic import BaseModel
from typing import Dict, List, Optional

class LogRequest(BaseModel):
    log_group: str
    minutes_back: int = 10

class MetricsRequest(BaseModel):
    cpu_utilization: float
    memory_utilization: float
    request_latency: float
    error_rate: float = 0.0
    request_count: int = 0

class IncidentRequest(BaseModel):
    logs: Dict
    metrics: Dict
    blast_radius: Dict
    similar_incidents: Optional[List[Dict]] = None

class RemediationRequest(BaseModel):
    fix_type: str
    parameters: Dict
    permission_level: int = 1

class AlertRequest(BaseModel):
    metrics: Dict
    error_count: int
    affected_services: List[str]

class IncidentResponse(BaseModel):
    id: str
    severity: str
    root_cause: str
    recommended_fix: str

__all__ = [
    "LogRequest",
    "MetricsRequest",
    "IncidentRequest",
    "RemediationRequest",
    "AlertRequest",
    "IncidentResponse"
]