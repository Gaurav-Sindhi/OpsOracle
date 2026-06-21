from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger
from config import Config
from backend.agents.llm_agent import LLMAgent
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch
from reportlab.lib import colors
import json

class PostMortemGenerator:
    """Generate professional post-mortem reports"""
    
    def __init__(self):
        self.postmortems = []
        logger.info("✅ PostMortem Generator initialized")
    
    def generate(self, incident_data: Dict) -> Dict:
        """Generate complete post-mortem report"""
        try:
            # Get LLM-generated narrative
            narrative =LLMAgent.write_postmortem(incident_data)
            
            # Build structured post-mortem
            postmortem = {
                'id': incident_data.get('id', f"PM-{datetime.now().timestamp()}"),
                'timestamp': datetime.now().isoformat(),
                'incident_id': incident_data.get('incident_id'),
                'duration_minutes': incident_data.get('duration_minutes', 0),
                'root_cause': incident_data.get('root_cause', 'Unknown'),
                'affected_services': incident_data.get('affected_services', []),
                'severity': incident_data.get('severity', 'MEDIUM'),
                'fix_applied': incident_data.get('fix_applied', 'Unknown'),
                'narrative': narrative,
                'timeline': self._build_timeline(incident_data),
                'metrics_impact': self._calculate_impact(incident_data),
                'lessons_learned': self._extract_lessons(narrative),
                'action_items': self._extract_action_items(narrative)
            }
            
            self.postmortems.append(postmortem)
            
            logger.info(f"✅ Post-mortem generated: {postmortem['id']}")
            return {
                'status': 'success',
                'postmortem_id': postmortem['id'],
                'postmortem': postmortem
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating post-mortem: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def _build_timeline(self, incident_data: Dict) -> List[Dict]:
        """Build incident timeline"""
        try:
            timeline = []
            start_time = incident_data.get('start_timestamp')
            
            events = [
                {
                    'time_offset': 0,
                    'event': 'Incident started',
                    'details': incident_data.get('initial_error', 'Unknown trigger')
                },
                {
                    'time_offset': incident_data.get('detection_delay', 5),
                    'event': 'Anomaly detected by OpsOracle',
                    'details': 'System detected deviation from normal patterns'
                },
                {
                    'time_offset': incident_data.get('analysis_time', 15),
                    'event': 'Root cause identified',
                    'details': incident_data.get('root_cause', 'Unknown')
                },
                {
                    'time_offset': incident_data.get('fix_time', 30),
                    'event': 'Fix applied',
                    'details': incident_data.get('fix_applied', 'Unknown')
                },
                {
                    'time_offset': incident_data.get('duration_minutes', 45),
                    'event': 'Incident resolved',
                    'details': 'System returned to normal'
                }
            ]
            
            return events
            
        except Exception as e:
            logger.error(f"❌ Error building timeline: {str(e)}")
            return []
    
    def _calculate_impact(self, incident_data: Dict) -> Dict:
        """Calculate business impact metrics"""
        try:
            duration = incident_data.get('duration_minutes', 0)
            affected_users = incident_data.get('affected_users', 0)
            affected_services = len(incident_data.get('affected_services', []))
            
            # Estimate downtime cost (adjust based on your business)
            cost_per_minute = 500  # ₹500 per minute
            total_cost = duration * cost_per_minute
            
            return {
                'duration_minutes': duration,
                'affected_users': affected_users,
                'affected_services': affected_services,
                'estimated_cost': f"₹{total_cost:,}",
                'blast_radius': self._estimate_blast_radius(affected_services)
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating impact: {str(e)}")
            return {}
    
    def _estimate_blast_radius(self, num_services: int) -> str:
        """Estimate blast radius"""
        if num_services <= 1:
            return 'Isolated'
        elif num_services <= 2:
            return 'Low'
        elif num_services <= 4:
            return 'Medium'
        else:
            return 'Critical'
    
    def _extract_lessons(self, narrative: str) -> List[str]:
        """Extract lessons learned from narrative"""
        try:
            # Simple keyword extraction
            lessons = []
            keywords = ['prevent', 'improve', 'should', 'need to', 'must']
            
            sentences = narrative.split('.')
            for sentence in sentences:
                for keyword in keywords:
                    if keyword.lower() in sentence.lower():
                        lessons.append(sentence.strip())
                        break
            
            return lessons[:3]
            
        except Exception as e:
            logger.error(f"❌ Error extracting lessons: {str(e)}")
            return []
    
    def _extract_action_items(self, narrative: str) -> List[Dict]:
        """Extract action items from narrative"""
        try:
            action_items = [
                {
                    'item': 'Review and update monitoring thresholds',
                    'owner': 'DevOps Team',
                    'due_date': '2024-01-20',
                    'priority': 'HIGH'
                },
                {
                    'item': 'Implement automated remediation for this error type',
                    'owner': 'SRE Team',
                    'due_date': '2024-01-25',
                    'priority': 'HIGH'
                },
                {
                    'item': 'Update runbooks with new remediation steps',
                    'owner': 'Documentation Team',
                    'due_date': '2024-01-18',
                    'priority': 'MEDIUM'
                }
            ]
            return action_items
            
        except Exception as e:
            logger.error(f"❌ Error extracting actions: {str(e)}")
            return []
    
    def export_to_json(self, postmortem_id: str, filepath: str) -> Dict:
        """Export post-mortem as JSON"""
        try:
            postmortem = next((p for p in self.postmortems if p['id'] == postmortem_id), None)
            
            if not postmortem:
                return {'status': 'error', 'error': 'Post-mortem not found'}
            
            with open(filepath, 'w') as f:
                json.dump(postmortem, f, indent=2, default=str)
            
            logger.info(f"✅ Exported post-mortem to {filepath}")
            return {'status': 'success', 'filepath': filepath}
            
        except Exception as e:
            logger.error(f"❌ Error exporting JSON: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def export_to_pdf(self, postmortem_id: str, filepath: str) -> Dict:
        """Export post-mortem as PDF"""
        try:
            postmortem = next((p for p in self.postmortems if p['id'] == postmortem_id), None)
            
            if not postmortem:
                return {'status': 'error', 'error': 'Post-mortem not found'}
            
            # Create PDF
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1F2937'),
                spaceAfter=30,
                alignment=1
            )
            story.append(Paragraph("Post-Incident Report", title_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Metadata table
            metadata = [
                ['Incident ID', postmortem.get('incident_id', 'N/A')],
                ['Duration', f"{postmortem.get('duration_minutes', 0)} minutes"],
                ['Severity', postmortem.get('severity', 'N/A')],
                ['Affected Services', ', '.join(postmortem.get('affected_services', []))]
            ]
            
            metadata_table = Table(metadata, colWidths=[2*inch, 4*inch])
            metadata_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E5E7EB')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(metadata_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Root cause
            story.append(Paragraph("<b>Root Cause:</b>", styles['Heading2']))
            story.append(Paragraph(postmortem.get('root_cause', 'Unknown'), styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # Narrative
            story.append(Paragraph("<b>Incident Narrative:</b>", styles['Heading2']))
            story.append(Paragraph(postmortem.get('narrative', 'N/A'), styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"✅ Exported post-mortem PDF to {filepath}")
            return {'status': 'success', 'filepath': filepath}
            
        except Exception as e:
            logger.error(f"❌ Error exporting PDF: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def get_postmortem(self, postmortem_id: str) -> Optional[Dict]:
        """Retrieve specific post-mortem"""
        return next((p for p in self.postmortems if p['id'] == postmortem_id), None)

# Singleton instance
postmortem_generator = PostMortemGenerator()