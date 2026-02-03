from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from datetime import datetime
from src.core.models import ProcessingJob, QualityMetrics

class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(name='CustomTitle', parent=self.styles['Title'], fontSize=24, spaceAfter=30))
        self.styles.add(ParagraphStyle(name='SectionHeader', parent=self.styles['Heading2'], fontSize=16, spaceBefore=20, spaceAfter=10, textColor=colors.HexColor('#4F46E5')))
        self.styles.add(ParagraphStyle(name='MetricLabel', parent=self.styles['Normal'], fontSize=10, textColor=colors.gray))
        self.styles.add(ParagraphStyle(name='MetricValue', parent=self.styles['Normal'], fontSize=12, fontName='Helvetica-Bold'))

    def generate_pdf(self, job: ProcessingJob) -> bytes:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
        story = []

        # Title
        story.append(Paragraph("Data Quality Report", self.styles['CustomTitle']))
        
        # Job Info
        story.append(Paragraph(f"Job ID: {job.job_id}", self.styles['Normal']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles['Normal']))
        story.append(Spacer(1, 20))

        if not job.quality_metrics:
            story.append(Paragraph("No quality metrics available for this job.", self.styles['Normal']))
            doc.build(story)
            return buffer.getvalue()

        metrics = job.quality_metrics

        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        # Quality Score
        score_color = colors.green if metrics.quality_score > 0.8 else (colors.orange if metrics.quality_score > 0.5 else colors.red)
        story.append(Paragraph(f"Quality Score: <b>{metrics.quality_score * 100:.1f}%</b>", 
                             ParagraphStyle('Score', parent=self.styles['Normal'], fontSize=14, textColor=score_color)))
        story.append(Spacer(1, 10))

        # Key Metrics Table
        data = [
            ["Metric", "Value"],
            ["Total Records", f"{metrics.total_records:,}"],
            ["Valid Records", f"{metrics.valid_records:,}"],
            ["Missing Values", f"{metrics.missing_values_percent:.1f}%"],
            ["Duplicates", f"{metrics.duplicate_percent:.1f}%"]
        ]
        
        t = Table(data, colWidths=[200, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#F3F4F6')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.HexColor('#374151')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(t)
        story.append(Spacer(1, 20))

        # Detailed Issues
        if metrics.issues:
            story.append(Paragraph("Identified Issues & Actions", self.styles['SectionHeader']))
            for issue in metrics.issues:
                story.append(Paragraph(f"• {issue}", self.styles['Normal']))
                story.append(Spacer(1, 5))

        # Column Statistics (if available in report dict)
        if metrics.report and "columns" in metrics.report:
            story.append(Paragraph("Column Statistics", self.styles['SectionHeader']))
            col_stats = metrics.report["columns"]
            
            col_data = [["Column", "Type", "Missing", "Unique"]]
            for col, stats in list(col_stats.items())[:15]:  # Limit to 15 columns to avoid overflow
                if isinstance(stats, dict) and "error" not in stats:
                    col_data.append([
                        col[:20] + ('...' if len(col)>20 else ''),
                        stats.get("dtype", "N/A"),
                        str(stats.get("missing", 0)),
                        str(stats.get("unique", 0))
                    ])
            
            if len(col_stats) > 15:
                col_data.append(["...", "...", "...", "..."])

            t2 = Table(col_data, colWidths=[150, 80, 80, 80])
            t2.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F3F4F6')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
                ('PADDING', (0, 0), (-1, -1), 6),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
            ]))
            story.append(t2)

        doc.build(story)
        return buffer.getvalue()
