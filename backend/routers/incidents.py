"""Incidents Router - GET/POST endpoints for incidents"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger
from backend.services.alert_service import alert_service
from backend.services.aws_manager import aws_manager
from backend.services.log_parser import log_parser
from backend.services.rag_service import rag_service
from backend.services.blast_radius_service import blast_radius_service
from backend.agents.llm_agent import llm_agent
from backend.ml.anomaly_detector import anomaly_detector

router = APIRouter(prefix="/api/incidents", tags=["incidents"])

@router.get("/")
def list_incidents(limit: int = 50, offset: int = 0):
    """Get list of incidents"""
    try:
        # In production, fetch from database
        triaged = alert_service.get_triaged_incidents()
        incidents = triaged[offset:offset + limit]
        
        return {
            'status': 'success',
            'incidents': incidents,
            'total': len(triaged),
            'limit': limit,
            'offset': offset
        }
    except Exception as e:
        logger.error(f"❌ Error listing incidents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{incident_id}")
def get_incident(incident_id: str):
    """Get specific incident by ID"""
    try:
        triaged = alert_service.get_triaged_incidents()
        incident = next((i for i in triaged if i.get('id') == incident_id), None)
        
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        return {
            'status': 'success',
            'incident': incident
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching incident: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
def create_incident(incident_data: Dict):
    """Create a new incident"""
    try:
        # Ingest alert
        ingest_result = alert_service.ingest_alert(incident_data)
        
        if ingest_result['status'] != 'success':
            raise HTTPException(status_code=400, detail="Failed to ingest alert")
        
        # Triage alert
        triage_result = alert_service.triage_alert(incident_data)
        
        return {
            'status': 'success',
            'incident_id': triage_result.get('id'),
            'severity': triage_result.get('severity'),
            'requires_immediate_action': triage_result.get('requires_immediate_action')
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating incident: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
def analyze_incident(incident_data: Dict):
    """Full incident analysis pipeline"""
    try:
        # Extract data
        logs = incident_data.get('logs', {})
        metrics = incident_data.get('metrics', {})
        
        # Parse logs
        parsed_logs = log_parser.parse_raw_logs(str(logs))
        
        # Detect blast radius
        blast_radius = log_parser.extract_blast_radius(parsed_logs)
        
        # Detect cascade
        cascade = blast_radius_service.detect_cascade({
            'service': incident_data.get('service', 'unknown')
        })
        
        # Check for anomaly
        anomaly = anomaly_detector.predict(metrics)
        
        # Search RAG
        similar = rag_service.search_similar_incidents(str(logs), top_k=3)
        
        # LLM analysis
        analysis = llm_agent.analyze_incident(
            parsed_logs,
            metrics,
            blast_radius,
            similar
        )
        
        # Create incident
        incident_id = f"INC-{datetime.now().timestamp()}"
        
        incident = {
            'id': incident_id,
            'parsed_logs': parsed_logs,
            'metrics': metrics,
            'blast_radius': blast_radius,
            'cascade': cascade,
            'anomaly': anomaly,
            'analysis': analysis,
            'similar_incidents': similar,
            'severity': analysis.get('severity', 'MEDIUM'),
            'timestamp': datetime.now().isoformat()
        }
        
        # Save incident so it shows up in GET /api/incidents
        alert_service.triaged_incidents.append(incident)
        
        # Also add to RAG knowledge base for future similarity search
        rag_service.add_incident({
            'id': incident_id,
            'error_type': parsed_logs.get('summary', 'unknown'),
            'root_cause': analysis.get('root_cause', 'unknown'),
            'service': incident_data.get('service', 'unknown'),
            'fix_applied': analysis.get('recommended_fix', 'unknown')
        })
        
        return {
            'status': 'success',
            'incident_id': incident_id,
            'analysis': analysis,
            'cascade': cascade,
            'severity': analysis.get('severity')
        }
    except Exception as e:
        logger.error(f"❌ Error analyzing incident: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/overview")
def get_incident_stats():
    """Get incident statistics"""
    try:
        stats = alert_service.get_alert_stats()
        return {
            'status': 'success',
            'stats': stats
        }
    except Exception as e:
        logger.error(f"❌ Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))