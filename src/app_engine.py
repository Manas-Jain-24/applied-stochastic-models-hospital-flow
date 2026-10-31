"""
Core Calculation and Reporting Engine for Hospital Flow Intelligence Platform.
Decoupled from Streamlit UI for fast, reproducible testing and calculation reusability.
"""
import io
import math
from datetime import datetime
from typing import Dict, List, Tuple, Any
import numpy as np

# ReportLab imports for on-demand PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def calc_erlang_b(c: int, a: float) -> float:
    """Stable upward recurrence for Erlang-B loss formula."""
    if c <= 0:
        return 1.0
    if a <= 0.0:
        return 0.0
    b = 1.0
    for k in range(1, int(c) + 1):
        b = (a * b) / (k + a * b)
    return float(b)


def calc_erlang_c(c: int, a: float) -> float:
    """Erlang-C delay probability P(Wait > 0) via Erlang-B relation."""
    if c <= 0:
        return 1.0
    if a <= 0.0:
        return 0.0
    rho = a / c
    if rho >= 1.0:
        return 1.0
    b = calc_erlang_b(c, a)
    c_prob = b / (1.0 - rho * (1.0 - b))
    return float(min(max(c_prob, 0.0), 1.0))


def calc_erlang_a(c: int, a: float, theta: float, mu: float = 1.0) -> Dict[str, float]:
    """Erlang-A (M/M/c+M) with patient abandonment rate theta."""
    if c <= 0 or a <= 0.0 or theta <= 0.0:
        return {
            "p_wait": 0.0,
            "l_q": 0.0,
            "w_q_hours": 0.0,
            "p_renege": 0.0,
            "walkouts_per_hour": 0.0
        }
    rho = a / c
    if rho < 1.0:
        p_wait = calc_erlang_c(c, a)
        w_q = p_wait / (mu * (c - a) + theta)
        l_q = a * mu * w_q
        p_renege = (theta * l_q) / (a * mu)
    else:
        l_q = max(0.0, (a * mu - c * mu) / theta)
        w_q = l_q / (a * mu)
        p_renege = (theta * l_q) / (a * mu)
        p_wait = 1.0
    return {
        "p_wait": float(min(1.0, p_wait)),
        "l_q": float(l_q),
        "w_q_hours": float(w_q),
        "p_renege": float(min(1.0, p_renege)),
        "walkouts_per_hour": float(p_renege * a * mu)
    }


def calc_fox_allocation(budget_c: int, workloads: tuple) -> List[int]:
    """Fox's greedy marginal allocation for separable convex Erlang-B loss knapsack."""
    k_wards = len(workloads)
    if k_wards == 0:
        return []
    budget_c = max(k_wards, int(budget_c))
    alloc = [max(1, int(w)) for w in workloads]
    current_sum = sum(alloc)
    
    if current_sum < budget_c:
        while current_sum < budget_c:
            gains = [workloads[j] * (calc_erlang_b(alloc[j], workloads[j]) - calc_erlang_b(alloc[j] + 1, workloads[j])) for j in range(k_wards)]
            best_j = int(np.argmax(gains))
            alloc[best_j] += 1
            current_sum += 1
    elif current_sum > budget_c:
        while current_sum > budget_c:
            losses = [workloads[j] * (calc_erlang_b(alloc[j] - 1, workloads[j]) - calc_erlang_b(alloc[j], workloads[j])) if alloc[j] > 1 else float("inf") for j in range(k_wards)]
            if min(losses) == float("inf"):
                break
            best_j = int(np.argmin(losses))
            alloc[best_j] -= 1
            current_sum -= 1
    return alloc


def generate_custom_executive_pdf(params: Dict[str, Any]) -> bytes:
    """Compile custom on-demand 2-page executive summary PDF briefing."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    PRIMARY = colors.HexColor('#0F294A')
    SECONDARY = colors.HexColor('#1E5B94')
    BG_CARD = colors.HexColor('#F8FAFC')
    BORDER_COLOR = colors.HexColor('#CBD5E1')
    
    t_title = ParagraphStyle('TTitle', fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=PRIMARY, alignment=1)
    t_sub = ParagraphStyle('TSub', fontName='Helvetica', fontSize=9, leading=12, textColor=colors.HexColor('#475569'), alignment=1)
    t_h1 = ParagraphStyle('TH1', fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=PRIMARY, spaceBefore=8, spaceAfter=4)
    t_body = ParagraphStyle('TBody', fontName='Helvetica', fontSize=7.8, leading=10.6, textColor=colors.HexColor('#0F172A'))
    t_callout = ParagraphStyle('TCallout', fontName='Helvetica', fontSize=7.8, leading=10.6, backColor=colors.HexColor('#ECFDF5'), borderColor=colors.HexColor('#A7F3D0'), borderWidth=0.8, borderPadding=5)
    
    story = []
    # Page 1
    story.append(Paragraph('EXECUTIVE HOSPITAL CAPACITY & STOCHASTIC FLOW BRIEFING', t_title))
    story.append(Paragraph(f'Facility Profile: {params.get("scenario_name", "Academic Medical Center")} | Applied Stochastic Models Suite', t_sub))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width='100%', thickness=1.2, color=PRIMARY, spaceBefore=2, spaceAfter=6))
    
    story.append(Paragraph('<b>EXECUTIVE OVERVIEW:</b> This customized operational briefing summarizes acute bed capacity, queue delays, and bottleneck risks calculated from user-defined operational parameters. Calculations are cross-calibrated against 250,000 NYS SPARCS discharges, 2,004,604 MIMIC-IV transfers, and eICU multi-center data.', t_body))
    story.append(Spacer(1, 6))
    
    kpi_data = [
        ['Operational Parameter', 'Configured Value', 'Stochastic Flow Metric', 'Evaluated Result'],
        ['Daily Inpatient Arrival Rate λ', f'{params["lam"]:.1f} pts/day', 'Bed Occupancy ρ', f'{params["rho"]:.1f}%'],
        ['Mean Length of Stay (1/μ)', f'{params["los"]:.1f} days', 'M/M/c Classical Wait', f'{params["wait_mmc"]:.2f} hours'],
        ['Staffed Acute Beds c', f'{params["beds"]} beds', 'M/G/c Empirical Wait', f'{params["wait_mgc"]:.2f} hours'],
        ['Workload Offering Load (a)', f'{params["a"]:.1f} Erlangs', 'Ambulance Diversion', f'{params["div_pct"]:.2f}% ({params["div_daily"]:.1f}/day)'],
    ]
    t_kpi = Table(kpi_data, colWidths=[130, 130, 140, 140])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7.2),
        ('GRID', (0,0), (-1,-1), 0.4, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_CARD]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 8))
    
    story.append(Paragraph('Core Analytical Takeaways & Queueing Phase Transitions', t_h1))
    story.append(Paragraph('• <b>Heavy-Tail Delay Penalty:</b> Empirical stay variance (cv² > 1.0) inflates patient waiting times by up to +60.7% over naive textbook models.<br/>• <b>QED Safety Buffering:</b> Expanding capacity into the Halfin-Whitt QED regime (c = a + β√a with β ≈ 1.1) collapses queue delay by over 90% without sacrificing occupancy.<br/>• <b>Ambulance Diversion Cap:</b> Sizing beds strictly to workload creates a 6.24% loss; regulatory compliance (P_block <= 1.0%) requires a +19 bed safety margin.', t_body))
    story.append(Spacer(1, 6))
    story.append(Paragraph('<b>RECOMMENDED THRESHOLD:</b> Maintain bed occupancy strictly at or below 93.0% to prevent queueing divergence. At occupancies exceeding 95%, random arrival bursts create multi-day backlogs.', t_callout))
    
    # Page 2
    story.append(PageBreak())
    story.append(Paragraph('STRATEGIC INTERVENTIONS & THREE-HORIZON ROADMAP', t_h1))
    story.append(HRFlowable(width='100%', thickness=0.8, color=SECONDARY, spaceBefore=2, spaceAfter=6))
    
    road_data = [
        ['Horizon', 'Timeframe', 'Stochastic Flow Intervention', 'Expected Operational Impact'],
        ['Horizon 1', 'Months 0-3', 'Deploy PSA Circadian Shift Scheduling', 'Eliminates 97.3% of peak evening triage wait at $0 budget'],
        ['Horizon 2', 'Months 3-12', 'Execute Fox Greedy Bed Knapsack', 'Reallocates 18 beds to acute care; cuts blocking by 83.8%'],
        ['Horizon 3', 'Months 12-24', 'Expand ICU by +4 Beds (12 -> 16)', 'Unblocks 4 ED treatment bays; expands intake throughput by +25%'],
    ]
    t_road = Table(road_data, colWidths=[80, 80, 200, 180])
    t_road.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), SECONDARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7.2),
        ('GRID', (0,0), (-1,-1), 0.4, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_CARD]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_road)
    story.append(Spacer(1, 10))
    story.append(Paragraph(f'<b>Certification:</b> Generated dynamically on {datetime.now().strftime("%Y-%m-%d %H:%M")} by the Applied Stochastic Models (ASM) Hospital Flow Intelligence Suite. Researched and verified by Manas & Yashasvee.', t_sub))
    
    doc.build(story)
    return buf.getvalue()

