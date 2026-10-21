# Deep-Dive Investigative Modules: Advanced Applied Stochastic Hospital Models

## Purpose & Architecture
This directory contains **standalone, specialized deep-dive investigations** that expand upon the foundational models developed in the main repository.

### Key Safeguard: Pristine Baseline Backup
The main project codebase, reports, test suites, and notebooks remain **100% intact, pristine, and untouched**:
* **Main Report PDF:** [`reports/Hospital_Stochastic_Modeling_Project_Report.pdf`](file:///c:/Users/HP/Desktop/ASM/reports/Hospital_Stochastic_Modeling_Project_Report.pdf) (2.38 MB formal publication report)
* **Team Master Briefing:** [`reports/project_overview_for_team.md`](file:///c:/Users/HP/Desktop/ASM/reports/project_overview_for_team.md) (exhaustive 687-line walkthrough of all 11 questions)
* **Unified Verification Suite:** [`scripts/verify_all.py`](file:///c:/Users/HP/Desktop/ASM/scripts/verify_all.py) (33 unit tests, 100% passing)

If your team prefers the broad 11-question narrative for final submission, the main project is fully preserved. If you or your instructor want deep mathematical, empirical, or operational scrutiny into specific core questions, these deep-dive modules provide graduate-level rigor.

---

## The Three Deep-Dive Investigation Tracks

| Track | Title & Primary Scope | Core Questions Expanded | Key Mathematical Models |
| :--- | :--- | :--- | :--- |
| **Track 1** | [**01: Heavy-Tail Service & The $M/G/c$ Delay Penalty**](file:///c:/Users/HP/Desktop/ASM/deep_dives/01_heavy_tail_service_deep_dive.md) | **Q1** (Empirical LOS Fitting & Service Variance) | • Pollaczek-Khinchine & Allen-Cunneen derivations<br>• Hazard rate functions $h(t)$ (Exponential vs Lognormal vs Weibull)<br>• MLE Log-Likelihood derivations & K-S hypothesis tests<br>• Variance sensitivity curve ($c_s^2 \in [0.1, 4.0]$) |
| **Track 2** | [**02: Bed Capacity Sizing & Multi-Class Priority Triage**](file:///c:/Users/HP/Desktop/ASM/deep_dives/02_capacity_and_priority_deep_dive.md) | **Q2, Q3, Q5** (Bed Sizing, Triage & Finite Buffers) | • Erlang-B CTMC birth-death balance equations & recursion proof<br>• Cobham's conservation law of work $\sum \rho_i W_{q,i} = W_0/(1-\rho)$<br>• Log-Sum-Exp $M/M/c/K$ loss vs boarding delay Pareto frontier<br>• Hospital safety buffer dimensioning under stochastic bursts |
| **Track 3** | [**03: Diurnal Arrivals, Dynamic Shift Staffing & Network Allocation**](file:///c:/Users/HP/Desktop/ASM/deep_dives/03_diurnal_staffing_and_network_deep_dive.md) | **Q8, Q9, Q10** (Time-Varying Queues & Optimal Allocation) | • Non-Homogeneous Poisson Process (NHPP) & Lewis-Shedler thinning<br>• Pointwise Stationary Approximation (PSA) & Afternoon lag effect<br>• Open Jackson Network traffic equations $(I - P^T)\vec{\Lambda} = \vec{\gamma}$<br>• Fox's greedy marginal allocation on separable convex Erlang-B loss |

---

## How to Use These Deep Dives in Your Defense / Presentation
1. **Report Submission:** You can include these deep-dive modules as targeted appendices (e.g., Appendix A, B, C) in your final PDF or report.
2. **15-Minute Viva / Presentation:** Spend 3–4 minutes introducing the full hospital patient journey, then dedicate 7–8 minutes presenting one of these deep-dive tracks as your flagship research contribution.
