"""LLM Agent - Groq-powered incident analysis and reasoning (FREE, no card needed)"""

from groq import Groq
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger
from backend.config import Config

class LLMAgent:
    """LLM-based incident analysis using Groq API (free tier, Llama 3.3 70B)"""

    def __init__(self):
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"
        logger.info("✅ LLM Agent initialized with Groq API (free tier)")

    def analyze_incident(
        self,
        logs: Dict,
        metrics: Dict,
        blast_radius: Dict,
        similar_incidents: List[Dict] = None
    ) -> Dict:
        """Analyze incident using Groq API"""
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
                'model': 'llama-3.3-70b (Groq)'
            }

            logger.info(f"🧠 Groq analysis complete: Severity={severity}")
            return result

        except Exception as e:
            logger.error(f"❌ Error in Groq analysis: {str(e)}")
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
        """Build comprehensive context for LLM"""
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

    def _call_groq(self, prompt: str, max_tokens: int = 500) -> str:
        """Helper to call Groq chat completion"""
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.3
        )
        return completion.choices[0].message.content.strip()

    def _get_root_cause(self, context: str) -> str:
        """Get root cause from Groq"""
        try:
            prompt = f"""Based on the following incident context, identify the root cause in 1-2 sentences.
Be specific and technical.

{context}

Root Cause:"""
            return self._call_groq(prompt, max_tokens=300)
        except Exception as e:
            logger.error(f"❌ Error getting root cause: {str(e)}")
            return "Unable to determine root cause"

    def _get_recommended_fix(self, context: str, root_cause: str) -> str:
        """Get fix recommendation from Groq"""
        try:
            prompt = f"""Given this root cause: {root_cause}

And this incident context:
{context}

Provide a specific, actionable fix (1-3 sentences). Include specific AWS commands or configurations if applicable.

Recommended Fix:"""
            return self._call_groq(prompt, max_tokens=300)
        except Exception as e:
            logger.error(f"❌ Error getting fix: {str(e)}")
            return "Unable to determine fix"

    def _assess_severity(self, context: str, blast_radius: Dict) -> str:
        """Assess incident severity"""
        try:
            blast_level = blast_radius.get('blast_radius_level', 'unknown')
            prompt = f"""Based on blast radius level '{blast_level}' and context:
{context}

Rate severity as exactly one word from: CRITICAL, HIGH, MEDIUM, LOW

Severity:"""
            severity = self._call_groq(prompt, max_tokens=10).strip().split('\n')[0].upper()
            return severity if severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'] else 'MEDIUM'
        except Exception as e:
            logger.error(f"❌ Error assessing severity: {str(e)}")
            return 'MEDIUM'

    def _generate_remediation_steps(self, fix: str, context: str) -> List[str]:
        """Generate step-by-step remediation"""
        try:
            prompt = f"""For this fix: {fix}

Generate 3-4 specific, actionable steps to implement this fix. Number them.

Steps:"""
            text = self._call_groq(prompt, max_tokens=300)
            steps = [s.strip() for s in text.split('\n') if s.strip()]
            return steps[:4]
        except Exception as e:
            logger.error(f"❌ Error generating steps: {str(e)}")
            return ["Check logs", "Identify root cause", "Apply fix", "Monitor system"]

    def write_postmortem(self, incident_data: Dict) -> str:
        """Generate post-mortem narrative"""
        try:
            from datetime import datetime
            ts = incident_data.get('timestamp', datetime.now().isoformat())
            try:
                dt = datetime.fromisoformat(ts)
                formatted_time = dt.strftime("%d %B %Y at %H:%M:%S UTC")
            except Exception:
                formatted_time = ts

            affected = ', '.join(incident_data.get('affected_services', [])) or 'Lambda, API Gateway, RDS'

            prompt = f"""Write a professional post-mortem report for this incident. Use the EXACT values provided — do not use placeholders like [Date] or [Time].

    Incident ID: {incident_data.get('id', 'Unknown')}
    Detection Time: {formatted_time}
    Duration: {incident_data.get('duration_minutes', 45)} minutes
    Severity: {incident_data.get('severity', 'MEDIUM')}
    Service: {incident_data.get('service', 'lambda')}
    Root Cause: {incident_data.get('root_cause', 'Unknown')}
    Affected Services: {affected}
    Fix Applied: {incident_data.get('fix_applied', 'Unknown')}

    Write the following 7 sections using the exact values above:
    1. What Happened
    2. Timeline (use {formatted_time} as the detection time)
    3. Root Cause
    4. Impact (mention {affected})
    5. Resolution
    6. Lessons Learned
    7. Action Items"""

            return self._call_groq(prompt, max_tokens=1500)
        except Exception as e:
            logger.error(f"❌ Error writing postmortem: {str(e)}")
            return "Post-mortem generation failed"

# Singleton instance
llm_agent = LLMAgent()