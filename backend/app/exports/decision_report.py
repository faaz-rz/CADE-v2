import io
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage
import matplotlib.pyplot as plt

def _create_header(elements, styles, title):
    elements.append(Paragraph(f"<b>CADE</b> | {title}", styles["Heading1"]))
    elements.append(Paragraph(datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"), styles["Normal"]))
    elements.append(Spacer(1, 12))

def generate_decision_report(
    decision,
    vendor_trend,
    price_shock_snapshot: dict | None,
    mc_snapshot: dict | None,
    decision_snapshots: list[dict],
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(name='CustomTitle', parent=styles['Heading1'], textColor=colors.navy, fontSize=20))
    styles.add(ParagraphStyle(name='VendorName', parent=styles['Heading2'], textColor=colors.navy, fontSize=16))
    styles.add(ParagraphStyle(name='RiskBadge', parent=styles['Normal'], textColor=colors.white, fontSize=10, backColor=colors.red))
    styles.add(ParagraphStyle(name='AINarrative', parent=styles['Normal'], textColor=colors.darkblue, fontSize=11, fontName="Helvetica-Oblique"))
    
    elements = []
    
    # ==========================
    # PAGE 1: Decision Summary
    # ==========================
    elements.append(Paragraph("<b>CADE</b>", styles['CustomTitle']))
    elements.append(Paragraph("Decision Evidence Package", styles['Heading3']))
    elements.append(Paragraph(f"Generated: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", styles['Normal']))
    elements.append(Spacer(1, 10))
    
    # Decision Card
    vendor_name = decision.entity.upper()
    elements.append(Paragraph(vendor_name, styles['VendorName']))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph(decision.recommended_action, styles['Normal']))
    elements.append(Spacer(1, 10))
    
    risk_color = colors.green if decision.risk_level.value == "LOW" else (colors.orange if decision.risk_level.value == "MEDIUM" else colors.red)
    elements.append(Paragraph(f"<font color='white'><b> RISK: {decision.risk_level.value} </b></font>", ParagraphStyle('r', backColor=risk_color, alignment=1)))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph(f"<b>Status:</b> {decision.status.value} | <b>Confidence:</b> {decision.confidence * 100:.1f}%", styles['Normal']))
    elements.append(Spacer(1, 15))
    
    # Financial Profile Table
    data = [["Annual Spend", "Category", "Worst Case Impact", "Expected Savings"]]
    data.append([
        f"${decision.expected_monthly_impact * 12:,.0f}", # Using as proxy if exact annual_spend not in decision
        decision.scope.value,
        f"${decision.cost_of_inaction:,.0f}",
        f"${decision.annual_impact:,.0f}"
    ])
    
    t = Table(data, colWidths=[130]*4)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.navy),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 25))
    
    # AI Narrative
    if decision.ai_narrative:
        elements.append(Paragraph("<b>AI RISK ASSESSMENT</b>", styles['Heading4']))
        elements.append(Paragraph(decision.ai_narrative, styles['AINarrative']))
        elements.append(Spacer(1, 5))
        elements.append(Paragraph("<font size=7 color='grey'>Powered by Llama 3.1</font>", styles['Normal']))

    elements.append(PageBreak())
    
    # ==========================
    # PAGE 2: Simulation Evidence
    # ==========================
    elements.append(Paragraph("<b>Simulation Evidence</b>", styles['Heading2']))
    elements.append(Spacer(1, 10))
    
    # Price Shock
    elements.append(Paragraph("<b>Price Shock Analysis</b>", styles['Heading3']))
    if price_shock_snapshot:
        params = price_shock_snapshot["parameters"]
        res = price_shock_snapshot["result"]
        elements.append(Paragraph(f"Simulated at {params.get('shock_percentage', 0)*100:.1f}% shock", styles['Normal']))
        elements.append(Spacer(1, 5))
        
        ps_data = [["Base Spend", "Shock %", "New Spend", "EBITDA Impact"]]
        ps_data.append([
            f"${res.get('base_spend', 0):,.0f}",
            f"{res.get('shock_percentage', 0)*100:.1f}%",
            f"${res.get('new_spend', 0):,.0f}",
            f"${res.get('estimated_ebitda_delta', 0):,.0f}"
        ])
        t_ps = Table(ps_data, colWidths=[130]*4)
        t_ps.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ]))
        elements.append(t_ps)
        elements.append(Spacer(1, 5))
        elements.append(Paragraph(f"<font size=8 color='grey'>User-defined simulation — {price_shock_snapshot['created_at']}</font>", styles['Normal']))
    else:
        elements.append(Paragraph("Default 10% scenario — no custom simulation performed.", styles['Normal']))

    elements.append(Spacer(1, 20))
    
    # Monte Carlo
    elements.append(Paragraph("<b>Probabilistic Risk Analysis</b>", styles['Heading3']))
    if mc_snapshot:
        params = mc_snapshot["parameters"]
        res = mc_snapshot["result"]
        elements.append(Paragraph(f"Config: {params.get('distribution', 'student_t')} | {params.get('simulations', 0):,} Sims | Seed: {params.get('seed', 'None')}", styles['Normal']))
        elements.append(Spacer(1, 5))
        
        mc_data = [["5th %ile", "10th %ile", "Median", "90th %ile", "95th %ile"]]
        mc_data.append([
            f"${res.get('percentile_05', 0):,.0f}",
            f"${res.get('percentile_10', 0):,.0f}",
            f"${res.get('percentile_50', 0):,.0f}",
            f"${res.get('percentile_90', 0):,.0f}",
            f"${res.get('percentile_95', 0):,.0f}",
        ])
        t_mc = Table(mc_data, colWidths=[100]*5)
        t_mc.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ]))
        elements.append(t_mc)
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"<b>P(>$50K):</b> {res.get('probability_exceeds_50k', 0)*100:.1f}% | <b>P(>$100K):</b> {res.get('probability_exceeds_100k', 0)*100:.1f}%", styles['Normal']))
    else:
        elements.append(Paragraph("Monte Carlo analysis not performed for this vendor.", styles['Normal']))

    elements.append(Spacer(1, 20))
    
    # Spend Trend Chart
    elements.append(Paragraph("<b>Spend Trajectory</b>", styles['Heading3']))
    if vendor_trend and vendor_trend.monthly_spends:
        months = [x.month for x in vendor_trend.monthly_spends]
        spends = [x.total_spend for x in vendor_trend.monthly_spends]
        
        fig, ax = plt.subplots(figsize=(6, 3), dpi=150)
        ax.plot(months, spends, marker='o', color='blue', linewidth=2)
        ax.grid(True, color='lightgrey')
        ax.set_ylabel("Spend Amount")
        ax.set_title("Historical Spend Trend")
        
        # Prevent x-axis text overlap by limiting number of labels
        n = len(months)
        step = max(1, n // 8)
        ax.set_xticks(range(0, n, step))
        ax.set_xticklabels([months[i] for i in range(0, n, step)], rotation=45, ha='right', fontsize=8)
        
        plt.tight_layout()
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        plt.close(fig)
        
        elements.append(RLImage(img_buffer, width=400, height=200))
    else:
        elements.append(Paragraph("Insufficient historical data.", styles['Normal']))
        
    elements.append(PageBreak())
    
    # ==========================
    # PAGE 3: Audit Trail
    # ==========================
    elements.append(Paragraph("<b>Decision Audit Trail</b>", styles['Heading2']))
    elements.append(Spacer(1, 10))
    
    if hasattr(decision, 'events') and decision.events:
        evt_data = [["Timestamp", "Event Type", "Actor", "Notes"]]
        for e in decision.events:
            evt_data.append([
                e.created_at.strftime("%Y-%m-%d %H:%M"),
                e.event_type.value,
                e.actor_id,
                e.note or ""
            ])
        t_evt = Table(evt_data, colWidths=[100, 100, 100, 200])
        t_evt.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ]))
        elements.append(t_evt)
    else:
        elements.append(Paragraph("No audit events recorded.", styles['Normal']))
        
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("<b>Simulation History</b>", styles['Heading3']))
    if decision_snapshots:
        snap_data = [["Timestamp", "Type", "Key Result"]]
        for s in decision_snapshots:
            snap_data.append([
                s["created_at"],
                s["snapshot_type"],
                "Saved output parameters"
            ])
        t_snap = Table(snap_data, colWidths=[150, 100, 250])
        t_snap.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ]))
        elements.append(t_snap)
    else:
        elements.append(Paragraph("No simulations linked to this decision.", styles['Normal']))

    def add_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.setStrokeColor(colors.lightgrey)
        canvas.line(40, 30, letter[0]-40, 30)
        canvas.drawString(40, 15, "CADE — Capital Allocation Decision Engine")
        canvas.drawRightString(letter[0]/2 + 20, 15, f"Page {doc.page}")
        canvas.drawRightString(letter[0]-40, 15, "Confidential")
        canvas.restoreState()

    doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)
    
    buffer.seek(0)
    return buffer.getvalue()
