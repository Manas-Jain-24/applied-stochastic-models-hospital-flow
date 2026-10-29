"""Build the 27-page ASM submission report from verified local project outputs."""
from pathlib import Path
import csv
import math
from io import BytesIO

from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "pdf" / "Hospital_Patient_Flow_ASM_Submission_Report.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)

pdfmetrics.registerFont(TTFont("Arial", r"C:\Windows\Fonts\arial.ttf"))
pdfmetrics.registerFont(TTFont("ArialBold", r"C:\Windows\Fonts\arialbd.ttf"))
pdfmetrics.registerFont(TTFont("Consolas", r"C:\Windows\Fonts\consola.ttf"))

NAVY = HexColor("#17324d")
BLUE = HexColor("#25618e")
TEAL = HexColor("#217c79")
PALE = HexColor("#eef4f7")
TEXT = HexColor("#23313a")
MUTED = HexColor("#586b77")
GRID = HexColor("#d9e3e8")
W, H = 595.28, 841.89  # A4
L, R = 49, 49
WIDTH = W - L - R

styles = {
    "body": ParagraphStyle("body", fontName="Arial", fontSize=10.5, leading=16.2, textColor=TEXT, spaceAfter=0),
    "small": ParagraphStyle("small", fontName="Arial", fontSize=9.0, leading=13.1, textColor=TEXT),
    "caption": ParagraphStyle("caption", fontName="Arial", fontSize=8.8, leading=12.6, textColor=MUTED),
    "table": ParagraphStyle("table", fontName="Arial", fontSize=9.0, leading=12.3, textColor=TEXT),
    "th": ParagraphStyle("th", fontName="ArialBold", fontSize=9.0, leading=12.3, textColor=white),
}

C = canvas.Canvas(str(OUT), pagesize=(W, H), pageCompression=1)
C.setTitle("Stochastic Modeling of Hospital Patient Flow and Bed Capacity")
C.setAuthor("Manas and Yashasvee")
C.setSubject("Applied Stochastic Models course project submission")
page_no = 0
y = 0

def begin(title, kicker="APPLIED STOCHASTIC MODELS"):
    global page_no, y
    page_no += 1
    C.setFillColor(NAVY)
    C.rect(0, H-12, W, 12, fill=1, stroke=0)
    C.setFont("ArialBold", 8.2)
    C.setFillColor(TEAL)
    C.drawString(L, H-43, kicker)
    C.setFont("ArialBold", 18)
    C.setFillColor(NAVY)
    C.drawString(L, H-71, title)
    C.setStrokeColor(GRID)
    C.line(L, H-81, W-R, H-81)
    y = H-103

def para(s, gap=11, style="body"):
    global y
    p = Paragraph(s, styles[style])
    _, h = p.wrap(WIDTH, 1000)
    if y-h < 55:
        raise ValueError(f"page {page_no} overflow on paragraph: {s[:50]}")
    p.drawOn(C, L, y-h)
    y -= h+gap

def sub(s):
    global y
    y -= 3
    C.setFont("ArialBold", 11)
    C.setFillColor(BLUE)
    C.drawString(L, y-11, s)
    y -= 25

def eq(s, note=None):
    global y
    height = 35 if note is None else 51
    if y-height < 55: raise ValueError(f"page {page_no} equation overflow")
    C.setFillColor(PALE)
    C.roundRect(L, y-height, WIDTH, height, 5, fill=1, stroke=0)
    C.setFillColor(NAVY)
    C.setFont("Consolas", 10.2)
    C.drawString(L+12, y-21, s)
    if note:
        C.setFont("Arial", 7.7)
        C.setFillColor(MUTED)
        C.drawString(L+12, y-40, note)
    y -= height+13

def table(headers, rows, widths=None, gap=13):
    global y
    if widths is None: widths = [WIDTH/len(headers)]*len(headers)
    data = [[Paragraph(str(v), styles["th"]) for v in headers]]
    data += [[Paragraph(str(v), styles["table"]) for v in row] for row in rows]
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, PALE]),
        ("GRID", (0,0), (-1,-1), .35, GRID),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    _, h=t.wrap(WIDTH, 1000)
    if y-h < 55: raise ValueError(f"page {page_no} table overflow")
    t.drawOn(C,L,y-h)
    y -= h+gap

def compact_table(headers, rows, widths):
    """Readable one-page index of all research questions."""
    global y
    cell = ParagraphStyle("index_cell", fontName="Arial", fontSize=8.0, leading=10.8, textColor=TEXT)
    head = ParagraphStyle("index_head", fontName="ArialBold", fontSize=8.2, leading=10.8, textColor=white)
    data = [[Paragraph(str(v), head) for v in headers]]
    data += [[Paragraph(str(v), cell) for v in row] for row in rows]
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, PALE]),
        ("GRID", (0,0), (-1,-1), .35, GRID),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    _, h = t.wrap(WIDTH, 1000)
    if y-h < 55: raise ValueError("question index does not fit page 1")
    t.drawOn(C, L, y-h)
    y -= h+10

def bars(labels, vals, title, caption, maximum=None, h=150):
    global y
    if y-h-32 < 55: raise ValueError(f"page {page_no} chart overflow")
    maximum = maximum or max(vals)*1.15
    x0=L+128; chartw=WIDTH-160
    C.setFont("ArialBold", 8.8); C.setFillColor(NAVY); C.drawString(L,y-8,title)
    top=y-24
    step=(h-25)/len(vals)
    for i,(lab,v) in enumerate(zip(labels,vals)):
        yy=top-(i+1)*step
        C.setFillColor(TEXT); C.setFont("Arial",8); C.drawRightString(x0-8,yy+5,lab)
        C.setFillColor(TEAL if i==len(vals)-1 else BLUE)
        C.rect(x0, yy, chartw*v/maximum, 11, fill=1, stroke=0)
        C.setFillColor(TEXT); C.drawString(x0+chartw*v/maximum+5, yy+2, f"{v:g}")
    y -= h+4
    para(caption, gap=13, style="caption")

def figure(path, caption, h=230):
    global y
    from reportlab.lib.utils import ImageReader
    img=ImageReader(str(ROOT/path))
    iw,ih=img.getSize()
    dw=min(WIDTH, h*iw/ih); dh=dw*ih/iw
    if y-dh-42 < 55: raise ValueError(f"page {page_no} figure overflow: {path}")
    C.drawImage(img,L+(WIDTH-dw)/2,y-dh,width=dw,height=dh,mask='auto')
    y -= dh+8
    para(caption, gap=13, style="caption")

def finish():
    C.setStrokeColor(GRID); C.line(L,42,W-R,42)
    C.setFont("Arial",7.4); C.setFillColor(MUTED)
    C.drawString(L,29,"Hospital patient flow and bed capacity | ASM course project")
    C.drawRightString(W-R,29,f"{page_no} / 27")
    C.showPage()

# 1 - Complete simple-word index, then one deep-dive page per question.
begin("Questions We Tackled", "HOSPITAL PATIENT FLOW | MANAS AND YASHASVEE")
para("Applied Stochastic Models course project | 29 October 2026<br/>Each question below has a full explanation on the next 13 pages.",gap=10)
compact_table(["Question", "Dataset", "Approach", "Short finding"], [
 ["1. Are patient stays predictable?", "SPARCS, eICU, MIMIC", "Compare stay distributions", "Stays vary far more than a simple exponential model."],
 ["2. Do arrivals change by hour?", "eICU + CMS", "Hourly Poisson model", "Illustrative peak is 2.89 times the trough."],
 ["3. How many beds limit waiting?", "Illustrative bed load", "Erlang-C waiting model", "230 to 242 beds cuts modeled wait from 15.55 to 1.30 h."],
 ["4. How many beds limit diversion?", "150-Erlang scenario", "Erlang-B loss model", "170 beds first gets modeled blocking below 1%."],
 ["5. Does stay variation add delay?", "SPARCS, eICU, MIMIC", "Variability correction", "Modeled wait is about 1.50 to 1.61 times the simple baseline."],
 ["6. What if patients leave the queue?", "CMS + partner model", "Erlang-A abandonment", "Simulation still misses CMS: 4.80% vs 2.33%."],
 ["7. Does a full ICU block the ED?", "eICU + partner model", "Two-stage queue", "At 90 ICU beds, modeled board delay is 2.25 h."],
 ["8. Does emergency priority help?", "Illustrative classes", "Two-class priority", "Current priority formula needs independent validation."],
 ["9. Which ward is the bottleneck?", "Three-ward scenario", "Jackson network", "Med/Surg has the highest modeled use, 86.5%."],
 ["10. Can staffing follow busy hours?", "Arrival scenario", "Hourly staffing model", "Modeled peak wait falls 41.5 to 1.1 min."],
 ["11. Where do patients end up?", "eICU pathways", "Absorbing Markov chain", "ICU-start home absorption is 88.88% in the model."],
 ["12. How should beds be split?", "230-bed scenario", "Marginal allocation", "Weighted blocking objective falls 0.40374 to 0.06550."],
 ["13. Do simulations check out?", "Synthetic, eICU, CMS", "Discrete-event simulation", "Code checks pass; external ED agreement does not."],
], [143,83,111,WIDTH-337])
para("<b>Reading key:</b> A scenario finding is a calculation under stated assumptions. It is not a measured hospital intervention. The detailed pages separate observed data from model outputs.",gap=0,style="small")
finish()

# 2
begin("Main Results Compared")
para("After the 13 question deep dives, this table brings the central numerical results together. Values are rounded; the preceding pages give the assumptions and caveats.")
table(["Question","Data / method","Finding"],[
 ["How variable is stay duration?","SPARCS, eICU, MIMIC; moments and parametric fits","SPARCS CV² 1.991; eICU 2.025; MIMIC ICU 2.215."],
 ["How does demand change by hour?","eICU hourly pattern scaled to CMS volume; NHPP","Illustrative very-high-volume facility: 5.92 to 17.09 arrivals/hour."],
 ["How many beds control waiting?","Erlang-C at load 225 Erlangs","230 beds: 15.55 h; 242 beds: 1.30 h mean model wait."],
 ["How many beds control loss?","Erlang-B at load 150 Erlangs","168 beds: 1.17% blocking; threshold of 1% requires more."],
 ["What is the variance penalty?","Allen-Cunneen approximation","SPARCS service variation gives 1.495 times M/M/c wait."],
 ["Where is the network bottleneck?","Three-node Jackson scenario","Med/Surg utilization 86.5%; modeled stay 5.19 days."],
 ["Can resources be reallocated?","PSA staffing and marginal allocation","Peak wait scenario 41.5 to 1.1 min; weighted blocking 0.40374 to 0.06550."],
 ["Does simulation match external benchmarks?","20-replication partner DES vs CMS","ED abandonment 4.80% vs 2.33%; mismatch remains."]],[126,164,WIDTH-290])
sub("Interpretation rule")
para("A dataset-derived estimate describes its source cohort. A queueing calculation is conditional on the chosen rates, capacities, distributional assumptions, and stationarity. A simulation result describes the implemented code and parameters. Neither a conditional model output nor a software test proves that a hospital intervention will achieve the same effect in practice.")
finish()

# 3
begin("How the Project Fits Together")
table(["Step","Purpose"],[
 ["Question list","Page 1 gives every question, dataset, method, and short finding."],
 ["Deep dives","Pages 2-14 examine one question each, with mathematics and results."],
 ["Study design and data","Pages 15-20 explain the overall problem, data sources, cleaning, and notation."],
 ["Checks and interpretation","Pages 21-27 compare results, validate the software, discuss limitations, and list references."]],[120,WIDTH-120])
sub("How to read the mathematical pages")
para("Each model page gives the operational question, the state or random variables, its main formula, an example computed from repository parameters, and the assumptions that limit interpretation. Rates are reported per hour or per day as marked. The offered load <i>a</i> is measured in Erlangs and equals arrivals per unit time multiplied by mean service duration in the same unit.")
eq("a = lambda / mu = lambda E[S]", "lambda: arrival rate; mu: service completion rate per occupied bed")
para("The figures and tables are numbered by page context. Values copied from local data or output tables are identified as empirical or calibrated. Values from theoretical calculations are labeled scenario results. This distinction is necessary because the project combines different hospitals and datasets.")
sub("Report scope")
para("The submission addresses the course pipeline from real-world problem to data, probability model, stochastic process, mathematical analysis, simulation, validation, and interpretation. It includes detailed formulas and a reproducible run log. It does not claim patient-level causal effects or a prospective hospital deployment.")
finish()

# 4
begin("Study Design and Problem Definition")
para("Hospital beds and treatment bays are shared resources. Admission demand varies over time, stays have long right tails, and patients move between departments. Even when average demand is below average capacity, random bunching can create a queue or block an arrival. The principal operational question is how much capacity, and which placement of that capacity, is needed to control delay and loss.")
sub("System boundary and outcomes")
table(["Component","Model representation","Primary outcome"],[["Arrivals","Poisson or non-homogeneous Poisson count process","Hourly counts and peak-to-trough variation"],["Service","Length of stay random variable S","Mean, variance, fitted distribution"],["Single ward","Multi-server waiting or loss system","P(wait), mean wait, P(block)"],["Transfers","Routing probabilities among departments","Throughput, occupancy, pathway absorption"],["Policies","Staffing schedule and integer bed allocation","Modeled delay or weighted loss objective"]],[90,190,WIDTH-280])
sub("Research questions")
para("The report asks whether service times are close to exponential, how time-varying arrivals affect capacity, how close-to-saturation systems behave, whether routing identifies a bottleneck, and whether a fixed bed budget can be used more effectively. A separate validation question asks whether simulation outputs agree with analytical results and external benchmarks.")
para("The models cover different abstractions. Erlang-C allows an unlimited waiting room; Erlang-B has no waiting space and counts blocked arrivals; Erlang-A includes abandonment; a Jackson network assumes memoryless service at each node and independent routing. The alternatives represent distinct care situations and cannot be compared without specifying the queue discipline and capacity rule.")
finish()

# 5
begin("Datasets and Their Coverage")
table(["Source","Local material","Role / limitation"],[
 ["NYS SPARCS 2009","250,000-record processed inpatient sample plus raw source files","Daily-resolution length of stay, admission type and disposition; no minute-level bed queue history."],
 ["MIMIC-IV v3.1","2,004,604 transfer records and 94,444 ICU stays in local calibration","Ward routing and ICU duration; one health system, de-identified timestamps."],
 ["eICU demo v2.0.1","2,520 ICU stays, 1,841 patients, 2,174 hospital stays","Service and admission-hour patterns; demo sample is small and selected."],
 ["CMS Timely and Effective Care","50 facility records, 48 with volume tier","Facility-level volume and ED benchmarks; not patient-level linkage to eICU."],
 ["Synthetic cohort","5,000 generated encounters","Pipeline and unit-test benchmark only; no empirical claim."]],[99,155,WIDTH-254])
para("<b>Provenance of the combined arrival scenario.</b> The hourly probability profile comes from eICU arrival-hour counts. The daily total comes from a very-high-volume CMS tier mean of 100,448 annual arrivals, or 275.20 per day. This is a hybrid illustrative facility, not a measured joint sample.")
para("<b>Comparability.</b> SPARCS measures inpatient discharges; MIMIC transfer rows represent ward movement; eICU rows represent ICU stays; CMS rows represent hospitals. Their counts have different denominators. We therefore compare shape and variability, but do not add the rows together or infer a common national rate.")
para("The SPARCS processed file is a selected extract rather than the entire state database. The MIMIC ICU and transfer counts likewise refer to different tables. We report each denominator beside its estimate so a reader can distinguish a patient stay from a transfer event. The CMS file provides facility-level measures and does not identify which eICU stay belongs to a listed facility.")
finish()

# 6
begin("Data Preparation and Quality Checks")
para("The code maps source columns into common concepts, checks required fields, removes invalid durations and computes cohort summaries. Disposition and transfer states are aggregated into model categories. The synthetic benchmark validates timestamp order, nonnegative duration, duplicates and schema completeness. The MIMIC adapter produces a processed JSON parameter file and transfer matrix.")
table(["Check","Observed result / action"],[["Synthetic schema and time order","5,000 encounters validated; no reported violations or duplicates."],["eICU cohort","2,520 ICU stays retained; ED-admitted subset 1,304 stays (51.75%)."],["eICU duration consistency","Overview mean ICU LOS 58.07 h; fit table uses 58.35 h after positive-duration fitting filters."],["MIMIC routing","2,004,604 transfers calibrated across five model departments."],["CMS missingness","50 facilities in benchmark extract; volume-tier table has two unavailable volume rows."]],[175,WIDTH-175])
sub("Statistical handling")
para("Length of stay is positive and right-skewed. The distribution code fits exponential, gamma, Weibull and lognormal laws by maximum likelihood, then records log likelihood, AIC, BIC and Kolmogorov-Smirnov statistics. Because parameters are estimated from the same data, ordinary KS p-values are only screening diagnostics; a bootstrap would be preferable for a formal composite-null test.")
para("The 24 arrival-hour counts are normalized to probabilities before scaling to a CMS daily volume. This guarantees that the sum of 24 hourly rates equals the selected daily mean. It does not establish that a CMS hospital has the same within-day timing as the eICU demo cohort.")
finish()

# 7
begin("Mathematical Framework and Notation")
table(["Symbol","Meaning","Unit"],[["N(t)","Cumulative arrival count by time t","patients"],["lambda(t)","Arrival intensity at time t","patients/hour or day"],["S, E[S]","Service or stay duration and its mean","hours or days"],["mu","Per-bed service rate, 1/E[S]","per hour or day"],["c, K","Servers or beds, total system capacity","beds"],["a, rho","Offered load lambda/mu; utilization a/c","Erlangs; fraction"],["Pq, Wq","Probability of waiting; mean queue wait","fraction; time"],["B(c,a)","Erlang-B blocking probability","fraction"],["P, Q","Discrete transition matrix; continuous generator","probability; per time"]],[70,WIDTH-182,112])
eq("CV^2 = Var(S) / E[S]^2", "Squared coefficient of variation; exponential reference value is 1")
para("For stationary birth-death queues, the state is the number of patients present. Arrivals raise the state by one, while service completions lower it. For a time-varying arrival process, the distribution of increments depends on the integrated intensity over an interval. For a patient pathway chain, states are departments and absorbing outcomes such as home or expired.")
para("All single-ward delay calculations require a stability check. Erlang-C needs <i>rho &lt; 1</i>. Erlang-B can be computed for any offered load because blocked customers leave. The Allen-Cunneen correction is an approximation, particularly unreliable at very low traffic or in transient overload. These assumptions are revisited with each result.")
para("Time is continuous in the arrival, queueing, simulation and CTMC models. The absorbing transition matrix instead advances one transfer at a time. A probability of absorption is dimensionless, while a CTMC holding time is measured in hours or days. Keeping those units separate prevents expected transfer steps from being misreported as expected days in hospital.")
finish()

# 8
begin("Question 2  Do Arrivals Change by Hour")
para("The partner analysis extracts an hourly arrival profile from the eICU demo and applies it to a selected CMS facility-volume tier. Let <i>n<sub>h</sub></i> be the number of arrivals in hour h and let p<sub>h</sub> = n<sub>h</sub> / sum(n<sub>j</sub>). The mean daily count is annual CMS arrivals divided by 365.")
eq("lambda_h = Lambda_day p_h,   sum_h lambda_h = Lambda_day", "For one-hour bins, the sum of hourly rates is the expected daily count")
para("With a mean annual volume of 100,448 in the very-high-volume tier, Lambda<sub>day</sub> is 275.20 patients. The modeled hourly peak is 17.09 patients at 20:00 and trough 5.92 at 11:00; their ratio is 2.89. The peak is based on the eICU profile and is not a directly observed CMS hourly measure.")
figure("partner_repo/output_plots/02_nhpp_diurnal_arrival_rates.png","Figure Q2. Hourly non-homogeneous Poisson rates by CMS volume tier, using the eICU hourly shape (partner output).",h=255)
para("For any interval (u,v], the NHPP count has a Poisson law with mean equal to the integral of lambda(t) over that interval. Independent increments are a modeling assumption. Real hospital arrivals may cluster during epidemics or incidents, so overdispersion should be checked before a deployment model uses this curve.")
finish()

# 9
begin("Question 1  Are Patient Stays Predictable")
para("A service model based only on the mean misses the long-stay tail. In the processed SPARCS sample, mean LOS is 5.386 days and CV² is 1.991. The MIMIC ICU summary gives mean 3.63 days and CV² 2.215. The eICU fitting subset has mean 58.35 hours and CV² about 2.025. All three have variance greater than that of an exponential variable with the same mean.")
table(["Cohort","Mean stay","CV²","Interpretation"],[["SPARCS inpatient","5.386 d","1.991","Sample of 250,000 discharges"],["MIMIC ICU","3.63 d","2.215","94,444 ICU stays"],["eICU fitting subset","58.35 h","2.025","Demo cohort with positive LOS"]],[113,84,54,WIDTH-251])
eq("AIC = 2k - 2 log L", "Lower AIC ranks candidate laws; it does not prove an adequate absolute fit")
para("In eICU, Weibull has the lowest AIC (25,374), while gamma has a slightly smaller KS distance (0.0771 versus 0.0823). The Weibull shape is 0.9126, consistent with a decreasing fitted hazard. Both candidate KS p-values are extremely small, so neither should be described as an adequate exact law for this cohort.")
figure("partner_repo/output_plots/02_icu_los_fitting_diagnostics.png","Figure Q1. Empirical eICU ICU-stay distribution and candidate fits; visual and numerical fit diagnostics must be read together.",h=230)
finish()

# 10
begin("Question 3  How Many Beds Limit Waiting")
para("An M/M/c queue represents c identical inpatient beds with Poisson arrivals, exponential stays and an unlimited waiting room. Define a = lambda/mu and rho = a/c. The system has a stationary distribution only when rho is below one. Erlang-C gives the probability that an arrival must wait; dividing by spare service capacity gives the mean waiting time.")
eq("Wq = C(c,a) / (c mu - lambda)", "C(c,a) is the Erlang-C probability of waiting; valid only when c > a")
table(["Beds c","Utilization","P(wait)","Mean Wq"],[["230","97.83%","0.6480","15.55 h"],["235","95.74%","0.3993","4.79 h"],["240","93.75%","0.2325","1.86 h"],["242","92.98%","0.1842","1.30 h"]],[95,125,110,WIDTH-330])
para("The example uses lambda = 45 admissions/day and mean stay = 5 days, so a = 225 Erlangs. Moving from 230 to 242 beds adds 12 beds (5.2%) and reduces the model's mean queue wait by about 91.6%. This nonlinear sensitivity near rho = 1 is the main capacity lesson; the input rates are a stylized scenario rather than a fitted queue history.")
bars(["230 beds","235 beds","240 beds","242 beds"],[15.55,4.79,1.86,1.30],"Figure Q3  Mean queue wait by capacity, hours","These values use the same 225-Erlang scenario as the table above. The steep decrease is a steady-state prediction, not an observed intervention effect.",maximum=18,h=180)
finish()

# 11
begin("Question 4  How Many Beds Limit Diversion")
para("A loss system has no waiting room: an arrival finding all c beds full is blocked. For Poisson arrivals and exponential stays, Erlang-B computes that probability. Because no queue accumulates, this model is useful for diversion or rejection scenarios, not for patients who remain boarding in an ED.")
eq("B(0,a)=1;  B(c,a)=a B(c-1,a)/(c+a B(c-1,a))", "Stable recursion avoids very large factorials in the closed-form expression")
table(["Beds c","Blocking probability","Expected blocked per 100 arrivals"],[["150","6.24%","6.24"],["160","2.82%","2.82"],["165","1.68%","1.68"],["168","1.17%","1.17"],["169","1.03%","1.03"],["170","0.90%","0.90"]],[90,160,WIDTH-250])
para("At offered load a = 150 Erlangs, 169 beds remain above a 1% blocking target. The first integer capacity meeting that target is 170 beds, as computed by the capacity solver and recorded in the updated results JSON. A 1% target is a selected planning criterion, not a measured clinical standard.")
para("The carried traffic in a pure loss model is a(1-B). For a = 150 and c = 170, this is approximately 148.7 Erlangs. A hospital with an ED boarding area must instead model the blocked patients and upstream occupancy explicitly.")
sub("How the threshold is found")
para("Start with B(0,150)=1 and apply the recurrence once for each extra bed. The result falls from 0.010252 at c=169 to 0.008965 at c=170. Because 0.010252 exceeds the chosen 0.01 limit and 0.008965 is below it, 170 is the minimum integer solution. This discrete check is more precise than rounding a continuous safety-capacity rule.")
para("By the Poisson-arrivals-see-time-averages property, the chance an arriving patient finds all beds occupied equals the long-run fraction of time the system is in the full state under the model. If arrivals are scheduled or correlated with occupancy, that equality need not hold.")
finish()

# 12
begin("Question 5  Does Stay Variation Add Delay")
para("Erlang-C assumes exponential service, whose squared coefficient of variation is one. The Allen-Cunneen approximation adjusts a baseline M/M/c wait to reflect arrival and service variability. With Poisson arrivals, arrival CV² is one.")
eq("Wq(M/G/c) approx [(1 + CVs^2)/2] Wq(M/M/c)", "Approximation at the same mean arrival rate, mean service time and bed count")
table(["Source service CV²","Multiplier","Increase over exponential"],[["SPARCS 1.991","1.4955","49.6%"],["eICU 2.025","1.5125","51.3%"],["MIMIC ICU 2.215","1.6075","60.8%"]],[165,100,WIDTH-265])
para("The earlier master report used a second SPARCS variance value of 1.371, which does not match the processed 250,000-record summary (1.991). This report consistently uses the processed cohort value for the SPARCS calculation. These multipliers express modeled sensitivity to variance; they are not observed increases in patient waiting because actual queue waits are not available in those datasets.")
bars(["SPARCS","eICU","MIMIC ICU"],[1.4955,1.5125,1.6075],"Figure Q5  Approximate wait multiplier","All three bars apply the same Poisson-arrival correction formula to source-specific service variation. They do not compare measured queue waits.",maximum=1.8,h=160)
finish()

# 13
begin("Question 8  Does Emergency Priority Help")
para("Hospitals often prioritize emergency admissions over scheduled elective admissions. A non-preemptive priority rule allows a patient already in service to finish; the next available bed or server goes to the highest-priority waiting class. The project includes both an analytic two-class approximation and a priority simulation module.")
table(["Class / rule","Illustrative calculation"],[["FIFO, 240 servers; 45 arrivals/day","1.86 hours (Erlang-C)"],["Emergency priority heuristic","0.15 hours"],["Elective priority heuristic","2.35 hours"]],[WIDTH*.55,WIDTH*.45])
para("At 240 servers, 10 emergency and 35 elective arrivals per day, and mean service time five days, the current priority function gives the class figures shown. They are heuristic outputs, not independently validated queue waits. A sound priority result needs an event simulation or a justified multiserver formula with matched inputs. No percentage policy benefit is claimed here.")
sub("Fairness and operational safeguards")
para("A practical policy would specify acuity categories, an upper bound on elective delay, escalation for long waits, and frequent recalibration. Average class waits alone can hide a long upper tail. A useful follow-up simulation should report 90th and 95th percentile delay for each class and track cancellations as well as emergency response.")
eq("lambda_total = lambda_emergency + lambda_elective", "Total arrival workload is unchanged by the queue discipline")
para("The implemented approximation first calculates the total Erlang-C delay probability. It then divides a shared residual-work term by factors involving the high-priority and total utilization. That formulation is a simplified priority model; a hospital-grade evaluation should compare it with an event simulation using the same c, lambda and mu, since multi-server priority formulas depend on the exact service and admission discipline.")
finish()

# 14
begin("Question 6  What If Patients Leave the Queue")
para("The M/M/c+M model adds exponential patience to a multi-server waiting line. It can remain mathematically stable even when nominal service capacity is below arrival demand, because some patients leave the queue. That stability is not desirable care: abandonment represents unmet need.")
eq("death(n) = n mu  (n<=c);  c mu+(n-c)theta  (n>c)", "theta is the per-waiting-patient abandonment hazard")
para("The partner module uses CMS ED measures as an external benchmark. Its revised illustrative baseline has 45 ED bays and 90 ICU beds. Across 20 replications it reports 4.80% ED abandonment (95% half-width 0.31 percentage points), against the CMS 2.33%. Mean ED sojourn is 206.7 +/- 1.6 minutes against 202.5 minutes. Neither benchmark lies within the simulation interval; this is still a failed external validation.")
table(["Metric","Simulation","CMS benchmark","Assessment"],[["ED abandonment","4.80% +/- 0.31%","2.33%","Fails"],["ED sojourn","206.7 +/- 1.6 min","202.5 min","Fails"]],[117,125,112,WIDTH-354])
para("The code's Erlang-A theoretical comparison matches a chosen 202.5-minute target by construction, so it is not an independent validation. Before reporting policy benefits for real patients, the model needs harmonized denominators, realistic arrival and service scales, a calibrated patience distribution, and out-of-sample validation.")
para("For n patients present, service departures occur at rate min(n,c)mu and abandonment departures at rate max(n-c,0)theta. A stationary probability sequence can be built recursively from successive birth-to-death rate ratios, then normalized to sum to one. The long-run abandonment rate divided by the arrival rate is the modeled fraction that leaves untreated. Its denominator must match the CMS benchmark definition before any direct comparison.")
finish()

# 15
begin("Question 7  Does a Full ICU Block the ED")
para("A two-stage network sends some ED patients to ICU. If ICU beds are full and transfers cannot occur, boarded patients can occupy ED treatment space. The project expresses this coupling as an effective ED capacity that falls with the number of boarders.")
eq("c_ED,effective(t) = max(0, c_ED - boarders(t))", "A conceptual coupling; actual bay blocking depends on the implemented event rules")
para("The eICU demo ED-admitted subset contains 1,304 ICU stays. Its hospital-admission offset suggests a 4.46-hour mean pre-ICU hospital interval. This offset does not establish that the entire interval was spent boarding in an ED bay. The fitted Weibull for that proxy has a very small KS p-value and is not an adequate exact law.")
table(["ICU beds","ICU use","ED abandonment","Mean delay if boarded"],[["70","98.9%","15.50%","8.23 h"],["90","86.3%","4.80%","2.25 h"],["110","71.2%","4.68%","0.04 h"]],[100,100,112,WIDTH-312])
para("The repaired simulation keeps an ICU bed occupied for the full ICU stay and an ED bay occupied only until transfer. It now records positive boarding delays; the displayed mean is conditional on a patient boarding. These are scenario outputs under a hybrid eICU and CMS input, not observed effects of adding ICU beds. The 90-bed baseline still fails the CMS ED benchmark.")
para("For an ICU-bound simulated patient, board delay equals ICU bed acquisition time minus ICU request time. The ED bay is released on transfer. A future validation dataset must include those actual timestamps so the simulated delay can be compared with a like-for-like observed measure.")
finish()

# 16
begin("Question 11  Where Do Patients End Up")
para("An absorbing discrete-time Markov chain summarizes transitions among transient departments until discharge home or death. Partition the one-step matrix into transient-to-transient probabilities Q and transient-to-absorbing probabilities R. The fundamental matrix counts expected visits before absorption, and its row sums count expected steps.")
eq("N = (I - Q)^(-1);   A = N R;   steps = N 1", "A is the matrix of eventual absorbing-outcome probabilities")
table(["Starting state","Home absorption","Expired absorption","Expected steps"],[["ED","87.60%","12.40%","1.53"],["ICU","88.88%","11.12%","1.60"],["Floor","79.65%","20.35%","-" ]],[110,125,135,WIDTH-370])
para("These are model-chain probabilities estimated from a selected transition representation. They differ from raw eICU overall mortality (5.0% ICU, 8.41% hospital) because the starting state and absorbing outcome definitions differ. The 11.12% ICU-start chain value should not be relabeled as observed ICU mortality.")
para("The matrix computation requires the transient block Q to have spectral radius below one, so absorption occurs with probability one. Each row of A should sum to one up to numerical error. These are useful implementation checks. A richer clinical model would estimate different transition probabilities by admission severity and diagnosis, then examine whether a memoryless one-step rule still describes the observed paths.")
figure("partner_repo/output_plots/03_markov_chain_analysis.png","Figure Q11. Partner transition and absorption analysis. Matrix entries represent model routing probabilities, not causal survival effects.",h=235)
finish()

# 17
begin("Question 9  Which Ward Is the Bottleneck")
para("A hospital is a network: patients can move from ED to ICU, from ICU to a floor, or between other units before leaving. An open Jackson model estimates the total arrivals to each ward after accounting for these transfers. If gamma is the vector of arrivals from outside and P contains routing probabilities, the total arrival vector Lambda solves the traffic equations below.")
eq("(I - P^T) Lambda = gamma", "Lambda includes external arrivals plus arrivals caused by transfers")
table(["Scenario ward","Total arrivals / day","Beds","Utilization"],[["ED","31.48","25","63.0%"],["ICU","14.75","55","80.5%"],["Med/Surg","34.59","200","86.5%"]],[123,144,70,WIDTH-337])
para("The verified three-node scenario identifies Med/Surg as the highest-utilization station and computes mean end-to-end time of 5.19 days. External arrivals are 30, 5 and 10 per day for ED, ICU and Med/Surg. The mean service durations are 0.5, 3 and 5 days. This is a demonstration model; the local MIMIC five-department matrix is a separate empirical routing calibration and is not the three-node scenario's exact input.")
para("For each ward j, the traffic equation reads Lambda_j = gamma_j + sum_i Lambda_i P_ij: arrivals consist of new patients plus transfers from every upstream ward. After solving this linear system, nominal ward utilization is Lambda_j E[S_j]/c_j. The largest value identifies the modeled capacity bottleneck. Little's law then links the total mean number in the network to mean end-to-end time using the total external arrival rate.")
para("The separate continuous-time Markov chain describes how pathway probabilities change with time: p(t)=p(0)exp(Gt), where generator G contains transition rates. It answers a different question from the Jackson network's long-run average ward loads.")
finish()

# 18
begin("Question 10  Can Staffing Follow Busy Hours")
para("Pointwise stationary approximation evaluates a stationary queue at each hour using that hour's arrival intensity and available capacity. It is a screening tool for staffing schedules when demand changes slowly relative to service. It can be inaccurate during rapid surges because a queue formed earlier persists after the arrival rate falls.")
eq("Wq(t) approx Wq_stationary(lambda(t), c(t), mu)", "The approximation ignores carryover between neighboring hours")
para("In the repository scenario, a constant 425-bed schedule has a calculated peak queue wait of 41.5 minutes. A dynamic schedule with 25 more peak-period bed equivalents and an offsetting night reduction gives a calculated peak of 1.1 minutes, a 97.3% reduction. Equal bed-hours in the modeled schedule do not guarantee equal staffing cost or physical feasibility.")
figure("reports/figures/fig8_time_varying_diurnal_queue.png","Figure Q10. Pointwise-stationary scenario comparing constant and shifted capacity across a day; peak reduction is a model estimate.",h=270)
para("A deployment analysis would add shift-length constraints, nurse-to-patient ratios, handoffs, bed cleaning time and a time-dependent discrete-event simulation to check transient carryover. Those elements are outside the current PSA result.")
para("The tested schedule changes 425 beds to 450 for an eight-hour peak window and to 400 for an eight-hour quiet window; the remaining eight hours retain 425. The gains and reductions each contribute 25 times 8 = 200 bed-hours, so the net modeled difference is zero. This accounting does not show whether the right staff can move between those periods or whether all physical beds can be opened on demand.")
finish()

# 19
begin("Question 12  How Should Beds Be Split")
para("When a fixed total C beds must be split among departments, a separable loss objective can weight blocking by department importance. The project starts at minimum capacities and repeatedly places the next bed where it produces the largest reduction in the weighted objective.")
eq("min sum_j w_j B(c_j, a_j),  subject to sum_j c_j = C", "The code's specific objective uses configured department weights and offered loads")
table(["Department","Proportional beds","Marginal allocation","Difference"],[["ICU","24","33","+9"],["Emergency","34","43","+9"],["Med/Surg","172","154","-18"],["Total","230","230","0"]],[WIDTH*.31,WIDTH*.25,WIDTH*.27,WIDTH*.17])
para("For loads 20, 30 and 150 Erlangs and weights 4, 2 and 1, the computed weighted blocking objective falls from 0.40374 to 0.06550 (83.8%) under the same 230-bed budget. The objective is not a directly observed hospital-wide diversion probability. The allocation could be infeasible if beds are specialty-specific or if converting ward space requires staff and equipment.")
eq("gain_j = w_j [B(c_j,a_j) - B(c_j+1,a_j)]", "At each step, allocate the next bed to the feasible ward with largest gain")
para("The code computes each ward's one-bed marginal gain with the Erlang-B recurrence and repeats until the integer budget is exhausted. Weights encode relative penalty and are a policy choice. A sensitivity study should vary those weights and minimum ward capacities before treating the numerical split as a recommendation.")
bars(["Proportional","Marginal"],[0.40374,0.06550],"Figure Q12  Weighted blocking objective","The two bars use the exact 230-bed scenario and configured weights in the table above. The measure is an optimization objective, not a patient-level event rate.",maximum=0.45,h=135)
finish()

# 20
begin("Question 13  Do Simulations Check Out")
para("The main repository's event-calendar simulator advances between arrival and service-completion events. A patient arriving to an available bed starts service; otherwise the patient waits. Random seeds make test scenarios reproducible. The partner module uses SimPy for ED-to-ICU experiments with abandonment and capacity sweeps.")
table(["Simulation element","Main test setup","Partner ED/ICU setup"],[["Input arrivals","Poisson, 50 per day","Hourly NHPP profile and CMS volume tier"],["Service","Gamma LOS, mean 5.386 days","ED and ICU service stages"],["Capacity","290 beds","45 ED bays; ICU 70 to 120"],["Horizon / replication","30 days, seed 42 in master check","20 replications per capacity"],["Recorded outcomes","Patients, utilization, waits","Abandonment, sojourn, ICU use, boarding"]],[115,172,WIDTH-287])
para("The master run simulated 1,518 patients over 30 days and reported 70.5% time-weighted utilization. It starts empty, so this short-run average is below a steady-state occupancy estimate and must not be presented as a calibrated hospital rate. A single seeded path is not an uncertainty interval. The partner sweep reports 95% Monte Carlo half-widths across replications; these quantify random simulation error, not bias from model structure or parameter mismatch.")
sub("Replication logic")
para("For output Y across r independent runs, the sample mean is the average of Y<sub>i</sub>, with a t-based half-width proportional to sample standard deviation divided by the square root of r. Replications should use independent seeds and remove initialization bias when a steady-state quantity is desired.")
eq("CI_95 = mean(Y) +/- t_(r-1,0.975) s(Y)/sqrt(r)")
para("A practical validation run should compare full outcome distributions, not only means. The 90th percentile wait, diversion count by shift and time spent boarding could be compared on held-out days. Increasing the replication count reduces Monte Carlo noise, while changes to event logic and parameter calibration address bias. Both are needed for a credible model, but they solve different problems.")
finish()

# 21
begin("Verification and Validation Results")
para("The local verification script completed its 11 stages on 29 October 2026. It discovered and passed 40 unit tests, validated 5,000 synthetic encounters, exercised queueing and Markov calculations, ran simulation, recalibrated the local MIMIC inputs, solved the network and optimization scenarios, and checked primary figures plus partner outputs.")
table(["Evidence","Result","What it establishes"],[["40 unit tests","Pass","Defined functions meet tested mathematical and data-handling cases."],["11 pipeline stages","Pass","The repository runs in the current environment with its inputs."],["MIMIC adapter","2,004,604 transfers","Local data calibration completed."],["Main DES","1,518 patients; 70.5% use","One seeded, empty-start run; not steady-state."],["External ED benchmark","4.80% vs 2.33% abandonment","Material model-data disagreement remains."]],[124,120,WIDTH-244])
para("Software verification asks whether the code implements intended calculations. Empirical validation asks whether outputs represent the target system. The first passed; the second is mixed. In particular, the eICU fitted Weibull ranks best among candidates by AIC but fails a strict KS test, and the ED/ICU simulation misses CMS abandonment and sojourn benchmarks. A report of code success cannot erase these discrepancies.")
para("The mathematical verification now reads the processed SPARCS data and computes the Erlang-B threshold of 170 beds directly. The remaining material gaps are empirical: the priority heuristic has not been independently validated, and the partner ED simulation does not match the external CMS benchmark.")
finish()

# 22
begin("Comparative Results and Model Choice")
table(["Decision question","Appropriate model","Key output","Important caution"],[["Will a patient wait?","Erlang-C M/M/c","P(wait), Wq","Assumes waiting allowed and rho below 1."],["Will a patient be turned away?","Erlang-B M/M/c/c","P(block)","Assumes no queue or boarding."],["Can a patient leave the queue?","Erlang-A M/M/c+M","Abandonment, wait","Patience must be calibrated."],["Does long LOS matter?","Allen-Cunneen M/G/c","Approximate Wq","Not an exact queue result."],["Where do transfers accumulate?","Open Jackson network","Station load and flow","Product-form assumptions are strong."],["What changes by hour?","NHPP + PSA","Hourly load and wait","PSA misses queue carryover."],["How to split fixed beds?","Discrete marginal allocation","Weighted objective","Weights and conversion feasibility matter."]],[125,112,96,WIDTH-333])
sub("Synthesis")
para("The evidence supports three robust qualitative statements. First, stay duration is more variable than the exponential benchmark in each examined cohort. Second, both waiting and blocking are very sensitive to capacity near a high offered load. Third, a network view is needed because patients can be delayed by a downstream ward even when an upstream station is not highly occupied.")
para("Specific percentage reductions from staffing and allocation are conditional model outputs. They should guide scenario screening and data collection, then be tested using observed operational timelines and a calibrated transient simulation before implementation.")
finish()

# 23
begin("Sensitivity and Uncertainty")
para("The queueing outputs depend on the arrival rate, mean service duration and capacity. Offered load is their product, so an error in either arrivals or stay duration propagates into both occupancy and the nonlinear waiting curve. At high rho, small parameter errors can cause large wait errors.")
eq("a = lambda E[S];  rho = a/c", "A 10% increase in lambda or E[S] causes a 10% increase in offered load")
table(["Change from base scenario","Expected consequence","What to test next"],[["Arrival surge","Higher a and possible transient backlog","Use measured hourly counts and incident days."],["Longer mean LOS","More occupied beds for the same arrivals","Fit by ward and case mix."],["Higher LOS variance","Higher approximate wait at same mean","Simulate fitted and empirical LOS resamples."],["Different routing","Load shifts across ED, ICU and floors","Re-estimate transition matrix by subgroup."],["Different objective weights","Different optimal bed split","Review clinical priorities and feasible conversions."]],[145,155,WIDTH-300])
para("Monte Carlo intervals in the partner output are narrow compared with the CMS mismatch, so adding simulation replications alone will not solve that discrepancy. Structural checks and out-of-sample comparison should take priority. Patient mix, seasonality and capacity calendars should be treated as additional sources of uncertainty.")
finish()

# 24
begin("Discussion and Operational Meaning")
para("The practical value of the project is a framework for asking capacity questions with the correct queue rule. If an arrival waits for a bed, delay-system mathematics applies; if admission is rejected, a loss model applies; if the person leaves the waiting room, patience must be modeled. Conflating these mechanisms can produce a precise-looking but irrelevant number.")
sub("What the current analysis suggests")
para("For the stylized 225-Erlang inpatient scenario, a buffer above the nominal 225 occupied beds matters greatly: 230 beds lead to a very long expected wait, while 242 beds substantially shorten it. For a fixed 230-bed, three-department scenario, weighting high-acuity loss changes the preferred split. A diurnal schedule can reduce peak modeled waiting when staffed capacity follows the modeled arrival curve.")
sub("What would be needed before a hospital decision")
para("A facility should provide timestamped arrivals, bed request times, actual service starts, ward transfers, bed cleaning intervals, staffed-bed counts and abandonment events. Model outputs should be checked on a held-out time period and by patient subgroup. Clinicians and operations staff should review the loss weights, safety constraints and fairness implications. The current datasets were assembled across different institutions and cannot establish an intervention effect for one hospital.")
para("The ED/ICU event logic is repaired, but the simulated abandonment rate still differs from CMS and its eICU timing proxy is not measured ED boarding. We therefore do not use that module to recommend a specific ICU expansion or to claim patient-level benefit.")
finish()

# 25
begin("Limitations and Responsible Interpretation")
table(["Limitation","Consequence"],[["Cross-source calibration","eICU hourly shares scaled to CMS volume create an illustrative hybrid, not a measured hospital."],["Temporal detail","SPARCS discharge data cannot reveal minute-level admission queues."],["Simple queue assumptions","Poisson arrivals, homogeneous servers and exponential stay assumptions may fail."],["Parametric LOS fit","Best AIC does not mean adequate absolute fit; KS screens reject candidate laws."],["Markov memorylessness","Routing may depend on diagnosis, severity and time already spent in a ward."],["Simulation mismatch","Partner ED abandonment and sojourn outputs do not match CMS benchmark."],["Optimization feasibility","Beds and trained staff are not instantly transferable across specialties."],["Uncertainty","Parameter, model and external validity uncertainty exceed reported Monte Carlo error."]],[162,WIDTH-162])
para("The report uses no patient-identifying records. Results are educational model demonstrations and should not be treated as clinical guidance. In particular, a modeled decrease in weighted blocking is not an observed reduction in diversion, mortality or time to care.")
para("The most useful extension is a single-facility time-stamped dataset with arrivals, bed requests, actual transfers, staffed capacity and abandonments. Fit parameters on one period and validate on another. Then compare a transient simulation against observed daily queues and use uncertainty intervals that include both input estimation and Monte Carlo variation. That would turn the present analytical screening framework into a more credible decision aid.")
finish()

# 26
begin("Reproducibility and Conclusions")
sub("Run procedure")
para("From the project root, install the packages listed in <font name='Consolas'>requirements.txt</font> and run <font name='Consolas'>python scripts/verify_all.py</font>. The separate <font name='Consolas'>python scripts/verify_all_math_results.py</font> writes numerical scenario summaries to <font name='Consolas'>data/processed/master_verified_math_results.json</font>. The partner scripts 01 through 05 can be run sequentially from the root. Raw credentialed MIMIC inputs require the user's authorized local access.")
table(["Local verification item","29 Oct 2026 run"],[["Unit tests","40 passed"],["Synthetic data check","5,000 records, no reported violations"],["MIMIC calibration","2,004,604 transfers"],["Main DES","1,518 patients, 70.5% time-weighted utilization"],["Figures and partner assets","9 main figures; partner plots and tables checked"]],[205,WIDTH-205])
sub("Conclusions")
para("The study demonstrates a complete applied stochastic modeling pipeline on real hospital-related datasets. Long and variable stays, time-varying demand and downstream routing materially affect calculated congestion. Erlang and network formulas make the mechanisms understandable; simulation checks implementation and exposes where calibration fails.")
para("The strongest numerical results are conditional: adding 12 beds in the chosen Erlang-C scenario changes mean wait from 15.55 to 1.30 hours; reallocating a fixed 230-bed budget changes its weighted blocking objective from 0.40374 to 0.06550. The next research step is to calibrate and validate the repaired ED/ICU model on coherent, time-stamped data before presenting patient-level policy effects.")
finish()

# 27
begin("References, source files, and notation")
para("<b>Data and project sources.</b> NYS SPARCS 2009 de-identified inpatient extract in <font name='Consolas'>data/raw/sparcs</font>; MIMIC-IV v3.1 local transfer and ICU files in <font name='Consolas'>data/raw/mimic_full</font>; eICU demo v2.0.1 local tables in <font name='Consolas'>partner_repo/eicu_demo_data</font>; CMS Timely and Effective Care local extract in <font name='Consolas'>partner_repo/cms_data</font>. Data access conditions and extraction details are recorded in the repository README and source scripts.")
table(["Official dataset record","Link"],[["NYS SPARCS de-identified inpatient data","<link href='https://health.data.ny.gov/Health/Hospital-Inpatient-Discharges-SPARCS-De-Identified/wqxw-9f5x'>Health Data NY dataset page</link>"],["MIMIC-IV version 3.1","<link href='https://physionet.org/content/mimiciv/3.1/'>PhysioNet; DOI 10.13026/kpb9-mt58</link>"],["eICU demo version 2.0.1","<link href='https://physionet.org/content/eicu-crd-demo/2.0.1/'>PhysioNet; DOI 10.13026/4mxk-na84</link>"],["CMS Timely and Effective Care","<link href='https://data.cms.gov/provider-data/dataset/yv7e-xc69'>CMS Provider Data Catalog</link>"]],[202,WIDTH-202],gap=10)
para("<b>Analytical source files.</b> <font name='Consolas'>src/queueing.py</font>, <font name='Consolas'>src/distributions.py</font>, <font name='Consolas'>src/arrival_process.py</font>, <font name='Consolas'>src/markov_chain.py</font>, <font name='Consolas'>src/jackson_network.py</font>, <font name='Consolas'>src/time_varying.py</font>, <font name='Consolas'>src/bed_allocation.py</font>, <font name='Consolas'>src/simulation.py</font>, and partner scripts 01-05. Local numeric sources are the processed JSON files and partner output tables named throughout this report.")
sub("Selected methodological references")
para("Kendall, D. G. (1953), <i>Stochastic Processes Occurring in the Theory of Queues...</i>, Annals of Mathematical Statistics 24(3), 338-354, DOI 10.1214/aoms/1177728975. Jackson, J. R. (1957), <i>Networks of Waiting Lines</i>, Operations Research 5(4), 518-521, DOI 10.1287/opre.5.4.518. Little, J. D. C. (1961), <i>A Proof for the Queuing Formula: L = lambda W</i>, Operations Research 9(3), 383-387, DOI 10.1287/opre.9.3.383. Numerical results come from the local project outputs.")
sub("Notation checklist")
table(["Expression","Meaning"],[["CV² = Var(S)/E[S]²","Relative service-time variation"],["a = lambda E[S]","Mean workload offered to the station"],["rho = a/c","Nominal server utilization"],["N = (I-Q)^(-1)","Expected transient-state visits in an absorbing chain"],["(I-P^T)Lambda = gamma","Open-network traffic balance"],["W = L/lambda","Little's law under consistent rates and populations"]],[180,WIDTH-180])
para("<b>Reproduction note.</b> The report is generated by <font name='Consolas'>scripts/generate_submission_report.py</font>. Page figures are taken from the repository's generated image outputs. The numerical tables and caveats were checked against local processed files and the verification run.",style="small")
finish()

assert page_no == 27, page_no
C.save()

# Put the 13 question deep dives immediately after the one-page question index.
# The remaining pages carry the project context, verification, interpretation,
# and references. Replace the original footer numbers after page reordering.
order = [0, 8, 7, 9, 10, 11, 13, 14, 12, 16, 17, 15, 18, 19,
         1, 2, 3, 4, 5, 6, 20, 21, 22, 23, 24, 25, 26]
reader = PdfReader(str(OUT))
assert len(reader.pages) == 27 and len(set(order)) == 27
writer = PdfWriter()
for new_number, old_index in enumerate(order, 1):
    page = reader.pages[old_index]
    layer_bytes = BytesIO()
    overlay = canvas.Canvas(layer_bytes, pagesize=(W, H))
    overlay.setFillColor(white)
    overlay.rect(0, 0, W, 51, fill=1, stroke=0)
    overlay.setStrokeColor(GRID)
    overlay.line(L, 42, W-R, 42)
    overlay.setFont("Arial", 7.4)
    overlay.setFillColor(MUTED)
    overlay.drawString(L, 29, "Hospital patient flow and bed capacity | ASM course project")
    overlay.drawRightString(W-R, 29, f"{new_number} / 27")
    overlay.save()
    layer_bytes.seek(0)
    page.merge_page(PdfReader(layer_bytes).pages[0])
    writer.add_page(page)
writer.add_metadata({"/Title":"Hospital Patient Flow and Bed Capacity - ASM Submission",
                     "/Author":"Manas and Yashasvee"})
tmp_out = OUT.with_suffix(".reordered.pdf")
with tmp_out.open("wb") as fh:
    writer.write(fh)
tmp_out.replace(OUT)
print(f"Created {OUT} ({page_no} pages; questions 1-13 on pages 2-14)")
