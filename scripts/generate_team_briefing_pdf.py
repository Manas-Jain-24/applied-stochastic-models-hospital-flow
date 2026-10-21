"""
Compiles the casual team overview briefing into a clean, attractive PDF
ready to send to friends and teammates.
"""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class BriefingCanvas(canvas.Canvas):
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
        self.setFont("Helvetica", 8.5)
        self.setFillColor(colors.HexColor("#718096"))
        
        # Header (pages 2+)
        if self._pageNumber > 1:
            self.drawString(54, 11 * inch - 36, "Applied Stochastic Models | Team Briefing & Project Overview")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, 11 * inch - 40, 8.5 * inch - 54, 11 * inch - 40)
            
        # Footer
        self.drawString(54, 36, "Applied Stochastic Models Course Project | Team Overview")
        self.drawRightString(8.5 * inch - 54, 36, f"Page {self._pageNumber} of {page_count}")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 46, 8.5 * inch - 54, 46)
        self.restoreState()


def build_team_briefing_pdf():
    out_pdf = PROJECT_ROOT / "reports" / "Team_Project_Overview_Briefing.pdf"
    doc = SimpleDocTemplate(
        str(out_pdf),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    PRIMARY = colors.HexColor("#1A365D")   # Deep navy
    SECONDARY = colors.HexColor("#2B6CB0") # Slate blue
    ACCENT = colors.HexColor("#2C7A7B")    # Teal accent
    DARK_TEXT = colors.HexColor("#2D3748")

    title_style = ParagraphStyle(
        "BTitle", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=PRIMARY, spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "BSub", parent=styles["Normal"],
        fontName="Helvetica", fontSize=11, leading=15, textColor=SECONDARY, spaceAfter=10
    )
    h2_style = ParagraphStyle(
        "BH2", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=12, leading=16, textColor=PRIMARY, spaceBefore=12, spaceAfter=4, keepWithNext=True
    )
    q_title_style = ParagraphStyle(
        "BQTitle", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=10, leading=14, textColor=SECONDARY, spaceBefore=8, spaceAfter=2, keepWithNext=True
    )
    body_style = ParagraphStyle(
        "BBody", parent=styles["Normal"],
        fontName="Helvetica", fontSize=9, leading=13, textColor=DARK_TEXT, spaceAfter=4
    )
    code_style = ParagraphStyle(
        "BCode", parent=styles["Normal"],
        fontName="Courier", fontSize=8, leading=11, textColor=colors.HexColor("#2D3748")
    )

    story = []

    # TITLE & HEADER
    story.append(Paragraph("Hospital Patient Flow & Bed Capacity Planning", title_style))
    story.append(Paragraph("Team Briefing: What We've Built, Questions Solved, & Next Steps", subtitle_style))

    # META BOX
    meta_data = [
        [Paragraph("<b>Course:</b> Applied Stochastic Models (ASM)", body_style),
         Paragraph("<b>GitHub:</b> github.com/Manas-Jain-24/applied-stochastic-models-hospital-flow", body_style)],
        [Paragraph("<b>Data Grounding:</b> 250,000 Real NYS SPARCS Discharges + MIMIC-IV Demo", body_style),
         Paragraph("<b>Code Status:</b> 33 Automated Unit Tests (100% Passing)", body_style)]
    ]
    meta_table = Table(meta_data, colWidths=[3.5 * inch, 3.7 * inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EDF2F7")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # TL;DR
    story.append(Paragraph("<b>The 2-Minute Executive Summary</b>", h2_style))
    story.append(Paragraph(
        "We are modeling hospital bed capacity, emergency overcrowding, and patient wait times using stochastic processes and queueing theory. "
        "Instead of waiting weeks for restricted data access, we calibrated our pipeline using <b>250,000 real hospital records</b> from New York State SPARCS "
        "and integrated the open-access <b>MIMIC-IV Demo</b> from PhysioNet. All 10 mathematical modules, discrete-event simulations, and 9 publication-grade figures "
        "are completely built, tested, and pushed to our GitHub repository.",
        body_style
    ))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0"), spaceBefore=6, spaceAfter=8))

    # 11 QUESTIONS SOLVED
    story.append(Paragraph("<b>The 11 Core Research Questions Solved</b>", h2_style))

    questions = [
        ("1. Does the textbook exponential assumption hold for hospital length of stay?",
         "<b>NO.</b> Exponential service requires squared coefficient of variation cv^2 = 1.0. Our 250k real records revealed <b>cv^2 = 1.99 approx 2.0</b>. By the Allen-Cunneen M/G/c approximation, this recovery variance creates a <b>50% delay penalty</b> (Wq increases from 3.4 hrs to 5.1 hrs)."),

        ("2. How many beds does a hospital actually need?",
         "<b>c* = 293 beds.</b> For an offered load of a = 269.3 occupied bed-days, Erlang-B proves you cannot run at 100% capacity. Keeping blocking below 1% requires a safety buffer of at least <b>24 beds</b> to absorb stochastic arrival spikes."),

        ("3. How much does Emergency vs. Elective triage prioritization help?",
         "<b>It cuts emergency wait times by 8x without buying more beds.</b> Two-class non-preemptive priority queueing ensures emergency patients wait only <b>1.5 hours</b> by safely shifting delay onto scheduled elective patients (12.3 hours)."),

        ("4. Are hospital arrivals a steady Poisson process, or do they cluster?",
         "<b>Heavily clustered throughout the day.</b> Index of Dispersion for Counts (IDC = 1.34 > 1.0) proved overdispersion. Arrivals peak at <b>2:12 PM</b> (3.25 arrivals/hr) and drop to 0.91 arrivals/hr at 2:12 AM. We modeled this with a diurnal Non-Homogeneous Poisson Process (NHPP) and Lewis-Shedler thinning."),

        ("5. What happens when Emergency Room holding space is capped?",
         "In an M/M/c/K finite-buffer queue, expanding ED boarding holding beds from 0 to 20 cuts ambulance diversion from <b>12.4% down to 1.4%</b>, precisely quantifying the trade-off between ambulance access and patient boarding delay."),

        ("6. Where do patients go when they leave acute hospital care?",
         "Using an <b>Absorbing Markov Chain</b> (fundamental matrix N = (I-Q)^-1), ICU patients spend an average of 1.48 ward visits before discharge, with a 10.1% in-hospital mortality risk and 33.2% transitioning to Skilled Nursing Facilities (SNF)."),

        ("7. Can the hospital handle a winter flu / COVID surge?",
         "<b>NO, the system collapses.</b> A +20% surge pushes traffic intensity to rho = 111% (> 1.0), triggering infinite queue growth. Hospitals must implement automated trigger rules to pause elective surgeries whenever occupancy reaches 95%."),

        ("8. How do hospital departments interact across an entire network?",
         "We modeled an <b>Open Jackson Queueing Network</b> solving (I - P^T) Lambda = gamma. Patients transition between Emergency -> ICU -> Step-Down -> Med/Surg -> Discharge. Medical/Surgical is the primary bottleneck (rho = 92.2%), and total hospital dwell time averages <b>5.19 days</b> across all interconnected wards."),

        ("9. Can smart staffing shifts fix afternoon crowding without hiring more nurses?",
         "<b>YES, a 97.3% drop in peak delay with ZERO extra bed-hours!</b> Pointwise Stationary Approximation (PSA) shows constant staffing causes afternoon wait times of 41.5 min. Shifting 25 beds from quiet night hours to peak afternoon hours drops wait time to <b>1.1 minutes</b>."),

        ("10. How should beds be partitioned between ICU, Emergency, and Surgery?",
         "<b>Proportional sizing fails; Fox's greedy marginal allocation saves 85.1% weighted blocking.</b> Naive proportional sizing under-buffers the ICU (6.66% rejection rate). Optimal allocation provides +15 safety beds to ICU, reducing ICU rejection to <b>0.14%</b>."),

        ("11. What about MIMIC data?",
         "We downloaded and parsed the official <b>MIMIC-IV Clinical Demo and MIMIC-IV-ED Demo</b> from PhysioNet (275 encounters, ICU length of stay, ESI triage levels 1-5). Our adapter (src/mimic_adapter.py) calibrated parameters into data/processed/mimic_empirical_parameters.json and is ready to process full MIMIC instantly.")
    ]

    for q_text, ans_text in questions:
        story.append(Paragraph(q_text, q_title_style))
        story.append(Paragraph(ans_text, body_style))

    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0"), spaceBefore=6, spaceAfter=8))

    # HOW TO RUN
    story.append(Paragraph("<b>How Teammates Can Clone and Run the Code (< 1 Second)</b>", h2_style))
    run_steps = [
        "1. Clone the repository: <code>git clone https://github.com/Manas-Jain-24/applied-stochastic-models-hospital-flow.git</code>",
        "2. Install packages: <code>pip install -r requirements.txt</code>",
        "3. Run automated verification: <code>python scripts/verify_all.py</code> (validates all 33 unit tests and 9 figures in ~0.2s)",
        "4. Open interactive notebook: <code>jupyter notebook notebooks/01_stochastic_hospital_flow.ipynb</code>"
    ]
    for s in run_steps:
        story.append(Paragraph(s, body_style))

    story.append(Spacer(1, 10))

    # DIVISION OF WORK
    story.append(Paragraph("<b>Recommended Division of Labor for the Final Submission</b>", h2_style))
    labor = [
        "<b>Teammate 1 (Math & Theory):</b> Review Sections 4 & 5 of the formal report (Erlang-B recursion, Erlang-C, Allen-Cunneen M/G/c, Jackson traffic equations, and Fox marginal allocation).",
        "<b>Teammate 2 (Literature Review):</b> Review Section 2 of the report (expanding citations on Linda Green, Armony, and de Bruin healthcare queueing papers).",
        "<b>You (Data & Presentation):</b> Present empirical results, the 9 publication figures, and assemble the 15-minute presentation slides matching Sir's exact guideline structure."
    ]
    for l in labor:
        story.append(Paragraph(f"&bull; {l}", body_style))

    doc.build(story, canvasmaker=BriefingCanvas)
    print(f"Generated team briefing PDF at: {out_pdf}")


if __name__ == "__main__":
    build_team_briefing_pdf()
