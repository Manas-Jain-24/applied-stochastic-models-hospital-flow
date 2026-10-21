# Deep-Dive Investigative Modules: Advanced Applied Stochastic Hospital Models

## Purpose & Architecture
This directory contains **specialized, standalone deep-dive investigations** that expand upon the foundational models developed in the main repository.

### Safeguard: Pristine Baseline Backup
The main project codebase, formal reports, test suites, and notebooks remain **100% intact, pristine, and untouched**:
* **Main Report PDF:** [`reports/Hospital_Stochastic_Modeling_Project_Report.pdf`](../reports/Hospital_Stochastic_Modeling_Project_Report.pdf) (formal publication report with all 9 figures)
* **Team Master Briefing:** [`reports/project_overview_for_team.md`](../reports/project_overview_for_team.md) (comprehensive walkthrough of all 11 questions)
* **Unified Verification Suite:** [`scripts/verify_all.py`](../scripts/verify_all.py) (33 unit tests, 100% passing)

If your team presents the full 11-question breadth, the baseline is preserved. If you or your instructor want deep mathematical, empirical, or operational scrutiny into specific core themes, these deep-dive modules provide graduate-level rigor.

---

## The Three Deep-Dive Investigation Tracks

| Track | Title & Primary Scope | Core Questions Expanded | Key Mathematical Models |
| :--- | :--- | :--- | :--- |
| **Track 1** | [**01: Heavy-Tail Service & The $M/G/c$ Delay Penalty**](01_heavy_tail_service_deep_dive.md) | **Q1** (Empirical LOS Fitting & Service Variance) | • Pollaczek-Khinchine derivation & Allen-Cunneen approximation<br>• Hazard rate functions $h(t)$ (Exponential vs Lognormal vs Weibull)<br>• MLE Log-Likelihood & Information Criteria (AIC/BIC)<br>• Service variance sensitivity analysis ($c_s^2 \in [0.1, 3.5]$) |
| **Track 2** | [**02: Bed Capacity Sizing & Multi-Class Priority Triage**](02_capacity_and_priority_deep_dive.md) | **Q2, Q3, Q5** (Bed Sizing, Triage & Finite Buffers) | • Erlang-B CTMC birth-death derivation & stable recursion<br>• Multi-server non-preemptive priority queueing & work conservation<br>• Discrete-event simulation validation against heuristic approximations<br>• $M/M/c/K$ finite-buffer holding vs. ambulance diversion tradeoff |
| **Track 3** | [**03: Diurnal Arrivals, Dynamic Shift Staffing & Network Allocation**](03_diurnal_staffing_and_network_deep_dive.md) | **Q8, Q9, Q10** (Time-Varying Queues & Optimal Allocation) | • Non-Homogeneous Poisson Process (NHPP) & Lewis-Shedler thinning<br>• Pointwise Stationary Approximation (PSA) & shift reallocation<br>• 4-station Open Jackson Network traffic equations $(I - P^T)\vec{\Lambda} = \vec{\gamma}$ & stability analysis<br>• Fox's greedy marginal allocation on separable convex Erlang-B loss |

---

## Verification & Reproducibility
All mathematical claims, tables, and algorithms in these deep dives are validated by an automated test script:
```bash
python deep_dives/verify_deep_dives.py
```
This script validates:
1. $c_s^2 = 1.9915$ and the Allen-Cunneen delay factor ($\approx 1.496$) from Track 1.
2. Erlang-B blocking ($B(269, 269.3) = 0.0478$, $B(293, 269.3) = 0.0091$) and two-class priority queue metrics from Track 2.
3. Traffic equation balance $(I - P^T)\vec{\Lambda} = \vec{\gamma}$, bottleneck utilization ($\rho_4 = 1.2552$), instability detection, and Fox marginal allocation ($C = 230$, ICU = 33 beds) from Track 3.
