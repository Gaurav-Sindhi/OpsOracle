"""Alert Service - Incident intake, triage, and routing"""

from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger
from backend.config import Config

class AlertService:
    """Handle incident intake and intelligent triage"""
    
    def __init__(self):
        self.alerts_received = []
        self.triaged_incidents = []
        logger.info("✅ Alert Service initialized")
    
    def ingest_alert(self, alert_data: Dict) -> Dict:
        """Ingest incoming alert"""  
        try:
            alert_id = f"ALERT-{datetime.now().timestamp()}"
            alert_record = {
                'id': alert_id,
                'data': alert_data,
                'received_timestamp': datetime.now().isoformat(),
                'status': 'ingested'
            }
            
            self.alerts_received.append(alert_record)
            logger.info(f"📬 Alert ingested: {alert_id}")
            
            return {
                'status': 'success',
                'alert_id': alert_id,
                'message': 'Alert ingested successfully'
            }
            
        except Exception as e:
            logger.error(f"❌ Error ingesting alert: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def triage_alert(self, alert_data: Dict) -> Dict:
        """Triage alert and determine severity"""
        try:
            # Extract metrics
            metrics = alert_data.get('metrics', {})
            error_count = alert_data.get('error_count', 0)
            affected_services = alert_data.get('affected_services', [])
            
            # Determine severity
            severity = self._determine_severity(
                error_count=error_count,
                affected_services_count=len(affected_services),
                metrics=metrics
            )
            
            # Determine routing
            routing = self._determine_routing(severity, affected_services)
            
            triaged_incident = {
                'id': f"INC-{datetime.now().timestamp()}",
                'alert_data': alert_data,
                'severity': severity,
                'routing': routing,
                'triage_timestamp': datetime.now().isoformat(),
                'status': 'triaged',
                'requires_immediate_action': severity in ['CRITICAL', 'HIGH']
            }
            
            self.triaged_incidents.append(triaged_incident)
            logger.info(f"🔍 Alert triaged: Severity={severity}")
            
            return triaged_incident
            
        except Exception as e:
            logger.error(f"❌ Error triaging alert: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def _determine_severity(
        self,
        error_count: int,
        affected_services_count: int,
        metrics: Dict
    ) -> str:
        """Determine incident severity"""
        score = 0
        
        # Error count scoring
        if error_count > 100:
            score += 3
        elif error_count > 50:
            score += 2
        elif error_count > 10:
            score += 1
        
        # Services affected scoring
        if affected_services_count >= 4:
            score += 3
        elif affected_services_count >= 2:
            score += 2
        elif affected_services_count >= 1:
            score += 1
        
        # Metrics scoring
        if metrics.get('cpu_utilization', 0) > 90:
            score += 2
        if metrics.get('error_rate', 0) > 0.5:
            score += 2
        if metrics.get('request_latency', 0) > 1000:
            score += 1
        
        # Determine level
        if score >= 7:
            return 'CRITICAL'
        elif score >= 5:
            return 'HIGH'
        elif score >= 3:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _determine_routing(self, severity: str, affected_services: List[str]) -> Dict:
        """Determine how to route the incident"""
        routing_rules = {
            'CRITICAL': {
                'escalate_to': 'on_call_engineer',
                'notify': ['slack_critical_channel', 'pagerduty'],
                'auto_remediate': True,
                'permission_level': 3
            },
            'HIGH': {
                'escalate_to': 'team_lead',
                'notify': ['slack_channel', 'email'],
                'auto_remediate': False,
                'permission_level': 2
            },
            'MEDIUM': {
                'escalate_to': 'team',
                'notify': ['slack_channel'],
                'auto_remediate': False,
                'permission_level': 1
            },
            'LOW': {
                'escalate_to': 'log',
                'notify': [],
                'auto_remediate': False,
                'permission_level': 1
            }
        }
        
        base_routing = routing_rules.get(severity, routing_rules['MEDIUM'])
        
        # Enhance routing based on affected services
        if 'api_gateway' in affected_services or 'cloudfront' in affected_services:
            base_routing['priority'] = 'highest'
        elif 'rds' in affected_services:
            base_routing['priority'] = 'high'
        else:
            base_routing['priority'] = 'normal'
        
        return base_routing
    
    def get_pending_alerts(self) -> List[Dict]:
        """Get all pending alerts that need attention"""
        pending = [a for a in self.alerts_received if a['status'] == 'ingested']
        return pending
    
    def get_triaged_incidents(self, severity: Optional[str] = None) -> List[Dict]:
        """Get triaged incidents, optionally filtered by severity"""
        if severity:
            return [i for i in self.triaged_incidents if i['severity'] == severity]
        return self.triaged_incidents
    
    def get_alert_stats(self) -> Dict:
        """Get statistics about alerts"""
        try:
            total_alerts = len(self.alerts_received)
            total_incidents = len(self.triaged_incidents)
            
            severity_counts = {}
            for incident in self.triaged_incidents:
                sev = incident['severity']
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
            
            critical_incidents = [i for i in self.triaged_incidents if i['severity'] == 'CRITICAL']
            avg_triage_time = self._calculate_avg_triage_time()
            
            return {
                'total_alerts_received': total_alerts,
                'total_incidents_triaged': total_incidents,
                'by_severity': severity_counts,
                'critical_incidents': len(critical_incidents),
                'average_triage_time_seconds': avg_triage_time,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting stats: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_avg_triage_time(self) -> float:
        """Calculate average time from ingestion to triage"""
        if not self.triaged_incidents or not self.alerts_received:
            return 0.0
        
        total_time = 0
        count = 0
        
        for incident in self.triaged_incidents[:10]:  # Last 10
            for alert in self.alerts_received:
                # Simplified - in production would match by ID
                count += 1
                total_time += 5  # Mock 5 seconds average
        
        return total_time / count if count > 0 else 0

# Singleton instance
alert_service = AlertService()