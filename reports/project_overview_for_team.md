# Hey Team! Here's What We've Built So Far 🚀
**Project:** Stochastic Modeling of Hospital Patient Flow, Congestion & Resource Planning  
**Course:** Applied Stochastic Models (ASM)  
**GitHub Repo:** https://github.com/Manas-Jain-24/applied-stochastic-models-hospital-flow

---

## 💡 The Quick 2-Minute TL;DR

We are modeling **hospital bed shortages, emergency crowding, and patient wait times** using stochastic processes and queueing theory. 

Instead of waiting weeks for the restricted MIMIC dataset to get approved, we calibrated our models using **250,000 real hospital records** from the open New York State SPARCS inpatient database (which is already sitting on our machine) + generated clean, realistic synthetic benchmarks to test our code safely.

Everything is implemented in Python, 100% modular, tested with 33 automated unit tests, and fully pushed to our GitHub repo.

---

## 🔍 The 11 Big Questions We Formulated & Solved

### 1. Does the classic textbook exponential assumption hold for hospital stays?
* **Answer: NO.**
* **What we found:** For an exponential distribution (memoryless), the squared coefficient of variation ($c_v^2 = \text{Var}(S) / (E[S])^2$) must equal $1.0$. On our 250,000 real hospital encounters, **$c_v^2 \approx 1.99 \approx 2.0$**.
* **Why it matters:** Hospital recovery times have twice the variance of an exponential model. Under the Allen-Cunneen heavy-tailed formula, this adds a **50% delay penalty**. If a hospital uses textbook $M/M/c$ models, they underestimate patient waiting times by half!

### 2. How many beds does a hospital actually need?
* **Answer: $c^* = 301$ beds.**
* **What we found:** For an average daily demand of $269.3$ occupied beds, you cannot just build 270 beds. Using the **Erlang-B loss formula**, keeping patient diversion below $1\%$ requires at least **301 beds** (a safety buffer of ~32 beds to absorb stochastic arrival spikes).

### 3. How much does Emergency vs. Elective triage help?
* **Answer: It cuts emergency wait times by 8x without buying more beds.**
* **What we found:** Using 2-class non-preemptive priority queueing at 295 beds:
  * **Emergency arrivals wait only ~1.5 hours** before getting a bed.
  * **Elective/scheduled patients wait ~12.3 hours** (absorbing the queue delay safely).

### 4. Are arrivals a steady Poisson process, or do they cluster?
* **Answer: Highly clustered throughout the day.**
* **What we found:** We ran the **Index of Dispersion for Counts (IDC)** test. Daily arrivals are overdispersed ($IDC > 1.25$). Arrivals peak at **2:00 PM (14:00)** with a 2.3x peak-to-trough ratio compared to 2:00 AM. We implemented the **Lewis-Shedler thinning algorithm** to simulate this non-homogeneous Poisson process (NHPP).

### 5. What happens if emergency room boarding is capped?
* **Answer:** We solved the finite-buffer **$M/M/c/K$ queue**. Expanding the ED boarding buffer from 0 to 20 beds cuts ambulance diversion from **12.4% down to 1.4%**, but increases average boarding delay to 4.2 hours.

### 6. Where do patients go when they leave acute care?
* **Answer:** We built an **Absorbing Markov Chain** ($P = \begin{pmatrix} Q & R \\ 0 & I \end{pmatrix}$). ICU patients make an average of 1.48 ward transfers before discharge, with a 10.1% mortality rate and 12.4% transitioning to long-term nursing homes (SNFs).

### 7. Can the hospital handle a winter flu/COVID surge?
* **Answer: NO, the system collapses.**
* **What we found:** A +20% surge in daily arrivals pushes utilization to **111%** ($\rho = 1.11 > 1.0$). Queue lengths explode to infinity unless non-emergency elective admissions are postponed.

### 8. How do hospital departments interact as a complete network?
* **Answer: We modeled it as an Open Jackson Queueing Network.**
* **What we found:** By solving the traffic equations $(I - P^T) \vec{\Lambda} = \vec{\gamma}$, we tracked patients moving from Emergency $\to$ ICU $\to$ Step-Down $\to$ Med/Surg $\to$ Discharge. Medical/Surgical is the primary bottleneck ($\rho = 92.2\%$), and total hospital-wide dwell time averages **5.19 days** across all interconnected wards.

### 9. Can smart staffing shifts fix afternoon crowding without hiring more staff?
* **Answer: YES, a 97.3% drop in peak delay with ZERO extra bed-hours!**
* **What we found:** Using **Pointwise Stationary Approximation (PSA)**, keeping a constant 425 beds 24/7 causes afternoon wait times to spike to **41.5 minutes**. Shifting 25 beds from quiet night hours (10 PM – 6 AM) to peak afternoon hours (10 AM – 6 PM) slashes peak wait time to **1.1 minutes** under identical total staffing hours!

### 10. How should beds be divided between ICU, Emergency, and Surgery?
* **Answer: Proportional allocation fails; our optimal Fox algorithm saves 85.1% blocking.**
* **What we found:** Allocating beds strictly proportional to demand under-buffers the ICU, causing a 6.7% ICU rejection rate! Our optimal marginal allocation protects the ICU (+15 safety buffer), cutting ICU rejection to 0.14% and reducing total hospital-wide weighted blocking by **85.1%**.

### 11. What about MIMIC data?
* **We downloaded and calibrated the official open-access MIMIC-IV Clinical Demo & MIMIC-IV-ED Demo from PhysioNet!**
* It has 275 clinical encounters, ward transfer routing, ICU stays, and emergency triage acuity (ESI 1–5).
* Our new module `src/mimic_adapter.py` calibrated the parameters into `data/processed/mimic_empirical_parameters.json`. When our full credentialed MIMIC database arrives, our adapter will process it instantly with zero code changes!

---

## 🛠️ Codebase Structure (What's in the Repo)

```text
├── configs/                  # Settings and field mappings
├── data/
│   ├── raw/                  # Raw datasets (git-ignored)
│   │   ├── sparcs/           # NYS Inpatient 250k discharge CSVs
│   │   ├── mimic_demo/       # Open MIMIC-IV & MIMIC-IV-ED Demo
│   │   ├── nys_health/       # NYS demographics & bed census CSVs
│   │   └── oecd/             # OECD international hospital CSVs
│   ├── processed/            # Empirical parameters (SPARCS & MIMIC JSONs)
│   └── synthetic/            # Simulated benchmark datasets
├── docs/                     # Course assignment PDF & rubrics
├── notebooks/
│   └── 01_stochastic_hospital_flow.ipynb # Complete runnable demo notebook
├── reports/
│   ├── Hospital_Stochastic_Modeling_Project_Report.pdf # Formal ReportLab PDF
│   ├── Hospital_Stochastic_Modeling_Project_Report.md  # Full Markdown report
│   └── figures/              # 9 publication-grade 300 DPI figures
├── scripts/
│   ├── verify_all.py         # Complete 10-step verification suite
│   ├── download_mimic_demo.py# MIMIC demo downloader
│   └── generate_pdf_report.py# PDF report compiler
├── src/                      # Core stochastic modules
│   ├── queueing.py           # Erlang-B, Erlang-C, M/G/c, Priority Queue
│   ├── jackson_network.py    # Multi-stage Jackson queueing network
│   ├── time_varying.py       # PSA diurnal queueing & shift staffing
│   ├── bed_allocation.py     # Fox optimal multi-department bed allocation
│   ├── mimic_adapter.py      # MIMIC-IV & MIMIC-ED ingestion pipeline
│   ├── distributions.py      # MLE fitting & K-S tests
│   ├── arrival_process.py    # Diurnal arrival intensity & thinning
│   ├── markov_chain.py       # Absorbing Markov chains & MFPT
│   ├── simulation.py         # Discrete-event hospital simulator
│   └── visualization.py      # All 9 publication figures
└── tests/                    # 33 unit tests (100% passing in 0.13s)
```

---

## 🏃 How You Can Run It on Your Machine

1. **Clone the repo:**
   ```bash
   git clone https://github.com/Manas-Jain-24/applied-stochastic-models-hospital-flow.git
   cd applied-stochastic-models-hospital-flow
   ```
2. **Run all 33 unit tests and verification steps (takes ~1 second):**
   ```bash
   python scripts/verify_all.py
   ```
3. **Open the Jupyter Notebook:**
   ```bash
   jupyter notebook notebooks/01_stochastic_hospital_flow.ipynb
   ```
4. **Regenerate all 9 figures:**
   ```bash
   python src/visualization.py
   ```

---

## 🎯 Division of Work for the Report & Presentation

Since the code, math solvers, and simulations are already working, here is how we can divide the rest:

* **Teammate 1 (Math & Modeling Section):**
  * Write up the theoretical derivations: Erlang-B recursion, Erlang-C, Allen-Cunneen approximation, Jackson network traffic equations $(I-P^T)\Lambda = \gamma$, Pointwise Stationary Approximation (PSA), and Fox's marginal allocation algorithm.
* **Teammate 2 (Literature Review & Background):**
  * Write the literature review citing Green et al. on healthcare queueing, de Bruin et al. on Erlang models for bed allocation, and Bekker & de Bruin on time-dependent queues.
* **Teammate 3 / Me (Data, Results & Slides):**
  * Format the 9 figures into the final submission document and assemble the 15-minute presentation slide deck using our findings.
