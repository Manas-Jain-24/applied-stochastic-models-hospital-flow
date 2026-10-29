# Partner Contribution: eICU-CRD & CMS Hospital Queueing Network

**Repository Source:** [https://github.com/yshasvee11/ASM-project](https://github.com/yshasvee11/ASM-project)  
**Authors:** Yashasvee (Partner) & Manas (Main Project Lead)  
**Domain:** Operations Research & Applied Stochastic Modeling  

---

## 1. Overview & Architectural Role in the Project

This module provides the **Tandem Queue & Continuous-Time Markov Chain (CTMC)** track for the hospital patient flow project, calibrated using:
1. **eICU Collaborative Research Database Demo v2.0.1** (2,520 multi-center ICU encounters across 186 hospitals).
2. **CMS Timely and Effective Care (yv7e-xc69)** (annual hospital arrival volumes, wait benchmarks, and left-without-being-seen rates).

Together with the primary project track (**NYS SPARCS 250,000 records** + **MIMIC-IV v3.1 2,004,604 transfers** + **Jackson Networks** + **PSA Time-Varying Staffing**), this forms a comprehensive, multi-dataset stochastic evaluation of acute hospital crowding.

---

## 2. Directory Layout & Pipeline Components

```text
partner_repo/
├── 01_eda_and_preprocessing.py          # Data ingestion, cohort filters & CMS benchmarking
├── 02_nhpp_arrival_and_service_fitting.py# MLE distribution fitting (Weibull/Gamma) & NHPP diurnal rates
├── 03_markov_chain_analysis.py          # DTMC/CTMC routing, generator Q, matrix exponential P(t)=exp(Qt)
├── 04_tandem_queue_simulation.py        # SimPy DES: M_t/M/c1+M -> G/G/c2/K tandem queue with boarding
├── 05_model_validation_and_policy.py    # Erlang-A validation & policy counterfactual experiments
├── MATHEMATICAL_MODEL_AND_RESULTS.md    # Master mathematical formulation & empirical results
├── cms_data/                            # CMS Timely and Effective Care hospital dataset
│   └── cms_timely_and_effective_care_hospital.csv
├── eicu_demo_data/                      # eICU-CRD Demo v2.0.1 tables
│   ├── patient.csv                      # Stays, timestamps, admission offsets
│   ├── hospital.csv                     # Hospital census & region
│   ├── admissionDx.csv                  # Diagnostic records
│   ├── apachePatientResult.csv          # APACHE IV scores & predictions
│   ├── diagnosis.csv                    # Clinical problems
│   ├── treatment.csv                    # Active treatments
│   └── vitalAperiodic.csv               # Non-invasive vitals
├── output_plots/                        # 10 publication figures
└── output_tables/                       # 22 summary CSV tables
```

---

## 3. Core Stochastic Models & Theorems

1. **Zero-Scale-Mismatch NHPP Arrival Process:**
   $$\lambda(h) = \Lambda_{\text{day}} \cdot p_h, \quad \sum_{h=0}^{23} p_h = 1.0$$
   Guarantees exact conservation between patient-level hourly timestamps and annual CMS facility arrival volumes.

2. **Heavy-Tailed ICU Service Time Distribution ($S_{\text{ICU}}$):**
   * Empirical Mean: $58.35\text{ hours}$ ($2.43\text{ days}$)
   * Coefficient of Variation: $c_v = 1.429 > 1.0$ (proves violation of memoryless exponential assumption)
   * Best Parametric Fit: **Weibull** ($c = 0.9126, \beta = 55.57\text{ hrs}$, $\text{AIC} = 25,374$, lowest $D = 0.0822$)

3. **Stage 1: Erlang-A Upstream Queue ($M_t / M / c_1 + M$):**
   * Accommodates patient abandonment / reneging ($\tau \sim \text{Exp}(\theta)$).
   * Transition rate: $\mu_n = c_1 \mu + (n - c_1) \theta$ for $n > c_1$.

4. **Stage 2: Downstream Bed Contention & Boarding ($G / G / c_2 / K$):**
   * When downstream ICU beds ($c_2$) are saturated, patients board in upstream ED bays ($c_1$).
   * Effective ED service capacity: $c_{1,\text{effective}}(t) = \max(0, c_1 - B(t))$.

5. **Stage 3: Absorbing Continuous-Time Markov Chain (CTMC):**
   * Fundamental Matrix: $N = (I - Q_T)^{-1}$
   * Absorption Probability Matrix: $B = N \cdot R$
   * Transient state vector via matrix exponential: $\mathbf{p}(t) = \mathbf{p}(0) \exp(Qt)$.

---

## 4. How to Run the Pipeline

Each script can be executed sequentially from the workspace root or within `partner_repo`:

```powershell
python partner_repo/01_eda_and_preprocessing.py
python partner_repo/02_nhpp_arrival_and_service_fitting.py
python partner_repo/03_markov_chain_analysis.py
python partner_repo/04_tandem_queue_simulation.py
python partner_repo/05_model_validation_and_policy.py
```
