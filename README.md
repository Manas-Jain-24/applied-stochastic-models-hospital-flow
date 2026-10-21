# Applied Stochastic Models (ASM) Course Project

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
4. **Absorbing Markov Chains:**
   - Patient disposition and downstream care pathway transition matrix ($N = (I-Q)^{-1}$).
5. **Discrete-Event Stochastic Simulation (DES):**
   - Event calendar simulation validating theoretical queueing equations against stochastic arrival and departure dynamics.
   - Stress testing under surge scenarios ($\lambda + 25\%$, $c - 10\%$).

---

### Project Structure
```text
ASM/
├── .gitignore               # Excludes raw data (>2.5 GB), virtualenvs, cache files
├── README.md                # Project documentation and guide
├── requirements.txt         # Core scientific Python packages
├── configs/                 # Pipeline & schema configuration
│   ├── config.yaml          # Global pipeline & simulation settings
│   └── schema_mapping.yaml  # SPARCS dataset schema definitions
├── data/                    # Multi-tiered data directory
│   ├── raw/                 # Local raw data (git-ignored, >2.5 GB)
│   │   ├── sparcs/          # NYS SPARCS inpatient discharge CSVs
│   │   ├── nys_health/      # NYS Health demographics & bed census CSVs
│   │   └── oecd/            # OECD international hospital indicators CSVs
│   ├── interim/             # Staged intermediate datasets
│   ├── processed/           # Empirical parameters JSON & summary tables
│   └── synthetic/           # Benchmark synthetic patient cohorts
├── docs/                    # Course and project documentation
│   ├── ASM Project 2026M.pdf # Official course assignment & rubrics
│   └── project_guidelines.txt# Problem statement & milestone guidelines
├── notebooks/               # Interactive Jupyter analysis notebooks
│   └── 01_stochastic_hospital_flow.ipynb # Runnable end-to-end notebook
├── reports/                 # Deliverables, reports, and publication assets
│   ├── Hospital_Stochastic_Modeling_Project_Report.pdf # Formal 5-page PDF report
│   ├── Hospital_Stochastic_Modeling_Project_Report.md  # Markdown report source
│   ├── project_overview_for_team.md                   # Summary briefing for teammates
│   ├── data_feasibility_report.md                     # Data pipeline evaluation
│   ├── figures/             # 6 publication-grade 300 DPI figures
│   └── tables/              # Exported summary tables
├── scripts/                 # Standalone automation & verification scripts
│   ├── verify_all.py        # Automated test suite and artifact verification
│   ├── generate_pdf_report.py # PDF report compilation script
│   └── build_notebook.py    # Notebook generation script
├── src/                     # Core stochastic modeling Python package
│   ├── __init__.py
│   ├── queueing.py          # Erlang-B, Erlang-C, Allen-Cunneen, M/M/c/K, Priority
│   ├── distributions.py     # MLE parametric fitting, K-S tests, AIC/BIC
│   ├── arrival_process.py   # NHPP diurnal intensity, IDC dispersion, thinning
│   ├── markov_chain.py      # Absorbing Markov chains, fundamental matrix, MFPT
│   ├── simulation.py        # Event-calendar Discrete-Event Simulator (DES)
│   ├── visualization.py     # 6 publication figures generator
│   ├── data_validation.py   # Schema validation & integrity checks
│   ├── synthetic_generator.py # Reproducible benchmark patient generator
│   └── config.py            # Global project paths and constants
└── tests/                   # Complete unit test suite (24 unit tests)
    ├── test_queueing.py
    ├── test_distributions.py
    ├── test_arrival_process.py
    ├── test_markov_chain.py
    ├── test_simulation.py
    └── test_validation.py
```

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

