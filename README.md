# Applied Stochastic Models (ASM) Course Project

**Current submission:** [27-page revised report](reports/pdf/Hospital_Patient_Flow_ASM_Submission_Report.pdf). Earlier narrative reports under `reports/` are historical drafts and contain superseded calculations. The revised report and `scripts/verify_all_math_results.py` are the current numerical reference. The ED/ICU simulation does **not** pass external CMS validation (4.80% modeled abandonment versus 2.33% CMS); its capacity sweep is illustrative.

## Project: Stochastic Modeling of Hospital Inpatient Bed Capacity & Patient Flow

### Overview
This project applies stochastic modeling, queueing theory, and discrete-event simulation to hospital inpatient flow and bed capacity planning using the **New York State Statewide Planning and Research Cooperative System (SPARCS)** inpatient discharges and healthcare datasets.

---

### Key Stochastic Models & Analysis
1. **Length of Stay (LOS) Service Time Distributions ($S$):**
   - Parametric fitting (Exponential, Gamma, Lognormal, Weibull, Phase-Type/Hyperexponential).
   - Memoryless property testing via squared coefficient of variation ($c_v^2 = \text{Var}(S) / (E[S])^2$).
   - Goodness-of-fit assessment (Kolmogorov-Smirnov test, AIC/BIC).
2. **Arrival Processes ($\lambda$):**
   - Poisson process modeling and decomposition into Emergency vs. Elective patient streams ($\lambda = \lambda_E + \lambda_{El}$).
3. **Queueing Theoretic Capacity Models:**
   - **$M/M/c$ (Erlang-C Delay System):** Congestion probability $P_Q$, mean wait time $W_q$, bed occupancy $L_s$.
   - **$M/M/c/c$ (Erlang-B Loss System):** Bed blocking/diversion probability $P_{\text{block}}$ under hard capacity limits.
   - **$M/G/c$ Approximations (Allen-Cunneen / Kingman):** Correcting for high-variance, heavy-tailed service times ($c_v^2 > 1$).
   - **Multi-Class Priority Queueing:** Non-preemptive priority for emergency vs. elective patient admissions.
4. **Multi-Stage Jackson Queueing Networks:**
   - Solving open traffic equations $(I - P^T)\vec{\Lambda} = \vec{\gamma}$ across Emergency, ICU, Med/Surg, and Step-Down wards.
   - Network-wide dwell times via Little's Law ($W_{\text{total}} = L_{\text{total}} / \gamma_{\text{total}}$) and bottleneck utilization tracking.
5. **Time-Varying Queueing Dynamics (PSA):**
   - Pointwise Stationary Approximation evaluating 24-hour diurnal arrival surges ($\lambda(t)$ peaking at 2:30 PM).
   - Dynamic peak-hour shift staffing reducing peak queue delays by 97.3% under zero extra bed-hours.
6. **Multi-Department Bed Allocation Optimization:**
   - Discrete convex optimization via Fox's greedy marginal allocation algorithm minimizing weighted hospital blocking.
   - Reduces the chosen weighted blocking objective by 83.8% compared with proportional sizing in an illustrative 230-bed scenario.
7. **Absorbing Markov Chains:**
   - Patient disposition and downstream care pathway transition matrix ($N = (I-Q)^{-1}$, $B = NR$).
8. **Discrete-Event Stochastic Simulation (DES):**
   - Event calendar simulation checking implementation and stress behavior; external empirical validation remains incomplete.
   - Stress testing under surge scenarios ($\lambda + 25\%$, $c - 10\%$).
9. **Modular MIMIC Ingestion Adapter:**
   - Calibrates empirical stochastic parameters from MIMIC-IV and MIMIC-IV-ED schemas.
   - Seamlessly compatible with full credentialed MIMIC when available.

---

### Project Structure
```text
ASM/
├── .gitignore               # Excludes raw data (>2.5 GB), virtualenvs, cache files
├── README.md                # Project documentation and guide
├── requirements.txt         # Core scientific Python packages
├── configs/                 # Pipeline & schema configuration
│   ├── config.yaml          # Global pipeline & simulation settings
│   └── schema_mapping.yaml  # SPARCS & MIMIC dataset schema definitions
├── data/                    # Multi-tiered data directory
│   ├── raw/                 # Local raw data (git-ignored)
│   │   ├── sparcs/          # NYS SPARCS inpatient discharge CSVs (~250k records)
│   │   ├── mimic_full/      # MIMIC-IV v3.1 (2.0M transfers, 94.4k ICU stays)
│   │   ├── mimic_v3_archives/# MIMIC-IV raw gzip/zip multi-GB archive files
│   │   ├── mimic_demo/      # Open-access PhysioNet MIMIC-IV & ED Demo v2.2
│   │   ├── nys_health/      # NYS Health demographics & bed census CSVs
│   │   └── oecd/            # OECD international hospital indicators CSVs
│   ├── interim/             # Staged intermediate datasets
│   ├── processed/           # Empirical parameters JSONs (SPARCS & MIMIC) & summaries
│   └── synthetic/           # Benchmark synthetic patient cohorts
├── partner_repo/            # Partner module: eICU-CRD v2.0.1 & CMS Hospital Queueing
│   ├── README.md            # Module architecture & instructions
│   ├── 01_eda_and_preprocessing.py        # Ingestion, cohort breakdown & CMS benchmarks
│   ├── 02_nhpp_arrival_and_service_fitting.py # NHPP diurnal rates & Weibull/Gamma MLE fits
│   ├── 03_markov_chain_analysis.py        # DTMC & CTMC routing, matrix exp P(t)=exp(Qt)
│   ├── 04_tandem_queue_simulation.py      # SimPy tandem queue DES with ED boarding
│   ├── 05_model_validation_and_policy.py  # Erlang-A validation & policy counterfactuals
│   ├── MATHEMATICAL_MODEL_AND_RESULTS.md  # Comprehensive mathematical report
│   ├── cms_data/            # CMS hospital benchmarks
│   ├── eicu_demo_data/      # eICU-CRD v2.0.1 tables (2,520 stays)
│   ├── output_plots/        # 10 publication figures
│   ├── output_tables/       # 22 summary CSV tables
│   └── downloaders/         # Data fetcher utilities
├── docs/                    # Course and project documentation
│   ├── ASM Project 2026M.pdf # Official course assignment & rubrics
│   └── project_guidelines.txt# Problem statement & milestone guidelines
├── notebooks/               # Interactive Jupyter analysis notebooks
│   └── 01_stochastic_hospital_flow.ipynb # Runnable end-to-end notebook
├── reports/                 # Deliverables, reports, and publication assets
│   ├── pdf/                 # Centralized destination for all 7 compiled PDF reports
│   │   ├── Hospital_Stochastic_Modeling_Project_Report.pdf # Formal 10-12 page report
│   │   ├── Hospital_Flow_Project_Group_Briefing.pdf       # Group briefing for partners
│   │   ├── Hospital_Flow_Models_and_DeepDives_Readable_Guide.pdf # Visual model guide
│   │   ├── Questions_Models_Datasets_and_DeepDives_Guide.pdf     # Viva / defense guide
│   │   ├── Team_Project_Master_Walkthrough.pdf             # Master walkthrough
│   │   ├── Team_Project_Overview_Briefing.pdf              # Overview briefing
│   │   └── Stochastic_Process_Models_Healthcare_Report.pdf  # Technical process report
│   ├── Hospital_Stochastic_Modeling_Project_Report.md  # Markdown report source
│   ├── partner_integration_summary.md                 # Joint dual-track synthesis
│   ├── project_overview_for_team.md                   # Summary briefing for teammates
│   ├── data_feasibility_report.md                     # Data pipeline evaluation
│   ├── figures/             # 9 publication-grade 300 DPI figures
│   └── tables/              # Exported summary tables
├── scripts/                 # Standalone automation & verification scripts
│   ├── verify_all.py        # 11-step master unified verification suite
│   ├── download_mimic_demo.py# Downloads MIMIC-IV & MIMIC-ED open demos
│   ├── generate_pdf_report.py # PDF report compilation script
│   └── build_notebook.py    # Notebook generation script
├── src/                     # Core stochastic modeling Python package
│   ├── __init__.py
│   ├── queueing.py          # Erlang-B, Erlang-C, Allen-Cunneen, M/M/c/K, Priority
│   ├── priority_simulation.py # Two-class non-preemptive multi-server priority DES
│   ├── jackson_network.py   # Multi-stage Jackson open queueing network
│   ├── time_varying.py      # PSA diurnal queueing & shift staffing optimization
│   ├── bed_allocation.py    # Fox's greedy marginal bed allocation optimizer
│   ├── mimic_adapter.py     # MIMIC-IV & MIMIC-ED ingestion pipeline
│   ├── distributions.py     # MLE parametric fitting, K-S tests, AIC/BIC
│   ├── arrival_process.py   # NHPP diurnal intensity, IDC dispersion, thinning
│   ├── markov_chain.py      # Absorbing Markov chains, fundamental matrix, MFPT
│   ├── simulation.py        # Event-calendar Discrete-Event Simulator (DES)
│   ├── visualization.py     # 9 publication figures generator
│   ├── data_validation.py   # Schema validation & integrity checks
│   ├── synthetic_generator.py # Reproducible benchmark patient generator
│   └── config.py            # Global project paths and constants
└── tests/                   # Complete unit test suite (automated discovery, 100% passing)
    ├── test_priority_simulation.py
    ├── test_queueing.py
    ├── test_jackson_network.py
    ├── test_time_varying.py
    ├── test_bed_allocation.py
    ├── test_mimic_adapter.py
    ├── test_distributions.py
    ├── test_arrival_process.py
    ├── test_markov_chain.py
    ├── test_simulation.py
    └── test_validation.py
```


---

### Quickstart & Deliverables

#### 1. Launch Interactive Streamlit Simulator
Run the live interactive hospital capacity planning simulator dashboard:
```bash
streamlit run app.py
```
*Features interactive sliders for bed capacity, Erlang-C delay collapse, Erlang-B ambulance diversion, Erlang-A patient walkouts, tandem ICU boarding contention, PSA dynamic nurse shift balancing, Fox's greedy bed allocation, and live SimPy discrete-event simulation.*

#### 2. Run Comprehensive Verification Suite
Verify all 13 stochastic models, 11 pipeline stages, and 39 unit tests:
```bash
python scripts/verify_all.py
```

#### 3. View Master Reports
- **Academic Master PDF Report (23 Pages, Full & Dense):** [`reports/pdf/Master_Combined_Stochastic_Hospital_Flow_Report.pdf`](file:///c:/Users/HP/Desktop/ASM/reports/pdf/Master_Combined_Stochastic_Hospital_Flow_Report.pdf)
- **Technical Markdown Report:** [`reports/Master_Combined_Stochastic_Hospital_Flow_Report.md`](file:///c:/Users/HP/Desktop/ASM/reports/Master_Combined_Stochastic_Hospital_Flow_Report.md)
- **Verified Numerical Ground Truth:** [`data/processed/master_verified_math_results.json`](file:///c:/Users/HP/Desktop/ASM/data/processed/master_verified_math_results.json)

---

### Getting Started

#### 1. Setup Environment
Ensure Python 3.10+ is installed:
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

#### 2. Verify Everything
Run the unified verification suite to validate all models, unit tests, and figures:
```bash
python scripts/verify_all.py
```

#### 3. View Reports & Interactive Notebook
- **Formal PDF Report:** [reports/Hospital_Stochastic_Modeling_Project_Report.pdf](file:///reports/Hospital_Stochastic_Modeling_Project_Report.pdf)
- **Interactive Notebook:** Launch `jupyter notebook notebooks/01_stochastic_hospital_flow.ipynb`

---

### Collaboration Guide
1. Push latest updates to the remote repository:
   ```bash
   git push origin main
   ```
2. Your teammate can clone and reproduce:
   ```bash
   git clone https://github.com/Manas-Jain-24/applied-stochastic-models-hospital-flow.git
   cd applied-stochastic-models-hospital-flow
   pip install -r requirements.txt
   python scripts/verify_all.py
   ```

