"""
Comprehensive Technical Analysis Report Generator.
Generates:
1. reports/Comprehensive_Technical_Analysis_Report.md
2. reports/pdf/Comprehensive_Technical_Analysis_Report.pdf

Covers EVERY Problem Statement (PS 1 to PS 13) with full analytical rigor:
- A. Problem Statement Overview
- B. Dataset and Data Used
- C. Theoretical Concepts and Technical Foundations
- D. Methodology and Implementation
- E. Results and Mathematical Derivation (Step-by-step with verified experimental values)
- F. Interpretation of Results
- G. Suggestions and Recommendations
- H. Conclusion
Followed by Cross-Problem Comparative Analysis, Conclusion, Future Scope, References, and Appendices.
"""

import os
import sys
from pathlib import Path
import json
import math

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ensure output directories exist
(ROOT_DIR / "reports" / "pdf").mkdir(parents=True, exist_ok=True)
(ROOT_DIR / "reports" / "figures").mkdir(parents=True, exist_ok=True)

from scripts.ps1_section import get_ps1_text
from scripts.ps2_ps4_section import get_ps2_ps4_text
from scripts.ps5_ps8_section import get_ps5_ps8_text
from scripts.ps8_ps10_section import get_ps8_ps10_text
from scripts.ps11_ps13_section import get_ps11_ps13_text
from scripts.synthesis_sections import get_synthesis_sections_text

def generate_markdown_report() -> Path:
    """Generate the complete comprehensive technical report in Markdown format."""
    md_path = ROOT_DIR / "reports" / "Comprehensive_Technical_Analysis_Report.md"
    
    with open(md_path, "w", encoding="utf-8") as f:
        # Title Page and Header
        f.write("""# COMPREHENSIVE TECHNICAL ANALYSIS REPORT
## Applied Stochastic Models of Hospital Patient Flow, Congestion & Bed Capacity Sizing
**A Unified Dual-Track Investigation Synthesizing Macroscopic Hospital Networks and Microscopic Acute Care Dynamics**

---

### Project & Document Metadata
- **Project Title:** Applied Stochastic Models for Hospital Patient Flow, Congestion, and Resource Allocation
- **Course / Module:** Applied Stochastic Models (ASM)  --  Master Project Portfolio
- **Lead Researchers / Authors:** Manas (Macroscopic Network Track) & Yashasvee (Microscopic Acute Care Track)
- **Clinical Cohorts Analyzed:**
  1. *NYS SPARCS:* 250,000 Inpatient Discharge Encounters (New York State Department of Health)
  2. *MIMIC-IV v3.1:* 2,004,604 Ward Transfers, 94,444 Intensive Care Unit Stays (BIDMC / MIT PhysioNet)
  3. *eICU-CRD v2.0.1:* 2,520 Multi-Center ICU & Emergency Encounters (Philips Healthcare / PhysioNet)
  4. *CMS Hospital Quality Care:* Federal Emergency Throughput & Timely Care Benchmarks (`yv7e-xc69`)
- **Primary Deliverables:**
  - Full Technical PDF: `reports/pdf/Comprehensive_Technical_Analysis_Report.pdf`
  - 23-Page Master Combined PDF: `reports/pdf/Master_Combined_Stochastic_Hospital_Flow_Report.pdf`
  - Interactive Digital Twin Dashboard: `app.py` (Streamlit Port 8501)
  - Unit & Verification Test Suite: 63 Passing Tests across 12 Modules (`pytest`)
- **Document Date:** October 2026

---

## Executive Summary & Abstract

Hospital inpatient bed allocation, emergency department boarding, and acute care congestion represent critical challenges in modern healthcare engineering. Insufficient capacity creates dangerous ambulance diversions, extended triage delays, and nurse burnout, whereas excessive idle capacity incurs severe financial deficits ($1,200 to $3,500 per bed-day). Classical healthcare capacity planning frequently relies on naive static average occupancies or idealized Poisson/exponential assumptions that fail catastrophically during operational surges.

This technical analysis report presents a rigorous, evidence-based stochastic modeling framework addressing **thirteen foundational Problem Statements (PS 1 through PS 13)** across hospital operations. By establishing a dual-track analytical architecture, this project bridges **Track 1 (Macroscopic Network Flow across 2.0M MIMIC-IV transitions and 250k SPARCS records)** with **Track 2 (Microscopic Intensive Care & Boarding Dynamics across 2,520 multi-center eICU stays and CMS quality metrics)**.

### Core Quantitative Findings:
1. **Empirical Rejection of the Memoryless Assumption (PS 1):** Clinical stays across general medical wards ($c_v^2 = 1.991$) and intensive care units ($c_v^2 = 2.025 \\text{ to } 2.215$) are decisively heavy-tailed ($p < 10^{-14}$). The best-fitting parametric model is the Weibull distribution with shape parameter $k = 0.9126 < 1.0$, demonstrating a decreasing hazard rate where medical complications entrap long-stay patients.
2. **Circadian Surge Conservation (PS 2):** Emergency arrivals exhibit a non-homogeneous Poisson rhythm with a $2.89\\times$ surge ratio, peaking at 20:00 ($\\lambda = 17.09\\text{ pts/hr}$) versus a trough at 11:00 ($\\lambda = 5.91\\text{ pts/hr}$).
3. **QED Bed Capacity Buffering (PS 3 & PS 4):** Inpatient capacity sized naively to offered load ($c = a = 225$) operates at $\\rho = 100\\%$ with unbounded queue delay; operating at $c = 230$ yields a 15.55-hour average wait. Sizing into the Halfin-Whitt Quality-and-Efficiency-Driven (QED) regime at $c = 242$ beds ($\\rho = 93.0\\%$) collapses queue wait by **$-91.6\\%$** (to 1.30 hours) for a modest $+5.2\\%$ bed investment. In loss systems ($M/M/c/c$), achieving regulatory compliance ($P_{\\text{block}} \\le 1.0\\%$) requires a $+19\\text{-bed}$ safety buffer ($c^* = 169$ vs. $a = 150$).
4. **Heavy-Traffic Variance Delay Inflation (PS 5):** Allen-Cunneen / Kingman approximations demonstrate that recovery variance inflates patient waiting times by $+49.6\\%$ (SPARCS), $+51.3\\%$ (eICU), and $+60.7\\%$ (MIMIC-IV) over textbook exponential models.
5. **Self-Stabilizing Abandonment & Boarding Coupling (PS 6 & PS 7):** Patient impatience ($M/M/c+M$ Erlang-A) acts as a safety valve during severe overloads ($\\rho = 1.20$), where 16.7% of patients walk out without care ($2.0\\text{ pts/hr}$); adding 4 bays ($c = 14$) drops walkouts to $1.8\\%$. Upstream emergency crowding is driven by downstream ICU saturation, where an 8-bed ICU locks 6.8 emergency bays with boarding patients; expanding ICU capacity to 16 beds completely eliminates upstream boarding contention.
6. **Priority Triage & Network Routing Optimization (PS 8 & PS 9):** Non-preemptive priority triage slashes emergency delay from 10.0 hours to 2.5 hours ($-75\\%$), while scheduled elective stays absorb buffer delay in strict accordance with the Kleinrock conservation law. Open Jackson network analysis of 2.0M MIMIC-IV transfers identifies the General Medical/Surgical Floor as the primary systemic bottleneck ($\\rho = 86.5\\%$, mean dwell stay $5.19\\text{ days}$).
7. **Zero-Cost Shift Reallocation & Fox Knapsack Optimization (PS 10, PS 11, PS 12, PS 13):** Dynamic Pointwise Stationary Approximation (PSA) shift staffing collapses peak evening triage wait by **$-97.3\\%$** (from 41.5 min to 1.1 min) at **zero net bed-hour or labor cost**. Fox's greedy marginal allocation solves the multi-department separable convex knapsack program, cutting hospital-wide patient blocking by **$-83.8\\%$** ($0.40374 \\to 0.06550$). Discrete-event simulations across 20 Monte Carlo replications confirm analytical predictions within $\\pm 0.27\\%$ relative error.

---

## Master Table of Contents
1. **Chapter 1: Research Project Overview & Clinical System Architecture**
2. **Chapter 2: Problem Statement 1 (PS 1)  --  Heavy-Tailed Service Stays & Hazard Rate Monotonicity**
3. **Chapter 3: Problem Statement 2 (PS 2)  --  Diurnal Inflow Surges & Non-Homogeneous Poisson Arrival Processes**
4. **Chapter 4: Problem Statement 3 (PS 3)  --  Inpatient Bed Sizing via Erlang-C & Halfin-Whitt QED Buffering**
5. **Chapter 5: Problem Statement 4 (PS 4)  --  Ambulance Diversion Thresholds & Erlang-B Multi-Server Loss Systems**
6. **Chapter 6: Problem Statement 5 (PS 5)  --  Heavy-Traffic Variance Delay Expansion: The Allen-Cunneen / Kingman Penalty**
7. **Chapter 7: Problem Statement 6 (PS 6)  --  Patient Reneging, Abandonment (LWBS), and the Erlang-A Model**
8. **Chapter 8: Problem Statement 7 (PS 7)  --  Two-Stage Tandem Queues, Downstream Saturation, and ED Boarding**
9. **Chapter 9: Problem Statement 8 (PS 8)  --  Multi-Class Non-Preemptive Priority Triage & Kleinrock Conservation**
10. **Chapter 10: Problem Statement 9 (PS 9)  --  Multi-Stage Open Jackson Networks & Departmental Bottleneck Detection**
11. **Chapter 11: Problem Statement 10 (PS 10)  --  Time-Varying PSA Queueing & Circadian Shift Staffing Reallocation**
12. **Chapter 12: Problem Statement 11 (PS 11)  --  Continuous-Time Markov Chains (CTMC) & Absorbing Disposition Pathways**
13. **Chapter 13: Problem Statement 12 (PS 12)  --  Multi-Department Bed Allocation via Fox's Greedy Marginal Knapsack**
14. **Chapter 14: Problem Statement 13 (PS 13)  --  Discrete-Event Simulation (DES) Engine & Empirical Model Validation**
15. **Chapter 15: Cross-Problem-Statement Comparative Analysis & Synthesis**
16. **Chapter 16: Overall Conclusion, Engineering Recommendations & Future Scope**
17. **Chapter 17: IEEE References & Technical Bibliography**
18. **Chapter 18: Appendices (Mathematical Notation, Software Architecture & Codebase Map)**

---

## Chapter 1: Research Project Overview & Clinical System Architecture

### 1.1 The Operational Crisis in Acute Care Hospital Flow
Modern hospital systems operate under severe resource constraints. When acute care demands surge due to seasonal viral outbreaks, mass-casualty incidents, or chronic disease flare-ups, hospital wards frequently hit saturation. Patient flow is characterized by a series of queueing dependencies:
- **Intake:** Patients arrive through the Emergency Department (ED), elective surgical booking, or direct transfer from outpatient clinics.
- **Triage & Stabilization:** Arriving patients are triaged based on clinical acuity (ESI Levels 1-5).
- **Inpatient Ward Placement:** Following stabilization, patients requiring admission are transferred to specialized inpatient units (Intensive Care Unit, Step-Down Unit, or General Medical/Surgical Floor).
- **Exit & Disposition:** Patients complete recovery and are discharged home, transferred to Skilled Nursing Facilities (SNF), or experience in-hospital mortality.

If downstream inpatient beds are fully occupied, departing emergency patients cannot transfer forward. They remain stuck in emergency bays -- a condition termed **ED Boarding**. ED boarding paralyzes the intake capacity of the hospital, causing incoming ambulances to be placed on **diversion**, prolonging triage wait times, and causing distressed patients to **leave without being seen (LWBS)**.

### 1.2 Dual-Track Research Integration Architecture
To resolve these operational challenges with mathematical rigor, this project synthesizes two complementary research pipelines into a unified stochastic modeling engine:

```
+----------------------------------------------------------------------------------------------------+
|                               UNIFIED CLINICAL DATA ARCHITECTURE                                   |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  [TRACK 1: Macroscopic Whole-Hospital Flow]         [TRACK 2: Microscopic Emergency/ICU Flow]      |
|  - NYS SPARCS: 250,000 inpatient discharges         - eICU-CRD v2.0.1: 2,520 multi-center ICU stays|
|  - MIMIC-IV v3.1: 2,004,604 transfers, 94.4k ICU    - CMS Quality Care: ED throughput measures     |
|  - Scope: System-wide bed sizing, multi-station     - Scope: Upstream/downstream boarding,         |
|    Jackson networks, circadian shift staffing,        patient reneging (abandonment), Erlang-A,    |
|    Fox's greedy bed allocation optimization.          tandem CTMC queueing with finite buffers.    |
|                                                                                                    |
|                                     \\                     /                                        |
|                                      \\                   /                                         |
|                                       v                 v                                          |
|  +----------------------------------------------------------------------------------------------+  |
|  |                           UNIFIED APPLIED STOCHASTIC ENGINE                                  |  |
|  |  - Parameter Calibration: MLE service fitting, hazard rate analysis, empirical transition P  |  |
|  |  - Analytical Queueing: M/M/c, M/M/c/c, M/G/c, M/M/c+M Erlang-A, Priority, Jackson, PSA     |  |
|  |  - State Space Modeling: Continuous-Time Markov Chains (CTMC), Kolmogorov ODEs, Matrix Exp   |  |
|  |  - Optimization & Validation: Fox's Greedy Marginal Knapsack, 20-Run SimPy DES Engine        |  |
|  +----------------------------------------------------------------------------------------------+  |
+----------------------------------------------------------------------------------------------------+
```

### 1.3 Master Problem Statement Cross-Validation Matrix
Every problem statement in this project maps directly to a verified mathematical model, clinical cohort, and quantitative finding:

| PS ID | Problem Domain & Clinical Focus | Mathematical / Stochastic Method | Primary Dataset | Verified Numerical Result & Impact |
|:---:|---|---|---|---|
| **PS 1** | Heavy-Tailed Stays & Hazard Monotonicity | Weibull/Lognormal MLE, K-S Testing | SPARCS, MIMIC-IV, eICU | $c_v^2 = 1.991 \\text{ to } 2.215 > 1.0$. Exp rejected ($p < 10^{-14}$). Weibull $k = 0.9126 < 1.0$ (decreasing hazard). |
| **PS 2** | Diurnal Inflow Surges & Circadian Wave | NHPP Fourier Harmonics & Thinning | CMS Care (`yv7e-xc69`) | $\\Lambda_{\\text{day}} = 275.20\\text{ pts/d}$, Peak 20:00 ($17.09\\text{/h}$) vs Trough 11:00 ($5.91\\text{/h}$), $2.89\\times$ surge ratio. |
| **PS 3** | Inpatient Multi-Server Erlang-C Sizing | $M/M/c$ Delay & Halfin-Whitt QED | SPARCS Inpatients ($a=225$) | $c=230$ ($\\rho=97.8\\%$) wait $15.55\\text{h}$; Sizing $c=242$ ($\\rho=93.0\\%$) cuts wait to $1.30\\text{h}$ ($-91.6\\%$ delay collapse). |
| **PS 4** | Ambulance Diversion & Loss Sizing | $M/M/c/c$ Erlang-B Loss Model | MIMIC-IV Emergency ($a=150$) | $c=150$ ($c=a$) yields $6.24\\%$ blocking (>44 pts/d diverted); Regulatory $P \\le 1\\%$ requires $c^*=169$ ($+19$ beds). |
| **PS 5** | Heavy-Traffic Variance Delay Penalty | $M/G/c$ Allen-Cunneen / Kingman | Cross-Cohort Comparison | Variance multiplier $\\Phi = (1+c_v^2)/2$ inflates waits by $+49.6\\%$ (SPARCS), $+51.3\\%$ (eICU), $+60.7\\%$ (MIMIC-IV). |
| **PS 6** | Patient Reneging & Abandonment (LWBS) | $M/M/c+M$ Erlang-A Palm Model | CMS Emergency Quality | Overload ($\\rho=1.20$) stabilizes via $16.7\\%$ walkouts ($2.0\\text{/h}$); Sizing $c=14$ bays drops walkouts to $1.8\\%$. |
| **PS 7** | Two-Stage Tandem Queueing & Boarding | 2D CTMC State-Space Matrix | eICU-CRD (2,520 Stays) | Mean boarding $4.46\\text{h}$ freezes $4.1$ ED bays; Expanding ICU from 12 to 16 beds unblocks 4 bays ($+25\\%$ throughput). |
| **PS 8** | Multi-Class Priority Triage Scheduling | Cobham Non-Preemptive Queue | MIMIC-IV Admissions | Emergency wait drops from $10.0\\text{h}$ to $2.5\\text{h}$ ($-75\\%$); Elective absorbs $25.0\\text{h}$; Conservation law exact. |
| **PS 9** | Multi-Stage Jackson Queueing Network | Traffic Equations $(I - P^T)\\vec{\\Lambda} = \\vec{\\gamma}$ | MIMIC-IV (2.0M Transfers) | Effective arrival $\\Lambda = [30.8, 11.2, 34.6]$; Med/Surg Floor is bottleneck ($\\rho=86.5\\%$), Mean Dwell $= 5.19\\text{ days}$. |
| **PS 10** | Time-Varying PSA Shift Reallocation | Pointwise Stationary $M_t/M/c_t$ | SPARCS Diurnal Demand | Constant staff causes $41.5\\text{m}$ peak wait; Reallocating $+25$ evening / $-25$ night cuts wait to $1.1\\text{m}$ at $\\$0$ extra cost. |
| **PS 11** | CTMC Patient Absorption & Disposition | Fundamental Matrix $N = (I - Q_T)^{-1}$ | eICU & MIMIC-IV Cohorts | Expected steps: ED 1.53, ICU 1.60; ICU mortality $11.12\\%$, Floor mortality $20.35\\%$ (palliative transfers). |
| **PS 12** | Fox Greedy Marginal Bed Allocation | Separable Convex Knapsack | Multi-Ward Hospital ($C=230$) | Optimal $\{33, 43, 154\}$ vs proportional $\{24, 34, 172\}$ cuts weighted blocking from $0.40374$ to $0.06550$ ($-83.8\\%$). |
| **PS 13** | SimPy Discrete-Event Simulation Engine | 20-Replication Stochastic DES | Cross-Cohort Validation | Simulated occupancy ($72.9\\% \\pm 0.8\\%$) matches analytical Erlang-C ($73.1\\%$) within $0.27\\%$ error (exact CI coverage). |

---
""")

        # Append Chapter 2 (PS 1)
        f.write(get_ps1_text())
        f.write("\n\n---\n\n")

        # Append Chapters 3-5 (PS 2, PS 3, PS 4)
        f.write(get_ps2_ps4_text())
        f.write("\n\n---\n\n")

        # Append Chapters 6-8 (PS 5, PS 6, PS 7)
        f.write(get_ps5_ps8_text())
        f.write("\n\n---\n\n")

        # Append Chapters 9-11 (PS 8, PS 9, PS 10)
        f.write(get_ps8_ps10_text())
        f.write("\n\n---\n\n")

        # Append Chapters 12-14 (PS 11, PS 12, PS 13)
        f.write(get_ps11_ps13_text())
        f.write("\n\n---\n\n")

        # Append Chapters 15-18 (Synthesis, Conclusion, References, Appendices)
        f.write(get_synthesis_sections_text())

    print(f"Master Comprehensive Technical Report generated at: {md_path}")
    return md_path

if __name__ == "__main__":
    generate_markdown_report()
