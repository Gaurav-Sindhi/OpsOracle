"""Metrics Router - GET endpoints for metrics"""

from fastapi import APIRouter, HTTPException
from loguru import logger
from backend.services.aws_manager import aws_manager

router = APIRouter(prefix="/api/metrics", tags=["metrics"])

@router.get("/all")
def get_all_metrics():
    """Get metrics from all AWS services"""
    try:
        metrics = aws_manager.get_all_services_metrics()
        return {
            'status': 'success',
            'metrics': metrics
        }
    except Exception as e:
        logger.error(f"❌ Error fetching all metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{namespace}/{metric_name}")
def get_metric(namespace: str, metric_name: str, minutes_back: int = 10):
    """Get specific metric"""
    try:
        metrics = aws_manager.get_metrics(namespace, metric_name, minutes_back)
        return {
            'status': 'success',
            'metrics': metrics
        }
    except Exception as e:
        logger.error(f"❌ Error fetching metric: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/xray/traces")
def get_xray_traces(minutes_back: int = 10):
    """Get X-Ray trace data"""
    try:
        traces = aws_manager.get_xray_traces(minutes_back)
        return {
            'status': 'success',
            'traces': traces
        }
    except Exception as e:
        logger.error(f"❌ Error fetching X-Ray traces: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))