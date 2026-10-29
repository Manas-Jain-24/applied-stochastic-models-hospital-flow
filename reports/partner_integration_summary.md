# Unified Multi-Dataset Stochastic Hospital Flow Framework
## Joint Integration Summary: Partner Contributions & Main Modeling Engine

**Course:** Applied Stochastic Models (ASM)  
**Collaborators:** Manas (Main Repository) & Yashasvee (Partner Repository)  
**Partner GitHub Source:** [https://github.com/yshasvee11/ASM-project](https://github.com/yshasvee11/ASM-project)  
**Local Integration Directory:** [`partner_repo/`](file:///c:/Users/HP/Desktop/ASM/partner_repo)  

---

## 1. Executive Summary & Dual-Track Synergy

The complete project harmonizes two complementary, data-driven modeling tracks to analyze acute hospital patient congestion, bed capacity, and multi-ward patient routing:

```text
========================================================================================
                      UNIFIED MULTI-SCALE STOCHASTIC ARCHITECTURE
========================================================================================

TRACK 1: Micro-Scale Tandem Queue & Bed Contention (Partner Track)
  * Data Sources: eICU-CRD Demo v2.0.1 (2,520 ICU stays) + CMS Hospital Care (yv7e-xc69)
  * Stochastic Model: M_t / M / c1 + M (Erlang-A with reneging) -> G / G / c2 / K (ICU)
  * Key Mechanism: Upstream ED Bay Boarding Blocking: c1_effective(t) = max(0, c1 - B(t))
  * Continuous-Time Dynamics: 6-state CTMC with generator matrix Q and P(t) = exp(Qt)
  * Location: partner_repo/ (Scripts 01 to 05, 10 plots, 22 tables)

TRACK 2: Macro-Scale Network Routing, Staffing & Allocation Optimization (Main Track)
  * Data Sources: NYS SPARCS (250,000 discharges) + MIMIC-IV v3.1 (2,004,604 transfers)
  * Stochastic Model: Open Jackson Queueing Network with inter-ward feedback
  * Traffic Equations: (I - P^T) * Lambda = gamma across Emergency, ICU, MedSurg, StepDown
  * Time-Varying Optimization: Pointwise Stationary Approximation (PSA) shift staffing
  * Resource Planning: Fox's discrete convex marginal bed allocation optimizer
  * Location: src/ (queueing, jackson_network, time_varying, bed_allocation, mimic_adapter)
========================================================================================
```

---

## 2. Cross-Dataset Empirical Concordance

Both tracks were calibrated independently on real clinical databases, yielding powerful cross-validation:

| Clinical / Stochastic Metric | Track 1: Partner (eICU-CRD v2.0.1) | Track 2: Main (MIMIC-IV v3.1) | Concordance Verdict |
| :--- | :---: | :---: | :--- |
| **ICU Mean Length of Stay ($E[S]$)** | $58.35\text{ hours}$ ($2.43\text{ days}$) | $87.12\text{ hours}$ ($3.63\text{ days}$) | Consistent acute ICU duration |
| **LOS Coefficient of Variation ($c_v$)** | $1.429$ ($c_v^2 = 2.04$) | $1.488$ ($c_v^2 = 2.21$) | **Consensus: Heavy-tailed ($c_v > 1.0$)** |
| **Best-Fitting Parametric Law** | **Weibull** ($\Delta\text{AIC} = 0.0, D = 0.082$) | **Weibull / Log-Normal** ($D = 0.079$) | **Consensus: Rejects Exponential** |
| **Circadian Arrival Peak** | 2:00 PM – 8:00 PM ($p_{\text{max}} = 0.062$) | 2:12 PM – 3:30 PM ($\lambda_{\text{peak}} = 58.4/\text{day}$) | **Consensus: Diurnal surge** |
| **In-Hospital Mortality Rate** | $8.41\%$ overall | $5.45\%$ in admissions | Concordant acute mortality |

---

## 3. Structural File Organization in the Workspace

The partner's repository is cleanly stored, sorted, and linked inside the workspace root:

```text
c:\Users\HP\Desktop\ASM/
├── partner_repo/                          # Cloned & verified partner repository
│   ├── README.md                          # Dedicated architectural guide for partner work
│   ├── 01_eda_and_preprocessing.py        # Data ingestion & CMS facility benchmarking
│   ├── 02_nhpp_arrival_and_service_fitting.py # NHPP diurnal rates & MLE distribution fitting
│   ├── 03_markov_chain_analysis.py        # DTMC & CTMC routing, fundamental matrix N, exp(Qt)
│   ├── 04_tandem_queue_simulation.py      # SimPy tandem queue DES with ED boarding
│   ├── 05_model_validation_and_policy.py  # Erlang-A validation & policy counterfactuals
│   ├── MATHEMATICAL_MODEL_AND_RESULTS.md  # Comprehensive 369-line mathematical report
│   ├── cms_data/                          # CMS hospital benchmarks (CSV)
│   ├── eicu_demo_data/                    # eICU-CRD tables (7 CSVs)
│   ├── output_plots/                      # 10 generated publication PNG figures
│   └── output_tables/                     # 22 summary CSV tables
├── data/                                  # Primary project datasets
│   ├── raw/
│   │   ├── sparcs/                        # NYS SPARCS 2009 inpatient records
│   │   ├── mimic_full/                    # MIMIC-IV v3.1 (2.0M transfers, 94.4k ICU stays)
│   │   └── mimic_demo/                    # MIMIC-IV open demo
│   └── processed/                         # Calibrated JSON parameters
├── src/                                   # Primary stochastic modeling package
├── tests/                                 # 39 passing unit tests
└── scripts/
    └── verify_all.py                      # 11-step master verification suite
```

---

## 4. Git Integration & Future Collaboration

* **Remote Added:** `partner -> https://github.com/yshasvee11/ASM-project.git`
* **Fetch Partner Updates:** To pull any new changes pushed by your partner at any time:
  ```powershell
  git fetch partner
  ```
* **Unified Verification:** Run all 11 verification steps covering both tracks:
  ```powershell
  python scripts/verify_all.py
  ```
