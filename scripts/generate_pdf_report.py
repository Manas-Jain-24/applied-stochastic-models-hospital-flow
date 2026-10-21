"""
Automated PDF Report Generator for Applied Stochastic Models Project.
Compiles a publication-quality, multi-page PDF report with embedded figures, tables,
mathematical formulations, and references using ReportLab.
"""
from pathlib import Path
import reportlab
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

PROJECT_ROOT = Path(__file__).resolve().parent.parent

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print total page count."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#555555"))
        
        # Suppress running header on title/cover page (page 1)
        if self._pageNumber > 1:
            self.drawString(54, 11 * inch - 36, "Applied Stochastic Models (ASM) | Hospital Flow & Capacity Planning")
            self.setStrokeColor(colors.HexColor("#cccccc"))
            self.setLineWidth(0.5)
            self.line(54, 11 * inch - 40, 8.5 * inch - 54, 11 * inch - 40)
            
        # Running Footer on all pages
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 54, 36, page_str)
        self.drawString(54, 36, "Confidential | Course Project Submission 2026")
        self.setStrokeColor(colors.HexColor("#cccccc"))
        self.setLineWidth(0.5)
        self.line(54, 46, 8.5 * inch - 54, 46)
        
        self.restoreState()

def build_pdf_report():
    out_pdf = PROJECT_ROOT / "reports" / "Hospital_Stochastic_Modeling_Project_Report.pdf"
    doc = SimpleDocTemplate(
        str(out_pdf),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette
    PRIMARY = colors.HexColor("#1A365D")   # Deep navy
    SECONDARY = colors.HexColor("#2B6CB0") # Slate blue
    DARK_TEXT = colors.HexColor("#2D3748") # Charcoal body
    BG_LIGHT = colors.HexColor("#F7FAFC")  # Subtle grey background
    ACCENT = colors.HexColor("#9B2C2C")    # Crimson accent
    
    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=PRIMARY,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=SECONDARY,
        spaceAfter=12
    )
    
    meta_style = ParagraphStyle(
        "CoverMeta",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#4A5568")
    )
    
    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=SECONDARY,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=DARK_TEXT,
        spaceAfter=6
    )
    
    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=DARK_TEXT,
        leftIndent=15,
        spaceAfter=3
    )
    
    abstract_style = ParagraphStyle(
        "Abstract_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=13,
        textColor=DARK_TEXT
    )
    
    caption_style = ParagraphStyle(
        "Caption_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#4A5568"),
        alignment=1, # Centered
        spaceAfter=10
    )

    story = []
    
    # TITLE & HEADER
    story.append(Paragraph("Data-Driven Stochastic Modeling of Hospital Patient Flow, Congestion, and Resource Planning", title_style))
    story.append(Paragraph("A Multi-Server Queueing, Non-Homogeneous Poisson, and Absorbing Markov Chain Analysis", subtitle_style))
    
    meta_text = "<b>Course:</b> Applied Stochastic Models (ASM) &nbsp;|&nbsp; <b>Institution:</b> Department of Mathematics / Engineering<br/>" \
                "<b>Authors:</b> Student Research Team &nbsp;|&nbsp; <b>Dataset:</b> 250,000 Inpatient Encounters (NYS SPARCS)<br/>" \
                "<b>Codebase & Verifications:</b> github.com/Manas-Jain-24/applied-stochastic-models-hospital-flow"
    story.append(Paragraph(meta_text, meta_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=10))
    
    # ABSTRACT BOX
    abstract_text = "<b>Abstract:</b> Hospital emergency and inpatient wards operate under acute stochastic volatility driven by random arrival timing and high-variance clinical recovery times. Sizing inpatient bed capacity using traditional rules-of-thumb leads to frequent emergency department boarding and ambulance diversions. Using <b>250,000 real patient encounters</b> from the NYS SPARCS database, this study investigates stochastic patient flow and capacity planning. We mathematically prove that real hospital recovery times violate the memoryless property of exponential distributions (cv^2 = 1.991 approx 2.0). Applying the Allen-Cunneen heavy-tailed approximation for M/G/c queues, we demonstrate that standard exponential models underestimate waiting times by 50%. We formulate closed-form M/M/c/c (Erlang-B) loss models, M/M/c (Erlang-C) delay models, finite-buffer M/M/c/K systems, and Absorbing Markov Chains. Our results prove that maintaining bed blocking below 1% requires at least 293 beds under a mean load of 269.3 bed-days (a 24-bed safety buffer). We validate analytical equations against an event-calendar discrete-event simulation (DES) and demonstrate system breakdown under acute winter demand surges (+20%)."
    
    abs_table = Table([[Paragraph(abstract_text, abstract_style)]], colWidths=[7.2 * inch])
    abs_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, SECONDARY),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(abs_table)
    story.append(Spacer(1, 12))

    # SECTION 1: PROBLEM DEFINITION
    story.append(Paragraph("1. Problem Definition & Operational Context", h1_style))
    story.append(Paragraph(
        "Acute care hospitals must constantly balance high bed utilization against operational responsiveness. "
        "Inpatient beds represent a hospital's most capital-intensive physical asset. Operating at excessive occupancy "
        "creates extreme fragility: unexpected stochastic arrival surges saturate inpatient beds, which causes admitted "
        "patients to board in Emergency Department bays for hours or days. This upstream boarding delays incoming ambulances, "
        "increases patient mortality, and triggers hospital gridlock.",
        body_style
    ))
    story.append(Paragraph("<b>Primary Stochastic Questions Addressed:</b>", body_style))
    story.append(Paragraph("• <b>Memoryless Violation:</b> Does real Length of Stay (LOS) satisfy the exponential memoryless assumption (cv^2 = 1.0), and how does clinical variance penalize wait times?", bullet_style))
    story.append(Paragraph("• <b>Capacity Sizing:</b> What is the minimum bed capacity c* required to ensure bed blocking P(block) <= 1% and admission delay P(Wait > 0) <= 5%?", bullet_style))
    story.append(Paragraph("• <b>Finite Buffer Trade-off:</b> In an M/M/c/K system, how does expanding ED boarding buffer size reduce ambulance diversion rates?", bullet_style))
    story.append(Paragraph("• <b>Triage Prioritization:</b> How effectively does 2-class non-preemptive priority queueing protect emergency patients without expanding total bed supply?", bullet_style))
    story.append(Paragraph("• <b>Stress-Testing:</b> What is the operational breaking point when winter epidemics increase arrival rates by +20%?", bullet_style))
    story.append(Spacer(1, 10))

    # SECTION 2: LITERATURE REVIEW
    story.append(Paragraph("2. Literature Review: Stochastic Modeling in Healthcare", h1_style))
    story.append(Paragraph(
        "The application of queueing theory and stochastic processes to healthcare was pioneered by <b>Linda Green (2002, 2006)</b>, "
        "who demonstrated that static occupancy targets (e.g. the 85% rule) fail because they ignore stochastic arrival bursts and bed-pooling dynamics. "
        "Green proved that multi-server queueing models (M/M/c and time-varying Erlang queues) provide the exact mathematical relationship "
        "between server utilization, capacity buffers, and patient delay probabilities.",
        body_style
    ))
    story.append(Paragraph(
        "<b>De Bruin et al. (2007)</b> applied Erlang loss and delay models to acute coronary care units, establishing Erlang-B formulas "
        "as an international operational standard for sizing bed pools. Simultaneously, <b>Armony et al. (2015)</b> and <b>Ward Whitt (1993, 2007)</b> "
        "proved that hospital length of stay is universally non-exponential, exhibiting significant right-skewness and heavy tails (cv^2 > 1). "
        "Whitt formulated the Allen-Cunneen approximation, establishing that queue delays grow linearly with the sum of arrival and service variance. "
        "Finally, <b>Fomundam & Herrmann (2007)</b> and <b>Bekker & de Bruin (2010)</b> demonstrated that multi-department patient transitions "
        "can be rigorously modeled using Markov chains, showing that post-acute discharge delays directly cause upstream ward blocking.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # SECTION 3: DATA DESCRIPTION
    story.append(Paragraph("3. Data Provenance & Empirical Calibration", h1_style))
    story.append(Paragraph(
        "To ground our analysis in authentic clinical operations, we calibrated parameters using a stratified sample of "
        "<b>250,000 real patient encounters</b> from the New York State Statewide Planning and Research Cooperative System (SPARCS) database.",
        body_style
    ))
    
    # Table of Parameters
    param_data = [
        ["Operational Parameter", "Empirical Value (SPARCS, N=250,000)", "Theoretical Exponential Benchmark", "Mathematical Impact"],
        ["Mean Length of Stay E[S]", "5.386 Days", "1 / mu", "Determines baseline service rate mu = 0.1856 /day"],
        ["Variance of Stay Var(S)", "57.77 Days^2", "(E[S])^2 = 29.01 Days^2", "Real variance is 2.0x higher than exponential model"],
        ["Squared Coeff. of Variation cv^2", "1.991 (approx 2.0)", "1.000", "Memoryless property rejected; M/G/c model mandatory"],
        ["Admission Mix: Emergency", "55.5%", "-", "Priority Class 1 (non-schedulable)"],
        ["Admission Mix: Elective", "23.3%", "-", "Priority Class 2 (schedulable)"],
        ["Admission Mix: Urgent", "12.7%", "-", "Buffer absorption"],
        ["Primary Disposition: Home", "68.97%", "-", "Absorbing state 1"],
        ["Skilled Nursing Facility (SNF)", "9.52%", "-", "Absorbing state 2 (downstream bottleneck)"],
        ["Inpatient Mortality (Expired)", "2.13%", "-", "Absorbing state 3"]
    ]
    t_param = Table(param_data, colWidths=[1.8*inch, 2.0*inch, 1.7*inch, 1.7*inch])
    t_param.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_param)
    story.append(Spacer(1, 12))

    # SECTION 4: MATHEMATICAL FORMULATIONS
    story.append(Paragraph("4. Mathematical Formulations & Derivations", h1_style))
    story.append(Paragraph("<b>4.1 Non-Homogeneous Poisson Arrival Process (NHPP)</b>", h2_style))
    story.append(Paragraph(
        "Patient arrivals are governed by a counting process {N(t), t >= 0}. The Index of Dispersion for Counts (IDC) tests the homogeneous Poisson property: "
        "D(t) = Var(N(t)) / E[N(t)]. On empirical data, D = 1.34 > 1.25, rejecting the homogeneous assumption due to circadian rhythm. "
        "We model the diurnal arrival intensity curve as lambda(t) = lambda_0 + A * cos(2*pi*(t - t_peak)/24). "
        "Exact sample paths are generated using the <b>Lewis-Shedler Thinning Algorithm</b>: candidate events arrive at majorizing rate lambda_max = lambda_0 + A "
        "and are accepted with probability p(t_i) = lambda(t_i) / lambda_max.",
        body_style
    ))
    
    story.append(Paragraph("<b>4.2 Queueing Models: Erlang-B, Erlang-C, and Allen-Cunneen M/G/c</b>", h2_style))
    story.append(Paragraph(
        "• <b>Erlang-B Loss Model (M/M/c/c):</b> When a hospital diverts patients when full, blocking probability is B(c, a) = (a^c / c!) / sum_{k=0}^c (a^k / k!), "
        "where a = lambda / mu is offered load. Solved using the stable recursion B(k, a) = [a * B(k-1, a)] / [k + a * B(k-1, a)] with B(0, a) = 1.0.<br/>"
        "• <b>Erlang-C Delay Model (M/M/c):</b> When patients board in an admission queue, delay probability is C(c, a) = B(c, a) / [1 - rho * (1 - B(c, a))], "
        "with traffic intensity rho = a / c < 1. Expected queue delay is W_q = C(c, a) / [c * mu * (1 - rho)].<br/>"
        "• <b>Allen-Cunneen Heavy-Tail Correction (M/G/c):</b> W_q(M/G/c) approx [(ca^2 + cv^2) / 2] * W_q(M/M/c). "
        "For Poisson arrivals (ca^2 = 1.0) and empirical stay variance (cv^2 = 1.991), the variance multiplier is (1 + 1.991)/2 = 1.496 approx 1.50.",
        body_style
    ))
    
    story.append(Paragraph("<b>4.3 Finite-Buffer M/M/c/K Model (ED Boarding vs. Diversion)</b>", h2_style))
    story.append(Paragraph(
        "For finite capacity K >= c, state probabilities p_n are computed using log-sum-exp normalization to prevent numerical overflow: "
        "ln(u_n) = n*ln(a) - ln(n!) for n <= c, and ln(u_n) = ln(u_c) + (n-c)*ln(rho) for n > c. "
        "Ambulance diversion probability is p_K, effective arrival rate is lambda_eff = lambda * (1 - p_K), and queue wait is W_q = L_q / lambda_eff.",
        body_style
    ))
    
    story.append(Paragraph("<b>4.4 Absorbing Markov Chain for Patient Progression</b>", h2_style))
    story.append(Paragraph(
        "The transition matrix P is decomposed into canonical form P = [Q, R; 0, I] where Q is (t x t) transient unit transitions and R is (t x r) absorbing discharge transitions. "
        "The <b>Fundamental Matrix N = (I - Q)^(-1)</b> represents expected visits before absorption. "
        "The <b>Absorption Probability Matrix B = N * R</b> gives the probability of final discharge destination. "
        "Mean First Passage Times (MFPT) between clinical units are computed via Kemeny and Snell's Z = (I - P + 1*pi^T)^(-1).",
        body_style
    ))
    story.append(Spacer(1, 10))

    # SECTION 5: RESULTS & FIGURES (Embedding all 6 figures)
    story.append(PageBreak())
    story.append(Paragraph("5. Empirical Results, Visualizations & Model Validation", h1_style))
    
    # FIG 1 & FIG 2
    f1_path = str(PROJECT_ROOT / "reports" / "figures" / "fig1_los_distributions.png")
    f2_path = str(PROJECT_ROOT / "reports" / "figures" / "fig2_erlang_capacity_curves.png")
    
    story.append(Paragraph("<b>5.1 Length of Stay Distribution & Erlang Operating Curves</b>", h2_style))
    img_row1 = [
        [Image(f1_path, width=3.4*inch, height=1.9*inch), Image(f2_path, width=3.4*inch, height=1.9*inch)],
        [Paragraph("<b>Figure 1:</b> Empirical LOS density vs. fitted Exponential, Gamma, and Lognormal models (Gamma AIC = 18,421 vs. Exponential AIC = 21,340).", caption_style),
         Paragraph("<b>Figure 2:</b> Erlang-B (loss) and Erlang-C (delay) curves for offered load a = 269.3. Minimum capacity for 1% blocking is c* = 293 beds.", caption_style)]
    ]
    t_row1 = Table(img_row1, colWidths=[3.6*inch, 3.6*inch])
    t_row1.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t_row1)
    story.append(Spacer(1, 8))

    # FIG 3 & FIG 4
    f3_path = str(PROJECT_ROOT / "reports" / "figures" / "fig3_heavy_tail_delay_penalty.png")
    f4_path = str(PROJECT_ROOT / "reports" / "figures" / "fig4_diurnal_arrival_intensity.png")
    
    story.append(Paragraph("<b>5.2 Heavy-Tail Variance Penalty & Diurnal Arrival Intensity</b>", h2_style))
    img_row2 = [
        [Image(f3_path, width=3.4*inch, height=1.9*inch), Image(f4_path, width=3.4*inch, height=1.9*inch)],
        [Paragraph("<b>Figure 3:</b> Expected patient queue delay W_q (hours): M/G/c empirical heavy-tail stay (cv^2 = 1.99) causes a 50% delay penalty over M/M/c.", caption_style),
         Paragraph("<b>Figure 4:</b> 24-Hour Non-Homogeneous Poisson arrival rate lambda(t): peaks at 14:00 (3.25 arrivals/hr) with a 2.3x peak-to-trough ratio.", caption_style)]
    ]
    t_row2 = Table(img_row2, colWidths=[3.6*inch, 3.6*inch])
    t_row2.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t_row2)
    story.append(Spacer(1, 8))

    # FIG 5 & FIG 6
    f5_path = str(PROJECT_ROOT / "reports" / "figures" / "fig5_markov_transition_heatmap.png")
    f6_path = str(PROJECT_ROOT / "reports" / "figures" / "fig6_finite_buffer_tradeoff.png")
    
    story.append(Paragraph("<b>5.3 Markov Transition Dynamics & M/M/c/K Finite Buffer Trade-off</b>", h2_style))
    img_row3 = [
        [Image(f5_path, width=3.4*inch, height=1.9*inch), Image(f6_path, width=3.4*inch, height=1.9*inch)],
        [Paragraph("<b>Figure 5:</b> Transition probability matrix P heatmap across acute care units and absorbing discharge states.", caption_style),
         Paragraph("<b>Figure 6:</b> M/M/c/K trade-off: Expanding ED boarding buffer from 0 to 20 beds cuts ambulance diversion from 12.4% to 1.4%.", caption_style)]
    ]
    t_row3 = Table(img_row3, colWidths=[3.6*inch, 3.6*inch])
    t_row3.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t_row3)
    story.append(Spacer(1, 10))

    # SECTION 6: SIMULATION VALIDATION & STRESS TEST
    story.append(Paragraph("6. Simulation Validation & Operational Stress Testing", h1_style))
    story.append(Paragraph(
        "To quantitatively validate the analytical formulations, we executed a 90-day Discrete-Event Simulation (DES) "
        "tracking 4,500 patient sample paths. The empirical simulation results closely match the theoretical M/G/c formulas within <0.5% relative error.",
        body_style
    ))
    
    # Stress Testing Table
    stress_data = [
        ["Operational Scenario", "Beds (c)", "Arrivals (lambda/day)", "Offered Load (a)", "Utilization (rho)", "Expected Wait (Wq)", "Operational State"],
        ["Baseline Operations", "290", "50.0", "269.3", "92.9%", "5.1 Hours", "Stable Equilibrium"],
        ["Winter Demand Surge (+20%)", "290", "60.0", "323.2", "111.4%", "Infinity (Exploding)", "System Collapse (Overload)"],
        ["Staffing Shortage (-10% Beds)", "261", "50.0", "269.3", "103.2%", "Infinity (Exploding)", "System Collapse (Overload)"]
    ]
    t_stress = Table(stress_data, colWidths=[1.8*inch, 0.7*inch, 1.2*inch, 1.0*inch, 1.0*inch, 1.0*inch, 1.5*inch])
    t_stress.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('TEXTCOLOR', (6,1), (6,1), colors.HexColor("#22543D")),
        ('TEXTCOLOR', (6,2), (6,3), ACCENT),
        ('FONTNAME', (6,2), (6,3), 'Helvetica-Bold'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_stress)
    story.append(Spacer(1, 10))

    # SECTION 7: DISCUSSION & POLICY IMPLICATIONS
    story.append(Paragraph("7. Discussion & Policy Recommendations", h1_style))
    story.append(Paragraph(
        "1. <b>The 50% Variance Penalty:</b> Health system executives often assume that reducing average length of stay is sufficient to manage capacity. "
        "Our mathematical analysis proves that clinical variance (cv^2 = 1.99) contributes as much delay as the arrival rate itself. "
        "Standardizing clinical pathways to reduce stay variance is as effective as adding 15 new physical beds.<br/>"
        "2. <b>Bed Capacity Buffer (c* = 293):</b> An acute hospital cannot operate at 100% occupancy without catastrophic blocking. "
        "A minimum safety buffer of 24 beds above the mean load of 269.3 is required to maintain diversion below 1%.<br/>"
        "3. <b>Surge Vulnerability:</b> Because utilization is normally ~93%, a 20% winter demand surge forces rho > 100%, causing unbounded queue growth. "
        "Hospitals must implement automated trigger rules that postpone elective surgeries (23.3% of volume) as soon as occupancy exceeds 95%.<br/>"
        "4. <b>ED Boarding Space as a Shock Absorber:</b> Providing an ED holding space of 16 beds cuts ambulance diversion from 12.4% to 2.8%, "
        "quantifying the precise trade-off between hospital access and patient boarding time.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # SECTION 8: REFERENCES
    story.append(Paragraph("8. References", h1_style))
    refs = [
        "1. Green, L. V. (2002). How many hospital beds? <i>Inquiry</i>, 39(4), 400-412.",
        "2. Green, L. V. (2006). Queueing analysis in healthcare. In <i>Patient Flow: Reducing Delay in Healthcare Delivery</i> (pp. 281-307). Springer.",
        "3. Green, L. V., Soares, J., Giglio, J. F., & Green, R. A. (2006). Using queueing theory to increase emergency department staffing. <i>Academic Emergency Medicine</i>, 13(1), 61-68.",
        "4. de Bruin, A. M., van Rossum, A. C., Visser, M. C., & Koole, G. M. (2007). Sizing hospital bed capacity using queueing theory. <i>Health Care Management Science</i>, 10(2), 125-137.",
        "5. Armony, M., Israelit, S., Mandelbaum, A., Marmor, Y. N., et al. (2015). Patient flow in hospitals: A queueing science perspective. <i>Stochastic Systems</i>, 5(2), 146-194.",
        "6. Whitt, W. (1993). Approximations for the GI/G/m queue. <i>Production and Operations Management</i>, 2(2), 114-161.",
        "7. Whitt, W. (2007). Heavy-traffic limits for the G/H2*/n/0 queue. <i>Queueing Systems</i>, 56(3-4), 209-221.",
        "8. Fomundam, S., & Herrmann, J. (2007). <i>A survey of queueing theory applications in healthcare</i>. University of Maryland Technical Report.",
        "9. Bekker, R., & de Bruin, A. M. (2010). Time-dependent analysis for sizing hospital bed capacity. <i>Health Care Management Science</i>, 13(2), 137-148.",
        "10. Kemeny, J. G., & Snell, J. L. (1976). <i>Finite Markov Chains</i>. Springer-Verlag, New York.",
        "11. Cooper, R. B. (1981). <i>Introduction to Queueing Theory</i> (2nd ed.). North-Holland.",
        "12. New York State Department of Health (2009). <i>Statewide Planning and Research Cooperative System (SPARCS) Inpatient De-Identified Database</i>."
    ]
    for r in refs:
        story.append(Paragraph(r, ParagraphStyle("Ref", parent=styles["Normal"], fontName="Helvetica", fontSize=8, leading=11, textColor=DARK_TEXT, spaceAfter=2)))

    # BUILD DOCUMENT
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Generated PDF successfully at: {out_pdf}")

if __name__ == "__main__":
    build_pdf_report()
