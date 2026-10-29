# Applied Stochastic Modelling (ASM) Course Project: Master Blueprint & Implementation Plan

* Project Theme: Data-Driven Stochastic Modeling and Simulation of Real-World Systems
* Project Title: Hybrid Multi-Scale Queueing & Continuous-Time Markov Network for Hospital Emergency-to-ICU Patient Flow Under Resource Contention
* Domain: Healthcare Operations Research & Applied Stochastic Processes
* Duration: 6 Weeks | Group Size: 2-3 Students
* Workspace Directory: d:\study\college\5th semester\ASM\courseProject

---

## 1. Executive Summary & Pipeline Overview

The project follows the complete end-to-end stochastic engineering pipeline:

```
[Real-World Problem] 
        │
        ▼
[Real Data Ingestion: eICU-CRD v2.0.1 + CMS yv7e-xc69] 
        │
        ▼
[Parametric Probability Distribution Fitting: MLE & AIC/BIC] 
        │
        ▼
[Stochastic Processes: NHPP, Erlang-A Queue, G/G/c2 Blocking, CTMC] 
        │
        ▼
[Mathematical Analysis: Equilibrium Laws & Matrix Exponentials] 
        │
        ▼
[Discrete-Event Simulation (DES): SimPy Tandem Queue Engine] 
        │
        ▼
[Model Validation: Empirical vs. Simulated Sojourn Times] 
        │
        ▼
[Operational Policy Recommendations: ICU Bed Capacity & Boarding Mitigation]
```

### Problem Statement
Emergency Department (ED) crowding and Intensive Care Unit (ICU) boarding represent severe operational failure modes in acute healthcare. When downstream ICU beds (c2) are saturated, critically ill patients are "boarded" inside upstream ED acute treatment bays (c1). 

This blocks ED beds, reducing effective ED service capacity:
```
c1_effective(t) = max(0, c1 - B(t))
```
where B(t) is the count of boarded ICU patients. This causes prolonged waiting times, increased queue lengths, and higher patient abandonment rates (Left Without Being Seen, LWBS).

---

## 2. Mathematical System Specification

```
                                  NETWORK FLOW TOPOLOGY
                                  
   Non-Homogeneous Poisson Process
             lambda(t)
                │
                ▼
      ┌─────────────────────────────────────────────────────────────┐
      │ STAGE 1: Emergency Department (ED)                          │
      │ Capacity: Infinite Queue + c1 Treatment Bays                │
      │ Abandonment: tau ~ Exponential(theta)                       │
      │ Service Duration: S_ED ~ Exponential(mu_ED)                 │
      └─────────────────────────────────────────────────────────────┘
             │                                       │
             │ (1 - p_ICU)                           │ p_ICU
             ▼                                       ▼
      [Discharge / General Floor]             ICU Bed Available?
                                                /           \
                                          YES  /             \  NO
                                              ▼               ▼
                           ┌──────────────────────┐  ┌──────────────────────┐
                           │ STAGE 2: ICU Service │  │ ED Boarding Block    │
                           │ c2 Dedicated Beds    │  │ Patient holds c1     │
                           │ S_ICU ~ Weibull/Gamma│  │ bay until ICU bed    │
                           └──────────────────────┘  │ frees up             │
                                      │              └──────────────────────┘
                                      ▼                         │
                           ┌──────────────────────┐             │
                           │ Multi-Ward CTMC      │◄────────────┘
                           │ SDU, Floor, Home,    │
                           │ Expired (Absorbing)  │
                           └──────────────────────┘
```

### A. Stage 1: Zero-Mismatch Diurnal Arrival Process (NHPP)
Let {N(t), t >= 0} be a Non-Homogeneous Poisson Process with continuous arrival intensity lambda(t).

1. Circadian periodicity condition:
```
lambda(t + 24) = lambda(t)   for all t >= 0
```

2. Hourly discretization over h in {0, 1, 2, ..., 23}:
```
p(h) = n(h) / Sum_{k=0 to 23} n(k),    where Sum_{h=0 to 23} p(h) = 1.0
```
where n(h) is the empirical count of ED patient arrivals at hour h in eICU patient.csv.

3. Scaling with CMS annual arrival volume (N_annual from Measure OP_22):
```
Lambda_day = N_annual / 365

lambda(h) = Lambda_day * p(h)
```

4. Conservation of total daily volume:
```
Integral from 0 to 24 of lambda(t) dt = Sum_{h=0 to 23} lambda(h)
                                      = Lambda_day * Sum_{h=0 to 23} p(h)
                                      = Lambda_day * 1.0
                                      = Lambda_day
```

### B. Stage 1 Queue: Erlang-A ED Model (M_t / M / c1 + M)
Let X(t) be the number of patients present in the ED (queue + treatment).

1. Transition rates:
```
Birth Rate:
  lambda_n = lambda                        for all n >= 0

Death Rate:
  mu_n = n * mu_ED                         if 1 <= n <= c1
  mu_n = c1 * mu_ED + (n - c1) * theta     if n > c1
```

2. Steady-state distribution pi_n:
```
pi_n = pi_0 * ( (lambda / mu_ED)^n / n! )                                         for 0 <= n <= c1

pi_n = pi_0 * ( (lambda / mu_ED)^c1 / c1! ) * Product_{j=1 to n-c1} [ lambda / (c1 * mu_ED + j * theta) ]   for n > c1
```
where pi_0 is calculated such that Sum_{n=0 to infinity} pi_n = 1.

3. Equilibrium invariants:
```
Expected Queue Waiting Time:
  E[W_q] = P_abandon / theta

Total ED Sojourn Time:
  W_ED = E[W_q] + E[S_ED] = (P_abandon / theta) + (1 / mu_ED)
```

4. Calibration from CMS measures:
```
P_abandon = Score_OP_22 / 100
W_ED = Score_OP_18b   (minutes)
1 / mu_ED = W_ED - (P_abandon / theta)
```

### C. Stage 2 Queue: Downstream ICU (G / G / c2 / K) with Boarding Block
1. Routing: A fraction p_ICU in [0.10, 0.15] of treated ED patients transition to the ICU.
2. Parametric service duration models S_ICU:
```
Exponential:
  f(t) = lambda * exp(-lambda * t)
  Hazard rate: h(t) = lambda (Constant)

Weibull:
  f(t) = (c / beta) * (t / beta)^(c - 1) * exp( -(t / beta)^c )
  Hazard rate: h(t) = (c / beta) * (t / beta)^(c - 1)
  (c < 1 indicates decreasing hazard / heavy tail)

Gamma:
  f(t) = [ 1 / (Gamma(alpha) * beta^alpha) ] * t^(alpha - 1) * exp(-t / beta)

Log-Normal:
  f(t) = [ 1 / (t * sigma * sqrt(2 * pi)) ] * exp( -(ln(t) - mu)^2 / (2 * sigma^2) )
```

3. Boarding and blocking coupling:
```
Boarded Patients in ED:
  B(t) = max(0, N_ICU(t) - c2)

Available ED Treatment Beds:
  c1_effective(t) = max(0, c1 - B(t))
```

### D. Multi-Ward Patient Trajectory (Absorbing DTMC & CTMC)
1. State space:
```
S = { 1: ED,  2: ICU,  3: SDU,  4: Floor,  5: Home (Absorbing),  6: Expired (Absorbing) }

Transient States: S_T = { ED, ICU, SDU, Floor }
Absorbing States:  S_A = { Home, Expired }
```

2. Canonical form transition matrix P:
```
     [ Q_T  |  R  ]
P =  [──────┼─────]
     [  0   |  I  ]
```
where Q_T is 4x4, R is 4x2, I is 2x2, and 0 is 2x4.

3. Absorption properties:
```
Fundamental Matrix:
  N = (I - Q_T)^(-1) = I + Q_T + Q_T^2 + ...
  (N_ij = expected number of visits to transient ward j starting from ward i)

Expected Steps to Absorption:
  t = N * [1, 1, 1, 1]^T

Absorption Probabilities:
  B = N * R
  (B_i,Home = survival probability; B_i,Expired = mortality probability)
```

4. Continuous-Time Markov Chain (CTMC):
```
Infinitesimal Generator Q = [q_ij]:
  q_ii = -1 / E[S_i]      (where E[S_i] is mean holding time in ward i)
  q_ij = -q_ii * P_ij     (for j != i)

Transient State Distribution:
  P(t) = exp(Q * t) = Sum_{k=0 to infinity} [ (Q * t)^k / k! ]
```

---

## 3. Six-Week Milestone Execution Plan

```
+──────┬───────────────────────────────┬───────────────────────────────────────────┬──────────────────────+
| Week | Milestone Objectives          | Key Computational Deliverables            | Group Responsibility |
+──────┼───────────────────────────────┼───────────────────────────────────────────┼──────────────────────+
| Wk 1 | Ingestion & Preprocessing     | 01_eda_and_preprocessing.py               | Student 1 (Lead)     |
|      | - eICU patient & hospital csv | output_tables/01_overall_cohort_overview  | Student 2 (Assist)   |
|      | - CMS timely care benchmarks  | output_tables/01_cms_volume_tiers         |                      |
|      | - Cohort metrics & offsets    | output_plots/01_eda_distributions.png     |                      |
+──────┼───────────────────────────────┼───────────────────────────────────────────┼──────────────────────+
| Wk 2 | NHPP & Service Time Fitting   | 02_nhpp_arrival_and_service_fitting.py    | Student 2 (Lead)     |
|      | - Diurnal hourly curves p(h)  | output_tables/02_nhpp_diurnal_hourly_rate | Student 3 (Assist)   |
|      | - MLE distribution fitting    | output_tables/02_icu_los_distribution_fit |                      |
|      | - AIC/BIC & KS tests          | output_plots/02_nhpp_diurnal_arrival_rate |                      |
|      | - Q-Q & CDF diagnostic plots  | output_plots/02_icu_los_fitting_diag.png  |                      |
+──────┼───────────────────────────────┼───────────────────────────────────────────┼──────────────────────+
| Wk 3 | Markov Chain Routing Network  | 03_markov_chain_analysis.py               | Student 3 (Lead)     |
|      | - Transition matrix P & Q     | output_tables/03_dtmc_transition_matrix   | Student 1 (Assist)   |
|      | - Fundamental matrix N        | output_tables/03_absorption_probabilities |                      |
|      | - Absorption matrix B = N * R | output_plots/03_markov_transition_heat.png|                      |
|      | - Trajectories P(t)=exp(Q*t)  | output_plots/03_state_trajectories.png    |                      |
+──────┼───────────────────────────────┼───────────────────────────────────────────┼──────────────────────+
| Wk 4 | Discrete-Event Simulation     | 04_tandem_queue_simulation.py             | Student 1 & 2 (Joint)|
|      | - SimPy / Python DES engine   | output_tables/04_sim_capacity_metrics     | Student 3 (Assist)   |
|      | - 30 days horizon, 5d warmup  | output_plots/04_icu_capacity_sens.png     |                      |
|      | - Sensitivity across c2 in    | output_plots/04_ed_wait_vs_boarding.png   |                      |
|      |   {8, 10, 12, 14, 16, 20}     |                                           |                      |
+──────┼───────────────────────────────┼───────────────────────────────────────────┼──────────────────────+
| Wk 5 | Validation & Counterfactuals  | 05_model_validation_and_policy.py         | Full Group           |
|      | - Empirical vs. simulated LOS | output_tables/05_validation_metrics       |                      |
|      | - Hypothesis testing (KS/Chi) | output_plots/05_empirical_vs_simulated    |                      |
|      | - Policy: Virtual Step-Down   | Formal Report Draft (Sections 1 to 10)    |                      |
+──────┼───────────────────────────────┼───────────────────────────────────────────┼──────────────────────+
| Wk 6 | Report & Presentation Prep    | ASM_Course_Project_Report.pdf (12 pages)  | Full Group           |
|      | - 10-12 page formal report    | Presentation Slide Deck (11 slides)       |                      |
|      | - Code appendix & references  | 15-minute rehearsal & Q&A preparation     |                      |
+──────┴───────────────────────────────┴───────────────────────────────────────────┴──────────────────────+
```

---

## 4. Final Deliverables: Report & Presentation Structure

### 10-12 Page Final Report Structure
1. **Title & Abstract:** Operational motivation, stochastic formulation, dataset summary, primary policy insights.
2. **Introduction:** Hospital overcrowding, clinical risk of ED boarding, and queueing bottlenecks.
3. **Problem Statement:** Resource contention in tandem acute care systems and key research questions.
4. **Literature Review:** Classical Erlang queueing, Erlang-A with abandonment, non-exponential service distributions, and absorbing Markov chains in healthcare.
5. **Data Description:** 
   - Micro Patient-Level Data: eICU-CRD v2.0.1 (2,520 stays, admission/discharge offsets, routing).
   - Macro Facility-Level Data: CMS Hospital Care (Measure OP_22 annual arrivals and abandonment; Measure OP_18b median stay; EDV volume tiers).
6. **Mathematical Background:** Poisson processes, renewal theory, phase-type distributions, and continuous-time generator algebra.
7. **Stochastic Model Formulation:**
   - NHPP diurnal arrival intensity lambda(t).
   - Erlang-A ED queue with abandonment (M_t / M / c1 + M).
   - Downstream G / G / c2 queue with boarding block.
   - Absorbing DTMC and CTMC patient pathway network.
8. **Methodology:** Parameter estimation (MLE), Kolmogorov-Smirnov goodness-of-fit, information criteria (AIC/BIC), and matrix exponentiation.
9. **Computational Implementation:** Modular Python scripts, random number generators, thinning algorithm, and discrete-event simulation architecture.
10. **Simulation Results:** Queue length trajectories, server utilization, boarding delays, and abandonment across arrival loads.
11. **Real Data Results:** Empirical transition probabilities, mortality rates, diurnal arrival distributions, and fitted distribution parameters.
12. **Model Validation:** Goodness-of-fit comparison between empirical data and simulated sample paths.
13. **Discussion:** Capacity tipping points (critical c2 bed threshold where upstream ED abandonment escalates non-linearly).
14. **Limitations:** Truncated demo cohort, lack of ED nurse staffing data, and right-censoring of transfers.
15. **Conclusion & Policy Recommendations:** Optimal bed-allocation policies, dedicated step-down buffer beds, and proactive ED discharge planning.
16. **References:** Standard academic citations in Operations Research, Stochastic Modelling, and Medical Informatics.
17. **Appendix - Reproducible Code:** Complete code listings for scripts 01 through 04.

### 15-Minute Final Presentation Timing Breakdown
* **0:00 - 1:00 (1 min):** Slide 1 - Introduction, Real-World Problem & Clinical Motivation
* **1:00 - 2:00 (1 min):** Slide 2 - Real Datasets (eICU Micro + CMS Macro Benchmarks)
* **2:00 - 4:00 (2 min):** Slide 3 & 4 - Mathematical Formulation (NHPP, Erlang-A ED, Heavy-Tailed ICU LOS)
* **4:00 - 6:00 (2 min):** Slide 5 & 6 - Computational Methodology & Discrete-Event Simulation Architecture
* **6:00 - 9:00 (3 min):** Slide 7 & 8 - Simulation Results & Markov Absorption Analysis
* **9:00 - 10:00 (1 min):** Slide 9 - Operational Interpretation & Capacity Tipping Points
* **10:00 - 11:00 (1 min):** Slide 10 - Model Limitations, Assumptions & Future Extensions
* **11:00 - 12:00 (1 min):** Slide 11 - Individual Team Member Contributions
* **12:00 - 15:00 (3-4 min):** Interactive Q&A & Live Demonstration of Code Output
