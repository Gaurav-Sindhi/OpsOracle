"""PDF Generator - Post-mortem report generation using ReportLab"""

import io
from datetime import datetime
from typing import Dict, List
from loguru import logger

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT


class PDFGenerator:
    """Generates professional post-mortem PDF reports"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        logger.info("✅ PDF Generator initialized")

    def _setup_styles(self):
        self.title_style = ParagraphStyle(
            "OC_Title",
            parent=self.styles["Title"],
            fontSize=20,
            leading=26,
            textColor=colors.HexColor("#0F172A"),
            spaceAfter=4,
            fontName="Helvetica-Bold"
        )
        self.subtitle_style = ParagraphStyle(
            "OC_Sub",
            parent=self.styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#64748B"),
            spaceAfter=20,
            fontName="Helvetica"
        )
        self.h1_style = ParagraphStyle(
            "OC_H1",
            parent=self.styles["Heading1"],
            fontSize=13,
            leading=18,
            textColor=colors.HexColor("#0F172A"),
            spaceBefore=16,
            spaceAfter=6,
            fontName="Helvetica-Bold"
        )
        self.body_style = ParagraphStyle(
            "OC_Body",
            parent=self.styles["Normal"],
            fontSize=10,
            leading=16,
            textColor=colors.HexColor("#334155"),
            spaceAfter=6,
            fontName="Helvetica"
        )
        self.mono_style = ParagraphStyle(
            "OC_Mono",
            parent=self.styles["Normal"],
            fontSize=9,
            leading=14,
            textColor=colors.HexColor("#1E40AF"),
            fontName="Courier",
            backColor=colors.HexColor("#EFF6FF"),
            leftIndent=8,
            rightIndent=8,
            spaceAfter=8
        )
        self.label_style = ParagraphStyle(
            "OC_Label",
            parent=self.styles["Normal"],
            fontSize=8,
            textColor=colors.HexColor("#94A3B8"),
            fontName="Helvetica",
            spaceAfter=2,
            spaceBefore=8
        )

    def generate_postmortem_pdf(self, data: Dict) -> bytes:
        """Generate a complete post-mortem PDF report and return as bytes"""
        try:
            buffer = io.BytesIO()

            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                leftMargin=20*mm,
                rightMargin=20*mm,
                topMargin=20*mm,
                bottomMargin=20*mm
            )

            story = []

            # ── Header ──────────────────────────────────────────────────────
            story.append(Paragraph("OpsOracle", self.title_style))
            story.append(Paragraph("Incident Post-Mortem Report", self.subtitle_style))
            story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0F172A")))
            story.append(Spacer(1, 8))

            # ── Metadata table ───────────────────────────────────────────────
            sev = data.get('severity', 'MEDIUM').upper()
            sev_colors = {
                'CRITICAL': '#FF3B30', 'HIGH': '#FF9500',
                'MEDIUM': '#007AFF', 'LOW': '#34C759'
            }
            sev_color = sev_colors.get(sev, '#64748B')

            ts = data.get('timestamp', datetime.now().isoformat())
            try:
                dt = datetime.fromisoformat(ts)
                ts_formatted = dt.strftime("%d %B %Y, %H:%M:%S UTC")
            except Exception:
                ts_formatted = ts

            affected = data.get('affected_services', [])
            affected_str = ', '.join(affected) if affected else '—'

            meta_data = [
                ["Incident ID", data.get('id', '—')],
                ["Generated", ts_formatted],
                ["Severity", sev],
                ["Affected Services", affected_str],
                ["Anomaly Score", str(data.get('anomaly_score', '—'))],
                ["LLM Model", data.get('model', 'Llama 3.3 70B (Groq)')]
            ]

            meta_table = Table(meta_data, colWidths=[45*mm, 125*mm])
            meta_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#F1F5F9")),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor("#64748B")),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor("#0F172A")),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ('PADDING', (0, 0), (-1, -1), 6),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))

            story.append(meta_table)
            story.append(Spacer(1, 12))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0")))

            # ── Root Cause ───────────────────────────────────────────────────
            story.append(Paragraph("Root Cause", self.h1_style))
            root_cause = data.get('root_cause', 'Root cause analysis not available')
            story.append(Paragraph(root_cause, self.body_style))

            # ── Post-Mortem Narrative ────────────────────────────────────────
            story.append(Paragraph("Post-Mortem Report", self.h1_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0")))
            story.append(Spacer(1, 6))

            postmortem_text = data.get('postmortem', 'Post-mortem report not available')

            # Parse sections from LLM output
            lines = postmortem_text.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    story.append(Spacer(1, 4))
                    continue

                # Section headers (numbered like "1. What Happened")
                if (line[0].isdigit() and '. ' in line[:5]) or (line.startswith('#')):
                    clean = line.lstrip('#').strip()
                    if '. ' in clean[:5]:
                        clean = clean.split('. ', 1)[1] if '. ' in clean else clean
                    story.append(Spacer(1, 6))
                    story.append(Paragraph(clean, self.h1_style))
                    continue

                # Bold headers with **
                if line.startswith('**') and line.endswith('**'):
                    clean = line.strip('*').strip()
                    story.append(Paragraph(f"<b>{clean}</b>", self.body_style))
                    continue

                # Bullet points
                if line.startswith('- ') or line.startswith('• '):
                    clean = line[2:].strip()
                    story.append(Paragraph(f"• {clean}", self.body_style))
                    continue

                # Code-like lines
                if line.startswith('`') or line.startswith('aws ') or line.startswith('kubectl '):
                    story.append(Paragraph(line, self.mono_style))
                    continue

                # Normal paragraph
                story.append(Paragraph(line, self.body_style))

            # ── Footer ───────────────────────────────────────────────────────
            story.append(Spacer(1, 20))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0")))
            story.append(Spacer(1, 6))

            footer_style = ParagraphStyle(
                "Footer",
                parent=self.styles["Normal"],
                fontSize=8,
                textColor=colors.HexColor("#94A3B8"),
                alignment=TA_CENTER
            )
            story.append(Paragraph(
                f"Generated by OpsOracle v1.1 · {ts_formatted} · Powered by Llama 3.3 70B (Groq)",
                footer_style
            ))

            doc.build(story)
            pdf_bytes = buffer.getvalue()
            buffer.close()

            logger.info(f"✅ PDF generated: {len(pdf_bytes)} bytes")
            return pdf_bytes

        except Exception as e:
            logger.error(f"❌ Error generating PDF: {str(e)}")
            raise


# Singleton
pdf_generator = PDFGenerator()