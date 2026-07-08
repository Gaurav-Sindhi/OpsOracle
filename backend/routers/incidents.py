"""Incidents Router - Full pipeline with postmortem, anomaly, RAG all wired"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
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
from backend.utils.pdf_generator import pdf_generator

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


def run_full_pipeline(logs_raw: str, metrics: Dict, service: str, source: str = "manual", extra: Dict = None) -> Dict:
    """Core OpsOracle pipeline — called by both /analyze and /trigger-aws-incident"""

    # 1. Parse logs
    parsed_logs = log_parser.parse_raw_logs(logs_raw)

    # 2. Blast radius
    blast_radius = log_parser.extract_blast_radius(parsed_logs)
    cascade = blast_radius_service.detect_cascade({'service': service})

    # 3. Anomaly detection (Isolation Forest)
    anomaly = anomaly_detector.predict(metrics)
    logger.info(f"Anomaly: is_anomaly={anomaly.get('is_anomaly')}, score={anomaly.get('anomaly_score', 0):.3f}")

    # 4. RAG — search similar past incidents
    similar = rag_service.search_similar_incidents(logs_raw, top_k=3)
    rag_count = len(similar) if similar else 0
    logger.info(f"RAG found {rag_count} similar past incidents")

    # 5. LLM analysis (Groq)
    analysis = llm_agent.analyze_incident(parsed_logs, metrics, blast_radius, similar)

    # 6. Post-mortem generation
    incident_id = f"{source.upper().replace(' ', '-')}-INC-{datetime.now().timestamp()}"
    postmortem_text = llm_agent.write_postmortem({
        'id': incident_id,
        'duration_minutes': 45,
        'root_cause': analysis.get('root_cause', 'Unknown'),
        'affected_services': cascade.get('all_affected_services', []),
        'fix_applied': analysis.get('recommended_fix', 'Unknown'),
        'severity': analysis.get('severity', 'MEDIUM'),
        'service': service
    })
    logger.info(f"Post-mortem generated: {len(postmortem_text)} chars")

    # 7. Build full incident record
    incident = {
        'id': incident_id,
        'source': source,
        'service': service,
        'parsed_logs': parsed_logs,
        'metrics': metrics,
        'blast_radius': blast_radius,
        'cascade': cascade,
        'severity': analysis.get('severity', 'MEDIUM'),
        'analysis': analysis,
        'anomaly': {
            'is_anomaly': anomaly.get('is_anomaly', False),
            'anomaly_score': round(anomaly.get('anomaly_score', 0.0), 3),
            'detection_method': anomaly.get('method', 'isolation_forest'),
            'threshold_breaches': anomaly.get('threshold_breaches', [])
        },
        'rag_context': {
            'similar_count': rag_count,
            'knowledge_base_size': len(rag_service.incident_memory),
            'similar_incidents': [
                {
                    'id': s.get('incident', {}).get('id', 'unknown'),
                    'root_cause': s.get('incident', {}).get('root_cause', 'unknown'),
                    'similarity_score': round(s.get('similarity', 0), 3)
                }
                for s in (similar or [])
            ]
        },
        'postmortem': postmortem_text,
        'timestamp': datetime.now().isoformat(),
        **(extra or {})
    }

    # 8. Save + add to RAG KB
    alert_service.triaged_incidents.append(incident)
    rag_service.add_incident({
        'id': incident_id,
        'error_type': parsed_logs.get('summary', 'unknown'),
        'root_cause': analysis.get('root_cause', 'unknown'),
        'service': service,
        'fix_applied': analysis.get('recommended_fix', 'unknown')
    })

    logger.info(f"Incident {incident_id} stored | Severity={incident['severity']}")
    return incident


@router.get("/")
def list_incidents(limit: int = 50, offset: int = 0):
    try:
        all_incidents = alert_service.get_triaged_incidents()
        return {
            'status': 'success',
            'incidents': all_incidents[offset:offset + limit],
            'total': len(all_incidents),
            'rag_knowledge_base_size': len(rag_service.incident_memory)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/overview")
def get_incident_stats():
    try:
        all_incidents = alert_service.get_triaged_incidents()
        sev_counts = {}
        anomaly_count = 0
        aws_count = 0
        for i in all_incidents:
            sev = i.get('severity', 'MEDIUM').upper()
            sev_counts[sev] = sev_counts.get(sev, 0) + 1
            if i.get('anomaly', {}).get('is_anomaly'):
                anomaly_count += 1
            if i.get('source') == 'REAL AWS':
                aws_count += 1
        return {
            'status': 'success',
            'stats': {
                'total': len(all_incidents),
                'by_severity': sev_counts,
                'anomaly_detected': anomaly_count,
                'from_aws': aws_count,
                'rag_kb_size': len(rag_service.incidents)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{incident_id}/postmortem")
def get_postmortem(incident_id: str):
    try:
        all_incidents = alert_service.get_triaged_incidents()
        incident = next((i for i in all_incidents if i.get('id') == incident_id), None)
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")
        return {
            'status': 'success',
            'incident_id': incident_id,
            'postmortem': incident.get('postmortem', 'Post-mortem not available'),
            'severity': incident.get('severity'),
            'timestamp': incident.get('timestamp')
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{incident_id}/postmortem/pdf")
def download_postmortem_pdf(incident_id: str):
    try:
        all_incidents = alert_service.get_triaged_incidents()
        incident = next((i for i in all_incidents if i.get('id') == incident_id), None)
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")

        pdf_bytes = pdf_generator.generate_postmortem_pdf({
            'id': incident_id,
            'postmortem': incident.get('postmortem', 'Post-mortem not available'),
            'root_cause': incident.get('analysis', {}).get('root_cause', 'unknown'),
            'severity': incident.get('severity', 'MEDIUM'),
            'timestamp': incident.get('timestamp', ''),
            'affected_services': incident.get('cascade', {}).get('all_affected_services', []),
            'anomaly_score': incident.get('anomaly', {}).get('anomaly_score', 0),
            'model': incident.get('analysis', {}).get('model', 'Llama 3.3 70B')
        })

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=postmortem_{incident_id}.pdf"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{incident_id}")
def get_incident(incident_id: str):
    try:
        all_incidents = alert_service.get_triaged_incidents()
        incident = next((i for i in all_incidents if i.get('id') == incident_id), None)
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")
        return {'status': 'success', 'incident': incident}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
def analyze_incident(incident_data: Dict):
    try:
        incident = run_full_pipeline(
            logs_raw=str(incident_data.get('logs', {})),
            metrics=incident_data.get('metrics', {}),
            service=incident_data.get('service', 'unknown'),
            source='manual'
        )
        return {
            'status': 'success',
            'incident_id': incident['id'],
            'analysis': incident['analysis'],
            'cascade': incident['cascade'],
            'anomaly': incident['anomaly'],
            'rag_context': incident['rag_context'],
            'severity': incident['severity'],
            'postmortem_available': bool(incident.get('postmortem'))
        }
    except Exception as e:
        logger.error(f"Error analyzing incident: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger-aws-incident")
def trigger_real_aws_incident(
    failure_type: str = "timeout",
    function_name: str = "opsoracle-demo-failure"
):
    try:
        logger.info(f"Triggering REAL AWS incident: {failure_type}")

        real_logs = aws_manager.trigger_lambda_and_get_logs(
            function_name=function_name,
            failure_type=failure_type
        )
        real_metrics = aws_manager.get_real_metrics(function_name)

        incident = run_full_pipeline(
            logs_raw=real_logs.get('raw_logs', real_logs.get('summary', '')),
            metrics=real_metrics,
            service='lambda',
            source='REAL AWS',
            extra={
                'function_name': function_name,
                'failure_type': failure_type,
                'real_logs_fetched': True,
                'log_group': real_logs.get('log_group', ''),
                'log_lines': real_logs.get('error_count', 0)
            }
        )

        return {
            'status': 'success',
            'source': 'REAL AWS CloudWatch',
            'incident_id': incident['id'],
            'function_triggered': function_name,
            'failure_type': failure_type,
            'real_logs_fetched': True,
            'analysis': incident['analysis'],
            'cascade': incident['cascade'],
            'anomaly': incident['anomaly'],
            'rag_context': incident['rag_context'],
            'metrics': real_metrics,
            'postmortem_available': bool(incident.get('postmortem'))
        }

    except Exception as e:
        logger.error(f"AWS incident trigger failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))