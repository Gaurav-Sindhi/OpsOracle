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
        ingest_result = alert_service.ingest_alert(incident_data)
        if ingest_result['status'] != 'success':
            raise HTTPException(status_code=400, detail="Failed to ingest alert")
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
        logs = incident_data.get('logs', {})
        metrics = incident_data.get('metrics', {})

        parsed_logs = log_parser.parse_raw_logs(str(logs))
        blast_radius = log_parser.extract_blast_radius(parsed_logs)
        cascade = blast_radius_service.detect_cascade({
            'service': incident_data.get('service', 'unknown')
        })
        anomaly = anomaly_detector.predict(metrics)
        similar = rag_service.search_similar_incidents(str(logs), top_k=3)
        analysis = llm_agent.analyze_incident(
            parsed_logs, metrics, blast_radius, similar
        )

        incident_id = f"INC-{datetime.now().timestamp()}"
        incident = {
            'id': incident_id,
            'source': 'manual',
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

        # Save to incident store
        alert_service.triaged_incidents.append(incident)

        # Add to RAG knowledge base
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


@router.post("/trigger-aws-incident")
def trigger_real_aws_incident(
    failure_type: str = "timeout",
    function_name: str = "opsoracle-demo-failure"
):
    """Trigger a REAL AWS Lambda failure and run full OpsOracle pipeline"""
    try:
        logger.info(f"🔴 Triggering REAL AWS incident: {failure_type}")

        # Step 1: Trigger Lambda and get real CloudWatch logs
        real_logs = aws_manager.trigger_lambda_and_get_logs(
            function_name=function_name,
            failure_type=failure_type
        )

        # Step 2: Get real CloudWatch metrics
        real_metrics = aws_manager.get_real_metrics(function_name)

        # Step 3: Parse logs
        parsed_logs = log_parser.parse_raw_logs(
            real_logs.get('raw_logs', real_logs.get('summary', ''))
        )
        parsed_logs['summary'] = real_logs.get('summary', 'Lambda error detected')
        parsed_logs['error_count'] = real_logs.get('error_count', 1)

        # Step 4: Blast radius + cascade
        blast_radius = log_parser.extract_blast_radius(parsed_logs)
        cascade = blast_radius_service.detect_cascade({'service': 'lambda'})

        # Step 5: Anomaly detection
        anomaly = anomaly_detector.predict(real_metrics)

        # Step 6: RAG search
        similar = rag_service.search_similar_incidents(
            real_logs.get('summary', ''), top_k=3
        )

        # Step 7: LLM analysis
        analysis = llm_agent.analyze_incident(
            parsed_logs, real_metrics, blast_radius, similar
        )

        # Step 8: Store incident
        incident_id = f"AWS-INC-{datetime.now().timestamp()}"
        incident = {
            'id': incident_id,
            'source': 'REAL AWS',
            'function_name': function_name,
            'failure_type': failure_type,
            'parsed_logs': parsed_logs,
            'metrics': real_metrics,
            'blast_radius': blast_radius,
            'cascade': cascade,
            'anomaly': anomaly,
            'analysis': analysis,
            'similar_incidents': similar,
            'severity': analysis.get('severity', 'HIGH'),
            'timestamp': datetime.now().isoformat()
        }

        alert_service.triaged_incidents.append(incident)

        rag_service.add_incident({
            'id': incident_id,
            'error_type': failure_type,
            'root_cause': analysis.get('root_cause', ''),
            'service': 'lambda',
            'fix_applied': analysis.get('recommended_fix', '')
        })

        return {
            'status': 'success',
            'source': 'REAL AWS CloudWatch',
            'incident_id': incident_id,
            'function_triggered': function_name,
            'failure_type': failure_type,
            'real_logs_fetched': True,
            'log_lines': real_logs.get('error_count', 0),
            'analysis': analysis,
            'cascade': cascade,
            'metrics': real_metrics
        }

    except Exception as e:
        logger.error(f"❌ AWS incident trigger failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))