import json
import re
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger

class LogParser:
    """Parse and structure CloudWatch and application logs"""
    
    def __init__(self):
        self.error_patterns = {
            'timeout': r'(timeout|timed out|deadline exceeded)',
            'memory': r'(out of memory|memory limit|heap size)',
            'connection': r'(connection refused|connection timeout|no route)',
            'permission': r'(permission denied|access denied|forbidden)',
            'resource': r'(resource not found|no such file|not found)',
            'cpu': r'(high cpu|cpu spike|cpu usage)',
            'database': r'(database error|connection pool|query failed)',
        }
        logger.info("✅ LogParser initialized")
    
    def parse_raw_logs(self, raw_logs: str) -> Dict:
        """Parse raw log text into structured format"""
        try:
            lines = raw_logs.split('\n')
            parsed_logs = []
            
            for line in lines:
                if not line.strip():
                    continue
                
                parsed_entry = self._parse_log_line(line)
                if parsed_entry:
                    parsed_logs.append(parsed_entry)
            
            summary = self._summarize_logs(parsed_logs)
            
            result = {
                'logs': parsed_logs,
                'summary': summary,
                'error_count': len([l for l in parsed_logs if l['severity'] == 'ERROR']),
                'warning_count': len([l for l in parsed_logs if l['severity'] == 'WARNING']),
                'parsed_timestamp': datetime.now().isoformat()
            }
            logger.info(f"📊 Parsed {len(parsed_logs)} log entries")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error parsing logs: {str(e)}")
            return {'error': str(e), 'logs': []}
    
    def _parse_log_line(self, line: str) -> Optional[Dict]:
        """Parse individual log line"""
        try:
            # Try JSON format first
            try:
                log_json = json.loads(line)
                return self._format_log_entry(log_json)
            except json.JSONDecodeError:
                pass
            
            # Parse text format
            timestamp = self._extract_timestamp(line)
            severity = self._extract_severity(line)
            message = line
            error_type = self._classify_error(line)
            
            return {
                'timestamp': timestamp,
                'severity': severity,
                'message': message,
                'error_type': error_type,
                'raw': line
            }
            
        except Exception as e:
            logger.debug(f"Could not parse log line: {str(e)}")
            return None
    
    def _format_log_entry(self, log_json: Dict) -> Dict:
        """Format JSON log entry"""
        return {
            'timestamp': log_json.get('@timestamp', datetime.now().isoformat()),
            'severity': log_json.get('level', 'INFO').upper(),
            'message': log_json.get('@message', log_json.get('message', '')),
            'error_type': self._classify_error(str(log_json)),
            'raw': json.dumps(log_json)
        }
    
    def _extract_timestamp(self, line: str) -> str:
        """Extract timestamp from log line"""
        timestamp_pattern = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
        match = re.search(timestamp_pattern, line)
        return match.group(0) if match else datetime.now().isoformat()
    
    def _extract_severity(self, line: str) -> str:
        """Extract severity level from log"""
        line_upper = line.upper()
        if 'ERROR' in line_upper or 'FATAL' in line_upper:
            return 'ERROR'
        elif 'WARN' in line_upper:
            return 'WARNING'
        elif 'DEBUG' in line_upper:
            return 'DEBUG'
        return 'INFO'
    
    def _classify_error(self, line: str) -> Optional[str]:
        """Classify error type based on content"""
        for error_type, pattern in self.error_patterns.items():
            if re.search(pattern, line, re.IGNORECASE):
                return error_type
        return None
    
    def _summarize_logs(self, logs: List[Dict]) -> str:
        """Generate summary of logs"""
        if not logs:
            return "No errors found"
        
        error_logs = [l for l in logs if l['severity'] == 'ERROR']
        if not error_logs:
            return "No critical errors found"
        
        # Get most common error type
        error_types = [l['error_type'] for l in error_logs if l['error_type']]
        most_common = max(set(error_types), key=error_types.count) if error_types else 'unknown'
        
        summary = f"Found {len(error_logs)} errors, mostly {most_common} errors"
        return summary
    
    def extract_blast_radius(self, logs: Dict) -> Dict:
        """Identify affected services from logs"""
        try:
            affected_services = {
                'lambda': False,
                'rds': False,
                'api_gateway': False,
                'ec2': False,
                'external_service': False
            }
            
            logs_text = str(logs)
            
            if 'lambda' in logs_text.lower():
                affected_services['lambda'] = True
            if 'rds' in logs_text.lower() or 'database' in logs_text.lower():
                affected_services['rds'] = True
            if 'api' in logs_text.lower() or 'gateway' in logs_text.lower():
                affected_services['api_gateway'] = True
            if 'ec2' in logs_text.lower() or 'instance' in logs_text.lower():
                affected_services['ec2'] = True
            if 'http' in logs_text.lower() or 'external' in logs_text.lower():
                affected_services['external_service'] = True
            
            affected_count = sum(affected_services.values())
            
            result = {
                'affected_services': affected_services,
                'affected_count': affected_count,
                'blast_radius_level': self._calculate_blast_radius(affected_count)
            }
            logger.info(f"💥 Blast radius: {result['blast_radius_level']} ({affected_count} services)")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error extracting blast radius: {str(e)}")
            return {'affected_services': {}, 'affected_count': 0, 'blast_radius_level': 'unknown'}
    
    def _calculate_blast_radius(self, affected_count: int) -> str:
        """Calculate blast radius level"""
        if affected_count == 0:
            return 'isolated'
        elif affected_count == 1:
            return 'low'
        elif affected_count <= 3:
            return 'medium'
        else:
            return 'critical'

# Singleton instance
log_parser = LogParser()