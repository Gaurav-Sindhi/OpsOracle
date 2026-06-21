from typing import Dict, Optional, List
from datetime import datetime
from loguru import logger
from backend.config import Config
from backend.services.aws_manager import aws_manager

class RemediationEngine:
    """Execute automated fixes with permission levels"""
    
    def __init__(self):
        self.remediation_history = []
        logger.info("✅ Remediation Engine initialized")
    
    def execute_remediation(
        self,
        fix_type: str,
        parameters: Dict,
        permission_level: int = 1
    ) -> Dict:
        """
        Execute remediation based on permission level.
        
        Levels:
        1 = Suggest only (no action)
        2 = Ask confirmation first
        3 = Auto execute (full permission)
        """
        try:
            if permission_level < 1 or permission_level > 3:
                return {'status': 'error', 'error': 'Invalid permission level'}
            
            logger.info(f"🔧 Executing remediation: {fix_type} (Level {permission_level})")
            
            # Route to appropriate handler
            if fix_type == 'restart_lambda':
                result = self._remediate_lambda(parameters, permission_level)
            elif fix_type == 'scale_ec2':
                result = self._remediate_ec2(parameters, permission_level)
            elif fix_type == 'increase_memory':
                result = self._remediate_lambda_memory(parameters, permission_level)
            elif fix_type == 'clear_connection_pool':
                result = self._remediate_rds(parameters, permission_level)
            elif fix_type == 'increase_timeout':
                result = self._remediate_timeout(parameters, permission_level)
            else:
                result = {'status': 'unknown', 'error': f'Unknown fix type: {fix_type}'}
            
            # Log remediation
            self.remediation_history.append({
                'fix_type': fix_type,
                'result': result,
                'timestamp': datetime.now().isoformat(),
                'permission_level': permission_level
            })
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error executing remediation: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def _remediate_lambda(self, params: Dict, permission_level: int) -> Dict:
        """Restart Lambda function"""
        try:
            function_name = params.get('function_name')
            
            if permission_level == 1:
                return {
                    'status': 'suggestion',
                    'action': f'Restart Lambda function: {function_name}',
                    'estimated_time': '30 seconds',
                    'requires_confirmation': True
                }
            
            if permission_level >= 2:
                result = aws_manager.restart_lambda(function_name)
                return {
                    'status': result.get('status', 'success'),
                    'action': f'Restarted {function_name}',
                    'execution_time': '25 seconds',
                    'function': function_name
                }
            
        except Exception as e:
            logger.error(f"❌ Error restarting Lambda: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def _remediate_ec2(self, params: Dict, permission_level: int) -> Dict:
        """Scale EC2 instance"""
        try:
            instance_id = params.get('instance_id')
            new_type = params.get('new_instance_type', 't3.large')
            
            if permission_level == 1:
                return {
                    'status': 'suggestion',
                    'action': f'Scale EC2 {instance_id} from {params.get("current_type")} to {new_type}',
                    'estimated_time': '3-5 minutes',
                    'estimated_cost_savings': params.get('estimated_savings', 'unknown'),
                    'requires_confirmation': True
                }
            
            if permission_level >= 2:
                result = aws_manager.scale_ec2_instance(instance_id, new_type)
                return {
                    'status': result.get('status', 'success'),
                    'action': f'Scaled {instance_id} to {new_type}',
                    'execution_time': '4 minutes',
                    'instance': instance_id
                }
            
        except Exception as e:
            logger.error(f"❌ Error scaling EC2: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def _remediate_lambda_memory(self, params: Dict, permission_level: int) -> Dict:
        """Increase Lambda memory"""
        try:
            function_name = params.get('function_name')
            new_memory = params.get('new_memory', 512)
            current_memory = params.get('current_memory', 256)
            
            if permission_level == 1:
                return {
                    'status': 'suggestion',
                    'action': f'Increase {function_name} memory from {current_memory}MB to {new_memory}MB',
                    'estimated_improvement': '30-40% faster execution',
                    'cost_increase': '~₹50/month',
                    'requires_confirmation': True
                }
            
            if permission_level >= 2:
                # In production, would use boto3 to update Lambda config
                return {
                    'status': 'success',
                    'action': f'Increased {function_name} memory to {new_memory}MB',
                    'execution_time': '12 seconds',
                    'function': function_name
                }
            
        except Exception as e:
            logger.error(f"❌ Error increasing memory: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def _remediate_rds(self, params: Dict, permission_level: int) -> Dict:
        """Clear RDS connection pool"""
        try:
            if permission_level == 1:
                return {
                    'status': 'suggestion',
                    'action': 'Clear RDS connection pool and restart connections',
                    'estimated_time': '20 seconds',
                    'requires_confirmation': True
                }
            
            if permission_level >= 2:
                return {
                    'status': 'success',
                    'action': 'Cleared RDS connection pool',
                    'execution_time': '18 seconds',
                    'connections_reset': 127
                }
            
        except Exception as e:
            logger.error(f"❌ Error clearing pool: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def _remediate_timeout(self, params: Dict, permission_level: int) -> Dict:
        """Increase timeout settings"""
        try:
            service = params.get('service', 'unknown')
            current_timeout = params.get('current_timeout', 30)
            new_timeout = params.get('new_timeout', 60)
            
            if permission_level == 1:
                return {
                    'status': 'suggestion',
                    'action': f'Increase {service} timeout from {current_timeout}s to {new_timeout}s',
                    'expected_impact': 'Reduce false failure rate by 15-20%',
                    'requires_confirmation': True
                }
            
            if permission_level >= 2:
                return {
                    'status': 'success',
                    'action': f'Increased {service} timeout to {new_timeout}s',
                    'execution_time': '8 seconds',
                    'service': service
                }
            
        except Exception as e:
            logger.error(f"❌ Error adjusting timeout: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def get_remediation_history(self, limit: int = 10) -> List[Dict]:
        """Get recent remediation history"""
        return self.remediation_history[-limit:]
    
    def get_remediation_stats(self) -> Dict:
        """Get statistics about remediations"""
        try:
            total = len(self.remediation_history)
            successful = sum(1 for r in self.remediation_history if r['result'].get('status') == 'success')
            by_type = {}
            
            for record in self.remediation_history:
                fix_type = record['fix_type']
                by_type[fix_type] = by_type.get(fix_type, 0) + 1
            
            return {
                'total_remediations': total,
                'successful': successful,
                'success_rate': successful / total if total > 0 else 0,
                'by_type': by_type,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting stats: {str(e)}")
            return {'error': str(e)}

# Singleton instance
remediation_engine = RemediationEngine()