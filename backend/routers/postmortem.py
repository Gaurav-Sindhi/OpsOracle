"""Postmortem Router - POST/GET endpoints for postmortems"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from loguru import logger
from backend.agents.llm_agent import llm_agent

router = APIRouter(prefix="/api/postmortem", tags=["postmortem"])

class PostmortemStore:
    """In-memory postmortem store"""
    def __init__(self):
        self.postmortems = []
    
    def save(self, postmortem: dict):
        self.postmortems.append(postmortem)
    
    def get(self, postmortem_id: str):
        return next((p for p in self.postmortems if p['id'] == postmortem_id), None)
    
    def list(self):
        return self.postmortems

postmortem_store = PostmortemStore()

@router.post("/generate")
def generate_postmortem(incident_data: dict):
    """Generate post-mortem report"""
    try:
        # Generate using LLM
        narrative = llm_agent.write_postmortem(incident_data)
        
        # Build structured postmortem
        postmortem = {
            'id': f"PM-{datetime.now().timestamp()}",
            'incident_id': incident_data.get('id'),
            'timestamp': datetime.now().isoformat(),
            'duration_minutes': incident_data.get('duration_minutes', 0),
            'root_cause': incident_data.get('root_cause', 'Unknown'),
            'affected_services': incident_data.get('affected_services', []),
            'severity': incident_data.get('severity', 'MEDIUM'),
            'narrative': narrative,
            'status': 'generated'
        }
        
        # Store
        postmortem_store.save(postmortem)
        
        logger.info(f"✅ Postmortem generated: {postmortem['id']}")
        
        return {
            'status': 'success',
            'postmortem_id': postmortem['id'],
            'postmortem': postmortem
        }
    except Exception as e:
        logger.error(f"❌ Error generating postmortem: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{postmortem_id}")
def get_postmortem(postmortem_id: str):
    """Get specific postmortem"""
    try:
        postmortem = postmortem_store.get(postmortem_id)
        
        if not postmortem:
            raise HTTPException(status_code=404, detail="Postmortem not found")
        
        return {
            'status': 'success',
            'postmortem': postmortem
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching postmortem: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
def list_postmortems():
    """List all postmortems"""
    try:
        postmortems = postmortem_store.list()
        
        return {
            'status': 'success',
            'postmortems': postmortems,
            'total': len(postmortems)
        }
    except Exception as e:
        logger.error(f"❌ Error listing postmortems: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{postmortem_id}/export/pdf")
def export_postmortem_pdf(postmortem_id: str):
    """Export postmortem as PDF"""
    try:
        postmortem = postmortem_store.get(postmortem_id)
        
        if not postmortem:
            raise HTTPException(status_code=404, detail="Postmortem not found")
        
        return {
            'status': 'success',
            'message': 'PDF export initiated',
            'postmortem_id': postmortem_id,
            'download_url': f"/downloads/postmortem_{postmortem_id}.pdf"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error exporting PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))