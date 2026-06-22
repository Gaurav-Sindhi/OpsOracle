"""Remediation Router - POST endpoints for remediation"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
from loguru import logger
from backend.agents.remediation_agent import remediation_agent
from backend.services.blast_radius_service import blast_radius_service

router = APIRouter(prefix="/api/remediation", tags=["remediation"])

class RemediationRequest(BaseModel):
    fix_type: str
    parameters: Dict
    permission_level: int = 1

@router.post("/execute")
def execute_remediation(request: RemediationRequest):
    """Execute remediation fix"""
    try:
        result = remediation_agent.execute_remediation(
            request.fix_type,
            request.parameters,
            request.permission_level
        )
        
        return {
            'status': 'success',
            'remediation_result': result
        }
    except Exception as e:
        logger.error(f"❌ Error executing remediation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
def get_remediation_history(limit: int = 10):
    """Get remediation history"""
    try:
        history = remediation_agent.get_remediation_history(limit)
        stats = remediation_agent.get_remediation_stats()
        
        return {
            'status': 'success',
            'history': history,
            'stats': stats
        }
    except Exception as e:
        logger.error(f"❌ Error fetching history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cascade/{incident_id}")
def get_cascade_remediation(incident_id: str):
    """Get remediation plan for cascade"""
    try:
        # Mock cascade data
        cascade_data = {
            'primary_service': 'api_gateway',
            'all_affected_services': ['api_gateway', 'lambda', 'rds'],
            'total_affected': 3
        }
        
        priority = blast_radius_service.get_remediation_priority(cascade_data)
        
        return {
            'status': 'success',
            'remediation_plan': priority
        }
    except Exception as e:
        logger.error(f"❌ Error getting cascade remediation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))