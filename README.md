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
├── .gitignore               # Excludes large CSV files, virtualenvs, and temp files
├── README.md                # Project documentation and guide
├── requirements.txt         # Core scientific Python packages
├── data/
│   ├── raw/                 # Local directory for raw SPARCS CSV datasets (git-ignored)
│   └── processed/           # Processed summary tables & calibrated parameters
├── notebooks/               # Jupyter Notebooks for analysis, figures, and models
├── src/                     # Reusable Python modules
│   ├── __init__.py
│   ├── distribution_fit.py  # Fitting and testing LOS distributions
│   ├── queueing_models.py   # Analytical Erlang-B, Erlang-C, M/G/c solvers
│   ├── simulation.py        # Discrete-event hospital simulator
│   └── markov_chain.py      # Absorbing Markov chain for patient disposition
└── reports/                 # Project reports, figures, and presentation materials
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

#### 2. Data Note
The raw SPARCS and OECD datasets are large (>2.5 GB total) and are excluded from Git version control via `.gitignore`. Store the CSV files in your workspace root or the `data/raw/` directory.

---

### Collaboration Guide
1. Create a remote repository on [GitHub](https://github.com).
2. Link this local repository and push:
   ```bash
   git remote add origin <REMOTE_REPO_URL>
   git branch -M main
   git push -u origin main
   ```
3. Your teammate can clone the repository:
   ```bash
   git clone <REMOTE_REPO_URL>
   ```
