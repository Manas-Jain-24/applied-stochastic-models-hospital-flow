"""Create a detailed, group-friendly project briefing PDF."""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    Image, KeepTogether
)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output" / "pdf" / "Hospital_Flow_Project_Group_Briefing.pdf"
FIG = ROOT / "reports" / "figures"


def p(text, style):
    return Paragraph(text, style)


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D7E3F1"))
    canvas.line(doc.leftMargin, 30, A4[0] - doc.rightMargin, 30)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#496A8C"))
    canvas.drawString(doc.leftMargin, 18, "Applied Stochastic Models - Hospital Patient Flow")
    canvas.drawRightString(A4[0] - doc.rightMargin, 18, f"Page {doc.page}")
    canvas.restoreState()


def section(title, body, styles, story):
    story.append(p(title, styles["H1"]))
    for item in body:
        story.append(p(item, styles["Body"]))
        story.append(Spacer(1, 5))


def add_figure(path, caption, styles, story, width=6.3):
    if path.exists():
        image = Image(str(path), width=width * inch, height=width * inch * 0.57)
        story.append(KeepTogether([image, Spacer(1, 3), p(caption, styles["Caption"])]))
        story.append(Spacer(1, 10))


def table(data, widths):
    header_style = ParagraphStyle("TableHeader", fontName="Helvetica-Bold", fontSize=8,
                                  leading=10, textColor=colors.white)
    cell_style = ParagraphStyle("TableCell", fontName="Helvetica", fontSize=8,
                                leading=10, textColor=colors.HexColor("#172B3A"))
    wrapped = []
    for row_index, row in enumerate(data):
        style = header_style if row_index == 0 else cell_style
        wrapped.append([Paragraph(str(cell), style) for cell in row])
    t = Table(wrapped, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#184E77")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEADING", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#C8D6E5")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F8FC")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=46, leftMargin=46,
                            topMargin=48, bottomMargin=45)
    base = getSampleStyleSheet()
    styles = {
        "Title": ParagraphStyle("Title", parent=base["Title"], fontName="Helvetica-Bold", fontSize=25,
                                leading=30, textColor=colors.HexColor("#12355B"), alignment=TA_CENTER, spaceAfter=12),
        "Sub": ParagraphStyle("Sub", parent=base["Normal"], fontSize=11, leading=15,
                              textColor=colors.HexColor("#496A8C"), alignment=TA_CENTER),
        "H1": ParagraphStyle("H1", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=15,
                             leading=19, textColor=colors.HexColor("#12355B"), spaceBefore=14, spaceAfter=7),
        "H2": ParagraphStyle("H2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=11,
                             leading=14, textColor=colors.HexColor("#1E6091"), spaceBefore=8, spaceAfter=4),
        "Body": ParagraphStyle("Body", parent=base["BodyText"], fontSize=9.3, leading=13,
                               textColor=colors.HexColor("#172B3A"), alignment=TA_LEFT),
        "Caption": ParagraphStyle("Caption", parent=base["Normal"], fontSize=7.7, leading=10,
                                  textColor=colors.HexColor("#496A8C"), alignment=TA_CENTER),
        "Callout": ParagraphStyle("Callout", parent=base["BodyText"], fontSize=10, leading=14,
                                  textColor=colors.HexColor("#12355B"), backColor=colors.HexColor("#EAF4FB"),
                                  borderColor=colors.HexColor("#7EB8DA"), borderWidth=0.5, borderPadding=9),
    }
    story = []

    story += [Spacer(1, 0.55 * inch), p("Hospital Patient Flow and Bed Capacity", styles["Title"]),
              p("Detailed project briefing for group partners", styles["Sub"]), Spacer(1, 0.20 * inch),
              p("Applied Stochastic Models Course Project", styles["Sub"]), Spacer(1, 0.45 * inch),
              p("<b>Purpose.</b> This briefing explains the full project in plain language while retaining the mathematics needed for a confident report, viva, and presentation.", styles["Callout"]),
              Spacer(1, 0.35 * inch)]

    story.append(p("Executive summary", styles["H1"]))
    story.append(p("Our project studies a practical hospital-management question: <b>how many inpatient beds are needed to keep admission blocking low when arrivals are uncertain and length of stay is highly variable?</b> We use NYS SPARCS-derived parameters, queueing theory, discrete-event simulation, and operational scenarios. The results show why sizing a hospital from average occupancy alone is unsafe.", styles["Body"]))
    story.append(Spacer(1, 8))
    story.append(table([
        ["Headline finding", "What it means"],
        ["LOS variability: c_s^2 = 1.9915", "Stay durations are much more variable than the exponential assumption (c_s^2 = 1)."],
        ["Erlang-B sizing: 293 beds", "For offered load 269.3 Erlangs, 293 beds gives modeled blocking about 0.91%, versus 4.78% at 269 beds."],
        ["Priority DES", "Emergency patients have lower simulated waits than elective patients under non-preemptive triage priority."],
        ["Network result", "The documented MedSurg scenario is unstable at 120 beds, which identifies a concrete capacity bottleneck."],
        ["Verification", "38 automated tests and the project verification suite passed on the current repository state."],
    ], [1.75 * inch, 4.55 * inch]))
    story.append(PageBreak())

    section("1. The real-world problem", [
        "Hospitals must serve emergency arrivals, planned elective admissions, transfers, and patients requiring long or unpredictable stays. A bed that is occupied by one patient cannot be used by another. When all beds are full, hospitals face a choice: delay admission, place the patient in a holding area, defer a planned procedure, or divert an incoming ambulance.",
        "The key uncertainty is not just the average demand. Arrival times fluctuate, patients have different clinical needs, and length of stay has a long right tail. A small group of long-stay patients can consume a large fraction of bed-days and make a ward congested even when average demand looks manageable.",
        "The project therefore follows a complete data-to-decision pipeline: empirical data -> probability models -> queueing analysis -> simulation -> operational interpretation."
    ], styles, story)
    story.append(p("Primary decision question", styles["H2"]))
    story.append(p("How should a hospital choose capacity and scheduling policies to keep modeled admission blocking below a chosen safety target while accounting for stochastic arrivals, non-exponential LOS, and department-level bottlenecks?", styles["Callout"]))
    add_figure(FIG / "fig1_los_distributions.png", "Figure 1. Candidate length-of-stay distributions and the importance of the right tail.", styles, story)

    section("2. Data and parameter grounding", [
        "The main empirical anchor is the New York State Statewide Planning and Research Cooperative System (SPARCS) inpatient discharge data. The project records a 250,000-encounter analytical sample and uses it to estimate length-of-stay moments, admission mix, and patient-disposition proportions. Raw restricted data are intentionally not committed to the repository; processed parameters and reproducible analytical scenarios are included.",
        "The MIMIC adapter is modular. When a permitted MIMIC demo or credentialed dataset is available, it can calibrate admissions, ward transfers, and clinical pathways without rewriting the stochastic engines. Synthetic data are used only for safe test and benchmark scenarios and should always be labelled as synthetic."
    ], styles, story)
    story.append(KeepTogether([table([
        ["Empirical parameter", "Value", "Role in the models"],
        ["Mean LOS", "5.386 days", "Sets service rate mu = 1 / 5.386 = 0.18567 per bed-day."],
        ["LOS variance", "57.771 days squared", "Captures dispersion and drives the squared coefficient of variation."],
        ["Squared coefficient of variation", "1.9915", "Shows service variability is roughly twice the exponential benchmark."],
        ["Illustrative arrival rate", "50 admissions/day", "With mean LOS, produces offered load 50 x 5.386 = 269.3 Erlangs."],
    ], [1.8 * inch, 1.25 * inch, 3.2 * inch])]))

    section("3. Length of stay: why the exponential model is not enough", [
        "In the standard M/M/c queue, service time is exponential. This is convenient because it is memoryless: a patient who has stayed a long time has the same remaining stay distribution as a newly admitted patient. That is usually a poor approximation for inpatient recovery and discharge planning.",
        "For a random service time S, the squared coefficient of variation is c_s^2 = Var(S) / E[S]^2. An exponential distribution requires c_s^2 = 1. The SPARCS-derived estimate is c_s^2 = 1.9915, which indicates substantially greater service-time variation and a pronounced right tail.",
        "The project compares exponential, gamma, Weibull, and lognormal candidate distributions using likelihood, AIC/BIC, and K-S distance. In the documented fit, lognormal is the best among the evaluated candidates. With a very large sample, every simple parametric model can have a tiny K-S p-value; relative AIC/BIC and effect size are more informative than a binary reject/do-not-reject decision."
    ], styles, story)
    story.append(p("Queueing consequence", styles["H2"]))
    story.append(p("For Poisson arrivals, the Allen-Cunneen approximation adjusts the M/M/c queue wait by the multiplier Phi = (1 + c_s^2) / 2. With c_s^2 = 1.9915, Phi = 1.4958. Holding mean LOS, capacity, and arrivals fixed, the estimated queue delay is about 49.6% higher than the exponential M/M/c baseline. This is an approximation for M/G/c, not an exact theorem.", styles["Callout"]))
    add_figure(FIG / "fig3_heavy_tail_delay_penalty.png", "Figure 2. Higher service-time variance increases the estimated delay penalty.", styles, story)

    section("4. Core capacity models", [
        "The project uses multiple queueing models because different hospital questions have different operational meanings. Erlang-B represents a hard-capacity loss system. Erlang-C represents a delay system with a waiting queue. M/M/c/K adds a finite buffer. M/G/c introduces non-exponential service times. The models are not interchangeable, so the report clearly states which policy each model represents.",
        "In Erlang-B, the offered load is a = lambda / mu = lambda E[S]. The blocking probability B(c,a) is computed with a stable recursion, avoiding numerical overflow at hospital-sized capacity. The model is useful for a stylized question: if no waiting space exists, what fraction of arrivals find all beds occupied?"
    ], styles, story)
    story.append(table([
        ["Model", "Operational interpretation", "Main output"],
        ["M/M/c/c (Erlang-B)", "No waiting room; arrivals finding all c beds occupied are blocked/lost in the model.", "Blocking probability and required bed count."],
        ["M/M/c (Erlang-C)", "Patients may wait until a bed becomes free.", "Probability of delay, mean wait, queue length."],
        ["M/G/c approximation", "Same as M/M/c but LOS variability is represented through c_s^2.", "Variance-adjusted estimated wait."],
        ["M/M/c/K", "A fixed holding buffer exists beyond active treatment capacity.", "Trade-off between modeled loss and boarding delay."],
    ], [1.45 * inch, 3.1 * inch, 1.7 * inch]))
    add_figure(FIG / "fig2_erlang_capacity_curves.png", "Figure 3. Capacity curves show how blocking and delay fall as beds are added.", styles, story)
    story.append(PageBreak())

    section("5. Bed sizing result: the safety buffer", [
        "Using the illustrative arrival rate of 50 admissions/day and mean LOS of 5.386 days gives offered load a = 269.3 Erlangs. Building only 269 beds matches average demand but leaves little protection against random fluctuations. The Erlang-B calculation gives modeled blocking about 4.78% at 269 beds.",
        "The target scenario asks for modeled blocking at or below 1%. The minimum capacity returned by the stable Erlang-B recursion is 293 beds. This is about 23.7 beds above the nominal offered load and produces modeled blocking about 0.91%.",
        "This is not a literal construction recommendation for every hospital. It is a transparent scenario result whose validity depends on the assumptions: a Poisson arrival process, homogeneous beds, a loss policy, a stable demand rate, and the selected 1% target. Its main insight is robust: capacity must include a stochastic safety buffer, not only average occupied beds."
    ], styles, story)
    story.append(table([
        ["Capacity scenario", "Offered load", "Modeled blocking", "Interpretation"],
        ["269 beds", "269.3 Erlangs", "4.78%", "Capacity approximately equals average demand; vulnerable to variability."],
        ["293 beds", "269.3 Erlangs", "0.91%", "Meets the illustrative 1% modeled loss target."],
    ], [1.3 * inch, 1.5 * inch, 1.35 * inch, 2.1 * inch]))

    section("6. Priority triage and discrete-event simulation", [
        "The project models two admission classes: emergency (higher priority) and elective (lower priority). The operational policy is non-preemptive: a patient already in a bed is never interrupted, but when a bed becomes available, a waiting emergency patient is served before a waiting elective patient. Within each class, first-come, first-served order is used.",
        "The analytical multi-server priority formulas are labelled as a heuristic approximation, not as an exact Cobham result. The project compares them with an event-calendar discrete-event simulation. The DES uses a separate arrival horizon and drain period so every post-warm-up arrival is observed entering service. This eliminates right-censoring from patients still queued at the end of the arrival horizon.",
        "For the documented 293-bed scenario, the heuristic estimates approximately 6.05 minutes for emergency waiting and 74.45 minutes for elective waiting. Ten independent simulations produce mean waits of about 5.29 +/- 1.56 minutes for emergency admissions and 57.41 +/- 35.10 minutes for elective admissions. High variation is expected near 92% utilization, so confidence intervals and the replication range matter."
    ], styles, story)
    story.append(p("Important interpretation", styles["H2"]))
    story.append(p("Priority does not create capacity. It redistributes delay toward elective admissions to protect urgent cases. The exact size of this effect depends on service discipline, demand composition, and congestion; the simulation is included to test the analytical approximation rather than to overstate certainty.", styles["Callout"]))
    story.append(PageBreak())

    section("7. Time-varying arrivals and dynamic staffing", [
        "Daily averages hide predictable peaks. The project uses a non-homogeneous Poisson process (NHPP) to represent a diurnal arrival intensity. The illustrative curve has 50 admissions/day on average, a trough of about 0.92 arrivals/hour, and a peak of about 3.25 arrivals/hour around 2:12 PM.",
        "The Pointwise Stationary Approximation (PSA) evaluates an Erlang-C model at each time point using the instantaneous arrival rate. It is a useful planning approximation, but it is not a full transient queue solution. Its purpose here is to compare a constant 18-bed staffing plan with a cost-neutral 3-shift allocation using the same 432 bed-hours/day.",
        "The documented scenario reallocates beds from low-demand night hours to the peak day shift: 14 beds overnight, 22 beds during the day, and 18 beds in the evening. Under the specified assumptions, the peak modeled wait falls from 41.5 minutes to 1.1 minutes. This is a scenario result, not a guarantee of a 97.3% improvement in every hospital."
    ], styles, story)
    add_figure(FIG / "fig4_diurnal_arrival_intensity.png", "Figure 4. The NHPP arrival-rate profile used for the diurnal scenario.", styles, story)
    add_figure(FIG / "fig8_time_varying_diurnal_queue.png", "Figure 5. PSA comparison of constant and dynamic staffing under equal bed-hours.", styles, story)

    section("8. Jackson network: department flow and bottlenecks", [
        "A hospital is not a single queue. Patients transfer among ED, ICU, step-down, and MedSurg. The project applies an open Jackson network, where Lambda = gamma + P^T Lambda. Here gamma gives external arrivals and P gives transfer probabilities between departments.",
        "For the documented four-station scenario, traffic-balance equations produce total arrival rates [40.000, 6.229, 8.538, 30.126] patients/day for ED, ICU, StepDown, and MedSurg. The 120-bed MedSurg ward has service capacity 24 patients/day, so its utilization is 125.52%. The queue is mathematically unstable under this scenario: steady-state census and end-to-end stay do not exist as finite values.",
        "This is a useful result, not a failure of the project. It shows how a local capacity shortfall can be exposed through network flow. The scenario needs at least 151 MedSurg beds for strict stability and approximately 178 beds to target 85% utilization under the same parameters."
    ], styles, story)
    add_figure(FIG / "fig7_jackson_network_flow.png", "Figure 6. Multi-stage hospital network structure and station-level flow analysis.", styles, story)
    story.append(PageBreak())

    section("9. Multi-department bed allocation", [
        "Once a total capacity budget is fixed, the hospital must allocate beds among departments. The project minimizes a weighted sum of Erlang-B blocking probabilities. The weights represent relative clinical importance: ICU weight 4, ED weight 2, and MedSurg weight 1.",
        "Fox's greedy marginal allocation algorithm assigns each next bed to the department with the largest reduction in weighted blocking. In the documented 230-bed scenario, proportional allocation gives [24 ICU, 34 ED, 172 MedSurg], while the weighted greedy allocation gives [33 ICU, 43 ED, 154 MedSurg].",
        "The optimized scenario reduces the weighted loss objective from 0.4037 to 0.0655, an 83.8% reduction. The cost is a higher modeled MedSurg loss probability, which is an explicit policy trade-off rather than a free improvement."
    ], styles, story)
    add_figure(FIG / "fig9_optimal_bed_allocation.png", "Figure 7. Weighted marginal bed allocation compared with proportional sizing.", styles, story)

    section("10. Additional project modules", [
        "The repository also includes absorbing Markov-chain analysis for discharge dispositions and downstream care pathways. The fundamental matrix N = (I-Q)^-1 estimates expected transient-state visits, while B = NR estimates absorption probabilities for discharge destinations.",
        "There is also a modular MIMIC ingestion adapter, synthetic patient-data generation for safe testing, data-schema validation, distribution fitting, NHPP simulation, and visualization generation. These modules make the project broad and reusable, but they should be presented as support for the main capacity-planning narrative rather than as disconnected topics."
    ], styles, story)
    story.append(PageBreak())

    section("11. Verification and reproducibility", [
        "The project includes a unit-test suite and a unified ten-step verification script. The current repository state passed 38 automated tests. The unified script checks synthetic-data validation, queueing equations, Markov models, DES behavior, MIMIC-demo calibration, Jackson-network calculations, time-varying PSA, bed allocation, and the presence of all nine figures.",
        "The deep-dive verification separately checks the documented analytical scenarios. It explicitly notes that empirical distribution-fit statistics require the restricted SPARCS data and original fitting pipeline. This distinction is important: arithmetic and scenario results are reproducible from the repository; raw-data fitting requires authorized source data."
    ], styles, story)
    story.append(table([
        ["Command", "Purpose"],
        ["python -m unittest discover tests", "Runs the full automated test suite."],
        ["python scripts/verify_all.py", "Runs the unified project verification pipeline."],
        ["python deep_dives/verify_deep_dives.py", "Checks the documented deep-dive benchmark scenarios."],
    ], [2.65 * inch, 3.7 * inch]))

    section("12. Limitations to state honestly", [
        "SPARCS discharge records provide valuable LOS and disposition evidence but may not offer the detailed real-time timestamps required to directly estimate every queue waiting process. Some sub-daily arrival and staffing scenarios are therefore model-based illustrations.",
        "Erlang-B, Erlang-C, Jackson networks, PSA, and Allen-Cunneen each rely on simplifying assumptions such as Poisson arrivals, homogeneous capacity, or product-form routing. They are decision-support approximations, not clinical forecasts.",
        "Blocking, delayed admission, ED boarding, and ambulance diversion are related but not identical real-world outcomes. The project uses these terms carefully as model interpretations rather than claiming one metric measures every operational consequence.",
        "Priority DES results are based on the stated parameters and random seeds. Replication intervals communicate simulation uncertainty; different hospital policies, demand mixes, or LOS distributions can change outcomes."
    ], styles, story)

    section("13. Recommended 15-minute presentation plan", [
        "1 minute: Problem and why bed capacity is stochastic. 2 minutes: SPARCS data, LOS variability, and why exponential service fails. 3 minutes: Erlang-B capacity sizing and the 293-bed safety-buffer result. 3 minutes: priority simulation and why emergency versus elective handling matters. 2 minutes: diurnal staffing. 2 minutes: network bottleneck and allocation. 1 minute: limitations and conclusion. 1 minute: code, verification, and contribution summary.",
        "Do not attempt to derive every formula verbally. Explain the one or two formulas that support the primary story, show figures, and be ready to use the deep dives for questions. The strongest message is that data-informed stochastic models reveal safety buffers and bottlenecks that average occupancy planning misses."
    ], styles, story)
    story.append(p("Suggested division of speaking roles", styles["H2"]))
    story.append(table([
        ["Role", "Suggested responsibility"],
        ["Member 1", "Problem framing, data, LOS distribution, and M/G/c implication."],
        ["Member 2", "Erlang capacity models, priority DES, validation, and safety-buffer finding."],
        ["Member 3", "PSA staffing, Jackson network, bed allocation, limitations, and conclusion."],
    ], [1.25 * inch, 5.1 * inch]))
    story.append(PageBreak())

    section("14. Final group conclusion", [
        "This is not merely a set of queueing formulas. It is an integrated decision-support project. It starts with observed variation in hospital stays, translates that uncertainty into capacity and waiting consequences, validates key scenarios with simulation, and identifies where policy choices can reduce risk.",
        "The central conclusion is simple: <b>average load is not enough for hospital capacity planning.</b> Length-of-stay variability, arrival peaks, priority rules, and downstream bottlenecks all matter. A hospital that looks adequately sized on average can still experience meaningful modeled blocking, waiting, or instability.",
        "For submission and presentation, keep the main narrative focused on capacity safety buffers. Use the priority, diurnal, network, and allocation analyses as evidence that the project understands the operational system around that core decision."
    ], styles, story)
    story.append(Spacer(1, 0.25 * inch))
    story.append(p("Prepared from the current project repository, deep-dive investigations, verification scripts, and generated analysis figures.", styles["Caption"]))

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUT)


if __name__ == "__main__":
    main()
