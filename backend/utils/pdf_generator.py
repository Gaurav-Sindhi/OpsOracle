"""PDF Generator - Export postmortems and reports to PDF"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import json
from datetime import datetime
from loguru import logger

class PDFGenerator:
    """Generate professional PDF reports"""
    
    def __init__(self):
        logger.info("✅ PDF Generator initialized")
    
    def generate_postmortem_pdf(self, postmortem: dict, filepath: str) -> dict:
        """Generate postmortem as PDF"""
        try:
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1F2937'),
                spaceAfter=30
            )
            story.append(Paragraph("Post-Incident Report", title_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Metadata
            metadata = [
                ['Incident ID', postmortem.get('incident_id', 'N/A')],
                ['Duration', f"{postmortem.get('duration_minutes', 0)} minutes"],
                ['Severity', postmortem.get('severity', 'N/A')]
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
            
            # Root Cause
            story.append(Paragraph("<b>Root Cause:</b>", styles['Heading2']))
            story.append(Paragraph(postmortem.get('root_cause', 'Unknown'), styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # Narrative
            story.append(Paragraph("<b>Narrative:</b>", styles['Heading2']))
            story.append(Paragraph(postmortem.get('narrative', 'N/A'), styles['Normal']))
            
            # Build
            doc.build(story)
            logger.info(f"✅ PDF generated: {filepath}")
            
            return {
                'status': 'success',
                'filepath': filepath,
                'size': 'calculated'
            }
        except Exception as e:
            logger.error(f"❌ Error generating PDF: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def generate_incident_report(self, incident: dict, filepath: str) -> dict:
        """Generate incident report as PDF"""
        try:
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            story.append(Paragraph("Incident Report", styles['Title']))
            story.append(Spacer(1, 0.3*inch))
            
            # Details
            story.append(Paragraph(f"Incident ID: {incident.get('id', 'N/A')}", styles['Normal']))
            story.append(Paragraph(f"Severity: {incident.get('severity', 'N/A')}", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # Analysis
            analysis = incident.get('analysis', {})
            story.append(Paragraph("<b>Analysis:</b>", styles['Heading2']))
            story.append(Paragraph(f"Root Cause: {analysis.get('root_cause', 'N/A')}", styles['Normal']))
            story.append(Paragraph(f"Fix: {analysis.get('recommended_fix', 'N/A')}", styles['Normal']))
            
            doc.build(story)
            logger.info(f"✅ Incident report PDF generated: {filepath}")
            
            return {
                'status': 'success',
                'filepath': filepath
            }
        except Exception as e:
            logger.error(f"❌ Error generating incident report: {str(e)}")
            return {'status': 'error', 'error': str(e)}