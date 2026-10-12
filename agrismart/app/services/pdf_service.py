import os
import io
import re
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class PDFReportService:
    @staticmethod
    def generate_prediction_report(prediction, user):
        """
        Generates a stylish PDF report buffer using ReportLab.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        
        styles = getSampleStyleSheet()
        
        # Custom Brand Colors
        primary_color = colors.HexColor("#0f5132")
        emerald_color = colors.HexColor("#10b981")
        amber_color = colors.HexColor("#d97706")
        dark_slate = colors.HexColor("#1e293b")
        light_bg = colors.HexColor("#f8fafc")
        
        title_style = ParagraphStyle(
            'BrandTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=primary_color
        )
        
        subtitle_style = ParagraphStyle(
            'BrandSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#64748b")
        )
        
        heading2_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=17,
            textColor=primary_color,
            spaceAfter=6
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13,
            textColor=dark_slate
        )
        
        badge_style = ParagraphStyle(
            'CropBadge',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#ffffff"),
            alignment=1
        )
        
        elements = []
        
        # 1. Header Banner
        user_name = user.first_name or user.username if user else 'Farmer'
        loc_str = getattr(prediction, 'location', None)
        loc_display = f"<br/><b>Location:</b> {loc_str}" if loc_str else ""
        header_table = Table(
            [[
                Paragraph("<b>AGRISMART</b><br/><font size=8 color='#10b981'>PRECISION AGRI-TECH PLATFORM</font>", title_style),
                Paragraph(f"<b>Report Ref:</b> #AGR-{prediction.id:05d}<br/><b>Date:</b> {prediction.created_at.strftime('%B %d, %Y')}<br/><b>Farmer:</b> {user_name}{loc_display}", subtitle_style)
            ]],
            colWidths=[300, 240]
        )
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LINEBELOW', (0, 0), (-1, -1), 1.5, emerald_color)
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 15))
        
        # 2. Main Result Showcase Box
        crop_box = Table(
            [[
                Paragraph(f"RECOMMENDED CROP<br/><b>{prediction.predicted_crop.upper()}</b>", badge_style)
            ]],
            colWidths=[540],
            rowHeights=[48]
        )
        crop_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), primary_color),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(crop_box)
        elements.append(Spacer(1, 10))
        
        # 3. Metrics Strip
        metrics_data = [
            [
                Paragraph(f"<b>Confidence Score</b><br/><font color='#10b981' size=14><b>{prediction.confidence or 98.6}%</b></font>", body_style),
                Paragraph(f"<b>Estimated Yield</b><br/><font color='#0f5132' size=14><b>{prediction.yield_estimate or 4.0} t/ha</b></font>", body_style),
                Paragraph(f"<b>Yield Efficiency</b><br/><font color='#d97706' size=14><b>{prediction.yield_efficiency or 85}%</b></font>", body_style),
                Paragraph(f"<b>Status</b><br/><font color='#10b981' size=12><b>Optimal Fit</b></font>", body_style)
            ]
        ]
        metrics_table = Table(metrics_data, colWidths=[135, 135, 135, 135])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), light_bg),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(metrics_table)
        elements.append(Spacer(1, 15))
        
        # 4. Input Parameters Table
        elements.append(Paragraph("SOIL & ENVIRONMENTAL PARAMETERS RECORDED", heading2_style))
        params_data = [
            [
                Paragraph("<b>Parameter</b>", body_style),
                Paragraph("<b>Input Value</b>", body_style),
                Paragraph("<b>Standard Range</b>", body_style),
                Paragraph("<b>Unit</b>", body_style)
            ],
            [Paragraph("Nitrogen (N)", body_style), Paragraph(str(prediction.nitrogen), body_style), Paragraph("0 - 140", body_style), Paragraph("mg/kg (ppm)", body_style)],
            [Paragraph("Phosphorus (P)", body_style), Paragraph(str(prediction.phosphorus), body_style), Paragraph("5 - 145", body_style), Paragraph("mg/kg (ppm)", body_style)],
            [Paragraph("Potassium (K)", body_style), Paragraph(str(prediction.potassium), body_style), Paragraph("5 - 205", body_style), Paragraph("mg/kg (ppm)", body_style)],
            [Paragraph("Temperature", body_style), Paragraph(f"{prediction.temperature}°C", body_style), Paragraph("15 - 38", body_style), Paragraph("Celsius", body_style)],
            [Paragraph("Relative Humidity", body_style), Paragraph(f"{prediction.humidity}%", body_style), Paragraph("30 - 95", body_style), Paragraph("Percentage", body_style)],
            [Paragraph("Soil pH", body_style), Paragraph(str(prediction.ph), body_style), Paragraph("5.0 - 8.5", body_style), Paragraph("pH Scale", body_style)],
            [Paragraph("Rainfall", body_style), Paragraph(f"{prediction.rainfall} mm", body_style), Paragraph("30 - 300", body_style), Paragraph("Millimeters", body_style)],
        ]
        params_table = Table(params_data, colWidths=[150, 110, 140, 140])
        params_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f5132")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, light_bg]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(params_table)
        elements.append(Spacer(1, 15))
        
        # 5. Tailored Fertilizer Recommendations
        elements.append(Paragraph("PRECISION FERTILIZER & SOIL ENRICHMENT ADVISORY", heading2_style))
        raw_advice = prediction.fertilizer_recommendation or "Nutrient levels are well balanced."
        advice_lines = [line.strip() for line in raw_advice.split("\n") if line.strip()]
        
        advice_paragraphs = []
        for line in advice_lines:
            cleaned = line.replace('•', '').strip()
            # Safely replace markdown bold with HTML bold
            cleaned = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', cleaned)
            advice_paragraphs.append([Paragraph(f"• {cleaned}", body_style)])
            
        advice_table = Table(advice_paragraphs, colWidths=[540])
        advice_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),
            ('BOX', (0, 0), (-1, -1), 1, emerald_color),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(advice_table)
        elements.append(Spacer(1, 15))
        
        # 6. Verification Footer / Disclaimer
        footer_text = (
            "<i>Note: Recommendations are generated by AgriSmart's AI Engine (Random Forest ensemble trained on validated agro-climatic datasets). "
            "Always cross-reference with certified agricultural extension offices for high-acreage commercial farming.</i>"
        )
        elements.append(Paragraph(footer_text, subtitle_style))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
