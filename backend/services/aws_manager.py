"""AWS Manager Service - CloudWatch, Lambda, EC2, X-Ray integration"""

import boto3
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from backend.config import Config
from loguru import logger

class AWSManager:
    """Manages all AWS interactions"""
    
    def __init__(self):
        self.cloudwatch = boto3.client(
            'cloudwatch',
            region_name=Config.AWS_REGION,
            aws_access_key_id=Config.AWS_ACCESS_KEY,
            aws_secret_access_key=Config.AWS_SECRET_KEY
        )
        self.logs = boto3.client(
            'logs',
            region_name=Config.AWS_REGION,
            aws_access_key_id=Config.AWS_ACCESS_KEY,     
            aws_secret_access_key=Config.AWS_SECRET_KEY
        )
        self.ec2 = boto3.client(
            'ec2',
            region_name=Config.AWS_REGION,
            aws_access_key_id=Config.AWS_ACCESS_KEY,
            aws_secret_access_key=Config.AWS_SECRET_KEY
        )
        self.lambda_client = boto3.client(
            'lambda',
            region_name=Config.AWS_REGION,
            aws_access_key_id=Config.AWS_ACCESS_KEY,
            aws_secret_access_key=Config.AWS_SECRET_KEY
        )
        self.xray = boto3.client(
            'xray',
            region_name=Config.AWS_REGION,
            aws_access_key_id=Config.AWS_ACCESS_KEY,
            aws_secret_access_key=Config.AWS_SECRET_KEY
        )
        logger.info("✅ AWS Manager initialized")
    
    def get_cloudwatch_logs(
        self,
        log_group: str,
        log_stream: Optional[str] = None,
        minutes_back: int = 10
    ) -> Dict:
        """Fetch CloudWatch logs from the past N minutes"""
        try:
            end_time = int(datetime.now().timestamp() * 1000)
            start_time = int((datetime.now() - timedelta(minutes=minutes_back)).timestamp() * 1000)
            
            query = f"""
            fields @timestamp, @message, @duration
            | stats count() as event_count by @message
            | sort event_count desc
            """
            
            response = self.logs.start_query(
                logGroupName=log_group,
                startTime=int(start_time / 1000),
                endTime=int(end_time / 1000),
                queryString=query
            )
            
            query_id = response['queryId']
            
            import time
            while True:
                query_response = self.logs.get_query_results(queryId=query_id)
                if query_response['status'] == 'Complete':
                    break
                time.sleep(0.5)
            
            logs = {
                'log_group': log_group,
                'logs': query_response['results'],
                'timestamp': datetime.now().isoformat(),
                'duration_minutes': minutes_back
            }
            logger.info(f"📋 Fetched {len(query_response['results'])} log entries")
            return logs
            
        except Exception as e:
            logger.error(f"❌ Error fetching CloudWatch logs: {str(e)}")
            return {'error': str(e), 'logs': []}
    
    def get_metrics(self, namespace: str, metric_name: str, minutes_back: int = 10) -> Dict:
        """Fetch CloudWatch metrics"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=minutes_back)
            
            response = self.cloudwatch.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric_name,
                StartTime=start_time,
                EndTime=end_time,
                Period=60,
                Statistics=['Average', 'Maximum', 'Minimum']
            )
            
            metrics = {
                'metric_name': metric_name,
                'namespace': namespace,
                'datapoints': response['Datapoints'],
                'timestamp': datetime.now().isoformat()
            }
            logger.info(f"📊 Fetched {len(response['Datapoints'])} metric datapoints")
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error fetching metrics: {str(e)}")
            return {'error': str(e), 'datapoints': []}
    
    def get_xray_traces(self, minutes_back: int = 10) -> Dict:
        """Get X-Ray trace data for multi-service analysis"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=minutes_back)
            
            filter_expression = "service(id(name: '*'))"
            
            response = self.xray.get_trace_summaries(
                StartTime=start_time,
                EndTime=end_time,
                FilterExpression=filter_expression
            )
            
            traces = {
                'trace_summaries': response.get('TraceSummaries', []),
                'timestamp': datetime.now().isoformat(),
                'services_affected': self._extract_services(response.get('TraceSummaries', []))
            }
            logger.info(f"🔍 Found {len(traces['services_affected'])} affected services")
            return traces
            
        except Exception as e:
            logger.error(f"❌ Error fetching X-Ray traces: {str(e)}")
            return {'error': str(e), 'trace_summaries': [], 'services_affected': []}
    
    def _extract_services(self, traces: List) -> List[str]:
        """Extract unique service names from traces"""
        services = set()
        for trace in traces:
            if 'Service' in trace:
                services.add(trace['Service']['name'])
        return list(services)
    
    def restart_lambda(self, function_name: str) -> Dict:
        """Trigger a Lambda function restart"""
        try:
            response = self.lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='Event',
                Payload=json.dumps({'action': 'restart'})
            )
            logger.info(f"🔄 Lambda {function_name} restart triggered")
            return {
                'status': 'success',
                'function': function_name,
                'status_code': response['StatusCode']
            }
        except Exception as e:
            logger.error(f"❌ Error restarting Lambda: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def scale_ec2_instance(self, instance_id: str, new_instance_type: str) -> Dict:
        """Scale EC2 instance to new type"""
        try:
            self.ec2.stop_instances(InstanceIds=[instance_id])
            logger.info(f"⏸️  EC2 {instance_id} stopped")
            
            self.ec2.modify_instance_attribute(
                InstanceId=instance_id,
                InstanceType={'Value': new_instance_type}
            )
            logger.info(f"🔧 EC2 instance type changed to {new_instance_type}")
            
            self.ec2.start_instances(InstanceIds=[instance_id])
            logger.info(f"▶️  EC2 {instance_id} started")
            
            return {
                'status': 'success',
                'instance': instance_id,
                'new_type': new_instance_type
            }
        except Exception as e:
            logger.error(f"❌ Error scaling EC2: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def get_all_services_metrics(self) -> Dict:
        """Get metrics from all connected AWS services"""
        try:
            services_metrics = {
                'lambda': self.get_metrics('AWS/Lambda', 'Duration'),
                'rds': self.get_metrics('AWS/RDS', 'DatabaseConnections'),
                'api_gateway': self.get_metrics('AWS/ApiGateway', '4XXError'),
                'ec2': self.get_metrics('AWS/EC2', 'CPUUtilization'),
                'timestamp': datetime.now().isoformat()
            }
            logger.info("📡 Fetched metrics from all services")
            return services_metrics
        except Exception as e:
            logger.error(f"❌ Error fetching service metrics: {str(e)}")
            return {'error': str(e)}

# Singleton instance
aws_manager = AWSManager() 