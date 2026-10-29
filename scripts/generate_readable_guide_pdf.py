"""
Generates a 100% human-readable, plain-English executive PDF guide:
reports/Hospital_Flow_Models_and_DeepDives_Readable_Guide.pdf

Specifically designed for high readability:
- ZERO raw LaTeX math symbols or messy equations.
- Clear plain-English headings, intuitive terminology, and high-impact practical takeaways.
- Complete coverage of all 11 Questions and 3 Deep Dives:
  * The Plain Question / Problem
  * Intuitive Model Name
  * Real-World Dataset & Sample Size
  * Algorithm / Method Used (Explained Simply)
  * Real-World Observation & Actionable Numbers
"""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class CleanNumberedCanvas(canvas.Canvas):
    """Two-pass canvas for running header, footer, and page numbers."""
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
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Running header (pages 2+)
        if self._pageNumber > 1:
            self.drawString(42, 11 * inch - 30, "Applied Stochastic Models | Plain-English Hospital Flow & Capacity Guide")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(42, 11 * inch - 34, 8.5 * inch - 42, 11 * inch - 34)

        # Running footer (all pages)
        self.setFont("Helvetica", 8)
        self.drawString(42, 26, "Hospital Bed Capacity & Patient Flow Project | Executive Reference")
        self.drawRightString(8.5 * inch - 42, 26, f"Page {self._pageNumber} of {page_count}")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(42, 36, 8.5 * inch - 42, 36)

        self.restoreState()


def build_readable_pdf():
    out_pdf = PROJECT_ROOT / "reports" / "Hospital_Flow_Models_and_DeepDives_Readable_Guide.pdf"
    
    # Printable width: 612 - 84 = 528 pt
    doc = SimpleDocTemplate(
        str(out_pdf),
        pagesize=letter,
        leftMargin=42,
        rightMargin=42,
        topMargin=44,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()

    NAVY = colors.HexColor("#0F172A")       # Slate 900
    BLUE = colors.HexColor("#1E40AF")       # Blue 800
    TEAL = colors.HexColor("#0F766E")       # Teal 700
    TEXT_DARK = colors.HexColor("#1E293B")  # Slate 800
    TEXT_MUTED = colors.HexColor("#475569") # Slate 600
    CARD_BG = colors.HexColor("#F8FAFC")    # Slate 50
    CARD_BORDER = colors.HexColor("#E2E8F0")# Slate 200
    BADGE_BG = colors.HexColor("#EFF6FF")   # Blue 50

    title_style = ParagraphStyle(
        "RTitle", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=NAVY, spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "RSub", parent=styles["Normal"],
        fontName="Helvetica", fontSize=10.5, leading=14, textColor=BLUE, spaceAfter=8
    )
    h1_style = ParagraphStyle(
        "RH1", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=12.5, leading=16, textColor=NAVY, spaceBefore=10, spaceAfter=5, keepWithNext=True
    )
    body_style = ParagraphStyle(
        "RBody", parent=styles["Normal"],
        fontName="Helvetica", fontSize=8.5, leading=12.5, textColor=TEXT_DARK, spaceAfter=3
    )
    meta_style = ParagraphStyle(
        "RMeta", parent=styles["Normal"],
        fontName="Helvetica", fontSize=8, leading=11, textColor=TEXT_MUTED
    )
    card_title_style = ParagraphStyle(
        "RCardTitle", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=BLUE, spaceAfter=3
    )
    field_label_style = ParagraphStyle(
        "RFieldLabel", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=8.5, leading=12, textColor=NAVY
    )
    tbl_hdr_style = ParagraphStyle(
        "RTblHdr", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=7.5, leading=9.5, textColor=colors.white
    )
    tbl_cell_style = ParagraphStyle(
        "RTblCell", parent=styles["Normal"],
        fontName="Helvetica", fontSize=7.2, leading=9.5, textColor=TEXT_DARK
    )
    tbl_cell_bold = ParagraphStyle(
        "RTblCellBold", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=7.2, leading=9.5, textColor=BLUE
    )

    story = []

    # 1. TITLE & EXECUTIVE BANNER
    story.append(Paragraph("Hospital Patient Flow, Congestion & Bed Sizing", title_style))
    story.append(Paragraph("Plain-English Project Guide: Questions, Models, Datasets, Algorithms & Deep Dives", subtitle_style))

    # Meta Info Card
    meta_table = Table([
        [
            Paragraph("<b>Course:</b> Applied Stochastic Models (ASM)", meta_style),
            Paragraph("<b>Real-World Data:</b> 250,000 New York State Hospital Discharges (SPARCS)", meta_style)
        ],
        [
            Paragraph("<b>Code Status:</b> 38 Automated Unit Tests (100% Passing)", meta_style),
            Paragraph("<b>Clinical Focus:</b> Eliminating Waiting Spikes, Diversions & Gridlock", meta_style)
        ]
    ], colWidths=[260, 268])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BADGE_BG),
        ('BOX', (0,0), (-1,-1), 0.5, CARD_BORDER),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))

    # 2. MASTER SUMMARY MATRIX TABLE (PLAIN ENGLISH)
    story.append(Paragraph("Master Overview: All Questions & Deep Dives at a Glance", h1_style))
    story.append(Paragraph("A quick-reference summary of what model and data each question used, how it was computed, and what practical result it proved.", meta_style))
    story.append(Spacer(1, 4))

    table_data = [
        [
            Paragraph("<b>Q#</b>", tbl_hdr_style),
            Paragraph("<b>Everyday Operational Question</b>", tbl_hdr_style),
            Paragraph("<b>Practical Model</b>", tbl_hdr_style),
            Paragraph("<b>Dataset Used</b>", tbl_hdr_style),
            Paragraph("<b>Algorithm / Method</b>", tbl_hdr_style),
            Paragraph("<b>Key Takeaway in Plain English</b>", tbl_hdr_style)
        ],
        [
            Paragraph("<b>Q1</b>", tbl_cell_bold),
            Paragraph("Do patients recover at a constant, memoryless rate?", tbl_cell_style),
            Paragraph("Heavy-Tail Queue Model (M/G/c) & Stay Curves", tbl_cell_style),
            Paragraph("NYS SPARCS (250,000 patient records)", tbl_cell_style),
            Paragraph("Statistical curve fitting (MLE) & Variance penalty formula", tbl_cell_style),
            Paragraph("<b>NO.</b> Complicated patients stay for weeks, doubling stay variance and inflating wait times by <b>50%</b> over textbook models.", tbl_cell_style)
        ],
        [
            Paragraph("<b>Q2</b>", tbl_cell_bold),
            Paragraph("How many beds does a hospital actually need?", tbl_cell_style),
            Paragraph("Erlang Bed Loss Model (Zero-buffer system)", tbl_cell_style),
            Paragraph("NYS SPARCS (50 daily arrivals, 5.4-day stay)", tbl_cell_style),
            Paragraph("Step-by-step downward stable recursion", tbl_cell_style),
            Paragraph("Operating at 100% capacity turns away 872 patients/yr. Safe operation requires <b>293 beds (+24 safety buffer)</b>.", tbl_cell_style)
        ],
        [
            Paragraph("<b>Q3</b>", tbl_cell_bold),
            Paragraph("Can we prioritize emergency patients over elective surgery?", tbl_cell_style),
            Paragraph("Two-Class Priority Queue (Non-preemptive)", tbl_cell_style),
            Paragraph("SPARCS split (77% emergency vs 23% elective)", tbl_cell_style),
            Paragraph("Priority delay formula using Erlang-C waiting", tbl_cell_style),
            Paragraph("Cuts emergency wait time by <b>nearly 3x</b> (from 33 min down to 6 min) by shifting delay safely onto scheduled elective cases.", tbl_cell_style)
        ],
        [
            Paragraph("<b>Q4</b>", tbl_cell_bold),
            Paragraph("Do patients arrive steadily or in surges?", tbl_cell_style),
            Paragraph("Time-Varying Arrival Process (24-hour wave)", tbl_cell_style),
            Paragraph("NYS SPARCS & MIMIC-IV ED timestamps", tbl_cell_style),
            Paragraph("Overdispersion test & Random Thinning algorithm", tbl_cell_style),
            Paragraph("Arrivals surge <b>3.55x</b> from night (2:12 AM) to afternoon (2:12 PM), causing massive peak-hour congestion.", tbl_cell_style)
        ],
        [
            Paragraph("<b>Q5</b>", tbl_cell_bold),
            Paragraph("How many holding beds stop ambulance diversion?", tbl_cell_style),
            Paragraph("Finite-Buffer Queue (Inpatient + ED Holding)", tbl_cell_style),
            Paragraph("NYS SPARCS (285 beds + holding buffer)", tbl_cell_style),
            Paragraph("Log-Sum-Exp normalized state probabilities", tbl_cell_style),
            Paragraph("Adding 16 holding beds slashes ambulance diversion by <b>77%</b> (from 12.4% down to 2.8%) at a 3.6-hour boarding delay.", tbl_cell_style)
        ],
        [
            Paragraph("<b>Q6</b>", tbl_cell_bold),
            Paragraph("Where do patients go after leaving acute wards?", tbl_cell_style),
            Paragraph("Absorbing Markov Chain (Ward Transfer Network)", tbl_cell_style),
            Paragraph("SPARCS discharge outcomes (250,000 records)", tbl_cell_style),
            Paragraph("Fundamental matrix inversion & absorption math", tbl_cell_style),
            Paragraph("Direct ICU admissions face a <b>10.1% mortality rate</b> and a <b>33.2% chance of needing a nursing facility</b>.", tbl_cell_style)
        ],
        [
            Paragraph("<b>Q7</b>", tbl_cell_bold),
            Paragraph("Can the hospital survive a winter flu surge?", tbl_cell_style),
            Paragraph("System Stability Limits & Computer Simulation", tbl_cell_style),
            Paragraph("SPARCS baseline under +20% demand shock", tbl_cell_style),
            Paragraph("Traffic intensity threshold & Event simulation", tbl_cell_style),
            Paragraph("<b>NO.</b> A 20% surge pushes demand above 100% capacity, collapsing queues. Hospitals must pause elective surgery at 95% occupancy.", tbl_cell_style)
        ],
        [
            Paragraph("<b>Q8</b>", tbl_cell_bold),
            Paragraph("How do ER, ICU, and surgical wards interact?", tbl_cell_style),
            Paragraph("Multi-Department Open Network (4 stations)", tbl_cell_style),
            Paragraph("SPARCS & MIMIC ward transfer trajectories", tbl_cell_style),
            Paragraph("Linear traffic flow equation solver", tbl_cell_style),
            Paragraph("<b>Medical/Surgical</b> is the main bottleneck (92% full). Overall hospital stay across all connected wards averages <b>5.2 days</b>.", tbl_cell_style)
        ],
        [
            Paragraph("<b>Q9</b>", tbl_cell_bold),
            Paragraph("Can shifting nurse hours eliminate the afternoon rush?", tbl_cell_style),
            Paragraph("Hourly Dynamic Staffing (PSA queue analysis)", tbl_cell_style),
            Paragraph("SPARCS / MIMIC-ED 24-hour arrival curve", tbl_cell_style),
            Paragraph("Hourly queue evaluation & 3-shift bed adjustment", tbl_cell_style),
            Paragraph("Shifting 25 beds from quiet nights to busy afternoons cuts peak wait from <b>41.5 min to 1.1 min (-97.3%)</b> with <b>zero extra budget</b>.", tbl_cell_style)
        ],
        [
            Paragraph("<b>Q10</b>", tbl_cell_bold),
            Paragraph("How should beds be split between ICU, ER, and Surgery?", tbl_cell_style),
            Paragraph("Optimal Resource Allocator (Convex Optimization)", tbl_cell_style),
            Paragraph("Multi-ward patient demand from SPARCS", tbl_cell_style),
            Paragraph("<b>Fox's Greedy Marginal Allocation Algorithm</b>", tbl_cell_style),
            Paragraph("Proportional splitting starves the ICU (6.7% turnaways). Fox allocation provides square-root buffering, cutting turnaways by <b>84%</b>.", tbl_cell_style)
        ],
        [
            Paragraph("<b>Q11</b>", tbl_cell_bold),
            Paragraph("How did we connect real intensive care data?", tbl_cell_style),
            Paragraph("Automated Data Pipeline & Parameter Extractor", tbl_cell_style),
            Paragraph("PhysioNet MIMIC-IV Clinical & ED Demo v2.2", tbl_cell_style),
            Paragraph("Timestamp dwell extractor & JSON parameter writer", tbl_cell_style),
            Paragraph("Calibrated ICU stay (3.7 days), triage acuity (8.7% critical), and 5.5% mortality. Ready for full database with zero code changes.", tbl_cell_style)
        ],
        [
            Paragraph("<b>DD 1</b>", tbl_cell_bold),
            Paragraph("Deep Dive 1: Why Patient Stays Are Unpredictable", tbl_cell_style),
            Paragraph("Discharge Risk Over Time & Variance Penalty", tbl_cell_style),
            Paragraph("NYS SPARCS ($250,000$ patient stays)", tbl_cell_style),
            Paragraph("Curve fitting audit & Multi-server delay formula", tbl_cell_style),
            Paragraph("Discharge chance starts low, peaks on days 2–4, and drops for complex cases. Variance adds a <b>49.6% wait penalty</b>.", tbl_cell_style)
        ],
        [
            Paragraph("<b>DD 2</b>", tbl_cell_bold),
            Paragraph("Deep Dive 2: Rigorous Bed Sizing & Priority Simulation", tbl_cell_style),
            Paragraph("Erlang Loss, Priority Queue, and Event Simulator", tbl_cell_style),
            Paragraph("NYS SPARCS & MIMIC emergency triage", tbl_cell_style),
            Paragraph("10-run computer simulation (0 cut-off patients)", tbl_cell_style),
            Paragraph("Simulation confirms theory: emergency patients wait 5.3 min vs 57.4 min for elective. Required buffer scales as square root of demand.", tbl_cell_style)
        ],
        [
            Paragraph("<b>DD 3</b>", tbl_cell_bold),
            Paragraph("Deep Dive 3: Ward Bottlenecks & Shift Optimization", tbl_cell_style),
            Paragraph("24h Dynamic Staffing & Multi-Ward Flow Balance", tbl_cell_style),
            Paragraph("SPARCS & MIMIC departmental flow matrix", tbl_cell_style),
            Paragraph("Exact network traffic solver & Fox greedy algorithm", tbl_cell_style),
            Paragraph("Proves the general ward is overloaded (125% capacity under baseline flow) and needs at least 151 beds. Shift staffing slashes wait by 97%.", tbl_cell_style)
        ]
    ]

    col_w = [34, 96, 94, 82, 98, 124] # Exactly 528 pt
    matrix_table = Table(table_data, colWidths=col_w, repeatRows=1)
    matrix_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BLUE),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.35, CARD_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, CARD_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(matrix_table)
    story.append(Spacer(1, 10))

    # PAGE BREAK FOR DETAILED READABLE CARDS
    story.append(PageBreak())

    # 3. DETAILED PLAIN-ENGLISH BREAKDOWN OF QUESTIONS 1 TO 11
    story.append(Paragraph("Detailed Plain-English Breakdown of the 11 Questions", h1_style))
    story.append(Paragraph("Clear, intuitive explanations of each problem, the method used to solve it, and the real-world operational takeaway.", subtitle_style))
    story.append(Spacer(1, 4))

    q_cards = [
        (
            "Question 1: Does the textbook exponential assumption hold for hospital stays?",
            "Heavy-Tailed Multi-Server Queue Model (M/G/c) & Parametric Stay Distributions",
            "New York State SPARCS Inpatient Database (250,000 real patient discharges; average stay = 5.4 days, stay variance = 57.8 days).",
            "We used Maximum Likelihood curve fitting to test Exponential, Gamma, Lognormal, and Weibull distributions. We then applied the Allen–Cunneen variance correction formula to measure how stay variation inflates patient waiting times.",
            "<b>No, the textbook assumption fails completely.</b> Textbook models assume a patient who has been in bed for 10 days has the exact same chance of going home today as someone who arrived this morning (the memoryless property). In reality, complicated patients stay for weeks, creating huge stay variation (variance is double the mean squared). This extra uncertainty creates a <b>50% delay penalty</b>—meaning standard formulas underestimate patient waiting lines by half!",
            "src/distributions.py & src/queueing.py"
        ),
        (
            "Question 2: How many beds does a hospital actually need?",
            "Erlang Bed Loss Model (Zero-Buffer Multi-Server System)",
            "NYS SPARCS (50 patient arrivals per day, average length of stay of 5.4 days = ~269 occupied beds on average).",
            "We used a numerically stable downward recursion of the Erlang-B formula to calculate bed blocking for large capacities (around 300 beds) without causing computer calculation errors.",
            "If a hospital builds exactly enough beds to match its average demand (269 beds), it will turn away or divert <b>872 emergency patients every year (a 4.8% blocking rate)</b>. To guarantee that patient turnaways stay below 1%, the hospital must install at least <b>293 beds</b>. This proves that acute hospitals cannot run at 100% capacity; a <b>24-bed safety buffer</b> is mathematically mandatory to absorb random arrival spikes.",
            "src/queueing.py (erlang_b, min_capacity_erlang_b)"
        ),
        (
            "Question 3: How much does prioritizing emergency cases help?",
            "Two-Class Non-Preemptive Priority Queue Model",
            "NYS SPARCS admission types (77% emergency/urgent vs. 23% elective surgery) and MIMIC emergency triage data.",
            "We used a multi-server priority queue algorithm that gives emergency patients first pick of any newly freed bed, while allowing doctors to finish treating elective patients already in a bed.",
            "Prioritization cuts emergency waiting times by <b>nearly 3 times</b> (from 33.4 minutes down to just <b>6.0 minutes</b>) without building a single extra bed! It does this by safely shifting the waiting time onto scheduled elective patients (who wait 74.4 minutes, well within their elective preparation window). The total workload on hospital staff remains exactly the same.",
            "src/queueing.py (priority_queue_two_class)"
        ),
        (
            "Question 4: Are hospital arrivals steady, or do they cluster?",
            "Time-Varying Non-Homogeneous Arrival Process (24-Hour Wave)",
            "NYS SPARCS arrival census and PhysioNet MIMIC-IV Emergency Department timestamps.",
            "We used an overdispersion test (Index of Dispersion for Counts) to prove arrivals cluster, fitted a 24-hour sinusoidal wave to hourly arrivals, and used the Lewis–Shedler random thinning algorithm to simulate realistic patient arrival timing.",
            "Arrivals do not trickle in at a steady rate. They follow a dramatic daily wave: peaking at <b>2:12 PM</b> (3.25 arrivals per hour) and dropping to a trickle at <b>2:12 AM</b> (0.91 arrivals per hour). That is a <b>3.55-fold surge</b> during the daytime, explaining why emergency departments experience severe afternoon gridlock if staffing is kept flat all day.",
            "src/arrival_process.py (simulate_nhpp_thinning)"
        ),
        (
            "Question 5: What happens when Emergency Room holding space is capped?",
            "Finite-Buffer Queueing Model (Inpatient Beds + Emergency Holding Beds)",
            "NYS SPARCS baseline demand (285 inpatient beds with emergency holding capacity ranging from 0 to 20 beds).",
            "We solved the steady-state probabilities of a finite-capacity system using a Log-Sum-Exp numerical technique to ensure computer calculations remain accurate when handling hundreds of bed states.",
            "This model clearly reveals the trade-off between ambulance turnaways and hallway boarding delays. With zero holding beds, the hospital puts ambulances on diversion <b>12.4% of the time</b>. Adding 16 holding beds slashes ambulance diversion by <b>77% (down to 2.8%)</b>, but admitted patients now wait an average of <b>3.6 hours</b> in emergency bays before moving to an inpatient room.",
            "src/queueing.py (mmck_finite_buffer_metrics)"
        ),
        (
            "Question 6: Where do patients go when they leave acute hospital care?",
            "Absorbing Markov Chain (Downstream Patient Transfer Network)",
            "NYS SPARCS discharge records (250,000 encounters) tracking movements between Medical, Surgical, ICU, Home, and Care Facilities.",
            "We partitioned hospital wards into temporary transfer states and permanent exit states, inverted the transition matrix (the Fundamental Matrix), and computed absorption probabilities.",
            "Patients admitted directly into the Intensive Care Unit (ICU) spend an average of 1.48 ward transfers before leaving acute care. They face an in-hospital <b>mortality risk of 10.1%</b> and a <b>33.2% probability of needing long-term placement in a Skilled Nursing Facility (SNF)</b>. This shows that downstream care availability directly controls hospital discharge speed.",
            "src/markov_chain.py (analyze_absorbing_markov_chain)"
        ),
        (
            "Question 7: Can the hospital absorb a winter flu surge or staff shortage?",
            "System Stability Boundary Analysis and Event-Calendar Simulation",
            "Calibrated SPARCS parameters under simulated winter surge (+20% demand) and nurse shortage (-10% beds).",
            "We evaluated the queue stability rule (demand must be less than capacity) and simulated hospital operations using an event-calendar discrete-event simulator.",
            "<b>No, the hospital collapses into unbounded gridlock.</b> At normal times, the hospital runs at 92.9% occupancy. A 20% winter surge pushes demand to 111% of total capacity, and a 10% nurse shortage pushes demand to 103%. In both cases, queues explode. To survive seasonal surges, hospitals must have an automated rule to <b>pause elective surgeries</b> whenever occupancy hits 95%.",
            "src/simulation.py & tests/test_simulation.py"
        ),
        (
            "Question 8: How do hospital departments interact across the whole facility?",
            "4-Station Open Queueing Network (Emergency, ICU, Step-Down, Medical/Surgical)",
            "Inter-ward routing patterns from SPARCS diagnostic categories and MIMIC transfer records.",
            "We set up and solved a system of traffic flow equations to find the true patient volume entering each ward, accounting for patients who transfer between units multiple times.",
            "Departments cannot be studied in isolation. Even though the Emergency Department gets the most outside arrivals, <b>General Medical/Surgical</b> ends up being the biggest bottleneck in the entire hospital (operating at <b>92.2% occupancy</b>) because patients from both ER and ICU transfer there. The average total stay across the entire hospital network is <b>5.2 days</b>.",
            "src/jackson_network.py (solve_traffic_equations)"
        ),
        (
            "Question 9: Can smart shift scheduling fix the afternoon rush without hiring?",
            "Hourly Dynamic Queue Modeling (Pointwise Stationary Approximation)",
            "The 24-hour diurnal arrival curve calibrated from SPARCS and MIMIC emergency timestamps.",
            "We computed patient waiting times hour-by-hour across all 24 hours under a flat staffing schedule versus a dynamic 3-shift nursing schedule that adjusts available beds to match demand.",
            "Keeping a flat 18 beds open 24/7 wastes staff at night but creates a painful <b>41.5-minute wait</b> during the afternoon rush. By moving 25 beds from quiet night hours to busy daytime hours (14 night / 22 day / 18 evening), the afternoon peak wait collapses to just <b>1.1 minutes (a 97.3% reduction!)</b>. This massive improvement uses the exact same total bed-hours, costing <b>$0 in extra budget</b>.",
            "src/time_varying.py (compare_constant_vs_dynamic_staffing)"
        ),
        (
            "Question 10: How should beds be divided between ICU, ER, and Surgery?",
            "Optimal Bed Allocator (Convex Optimization under Erlang Loss)",
            "Patient loads across ICU, Emergency, and Medical/Surgical wards with clinical severity penalties.",
            "We used <b>Fox's Greedy Marginal Allocation Algorithm</b>, which awards one bed at a time to whichever ward will achieve the biggest immediate drop in patient turnaways.",
            "Traditional hospital management divides beds proportionally to demand. This fails dangerously: it gives the ICU too few beds, causing a <b>6.7% ICU turnaway rate</b>! Fox's algorithm honors the square-root staffing rule, giving the ICU a dedicated 15-bed safety buffer. This drops ICU turnaways to <b>0.14%</b> and slashes total hospital patient turnaways by <b>84% to 85%</b>.",
            "src/bed_allocation.py (marginal_bed_allocation)"
        ),
        (
            "Question 11: How did we integrate real clinical intensive care data?",
            "Automated Healthcare Ingestion Pipeline and Parameter Adapter",
            "PhysioNet open-access <b>MIMIC-IV Clinical Demo and MIMIC-IV-ED Demo v2.2</b> (admissions, transfers, ICU stays, triage).",
            "We built an automated script that calculates exact patient stay minutes from timestamps, traces patient transfer paths between care units, and exports calibrated parameters to clean JSON files.",
            "The pipeline extracted realistic ICU stays (average 3.7 days), triage urgency breakdowns (8.7% immediate resuscitation, 46.9% emergent), and a 5.5% in-hospital mortality rate. The adapter is <b>100% drop-in scalable</b>: when full credentialed MIMIC-IV access arrives, it will process millions of records with zero code changes.",
            "src/mimic_adapter.py (run_mimic_pipeline)"
        )
    ]

    for title, model, data, method, obs, code in q_cards:
        card_content = [
            [Paragraph(f"<b>{title}</b>", card_title_style)],
            [Paragraph(f"<b>Stochastic Model:</b> {model}", body_style)],
            [Paragraph(f"<b>Dataset Used:</b> {data}", body_style)],
            [Paragraph(f"<b>How We Solved It:</b> {method}", body_style)],
            [Paragraph(f"<b>Key Practical Observation:</b><br/>{obs}", body_style)],
            [Paragraph(f"<b>Code File:</b> <font face='Courier' color='#0F172A'>{code}</font>", meta_style)]
        ]
        card_table = Table(card_content, colWidths=[528])
        card_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
            ('BOX', (0,0), (-1,-1), 0.5, CARD_BORDER),
            ('LINELEFT', (0,0), (0,-1), 3.0, BLUE),
            ('TOPPADDING', (0,0), (-1,-1), 3.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(card_table)
        story.append(Spacer(1, 5))

    # PAGE BREAK FOR DEEP DIVES
    story.append(PageBreak())

    # 4. THE THREE DEEP-DIVE MODULES IN PLAIN ENGLISH
    story.append(Paragraph("The Three Deep-Dive Investigation Tracks", h1_style))
    story.append(Paragraph("Advanced investigations exploring why hospital recovery is unpredictable, how many beds are truly needed, and how inter-ward flow causes bottlenecks.", subtitle_style))
    story.append(Spacer(1, 4))

    dd_cards = [
        (
            "Deep Dive 1: Why Patient Recovery Is Unpredictable (Hazard Rates & Delay Penalty)",
            "Expands Question 1 | Length of Stay Variance and Multi-Server Congestion",
            "Discharge Likelihood Over Time (Hazard Function Analysis), Pollaczek–Khinchine Variance Expansion, and Allen–Cunneen Multi-Server Delay Modeling.",
            "New York State SPARCS Database (250,000 real patient stays; average = 5.4 days, median = 3.0 days, variance = 57.8 days).",
            "We analyzed how the daily chance of discharge changes over the course of a patient's stay, compared bell-shaped vs. skewed distribution curves, and derived the exact mathematical multiplier that stay variance adds to waiting times.",
            "1. <b>The Discharge Curve:</b> Patients cannot be discharged on Day 0 (they need stabilization). Discharge likelihood peaks during Days 2 to 4, then drops off for complex patients who develop complications. This matches a Lognormal curve, not an Exponential one.<br/>"
            "2. <b>The 50% Delay Penalty:</b> Because patient recovery times vary so widely, hospital beds free up unpredictably. Under the Allen–Cunneen formula, this real-world variation makes patient waiting times <b>49.6% longer</b> than standard textbook models estimate.<br/>"
            "3. <b>Methodological Lesson:</b> With 250,000 records, standard statistical tests reject any rigid textbook distribution because real human recovery has unique tails; administrators must rely on information criteria (AIC/BIC) rather than simple p-values.",
            "deep_dives/01_heavy_tail_service_deep_dive.md"
        ),
        (
            "Deep Dive 2: Sizing the Hospital & Priority Rules (Simulation & Capacity Audit)",
            "Expands Questions 2, 3 & 5 | Capacity Sizing, Triage Policies & Computer Simulation",
            "Erlang Bed Sizing Model, Two-Class Priority Triage, and a 10-Replication Discrete-Event Computer Simulator.",
            "NYS SPARCS (50 daily admissions, 60% emergency vs. 40% elective) and MIMIC Emergency Department triage categories.",
            "We used the Jagerman recursion for bed loss calculations, a priority queueing heuristic, and built a custom event-calendar computer simulation running over 730 days with a dedicated draining phase to ensure zero patients were cut off prematurely.",
            "1. <b>Exact Sizing Reconciled:</b> Sizing capacity to match average demand (269 beds) causes 4.8% of patients to be turned away (~872 patients/year). Achieving less than 1% turnaways requires exactly <b>293 beds (+24 bed safety buffer)</b>.<br/>"
            "2. <b>The Square-Root Staffing Law:</b> Safe capacity follows the Halfin–Whitt rule (Capacity = Demand + 1.44 times the square root of demand). Larger hospitals need smaller percentage buffers than small community hospitals.<br/>"
            "3. <b>Computer Simulation Confirms Theory:</b> 10 independent simulation runs proved that emergency patients wait only <b>5.3 minutes</b> while elective patients wait <b>57.4 minutes</b>. The mathematical formulas provide a safe, conservative estimate.",
            "deep_dives/02_capacity_and_priority_deep_dive.md & src/priority_simulation.py"
        ),
        (
            "Deep Dive 3: Ward Bottlenecks & Shift Scheduling (Flow Networks & Optimization)",
            "Expands Questions 8, 9 & 10 | 24-Hour Shift Adjustments & Inter-Ward Flow Networks",
            "Time-Varying Queue Analysis (PSA), 4-Station Open Jackson Network, and Fox's Greedy Bed Allocator.",
            "Diurnal arrival curves from SPARCS/MIMIC (peaking at 2:12 PM), 4-ward transfer matrices, and departmental patient loads.",
            "We used random thinning to simulate peak/trough arrivals, evaluated hourly queue waiting times across 3 nurse shifts, solved linear balance equations for ward-to-ward transfers, and ran Fox's greedy optimization algorithm.",
            "1. <b>Cost-Neutral Shift Scheduling:</b> Moving 25 beds from quiet night hours to the busy afternoon period drops peak wait times from <b>41.5 minutes down to 1.1 minutes (-97.3%)</b> with <b>zero extra staffing budget</b>.<br/>"
            "2. <b>The Hidden Network Bottleneck:</b> Solving inter-ward traffic revealed that the nominal 120-bed Medical/Surgical ward is actually <b>overloaded at 125% capacity</b> due to incoming transfers from the ER and ICU. It requires at least <b>151 beds</b> just to be stable, and <b>178 beds</b> for normal operation.<br/>"
            "3. <b>Optimal Bed Allocation:</b> Fox's greedy algorithm gives 33 beds to ICU, 43 to ER observation, and 154 to Medical/Surgical, cutting overall hospital patient turnaways by <b>83.8%</b> compared to naive proportional sizing.",
            "deep_dives/03_diurnal_staffing_and_network_deep_dive.md & deep_dives/verify_deep_dives.py"
        )
    ]

    for title, subtitle, model, data, method, obs, code in dd_cards:
        dd_card_content = [
            [Paragraph(f"<b>{title}</b>", card_title_style)],
            [Paragraph(f"<i>{subtitle}</i>", subtitle_style)],
            [Paragraph(f"<b>Stochastic Framework:</b> {model}", body_style)],
            [Paragraph(f"<b>Real Data Used:</b> {data}", body_style)],
            [Paragraph(f"<b>How We Investigated:</b> {method}", body_style)],
            [Paragraph(f"<b>Key Discoveries in Plain English:</b><br/>{obs}", body_style)],
            [Paragraph(f"<b>Source File:</b> <font face='Courier' color='#0F172A'>{code}</font>", meta_style)]
        ]
        dd_card_table = Table(dd_card_content, colWidths=[528])
        dd_card_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
            ('BOX', (0,0), (-1,-1), 0.5, CARD_BORDER),
            ('LINELEFT', (0,0), (0,-1), 3.0, TEAL),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(dd_card_table)
        story.append(Spacer(1, 8))

    # BUILD DOCUMENT
    doc.build(story, canvasmaker=CleanNumberedCanvas)
    print(f"Successfully generated: {out_pdf}")


if __name__ == "__main__":
    build_readable_pdf()
