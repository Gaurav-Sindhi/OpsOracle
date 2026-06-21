from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger
from backend.config import Config
import json

class IncidentStore:
    """Store and retrieve incidents from database"""
    
    def __init__(self):
        # In-memory store for now (replace with DynamoDB/MongoDB in production)
        self.incidents = []
        self.incident_index = {}
        logger.info("✅ Incident Store initialized")
    
    def save_incident(self, incident: Dict) -> Dict:
        """Save incident to storage"""
        try:
            incident_id = incident.get('id', f"INC-{datetime.now().timestamp()}")
            incident['id'] = incident_id
            incident['saved_timestamp'] = datetime.now().isoformat()
            
            self.incidents.append(incident)
            self.incident_index[incident_id] = len(self.incidents) - 1
            
            logger.info(f"💾 Incident saved: {incident_id}")
            return {
                'status': 'success',
                'incident_id': incident_id
            }
            
        except Exception as e:
            logger.error(f"❌ Error saving incident: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def get_incident(self, incident_id: str) -> Optional[Dict]:
        """Retrieve incident by ID"""
        try:
            if incident_id in self.incident_index:
                idx = self.incident_index[incident_id]
                return self.incidents[idx]
            
            logger.warning(f"⚠️  Incident not found: {incident_id}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error retrieving incident: {str(e)}")
            return None
    
    def list_incidents(
        self,
        limit: int = 50,
        offset: int = 0,
        filter_by: Optional[Dict] = None
    ) -> List[Dict]:
        """List incidents with optional filtering"""
        try:
            results = self.incidents[offset:offset + limit]
            
            # Apply filters
            if filter_by:
                results = self._apply_filters(results, filter_by)
            
            # Sort by timestamp descending
            results.sort(
                key=lambda x: x.get('saved_timestamp', ''),
                reverse=True
            )
            
            logger.info(f"📋 Retrieved {len(results)} incidents")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error listing incidents: {str(e)}")
            return []
    
    def _apply_filters(self, incidents: List[Dict], filters: Dict) -> List[Dict]:
        """Apply filters to incidents"""
        filtered = incidents
        
        if 'severity' in filters:
            filtered = [
                i for i in filtered
                if i.get('severity') == filters['severity']
            ]
        
        if 'service' in filters:
            filtered = [
                i for i in filtered
                if filters['service'] in i.get('affected_services', [])
            ]
        
        if 'error_type' in filters:
            filtered = [
                i for i in filtered
                if i.get('error_type') == filters['error_type']
            ]
        
        if 'date_from' in filters:
            filtered = [
                i for i in filtered
                if i.get('saved_timestamp', '') >= filters['date_from']
            ]
        
        return filtered
    
    def update_incident(self, incident_id: str, updates: Dict) -> Dict:
        """Update incident data"""
        try:
            if incident_id not in self.incident_index:
                return {'status': 'error', 'error': 'Incident not found'}
            
            idx = self.incident_index[incident_id]
            incident = self.incidents[idx]
            
            incident.update(updates)
            incident['updated_timestamp'] = datetime.now().isoformat()
            
            logger.info(f"✏️  Incident updated: {incident_id}")
            return {
                'status': 'success',
                'incident_id': incident_id
            }
            
        except Exception as e:
            logger.error(f"❌ Error updating incident: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def delete_incident(self, incident_id: str) -> Dict:
        """Delete incident from storage"""
        try:
            if incident_id not in self.incident_index:
                return {'status': 'error', 'error': 'Incident not found'}
            
            idx = self.incident_index[incident_id]
            del self.incidents[idx]
            del self.incident_index[incident_id]
            
            logger.info(f"🗑️  Incident deleted: {incident_id}")
            return {
                'status': 'success',
                'incident_id': incident_id
            }
            
        except Exception as e:
            logger.error(f"❌ Error deleting incident: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def get_statistics(self) -> Dict:
        """Get incident statistics"""
        try:
            total = len(self.incidents)
            
            # Count by severity
            severity_counts = {}
            error_type_counts = {}
            service_counts = {}
            
            for incident in self.incidents:
                # Severity
                severity = incident.get('severity', 'unknown')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                # Error type
                error_type = incident.get('error_type', 'unknown')
                error_type_counts[error_type] = error_type_counts.get(error_type, 0) + 1
                
                # Services
                for service in incident.get('affected_services', []):
                    service_counts[service] = service_counts.get(service, 0) + 1
            
            # Calculate average duration
            durations = [i.get('duration_minutes', 0) for i in self.incidents]
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            return {
                'total_incidents': total,
                'average_duration_minutes': round(avg_duration, 2),
                'by_severity': severity_counts,
                'by_error_type': error_type_counts,
                'by_service': service_counts,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting statistics: {str(e)}")
            return {'error': str(e)}
    
    def export_incidents(self, filepath: str, limit: int = None) -> Dict:
        """Export incidents to JSON file"""
        try:
            incidents = self.incidents[:limit] if limit else self.incidents
            
            with open(filepath, 'w') as f:
                json.dump(incidents, f, indent=2, default=str)
            
            logger.info(f"✅ Exported {len(incidents)} incidents to {filepath}")
            return {
                'status': 'success',
                'filepath': filepath,
                'count': len(incidents)
            }
            
        except Exception as e:
            logger.error(f"❌ Error exporting incidents: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def import_incidents(self, filepath: str) -> Dict:
        """Import incidents from JSON file"""
        try:
            with open(filepath, 'r') as f:
                incidents = json.load(f)
            
            count = 0
            for incident in incidents:
                result = self.save_incident(incident)
                if result['status'] == 'success':
                    count += 1
            
            logger.info(f"✅ Imported {count} incidents from {filepath}")
            return {
                'status': 'success',
                'count_imported': count
            }
            
        except Exception as e:
            logger.error(f"❌ Error importing incidents: {str(e)}")
            return {'status': 'error', 'error': str(e)}

# Singleton instance
incident_store = IncidentStore()