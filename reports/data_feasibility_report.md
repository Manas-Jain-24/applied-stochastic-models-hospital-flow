# Data Feasibility & Methodological Decision Report
**Course:** Applied Stochastic Models (ASM)  
**Project:** Data-Driven Stochastic Modeling and Simulation of Hospital Patient Flow, Congestion, and Resource Planning  
**Target Submission / Milestone:** Alignment with Course Project Rubric (10–12 Page Report & 15-Minute Presentation)

---

## 1. Real-World Operational Problem Options

Hospitals worldwide operate under high uncertainty in patient arrivals, clinical care times, and downstream discharge bottlenecks. We evaluated three specific operational problems:

1. **Inpatient Bed Sizing & Congestion Management (Selected Primary Problem):**
   * *Problem:* How many inpatient beds ($c$) does a hospital or clinical department need to maintain bed blockage probability below a critical threshold (e.g., $P_{\text{block}} \le 1\%$ or delay $P_Q \le 5\%$) given stochastic emergency arrivals and high-variance length of stay (LOS)?
   * *Randomness:* Unpredictable arrival timing (Poisson/NHPP) and heavy-tailed, non-exponential recovery times ($c_v^2 > 1$).
   * *Relevance:* Avoids emergency department boarding, ambulance diversion, and delayed admissions.

2. **Emergency Department (ED) Triage & Waiting Times (Contingent on MIMIC):**
   * *Problem:* Estimating patient waiting times from triage to physician assignment under non-preemptive priority queueing.
   * *Constraint:* Requires sub-hourly or minute-level timestamp data (`intime`, `outtime`). Feasible if MIMIC-IV-ED access is approved, but infeasible on daily aggregate datasets.

3. **Multi-State Post-Acute Patient Routing (Downstream Bottlenecks):**
   * *Problem:* Modeling the transition of hospitalized patients across care units into absorbing post-discharge states (Home, Skilled Nursing Facility, Inpatient Rehab, Hospice, Expired).
   * *Randomness:* Transition probabilities conditional on admission severity and diagnosis.

---

## 2. Data Candidates & Access Status

| Candidate | Official Source | Immediate Access? | Primary Entities Tracked |
| :--- | :--- | :---: | :--- |
| **MIMIC-IV / MIMIC-IV-ED** | PhysioNet ([link](https://physionet.org/content/mimiciv/)) | **No (Pending)** | Minute-level ED stays, ICU transfers, inpatient admissions |
| **NYS SPARCS 2009 Inpatient** | NYS Health Data ([link](https://health.data.ny.gov/)) | **Yes (Local)** | Individual patient encounter records with discrete LOS and disposition |
| **India HMIS (MoHFW)** | National Health Mission ([link](https://hmis.mohfw.gov.in/)) | **Yes (Portal)** | Facility-level monthly aggregated counts (OPD, IPD, bed census) |
| **OECD Health Statistics** | OECD.Stat ([link](https://stats.oecd.org/)) | **Yes (Local)** | Country-level annual hospital averages, wait times, bed supply |

---

## 3. Data Feasibility Comparison & Scoring

Scoring was conducted across six dimensions (1 = Unfavorable, 5 = Excellent):

| Dataset | Relevance | Time Res. | Obs. Count | ASM Fit | Access Ease | Repro. | Total Score | Recommendation |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **NYS SPARCS (Local)** | 4 | 3 | 5 | 4 | 5 | 5 | **26 / 30** | **Primary Anchor (Proceed immediately)** |
| **MIMIC-IV / ED** | 5 | 5 | 5 | 5 | 1 | 2 | **23 / 30** | **Plug-in Upgrade (If DUA clears)** |
| **India HMIS** | 3 | 2 | 4 | 2 | 4 | 4 | **19 / 30** | Secondary macro/context |
| **OECD Health** | 2 | 1 | 3 | 2 | 5 | 5 | **18 / 30** | International benchmark |

### Scoring Rationale:
* **NYS SPARCS** scored highest (26/30) because it is already completely available in the project workspace, de-identified, unencumbered by credentials, and provides over 2.3 million encounter records with actual Length of Stay (service duration), admission types (Emergency, Urgent, Elective), clinical departments, and final patient dispositions.
* **MIMIC-IV** is theoretically superior in time resolution (minute-level timestamps), but its strict credentialing, CITI verification, and human review timeline (often 1–3 weeks) present a severe single-point-of-failure risk if relied upon exclusively.

---

## 4. Methodological Strategy: Dual-Track Architecture

To guarantee the project succeeds regardless of when PhysioNet credentials arrive:

1. **Immediate Execution Track (NYS SPARCS + Safe Synthetic Pipeline):**
   * Calibrate empirical service time distributions ($S$) and daily arrival rates ($\lambda$) using the NYS SPARCS dataset.
   * Generate explicitly marked synthetic sub-daily timestamps to validate micro-queueing behaviors ($M/M/c$ vs. $M/G/c$).
2. **Conditional MIMIC Plug-in Track:**
   * Design all data loaders and mathematical engines using a modular `schema_mapping.yaml`.
   * If PhysioNet approves access, swap the input schema without rewriting any stochastic queueing, simulation, or validation code.

---

## 5. Minimum Required Variables for Feasible ASM Methods

| Stochastic Method | Minimum Required Variables | Available in SPARCS? | Available in MIMIC? |
| :--- | :--- | :---: | :---: |
| **Arrival Process (Poisson / NHPP)** | Date/Time of admission or daily encounter counts | Yes (Date/counts) | Yes (Minute timestamps) |
| **Service Duration Distribution ($S$)** | Length of stay (duration in days or hours) | Yes (`Length of Stay`) | Yes (`intime`, `outtime`) |
| **Multi-Class Queueing ($M/M/c$, $M/G/c$)** | Arrival rate $\lambda$, service rate $\mu$, bed capacity $c$ | Yes (Calibrated) | Yes (Observed) |
| **Absorbing Markov Chain** | Categorical patient disposition / destination state | Yes (`Patient Disposition`) | Yes (`disposition`) |
| **Priority Queueing** | Triage category or admission urgency type | Yes (`Type of Admission`) | Yes (`acuity`, `admission_type`) |

---

## 6. Appropriate ASM Models & Mathematical Formulations

### A. Service Time Distribution (Length of Stay $S$)
* **Hypothesis:** Hospital recovery times violate the memoryless exponential assumption:
  $$c_v^2 = \frac{\text{Var}(S)}{(E[S])^2} \neq 1$$
* **Candidate Distributions:** Exponential ($\text{Exp}(\mu)$), Gamma ($\alpha, \beta$), Lognormal ($\mu, \sigma$), Weibull ($k, \lambda$), and Hyperexponential (Phase-Type).
* **Validation:** Kolmogorov-Smirnov (K-S) test, Anderson-Darling test, and AIC/BIC model ranking.

### B. Queueing Models for Bed Capacity
* **$M/M/c$ Erlang-C Delay Model:**
  $$P_Q = C(c, \rho) = \frac{\frac{(c\rho)^c}{c!} \frac{1}{1-\rho}}{\sum_{k=0}^{c-1} \frac{(c\rho)^k}{k!} + \frac{(c\rho)^c}{c!} \frac{1}{1-\rho}}, \quad \rho = \frac{\lambda}{c\mu} < 1$$
  Expected waiting time in queue:
  $$W_q = \frac{P_Q}{c\mu(1-\rho)}$$
* **$M/M/c/c$ Erlang-B Loss Model:**
  $$P_{\text{block}} = B(c, a) = \frac{\frac{a^c}{c!}}{\sum_{k=0}^c \frac{a^k}{k!}}, \quad a = \frac{\lambda}{\mu}$$
  Determines minimum bed count $c^*$ ensuring $P_{\text{block}} \le \alpha$.
* **$M/G/c$ Heavy-Tailed Generalization (Allen-Cunneen / Kingman):**
  $$W_q(M/G/c) \approx \left(\frac{c_a^2 + c_v^2}{2}\right) W_q(M/M/c)$$
  Directly quantifies the operational penalty caused by medical complications and high-variance stays ($c_v^2 > 1$).

### C. Absorbing Markov Chain for Patient Discharge Flow
* **States:** Transient states (Medical Ward, Surgical Ward, ICU) and Absorbing states (Home/Self-Care, Skilled Nursing Facility, Inpatient Rehab, Hospice, Expired).
* **Canonical Form:**
  $$P = \begin{pmatrix} Q & R \\ 0 & I \end{pmatrix}$$
* **Fundamental Matrix:**
  $$N = (I - Q)^{-1}$$
  Yields the expected duration before discharge and the absorption probability matrix $B = N R$.

---

## 7. Concrete Next Steps
1. Initialize clean modular Python repository structure (`configs/`, `src/`, `tests/`, `notebooks/`).
2. Build `src/synthetic_generator.py` to create benchmark testbeds for unit tests.
3. Implement `src/queueing.py` (Erlang-B, Erlang-C, Allen-Cunneen $M/G/c$) with automated `pytest` verification.
4. Extract empirical parameters from NYS SPARCS 2009 into `data/processed/sparks_summary.csv`.
