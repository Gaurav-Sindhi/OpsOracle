"""Blast Radius Service - Multi-service cascade detection"""

from typing import Dict, List
from datetime import datetime
from loguru import logger

class BlastRadiusService:
    """Detect and analyze multi-service cascade effects"""
    
    def __init__(self):
        self.services_map = {
            'lambda': ['api_gateway', 'rds', 'dynamodb'],
            'rds': ['lambda', 'api_gateway', 'ec2'],
            'api_gateway': ['lambda', 'ec2', 'cloudfront'],
            'ec2': ['rds', 'lambda', 'elb'],
            'dynamodb': ['lambda', 'api_gateway'],
            'cloudfront': ['api_gateway'],
            'elb': ['ec2', 'lambda']
        }
        logger.info("✅ Blast Radius Service initialized")
    
    def detect_cascade(self, incident_data: Dict) -> Dict:
        """Detect which services are affected by an incident"""
        try:
            primary_service = incident_data.get('service', 'unknown')
            directly_affected = [primary_service]
            cascaded_services = self._get_cascaded_services(primary_service)
            
            all_affected = list(set(directly_affected + cascaded_services))
            
            cascade_data = {
                'primary_service': primary_service,
                'directly_affected': directly_affected,
                'cascaded_services': cascaded_services,
                'all_affected_services': all_affected,
                'total_affected': len(all_affected),
                'blast_radius_level': self._calculate_severity(len(all_affected)),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"💥 Cascade detected: {len(all_affected)} services affected")
            return cascade_data
            
        except Exception as e:
            logger.error(f"❌ Error detecting cascade: {str(e)}")
            return {'error': str(e)}
    
    def _get_cascaded_services(self, primary_service: str, depth: int = 2) -> List[str]:
        """Get all cascaded services"""
        cascaded = []
        
        def traverse(service: str, current_depth: int):
            if current_depth == 0:
                return
            
            dependencies = self.services_map.get(service, [])
            for dep in dependencies:
                if dep not in cascaded:
                    cascaded.append(dep)
                    traverse(dep, current_depth - 1)
        
        traverse(primary_service, depth)
        return cascaded
    
    def _calculate_severity(self, affected_count: int) -> str:
        """Calculate severity based on affected services"""
        if affected_count <= 1:
            return 'isolated'
        elif affected_count <= 2:
            return 'low'
        elif affected_count <= 4:
            return 'medium'
        else:
            return 'critical'
    
    def estimate_impact(self, cascade_data: Dict) -> Dict:
        """Estimate business impact of the cascade"""
        try:
            affected_count = cascade_data.get('total_affected', 0)
            
            # Estimate based on services affected
            impact_scores = {
                'api_gateway': 10,  # User-facing
                'lambda': 8,
                'rds': 9,  # Data layer
                'ec2': 7,
                'dynamodb': 8,
                'cloudfront': 10,  # CDN outage critical
                'elb': 9  # Load balancing critical
            }
            
            total_impact = 0
            affected_services = cascade_data.get('all_affected_services', [])
            
            for service in affected_services:
                total_impact += impact_scores.get(service, 5)
            
            avg_impact = total_impact / len(affected_services) if affected_services else 0
            
            return {
                'total_impact_score': total_impact,
                'average_impact_per_service': round(avg_impact, 2),
                'estimated_users_affected': affected_count * 1000,  # Mock calculation
                'estimated_cost_per_minute': affected_count * 100,  # Mock calculation
                'severity_level': self._impact_to_severity(total_impact),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error estimating impact: {str(e)}")
            return {'error': str(e)}
    
    def _impact_to_severity(self, impact_score: int) -> str:
        """Convert impact score to severity level"""
        if impact_score <= 10:
            return 'LOW'
        elif impact_score <= 25:
            return 'MEDIUM'
        elif impact_score <= 40:
            return 'HIGH'
        else:
            return 'CRITICAL'
    
    def get_remediation_priority(self, cascade_data: Dict) -> List[Dict]:
        """Get priority order for fixing affected services"""
        try:
            # Services that should be fixed first (critical path)
            priority_order = [
                'cloudfront',
                'api_gateway',
                'rds',
                'dynamodb',
                'lambda',
                'ec2',
                'elb'
            ]
            
            affected_services = cascade_data.get('all_affected_services', [])
            remediation_plan = []
            
            for service in priority_order:
                if service in affected_services:
                    remediation_plan.append({
                        'service': service,
                        'priority': len(remediation_plan) + 1,
                        'estimated_fix_time_minutes': self._estimate_fix_time(service),
                        'impact_if_not_fixed': 'Critical' if service in ['api_gateway', 'rds'] else 'High'
                    })
            
            return remediation_plan
            
        except Exception as e:
            logger.error(f"❌ Error getting priority: {str(e)}")
            return []
    
    def _estimate_fix_time(self, service: str) -> int:
        """Estimate time to fix a service"""
        fix_times = {
            'cloudfront': 5,
            'api_gateway': 3,
            'rds': 10,
            'dynamodb': 5,
            'lambda': 2,
            'ec2': 8,
            'elb': 4
        }
        return fix_times.get(service, 5)

# Singleton instance
blast_radius_service = BlastRadiusService()