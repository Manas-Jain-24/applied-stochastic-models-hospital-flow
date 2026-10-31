"""
Build Publication-Grade Comprehensive Technical Analysis Report PDF
===================================================================
Compiles `reports/Comprehensive_Technical_Analysis_Report.md` into:
`reports/pdf/Comprehensive_Technical_Analysis_Report.pdf`
Using ReportLab with custom NumberedCanvas, professional academic typography,
embedded figures for all 13 Problem Statements, formatted tables, and callouts.
"""

import sys
import os
import re
from pathlib import Path
from PIL import Image as PILImage

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle,
    Spacer, KeepTogether, PageBreak, Image, HRFlowable
)
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

class AcademicNumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute total pages and draw
    running headers and footers ("Page X of Y").
    Suppresses header/footer on title/cover page (Page 1).
    """
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

    def draw_page_decorations(self, total_pages):
        page_num = self._pageNumber
        if page_num == 1:
            return  # Suppress on cover page

        self.saveState()
        self.setFont("Helvetica-Bold", 7.2)
        self.setFillColor(colors.HexColor("#0F294A"))  # Dark Navy

        # Running Top Header
        self.drawString(36, 762, "COMPREHENSIVE TECHNICAL ANALYSIS REPORT | APPLIED STOCHASTIC MODELS")
        self.setFont("Helvetica", 7.0)
        self.setFillColor(colors.HexColor("#475569"))
        self.drawRightString(576, 762, "HOSPITAL PATIENT FLOW & CAPACITY PLANNING")

        # Header Rule
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(36, 756, 576, 756)

        # Running Footer Rule
        self.line(36, 40, 576, 40)

        # Running Footer
        self.setFont("Helvetica", 7.0)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(36, 28, "Course Project Technical Analysis & Viva Defense | NYS SPARCS, MIMIC-IV v3.1, eICU-CRD, CMS")
        self.setFont("Helvetica-Bold", 7.2)
        self.setFillColor(colors.HexColor("#0F294A"))
        self.drawRightString(576, 28, f"Page {page_num} of {total_pages}")

        self.restoreState()


def format_latex_to_reportlab(text: str) -> str:
    """Transform basic LaTeX symbols into clean HTML/ReportLab entities."""
    replacements = [
        (r'\\lambda', '&lambda;'),
        (r'\\mu', '&mu;'),
        (r'\\rho', '&rho;'),
        (r'\\alpha', '&alpha;'),
        (r'\\beta', '&beta;'),
        (r'\\theta', '&theta;'),
        (r'\\sigma', '&sigma;'),
        (r'\\Delta', '&Delta;'),
        (r'\\Phi', '&Phi;'),
        (r'\\phi', '&phi;'),
        (r'\\Gamma', '&Gamma;'),
        (r'\\omega', '&omega;'),
        (r'\\pi', '&pi;'),
        (r'\\tau', '&tau;'),
        (r'\\le', '&le;'),
        (r'\\ge', '&ge;'),
        (r'\\approx', '&asymp;'),
        (r'\\times', '&times;'),
        (r'\\to', '&rarr;'),
        (r'\\in', '&isin;'),
        (r'\\sum', '&Sigma;'),
        (r'\\pm', '&plusmn;'),
        (r'\\infty', '&infin;'),
        (r'\\mid', '|'),
        (r'\\cdot', '&middot;'),
        (r'\\partial', '&part;'),
        (r'\\forall', '&forall;'),
        (r'\\exists', '&exist;'),
        (r'\\neq', '&ne;'),
        (r'\\quad', '&nbsp;&nbsp;'),
        (r'\\qquad', '&nbsp;&nbsp;&nbsp;&nbsp;'),
        (r'\\text\{([^}]+)\}', r'\1'),
        (r'\\mathbf\{([^}]+)\}', r'<b>\1</b>'),
        (r'\\mathbb\{([A-Z])\}', r'<b>\1</b>'),
        (r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1 / \2)'),
        (r'\^\{([^}]+)\}', r'<sup>\1</sup>'),
        (r'_\{([^}]+)\}', r'<sub>\1</sub>'),
        (r'\^([0-9a-zA-Z\*\+\-]+)', r'<sup>\1</sup>'),
        (r'_([0-9a-zA-Z\*\+\-]+)', r'<sub>\1</sub>'),
        (r'\\vec\{([^}]+)\}', r'<b>\1</b>'),
        (r'\\left\(', '('),
        (r'\\right\)', ')'),
        (r'\\left\[', '['),
        (r'\\right\]', ']'),
        (r'\\left\\{', '{'),
        (r'\\right\\}', '}'),
        (r'\\', ''),
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)

    # Clean residual < or > that aren't tags
    parts = re.split(r'(</?[a-z0-9]+>)', text)
    for i in range(0, len(parts), 2):
        parts[i] = parts[i].replace('<', '&lt;').replace('>', '&gt;')
    return ''.join(parts)


def normalize_unicode(text: str) -> str:
    """Normalize special Unicode typographic characters for PDF compatibility."""
    return (text
        .replace('\u2014', ' -- ')
        .replace('\u2013', '-')
        .replace('\u2018', "'")
        .replace('\u2019', "'")
        .replace('\u201c', '"')
        .replace('\u201d', '"')
        .replace('\u2026', '...')
        .replace('\u25a0', ' - ')
    )


def clean_markdown_inline(text: str) -> str:
    """Safely convert markdown formatting to ReportLab XML tags."""
    if not text:
        return ""
    
    text = normalize_unicode(text.strip().replace('&', '&amp;'))

    # 1. Extract and protect math tokens
    math_tokens = {}
    def save_math(m):
        idx = len(math_tokens)
        key = f"@@MATHTOKEN{idx}@@"
        math_tokens[key] = format_latex_to_reportlab(m.group(1))
        return key
    text = re.sub(r'\$([^\$]+)\$', save_math, text)

    # 2. Extract and protect code tokens
    code_tokens = {}
    def save_code(m):
        idx = len(code_tokens)
        key = f"@@CODETOKEN{idx}@@"
        clean_code = m.group(1).replace('<', '&lt;').replace('>', '&gt;')
        code_tokens[key] = f'<font face="Courier" color="#0F294A"><b>{clean_code}</b></font>'
        return key
    text = re.sub(r'`([^`]+)`', save_code, text)

    # 3. Handle bold and italics
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
    text = re.sub(r'(?<!\w)\*([^\*]+?)\*(?!\w)', r'<i>\1</i>', text)
    text = re.sub(r'(?<!\w)_([^_]+?)_(?!\w)', r'<i>\1</i>', text)

    # 4. Clean brackets outside tags
    parts = re.split(r'(</?[bi]>)', text)
    for i in range(0, len(parts), 2):
        parts[i] = parts[i].replace('<', '&lt;').replace('>', '&gt;')
    text = ''.join(parts)

    # 5. Restore tokens
    for key, val in code_tokens.items():
        text = text.replace(key, val)

    for key, val in math_tokens.items():
        text = text.replace(key, f'<font color="#0F294A"><i>{val}</i></font>')

    return text


def safe_paragraph(text: str, style, fallback_plain: bool = True) -> Paragraph:
    """Create a Paragraph, safely falling back to plain text if XML parsing fails."""
    try:
        return Paragraph(text, style)
    except Exception as ex:
        if fallback_plain:
            # Strip all XML tags and try again
            plain = re.sub(r'<[^>]+>', '', text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            try:
                return Paragraph(plain, style)
            except Exception:
                return Paragraph("Content rendering fallback", style)
        raise ex


def build_comprehensive_pdf():
    pdf_out = ROOT / "reports" / "pdf" / "Comprehensive_Technical_Analysis_Report.pdf"
    pdf_out.parent.mkdir(parents=True, exist_ok=True)
    md_source = ROOT / "reports" / "Comprehensive_Technical_Analysis_Report.md"

    if not md_source.exists():
        print(f"Error: {md_source} does not exist. Run generate_comprehensive_technical_report.py first.")
        return

    print(f"Reading markdown source from {md_source}...")
    with open(md_source, "r", encoding="utf-8") as f:
        md_text = f.read()

    doc = SimpleDocTemplate(
        str(pdf_out),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=40,
        bottomMargin=42
    )

    styles = getSampleStyleSheet()

    # Palette
    PRIMARY = colors.HexColor("#0F294A")      # Navy Dark
    SECONDARY = colors.HexColor("#1E5B94")    # Steel Blue
    ACCENT = colors.HexColor("#0D9488")       # Teal 600
    TEXT_DARK = colors.HexColor("#0F172A")    # Slate 900
    TEXT_MUTED = colors.HexColor("#475569")   # Slate 600
    BG_LIGHT = colors.HexColor("#F8FAFC")     # Slate 50
    BG_CARD = colors.HexColor("#F1F5F9")      # Slate 100
    BORDER_COLOR = colors.HexColor("#CBD5E1") # Slate 300

    # Custom Typography Styles
    t_title = ParagraphStyle(
        "DocTitle", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=PRIMARY, alignment=1, spaceAfter=8
    )
    t_subtitle = ParagraphStyle(
        "DocSubTitle", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=10.5, leading=14, textColor=SECONDARY, alignment=1, spaceAfter=6
    )
    t_byline = ParagraphStyle(
        "DocByline", parent=styles["Normal"],
        fontName="Helvetica-Oblique", fontSize=8.2, leading=11, textColor=TEXT_MUTED, alignment=1, spaceAfter=12
    )
    t_h1 = ParagraphStyle(
        "Heading1_Custom", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=12.5, leading=16, textColor=PRIMARY, spaceBefore=10, spaceAfter=5, keepWithNext=True
    )
    t_h2 = ParagraphStyle(
        "Heading2_Custom", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=10.0, leading=13, textColor=SECONDARY, spaceBefore=8, spaceAfter=4, keepWithNext=True
    )
    t_h3 = ParagraphStyle(
        "Heading3_Custom", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=8.8, leading=11.5, textColor=PRIMARY, spaceBefore=5, spaceAfter=2, keepWithNext=True
    )
    t_body = ParagraphStyle(
        "Body_Custom", parent=styles["Normal"],
        fontName="Helvetica", fontSize=8.0, leading=11.0, textColor=TEXT_DARK, spaceAfter=3
    )
    t_bullet = ParagraphStyle(
        "Bullet_Custom", parent=styles["Normal"],
        fontName="Helvetica", fontSize=7.8, leading=10.5, textColor=TEXT_DARK, leftIndent=10, spaceAfter=2
    )
    t_code = ParagraphStyle(
        "Code_Custom", parent=styles["Normal"],
        fontName="Courier", fontSize=6.5, leading=8.4, textColor=PRIMARY
    )
    t_eq = ParagraphStyle(
        "Eq_Custom", parent=styles["Normal"],
        fontName="Helvetica-Oblique", fontSize=8.2, leading=11.0, textColor=PRIMARY, alignment=1
    )
    t_caption = ParagraphStyle(
        "Caption_Custom", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=7.0, leading=9.0, textColor=TEXT_MUTED, alignment=1, spaceAfter=5
    )
    t_th = ParagraphStyle(
        "TH_Custom", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=6.8, leading=8.6, textColor=colors.white, alignment=1
    )
    t_td = ParagraphStyle(
        "TD_Custom", parent=styles["Normal"],
        fontName="Helvetica", fontSize=6.6, leading=8.2, textColor=TEXT_DARK
    )

    story = []

    # Map Figures for each chapter
    chapter_figures = {
        2: (ROOT / "reports/figures/fig1_los_distributions.png", "Figure 1: Length of Stay Empirical Distributions & Heavy-Tailed Weibull / Lognormal Fits (SPARCS, MIMIC-IV, eICU)."),
        3: (ROOT / "reports/figures/fig4_diurnal_arrival_intensity.png", "Figure 2: Empirical Circadian Inflow Surge & Non-Homogeneous Poisson Arrival Intensity Wave."),
        4: (ROOT / "reports/figures/fig2_erlang_capacity_curves.png", "Figure 3: Multi-Server Inpatient Bed Sizing via Erlang-C Delay Curves and Halfin-Whitt QED Boundary."),
        5: (ROOT / "reports/figures/fig6_finite_buffer_tradeoff.png", "Figure 4: Ambulance Diversion & Blocking Probability in Finite Multi-Server Loss Queues (Erlang-B)."),
        6: (ROOT / "reports/figures/fig3_heavy_tail_delay_penalty.png", "Figure 5: Heavy-Traffic Variance Delay Expansion: Kingman / Allen-Cunneen Multiplier vs. Exponential Baseline."),
        7: (ROOT / "partner_repo/output_plots/04_icu_capacity_sensitivity.png", "Figure 6: Patient Abandonment (LWBS) vs. Staffing Capacity & Erlang-A Palm Equilibrium."),
        8: (ROOT / "partner_repo/output_plots/02_ed_boarding_fitting_diagnostics.png", "Figure 7: Two-Stage Tandem CTMC: Emergency Department Boarding Time & Downstream ICU Bed Starvation."),
        9: (ROOT / "partner_repo/output_plots/04_capacity_tradeoff_curves.png", "Figure 8: Non-Preemptive Multi-Class Priority Triage: Emergency vs. Elective Delay & Kleinrock Conservation."),
        10: (ROOT / "reports/figures/fig7_jackson_network_flow.png", "Figure 9: Open Jackson Network Topology & Multi-Department Equilibrium Flow Across MIMIC-IV Transfers."),
        11: (ROOT / "reports/figures/fig8_time_varying_diurnal_queue.png", "Figure 10: Pointwise Stationary Approximation (PSA): Zero-Cost Circadian Shift Staffing Reallocation."),
        12: (ROOT / "reports/figures/fig5_markov_transition_heatmap.png", "Figure 11: Continuous-Time Markov Chain (CTMC) Transition Matrix & Absorbing Disposition Probabilities."),
        13: (ROOT / "reports/figures/fig9_optimal_bed_allocation.png", "Figure 12: Fox's Greedy Marginal Knapsack: Multi-Department Optimal vs. Proportional Bed Allocation."),
        14: (ROOT / "partner_repo/output_plots/05_validation_and_policy.png", "Figure 13: SimPy Discrete-Event Simulation Engine: 20-Seed Monte Carlo Validation vs. Analytical Models.")
    }

    lines = md_text.split("\n")
    i = 0
    in_code_block = False
    code_block_lines = []
    current_chapter_num = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Handle Code / Diagram blocks
        if stripped.startswith("```"):
            if in_code_block:
                code_text = "<br/>".join([clean_markdown_inline(cl).replace(" ", "&nbsp;") for cl in code_block_lines])
                p_code = safe_paragraph(code_text, t_code)
                tbl_code = Table([[p_code]], colWidths=[540])
                tbl_code.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), BG_CARD),
                    ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
                    ('TOPPADDING', (0,0), (-1,-1), 3),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                    ('LEFTPADDING', (0,0), (-1,-1), 5),
                    ('RIGHTPADDING', (0,0), (-1,-1), 5),
                ]))
                story.append(tbl_code)
                story.append(Spacer(1, 3))
                in_code_block = False
                code_block_lines = []
            else:
                in_code_block = True
                code_block_lines = []
            i += 1
            continue

        if in_code_block:
            code_block_lines.append(line)
            i += 1
            continue

        # Blank line
        if not stripped:
            i += 1
            continue

        # Horizontal Rule
        if stripped in ["---", "***", "___"]:
            story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_COLOR, spaceBefore=3, spaceAfter=5))
            i += 1
            continue

        # Document Title
        if stripped.startswith("# COMPREHENSIVE TECHNICAL ANALYSIS REPORT"):
            story.append(Spacer(1, 10))
            story.append(safe_paragraph("COMPREHENSIVE TECHNICAL ANALYSIS REPORT", t_title))
            i += 1
            continue

        # Subtitle
        if stripped.startswith("## Applied Stochastic Models"):
            story.append(safe_paragraph(clean_markdown_inline(stripped.replace("## ", "")), t_subtitle))
            i += 1
            continue

        # Byline
        if stripped.startswith("**A Unified Dual-Track"):
            story.append(safe_paragraph(clean_markdown_inline(stripped), t_byline))
            i += 1
            continue

        # Chapter Headings
        if stripped.startswith("## Chapter "):
            m = re.match(r'## Chapter (\d+): (.*)', stripped)
            if m:
                ch_num = int(m.group(1))
                ch_title = m.group(2)
                current_chapter_num = ch_num

                if ch_num > 1:
                    story.append(PageBreak())

                # Stylized Chapter Banner
                p_banner = safe_paragraph(f"<b>CHAPTER {ch_num}</b><br/><font size=10 color='#1E5B94'>{clean_markdown_inline(ch_title)}</font>", t_h1)
                tbl_banner = Table([[p_banner]], colWidths=[540])
                tbl_banner.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
                    ('BOX', (0,0), (-1,-1), 0.8, PRIMARY),
                    ('TOPPADDING', (0,0), (-1,-1), 5),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                    ('LEFTPADDING', (0,0), (-1,-1), 6),
                    ('RIGHTPADDING', (0,0), (-1,-1), 6),
                ]))
                story.append(tbl_banner)
                story.append(Spacer(1, 4))
            else:
                story.append(safe_paragraph(clean_markdown_inline(stripped.replace("## ", "")), t_h1))
            i += 1
            continue

        # Other Level 2 Headings
        if stripped.startswith("## "):
            h2_text = clean_markdown_inline(stripped.replace("## ", ""))
            story.append(safe_paragraph(h2_text, t_h1))
            i += 1
            continue

        # Level 3 Headings (Subsections: ### A., ### B., etc.)
        if stripped.startswith("### "):
            h3_text = clean_markdown_inline(stripped.replace("### ", ""))
            story.append(safe_paragraph(h3_text, t_h2))
            i += 1
            continue

        # Level 4 Headings
        if stripped.startswith("#### "):
            h4_text = clean_markdown_inline(stripped.replace("#### ", ""))
            story.append(safe_paragraph(h4_text, t_h3))
            i += 1
            continue

        # Display Equation ($$...$$)
        if stripped.startswith("$$") and stripped.endswith("$$") and len(stripped) > 4:
            raw_eq = stripped[2:-2].strip()
            formatted_eq = format_latex_to_reportlab(raw_eq)
            p_eq = safe_paragraph(f"<b>{formatted_eq}</b>", t_eq)
            tbl_eq = Table([[p_eq]], colWidths=[540])
            tbl_eq.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
                ('BOX', (0,0), (-1,-1), 0.5, SECONDARY),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ]))
            story.append(Spacer(1, 2))
            story.append(tbl_eq)
            story.append(Spacer(1, 2))
            i += 1
            continue

        # Multi-line Display Equation ($$ ... $$)
        if stripped == "$$":
            eq_lines = []
            i += 1
            while i < len(lines) and lines[i].strip() != "$$":
                eq_lines.append(lines[i].strip())
                i += 1
            i += 1
            raw_eq = " ".join(eq_lines)
            formatted_eq = format_latex_to_reportlab(raw_eq)
            p_eq = safe_paragraph(f"<b>{formatted_eq}</b>", t_eq)
            tbl_eq = Table([[p_eq]], colWidths=[540])
            tbl_eq.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
                ('BOX', (0,0), (-1,-1), 0.5, SECONDARY),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ]))
            story.append(Spacer(1, 2))
            story.append(tbl_eq)
            story.append(Spacer(1, 2))
            continue

        # Markdown Table Detection
        if stripped.startswith("|") and stripped.endswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                table_lines.append(lines[i].strip())
                i += 1

            if len(table_lines) >= 2:
                header_raw = [c.strip() for c in table_lines[0].split("|")[1:-1]]
                data_rows_raw = []
                for tl in table_lines[2:]:
                    cells = [c.strip() for c in tl.split("|")[1:-1]]
                    if len(cells) == len(header_raw):
                        data_rows_raw.append(cells)
                    elif len(cells) < len(header_raw):
                        cells.extend([""] * (len(header_raw) - len(cells)))
                        data_rows_raw.append(cells)
                    else:
                        data_rows_raw.append(cells[:len(header_raw)])

                num_cols = len(header_raw)
                if num_cols > 0:
                    col_width = 540.0 / num_cols
                    if num_cols == 5 and "Dataset Name" in header_raw[0]:
                        widths = [90, 110, 75, 125, 140]
                    elif num_cols == 6 and "Dataset Name" in header_raw[0]:
                        widths = [75, 110, 65, 100, 70, 120]
                    elif num_cols == 5 and "PS ID" in header_raw[0]:
                        widths = [45, 115, 105, 95, 180]
                    elif num_cols == 3 and "Symbol" in header_raw[0]:
                        widths = [80, 200, 260]
                    elif num_cols == 4 and "Dataset Dimension" in header_raw[0]:
                        widths = [110, 140, 145, 145]
                    elif num_cols == 6 and "Analytical Framework" in header_raw[0]:
                        widths = [85, 95, 125, 75, 45, 115]
                    elif num_cols == 3 and "Method" in header_raw[0]:
                        widths = [110, 215, 215]
                    else:
                        widths = [col_width] * num_cols

                    table_data = []
                    hdr_cells = [safe_paragraph(f"<b>{clean_markdown_inline(c)}</b>", t_th) for c in header_raw]
                    table_data.append(hdr_cells)

                    for r in data_rows_raw:
                        row_cells = [safe_paragraph(clean_markdown_inline(c), t_td) for c in r]
                        table_data.append(row_cells)

                    tbl = Table(table_data, colWidths=widths, repeatRows=1)
                    t_style = [
                        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
                        ('ALIGN', (0,0), (-1,0), 'CENTER'),
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ('GRID', (0,0), (-1,-1), 0.35, BORDER_COLOR),
                        ('TOPPADDING', (0,0), (-1,-1), 2.5),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
                        ('LEFTPADDING', (0,0), (-1,-1), 3.5),
                        ('RIGHTPADDING', (0,0), (-1,-1), 3.5),
                    ]
                    for r_idx in range(1, len(table_data)):
                        bg = BG_LIGHT if r_idx % 2 == 1 else colors.white
                        t_style.append(('BACKGROUND', (0, r_idx), (-1, r_idx), bg))

                    tbl.setStyle(TableStyle(t_style))
                    story.append(Spacer(1, 2))
                    story.append(tbl)
                    story.append(Spacer(1, 3))
            continue

        # Bullet lists
        if stripped.startswith("- ") or stripped.startswith("* "):
            bullet_text = clean_markdown_inline(stripped[2:])
            story.append(safe_paragraph(f"&bull;&nbsp;&nbsp;{bullet_text}", t_bullet))
            i += 1
            continue

        # Numbered lists (1. , 2. )
        m_num = re.match(r'^(\d+)\.\s+(.*)', stripped)
        if m_num:
            num_idx = m_num.group(1)
            num_text = clean_markdown_inline(m_num.group(2))
            story.append(safe_paragraph(f"<b>{num_idx}.</b>&nbsp;&nbsp;{num_text}", t_bullet))
            i += 1
            continue

        # Check if we should insert the chapter figure after Subsection E or D
        if stripped.startswith("### F. Interpretation") or stripped.startswith("### E. Results"):
            if current_chapter_num in chapter_figures:
                fig_path, fig_cap = chapter_figures[current_chapter_num]
                if fig_path.exists():
                    try:
                        with PILImage.open(fig_path) as im:
                            w, h = im.size
                            aspect = h / float(w)
                        display_w = 460
                        display_h = min(220, display_w * aspect)
                        img_flowable = Image(str(fig_path), width=display_w, height=display_h)
                        img_flowable.hAlign = 'CENTER'
                        p_cap = safe_paragraph(f"<i>{fig_cap}</i>", t_caption)
                        
                        story.append(Spacer(1, 4))
                        story.append(KeepTogether([img_flowable, Spacer(1, 2), p_cap]))
                        story.append(Spacer(1, 4))
                        del chapter_figures[current_chapter_num]
                    except Exception as ex:
                        print(f"Warning: could not embed image {fig_path}: {ex}")

        # Regular Body Paragraph
        body_p = safe_paragraph(clean_markdown_inline(stripped), t_body)
        story.append(body_p)
        i += 1

    print(f"Compiled {len(story)} flowables into Platypus story. Building PDF...")
    doc.build(story, canvasmaker=AcademicNumberedCanvas)
    print(f"Publication PDF successfully generated at: {pdf_out}")
    return pdf_out

if __name__ == "__main__":
    build_comprehensive_pdf()
