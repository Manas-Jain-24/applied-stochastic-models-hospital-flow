# Hey Team! Here's What We've Built So Far 🚀
**Project:** Stochastic Modeling of Hospital Patient Flow, Congestion & Resource Planning  
**Course:** Applied Stochastic Models (ASM)  
**GitHub Repo:** https://github.com/Manas-Jain-24/applied-stochastic-models-hospital-flow

---

## 💡 The Quick 2-Minute TL;DR

We are modeling **hospital bed shortages, emergency crowding, and patient wait times** using stochastic processes and queueing theory. 

Instead of waiting weeks for the restricted MIMIC dataset to get approved, we calibrated our models using **250,000 real hospital records** from the open New York State SPARCS inpatient database (which is already sitting on our machine) + generated clean, realistic synthetic benchmarks to test our code safely.

Everything is implemented in Python, 100% modular, tested with 24 automated unit tests, and fully pushed to our GitHub repo.

---

## 🔍 The 7 Big Questions We Formulated & Solved

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

---

## 🛠️ Codebase Structure (What's in the Repo)

```text
├── configs/                  # Settings and field mappings
├── data/
│   ├── processed/            # 250k real SPARCS parameters (lambda, mu, cv^2)
│   └── synthetic/            # Simulated benchmark datasets
├── notebooks/
│   └── 01_stochastic_hospital_flow.ipynb   # Complete runnable demo notebook
├── reports/
│   ├── figures/              # 6 publication-ready 300 DPI figures
│   │   ├── fig1_los_distributions.png
│   │   ├── fig2_erlang_capacity_curves.png
│   │   ├── fig3_heavy_tail_delay_penalty.png
│   │   ├── fig4_diurnal_arrival_intensity.png
│   │   ├── fig5_markov_transition_heatmap.png
│   │   └── fig6_finite_buffer_tradeoff.png
│   └── data_feasibility_report.md
├── src/
│   ├── arrival_process.py    # IDC test, diurnal fitting, Lewis-Shedler thinning
│   ├── data_validation.py    # Schema & timestamp sanity checks
│   ├── distributions.py      # MLE fitting, K-S test, AIC/BIC
│   ├── markov_chain.py       # Canonical P=[Q R; 0 I], N=(I-Q)^-1, B=NR, MFPT
│   ├── queueing.py           # Erlang-B, Erlang-C, M/G/c, M/M/c/K, Priority
│   ├── simulation.py         # Fast discrete-event simulator (heapq)
│   ├── synthetic_generator.py# Generates [SYNTHETIC] benchmark data
│   └── visualization.py      # Generates all 6 figures automatically
└── tests/                    # 24 unit tests (100% passing in 0.07s)
```

---

## 🏃 How You Can Run It on Your Machine

1. **Clone the repo:**
   ```bash
   git clone https://github.com/Manas-Jain-24/applied-stochastic-models-hospital-flow.git
   cd applied-stochastic-models-hospital-flow
   ```
2. **Run all 24 unit tests (takes < 1 second):**
   ```bash
   python -m unittest discover -s tests -p "test_*.py" -v
   ```
3. **Open the Jupyter Notebook:**
   ```bash
   jupyter notebook notebooks/01_stochastic_hospital_flow.ipynb
   ```
   *(Or just open it in VS Code / PyCharm / Google Colab)*.
4. **Regenerate all figures:**
   ```bash
   python -m src.visualization
   ```

---

## 🎯 Division of Work for the Report & Presentation

Since the code, math solvers, and simulations are already working, here is how we can divide the rest:

* **Teammate 1 (Math & Modeling Section):**
  * Write up the theoretical derivations in Section 6 of the report: Erlang-B recursion, Erlang-C formula, Allen-Cunneen approximation, and the Markov fundamental matrix $N = (I-Q)^{-1}$. (All equations and numerical checks are already in `src/queueing.py` and `notebooks/01_stochastic_hospital_flow.ipynb`).
* **Teammate 2 (Literature Review & Background):**
  * Write the 1.5-page literature review on hospital queueing (citing Green et al. on healthcare queueing, de Bruin et al. on Erlang models for bed allocation).
* **Teammate 3 / Me (Data, Results & Slides):**
  * Format the 6 figures into the final 10–12 page report and prepare the 15-minute presentation slide deck using our findings.
