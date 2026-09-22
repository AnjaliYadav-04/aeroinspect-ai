import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_CENTER
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

class ReportGenerator:
    def __init__(self):
        self.reports_dir = "/app/reports"
        Path(self.reports_dir).mkdir(parents=True, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._custom_styles()

    def _custom_styles(self):
        self.styles.add(ParagraphStyle(name='CustomTitle', fontSize=24, leading=30, alignment=TA_CENTER, spaceAfter=30, textColor=colors.HexColor('#1a237e'), fontName='Helvetica-Bold'))
        self.styles.add(ParagraphStyle(name='SectionHeader', fontSize=14, leading=18, spaceAfter=12, spaceBefore=12, textColor=colors.HexColor('#283593'), fontName='Helvetica-Bold', borderWidth=1, borderColor=colors.HexColor('#c5cae9'), borderPadding=5, backColor=colors.HexColor('#e8eaf6')))
        self.styles.add(ParagraphStyle(name='CriticalAlert', fontSize=11, leading=14, textColor=colors.HexColor('#c62828'), backColor=colors.HexColor('#ffebee'), borderPadding=8, spaceAfter=10))
        self.styles.add(ParagraphStyle(name='StatsNumber', fontSize=36, leading=42, alignment=TA_CENTER, textColor=colors.HexColor('#1565c0'), fontName='Helvetica-Bold'))

    def generate_inspection_report(self, inspection_data: Dict) -> str:
        inspection_id = inspection_data.get("inspection_id", f"DRN-{datetime.now().strftime('%Y-%m%d')}")
        filename = f"report_{inspection_id}_{uuid.uuid4().hex[:8]}.pdf"
        filepath = os.path.join(self.reports_dir, filename)
        doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        story = []
        story.append(Paragraph("DRONE INSPECTION REPORT", self.styles['CustomTitle']))
        story.append(Paragraph(f"<b>Inspection ID:</b> {inspection_id}<br/><b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}<br/><b>Platform:</b> AI-Powered Solar Farm Inspection System", self.styles['Normal']))
        story.append(Spacer(1, 20))
        story.append(Paragraph("EXECUTIVE SUMMARY", self.styles['SectionHeader']))
        stats = inspection_data.get("statistics", {})
        total_assets = stats.get("total_assets", 0)
        total_defects = stats.get("total_defects", 0)
        critical = stats.get("critical", 0)
        high = stats.get("high", 0)
        medium = stats.get("medium", 0)
        low = stats.get("low", 0)
        stats_data = [
            [Paragraph(f"{total_assets}", self.styles['StatsNumber']), Paragraph(f"{total_defects}", self.styles['StatsNumber']), Paragraph(f"{critical}", self.styles['StatsNumber'])],
            [Paragraph("Assets Inspected", self.styles['Normal']), Paragraph("Defects Found", self.styles['Normal']), Paragraph("Critical Issues", self.styles['Normal'])]
        ]
        stats_table = Table(stats_data, colWidths=[2.3*inch]*3)
        stats_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('TOPPADDING', (0,0), (-1,0), 10), ('BOTTOMPADDING', (0,1), (-1,1), 10)]))
        story.append(stats_table)
        story.append(Spacer(1, 15))
        if critical > 0:
            story.append(Paragraph(f"URGENT ACTION REQUIRED: {critical} critical defect(s) detected. Immediate inspection and maintenance recommended within 24 hours.", self.styles['CriticalAlert']))
        story.append(Spacer(1, 10))
        story.append(Paragraph("SEVERITY BREAKDOWN", self.styles['SectionHeader']))
        severity_data = [
            ['Severity', 'Count', 'Percentage', 'Action Required'],
            ['Critical', str(critical), f"{(critical/total_defects*100):.1f}%" if total_defects else "0%", 'Immediate (24h)'],
            ['High', str(high), f"{(high/total_defects*100):.1f}%" if total_defects else "0%", 'Within 7 days'],
            ['Medium', str(medium), f"{(medium/total_defects*100):.1f}%" if total_defects else "0%", 'Within 30 days'],
            ['Low', str(low), f"{(low/total_defects*100):.1f}%" if total_defects else "0%", 'Next scheduled'],
        ]
        sev_table = Table(severity_data, colWidths=[1.5*inch, 1*inch, 1.2*inch, 1.8*inch])
        sev_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a237e')), ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,0), 11), ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#ffebee')), ('BACKGROUND', (0,2), (-1,2), colors.HexColor('#fff3e0')),
            ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#fffde7')), ('BACKGROUND', (0,4), (-1,4), colors.HexColor('#e8f5e9')),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#e0e0e0')), ('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold'),
        ]))
        story.append(sev_table)
        story.append(Spacer(1, 20))
        story.append(Paragraph("DEFECT DISTRIBUTION", self.styles['SectionHeader']))
        chart_path = self._create_severity_chart(severity_data[1:])
        if chart_path:
            story.append(Image(chart_path, width=5*inch, height=3*inch))
            story.append(Spacer(1, 15))
        story.append(PageBreak())
        story.append(Paragraph("DETECTED ISSUES", self.styles['SectionHeader']))
        detections = inspection_data.get("detections", [])
        class_groups = {}
        for det in detections:
            cls = det.get("class_name", "unknown")
            if cls not in class_groups: class_groups[cls] = []
            class_groups[cls].append(det)
        for class_name, items in sorted(class_groups.items()):
            story.append(Paragraph(f"<b>{class_name.replace('_', ' ').title()}</b> ({len(items)} found)", self.styles['Heading3']))
            for i, det in enumerate(items[:5], 1):
                gps = det.get("gps", {})
                story.append(Paragraph(f"  {i}. Confidence: {det.get('confidence', 0):.2%} | Severity: <b>{det.get('severity', 'low').upper()}</b> | Location: {gps.get('latitude', 'N/A')}, {gps.get('longitude', 'N/A')}", self.styles['Normal']))
            if len(items) > 5:
                story.append(Paragraph(f"  ... and {len(items) - 5} more", self.styles['Normal']))
            story.append(Spacer(1, 8))
        story.append(PageBreak())
        story.append(Paragraph("RECOMMENDED ACTIONS", self.styles['SectionHeader']))
        recommendations = self._generate_recommendations(inspection_data)
        for rec in recommendations:
            story.append(Paragraph(f"• {rec}", self.styles['Normal']))
            story.append(Spacer(1, 6))
        story.append(Spacer(1, 30))
        story.append(Paragraph("<para alignment='center' fontSize='8' textColor='grey'>This report was automatically generated by AI Drone Inspection Platform.<br/>For technical support, contact: support@droneinspection.ai</para>", self.styles['Normal']))
        doc.build(story)
        if chart_path and os.path.exists(chart_path): os.remove(chart_path)
        return filepath

    def _create_severity_chart(self, severity_data: List) -> Optional[str]:
        try:
            labels = [row[0] for row in severity_data]
            values = [int(row[1]) for row in severity_data]
            colors_list = ['#c62828', '#ef6c00', '#f9a825', '#2e7d32']
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
            ax1.pie(values, labels=labels, colors=colors_list, autopct='%1.1f%%', startangle=90, explode=[0.05 if v == max(values) else 0 for v in values])
            ax1.set_title('Defect Distribution by Severity')
            bars = ax2.bar(labels, values, color=colors_list, edgecolor='black', linewidth=0.5)
            ax2.set_title('Defect Count by Severity')
            ax2.set_ylabel('Count')
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}', ha='center', va='bottom')
            plt.tight_layout()
            chart_path = f"/tmp/chart_{uuid.uuid4().hex}.png"
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            return chart_path
        except Exception as e:
            print(f"Chart generation error: {e}")
            return None

    def _generate_recommendations(self, inspection_data: Dict) -> List[str]:
        recommendations = []
        stats = inspection_data.get("statistics", {})
        critical = stats.get("critical", 0)
        high = stats.get("high", 0)
        hotspots = stats.get("hotspot_count", 0)
        if critical > 0:
            recommendations.append(f"IMMEDIATE: Inspect {critical} critical asset(s) within 24 hours. Potential fire hazard or structural failure risk detected.")
        if high > 5:
            recommendations.append(f"SCHEDULE: {high} high-priority defects require attention within 7 days.")
        if hotspots > 0:
            recommendations.append(f"THERMAL: {hotspots} thermal hotspot(s) detected. Recommend infrared follow-up.")
        total = stats.get("total_defects", 0)
        if total > 50:
            recommendations.append(f"MAINTENANCE: High defect density ({total} total). Consider comprehensive cleaning.")
        if not recommendations:
            recommendations.append("ROUTINE: No critical issues found. Continue standard maintenance schedule.")
        recommendations.append("FOLLOW-UP: Schedule re-inspection in 30 days to verify remediation.")
        return recommendations

report_generator = ReportGenerator()
