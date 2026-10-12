"""
PDF Report Generator for Smart Crop Advisor.
Uses ReportLab to produce a branded, high-resolution advisory summary PDF
containing inputs, top-3 crop predictions, profit estimates, SHAP drivers,
fertilizer dosage, and crop rotation schedules.
"""
import io
import datetime
from typing import Dict, Any, List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)

class PDFReportGenerator:
    @staticmethod
    def generate_advisory_pdf(
        inputs: Dict[str, float],
        top_crops: List[Dict[str, Any]],
        explanation: Dict[str, Any],
        fertilizer_plan: Dict[str, Any],
        rotation_plan: Dict[str, Any]
    ) -> bytes:
        """
        Build and return PDF document as raw binary bytes.
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
        
        # Custom palette
        FOREST_GREEN = colors.HexColor('#0f5132')
        EMERALD = colors.HexColor('#10b981')
        SLATE_TEXT = colors.HexColor('#1e293b')
        LIGHT_BG = colors.HexColor('#f8fafc')

        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=24,
            textColor=FOREST_GREEN,
            alignment=0
        )
        
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=13,
            textColor=colors.HexColor('#64748b')
        )
        
        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=16,
            textColor=FOREST_GREEN,
            spaceBefore=10,
            spaceAfter=4
        )
        
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=SLATE_TEXT
        )
        
        bold_body_style = ParagraphStyle(
            'BoldBody',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=12,
            textColor=SLATE_TEXT
        )

        story = []

        # 1. Header Banner
        story.append(Paragraph("SMART CROP ADVISOR — AGRONOMIC & PROFIT REPORT", title_style))
        now_str = datetime.datetime.now().strftime("%d %B %Y, %I:%M %p")
        story.append(Paragraph(f"Generated on {now_str} | Open-Meteo Telemetry & Explainable AI Engine", subtitle_style))
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=1.5, color=EMERALD, spaceAfter=10))

        # 2. Input Parameters Table
        story.append(Paragraph("1. Soil & Meteorological Input Telemetry", section_style))
        input_data = [
            [
                Paragraph("<b>Nitrogen (N):</b>", body_style), Paragraph(f"{inputs.get('N', 0)} kg/ha", bold_body_style),
                Paragraph("<b>Phosphorus (P):</b>", body_style), Paragraph(f"{inputs.get('P', 0)} kg/ha", bold_body_style),
                Paragraph("<b>Potassium (K):</b>", body_style), Paragraph(f"{inputs.get('K', 0)} kg/ha", bold_body_style)
            ],
            [
                Paragraph("<b>Temperature:</b>", body_style), Paragraph(f"{inputs.get('temperature', 0):.1f} °C", bold_body_style),
                Paragraph("<b>Rel. Humidity:</b>", body_style), Paragraph(f"{inputs.get('humidity', 0):.1f} %", bold_body_style),
                Paragraph("<b>Soil pH:</b>", body_style), Paragraph(f"{inputs.get('ph', 0):.2f}", bold_body_style)
            ],
            [
                Paragraph("<b>30-Day Rainfall:</b>", body_style), Paragraph(f"{inputs.get('rainfall', 0):.1f} mm", bold_body_style),
                Paragraph("<b>Telemetry Source:</b>", body_style), Paragraph("Open-Meteo Real", bold_body_style),
                "", ""
            ]
        ]
        t_input = Table(input_data, colWidths=[80, 80, 95, 80, 85, 80])
        t_input.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(t_input)
        story.append(Spacer(1, 10))

        # 3. Top-3 Recommendations Table
        story.append(Paragraph("2. Top-3 Crop Suitability & Profitability Matrix", section_style))
        crop_rows = [
            [
                Paragraph("<b>Rank</b>", bold_body_style),
                Paragraph("<b>Recommended Crop</b>", bold_body_style),
                Paragraph("<b>Confidence</b>", bold_body_style),
                Paragraph("<b>Est. Yield (Q/Ha)</b>", bold_body_style),
                Paragraph("<b>Market Price (₹/Q)</b>", bold_body_style),
                Paragraph("<b>Net Profit (₹/Ha)</b>", bold_body_style)
            ]
        ]
        for c in top_crops:
            crop_rows.append([
                Paragraph(f"#{c['rank']}", bold_body_style),
                Paragraph(f"<b>{c['display_name']}</b> ({c['season']})", body_style),
                Paragraph(f"{c['confidence_pct']}%", bold_body_style),
                Paragraph(f"{c['estimated_yield_q_ha']:.1f}", body_style),
                Paragraph(f"₹{c['price_per_quintal']:,}", body_style),
                Paragraph(f"<b>₹{c['expected_profit_ha']:,}</b>", bold_body_style)
            ])
            
        t_crops = Table(crop_rows, colWidths=[40, 160, 70, 90, 85, 95])
        t_crops.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f5132')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
            ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(t_crops)
        story.append(Spacer(1, 10))

        # 4. Explainable AI Insights
        story.append(Paragraph("3. Explainable AI (SHAP) — Why This Crop?", section_style))
        story.append(Paragraph(f"<i>{explanation.get('explanation_sentence', '')}</i>", body_style))
        story.append(Spacer(1, 4))
        
        # Feature impacts
        shap_rows = [[
            Paragraph("<b>Factor</b>", bold_body_style),
            Paragraph("<b>Observed Value</b>", bold_body_style),
            Paragraph("<b>SHAP Attribution</b>", bold_body_style),
            Paragraph("<b>Influence Direction</b>", bold_body_style)
        ]]
        for fi in explanation.get('feature_impacts', [])[:5]:
            shap_rows.append([
                Paragraph(fi['feature_label'], body_style),
                Paragraph(fi['value_str'], body_style),
                Paragraph(f"{fi['shap_value']:+.3f}", body_style),
                Paragraph(fi['direction'], bold_body_style)
            ])
        t_shap = Table(shap_rows, colWidths=[140, 120, 120, 120])
        t_shap.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(t_shap)
        story.append(Spacer(1, 10))

        # 5. Smart Fertilizer Plan
        story.append(Paragraph("4. Fertilizer & Soil Nutrient Plan (per Acre)", section_style))
        fert_com = fertilizer_plan.get('commercial_fertilizers_kg_acre', {})
        fert_summary = (
            f"<b>Recommended Commercial Doses:</b> Urea: <b>{fert_com.get('urea', 0)} kg/acre</b> | "
            f"Single Super Phosphate (SSP): <b>{fert_com.get('ssp', 0)} kg/acre</b> | "
            f"Muriate of Potash (MOP): <b>{fert_com.get('mop', 0)} kg/acre</b>"
        )
        story.append(Paragraph(fert_summary, body_style))
        story.append(Spacer(1, 4))
        
        split_rows = [[
            Paragraph("<b>Crop Growth Stage</b>", bold_body_style),
            Paragraph("<b>Urea (kg)</b>", bold_body_style),
            Paragraph("<b>SSP (kg)</b>", bold_body_style),
            Paragraph("<b>MOP (kg)</b>", bold_body_style),
            Paragraph("<b>Application Guidelines</b>", bold_body_style)
        ]]
        for s in fertilizer_plan.get('split_schedule', []):
            split_rows.append([
                Paragraph(s['stage'], body_style),
                Paragraph(f"{s['urea_kg']} kg", body_style),
                Paragraph(f"{s['ssp_kg']} kg", body_style),
                Paragraph(f"{s['mop_kg']} kg", body_style),
                Paragraph(s['instructions'], body_style)
            ])
        t_split = Table(split_rows, colWidths=[130, 60, 60, 60, 190])
        t_split.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), LIGHT_BG),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(t_split)
        story.append(Spacer(1, 10))

        # 6. Sustainable Crop Rotation
        story.append(Paragraph("5. Sustainable Crop Rotation & Season Plan", section_style))
        story.append(Paragraph(rotation_plan.get('agronomic_rationale', ''), body_style))
        story.append(Spacer(1, 4))
        next_crops_names = ", ".join([c['display_name'] for c in rotation_plan.get('recommended_next_crops', [])])
        story.append(Paragraph(f"<b>Suggested Next Successor Crops ({rotation_plan.get('next_season', 'Next Season')}):</b> {next_crops_names}", bold_body_style))

        # Build PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
