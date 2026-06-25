"""LLM Agent - Claude API-powered incident analysis and reasoning"""
 
import anthropic
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger
from backend.config import Config
from backend.services.rag_service import rag_service
 
class LLMAgent:
    """LLM-based incident analysis using Claude API (Anthropic)"""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=Config.CLAUDE_API_KEY)
        self.model = "claude-3-5-sonnet-20241022"  # Claude 3.5 Sonnet
        logger.info("✅ LLM Agent initialized with Claude API (Anthropic)")
    
    def analyze_incident(
        self,
        logs: Dict,
        metrics: Dict,
        blast_radius: Dict,
        similar_incidents: List[Dict] = None
    ) -> Dict:
        """Analyze incident using Claude API"""
        try:
            context = self._build_analysis_context(
                logs, metrics, blast_radius, similar_incidents
            )
            
            root_cause = self._get_root_cause(context)
            fix = self._get_recommended_fix(context, root_cause)
            severity = self._assess_severity(context, blast_radius)
            remediation_steps = self._generate_remediation_steps(fix, context)
            
            result = {
                'root_cause': root_cause,
                'recommended_fix': fix,
                'severity': severity,
                'remediation_steps': remediation_steps,
                'confidence': 0.85,
                'timestamp': datetime.now().isoformat(),
                'model': 'claude-3-5-sonnet'
            }
            
            logger.info(f"🧠 Claude analysis complete: Severity={severity}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in Claude analysis: {str(e)}")
            return {
                'error': str(e),
                'root_cause': 'Unable to determine',
                'recommended_fix': 'Contact support',
                'severity': 'unknown'
            }
    
    def _build_analysis_context(
        self,
        logs: Dict,
        metrics: Dict,
        blast_radius: Dict,
        similar_incidents: List[Dict] = None
    ) -> str:
        """Build comprehensive context for Claude"""
        parts = ["=== INCIDENT ANALYSIS CONTEXT ===\n"]
        
        if logs and 'summary' in logs:
            parts.append(f"Log Summary: {logs['summary']}")
            parts.append(f"Error Count: {logs.get('error_count', 0)}")
            parts.append(f"Warning Count: {logs.get('warning_count', 0)}")
        
        if metrics:
            parts.append("\nCurrent Metrics:")
            for key, value in metrics.items():
                if key not in ['timestamp']:
                    parts.append(f"  - {key}: {value}")
        
        if blast_radius:
            parts.append(f"\nBlast Radius: {blast_radius.get('blast_radius_level', 'unknown')}")
            parts.append(f"Affected Services: {blast_radius.get('affected_count', 0)} services")
        
        if similar_incidents:
            parts.append("\nSimilar Historical Incidents:")
            for incident in similar_incidents[:2]:
                parts.append(f"  - {incident['incident'].get('root_cause', 'N/A')}")
        
        parts.append("\n=== END CONTEXT ===")
        return '\n'.join(parts)
    
    def _get_root_cause(self, context: str) -> str:
        """Get root cause from Claude"""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Based on the following incident context, identify the root cause in 1-2 sentences.
Be specific and technical.
 
{context}
 
Root Cause:"""
                    }
                ]
            )
            return message.content[0].text.strip()
        except Exception as e:
            logger.error(f"❌ Error getting root cause: {str(e)}")
            return "Unable to determine root cause"
    
    def _get_recommended_fix(self, context: str, root_cause: str) -> str:
        """Get fix recommendation from Claude"""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Given this root cause: {root_cause}
 
And this incident context:
{context}
 
Provide a specific, actionable fix (1-3 sentences). Include specific AWS commands or configurations if applicable.
 
Recommended Fix:"""
                    }
                ]
            )
            return message.content[0].text.strip()
        except Exception as e:
            logger.error(f"❌ Error getting fix: {str(e)}")
            return "Unable to determine fix"
    
    def _assess_severity(self, context: str, blast_radius: Dict) -> str:
        """Assess incident severity"""
        try:
            blast_level = blast_radius.get('blast_radius_level', 'unknown')
            message = self.client.messages.create(
                model=self.model,
                max_tokens=100,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Based on blast radius level '{blast_level}' and context:
{context}
 
Rate severity as one of: CRITICAL, HIGH, MEDIUM, LOW
 
Severity:"""
                    }
                ]
            )
            severity = message.content[0].text.strip().split('\n')[0]
            return severity if severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'] else 'MEDIUM'
        except Exception as e:
            logger.error(f"❌ Error assessing severity: {str(e)}")
            return 'MEDIUM'
    
    def _generate_remediation_steps(self, fix: str, context: str) -> List[str]:
        """Generate step-by-step remediation"""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": f"""For this fix: {fix}
 
Generate 3-4 specific, actionable steps to implement this fix. Number them.
 
Steps:"""
                    }
                ]
            )
            steps = [s.strip() for s in message.content[0].text.strip().split('\n') if s.strip()]
            return steps[:4]
        except Exception as e:
            logger.error(f"❌ Error generating steps: {str(e)}")
            return ["Check logs", "Identify root cause", "Apply fix", "Monitor system"]
    
    def write_postmortem(self, incident_data: Dict) -> str:
        """Generate post-mortem narrative using Claude"""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Generate a professional post-mortem report for this incident:
            
Incident ID: {incident_data.get('id', 'Unknown')}
Duration: {incident_data.get('duration_minutes', 0)} minutes
Root Cause: {incident_data.get('root_cause', 'Unknown')}
Services Affected: {', '.join(incident_data.get('affected_services', []))}
Fix Applied: {incident_data.get('fix_applied', 'Unknown')}
 
Include sections:
1. What Happened
2. Timeline
3. Root Cause
4. Impact
5. Resolution
6. Lessons Learned
7. Action Items"""
                    }
                ]
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"❌ Error writing postmortem: {str(e)}")
            return "Post-mortem generation failed"
 
# Singleton instance
llm_agent = LLMAgent()    