# Deep Dives Changelog: Mathematical and Methodological Auditing

This document records the exact corrections, recalibrations, and alignment changes applied to the deep-dive investigation modules in [`deep_dives/`](README.md).

---

## 1. Deep Dive 1: Heavy-Tail Service Times & Allen–Cunneen Multiplier ([`01_heavy_tail_service_deep_dive.md`](01_heavy_tail_service_deep_dive.md))

* **Causal Phrasing Recalibration:**
  * *Previous:* "real hospital waiting times are 49.6% higher driven purely by variance"
  * *Corrected:* "Under the Allen–Cunneen approximation, holding mean service time ($E[S] = 5.386$ days), bed capacity, and Poisson arrivals fixed, the estimated queueing delay is approximately 49.6% higher than the standard $M/M/c$ baseline."
  * *Rationale:* Allen–Cunneen is an approximation for general multi-server queues ($M/G/c$), not an exact closed-form law.
* **Kolmogorov–Smirnov $p$-Value Methodological Clarification:**
  * Added explicit explanation of large-sample statistical power: With $N = 250,000$, standard hypothesis tests reject null hypotheses ($p < 10^{-15}$) for any parametric family due to minor real-world tail differences. Model selection is properly guided by penalized information criteria (AIC/BIC) and empirical distance ($D$).
* **Model Selection Labeling:**
  * Changed label from "WINNER" to "Best among evaluated candidate distributions under this maximum-likelihood fitting procedure."
* **Removed Unsupported Claims & Added Citations:**
  * Removed speculative construction cost figures and unsupported hazard trajectory claims.
  * Added formal citations: Allen (1990), Cunneen (1972), Pollaczek (1930), Khinchine (1932), Green (2002), de Bruin et al. (2010), Armony et al. (2015).
* **Metadata & Structure:**
  * Added a dedicated "Data Provenance and Model Assumptions" box at the top.
  * Replaced all `file:///` URLs with repository-relative Markdown links.

---

## 2. Deep Dive 2: Capacity Sizing & Multi-Class Priority Triage ([`02_capacity_and_priority_deep_dive.md`](02_capacity_and_priority_deep_dive.md))

* **Erlang-B Sizing Reconciliation:**
  * *Previous:* Contradictory claims in prose ($8.20\%$) vs table ($4.78\%$).
  * *Corrected:* Recomputed directly from `src.queueing.erlang_b(269, 269.3) = 0.04777` ($4.78\%$, ~872 patients/year diverted). Target capacity $c^* = 293$ beds achieves $B(293, 269.3) = 0.0091$ ($0.91\%$, ~166 patients/year diverted) with a $+23.7$-bed ($+8.8\%$) safety buffer.
  * *Downstream impact:* All annual volume figures and text descriptions reconciled to $4.78\%$ and $0.91\%$.
* **Priority Queue Formulation & Multi-Server Status:**
  * Clarified that Cobham's original 1954 result is exact for single-server queues ($M/G/1$), and its multi-server implementation using the Erlang-C delay probability $W_0 = C(c, a) / (c\mu)$ is an established heuristic approximation (Buzacott & Shanthikumar, 1993; Davis, 1966).
  * Removed fabricated wait times (previously stated as 1.5h and 12.3h).
  * Evaluated exact outputs from `src.queueing.priority_queue_two_class(293, 30.0, 20.0, 0.18567)`:
    * Emergency ($W_{q,1}$): $0.0042$ days = $0.10$ hours = **6.0 minutes**.
    * Elective ($W_{q,2}$): $0.0517$ days = $1.24$ hours = **74.4 minutes**.
    * Unprioritized FCFS ($W_q^{\text{FCFS}}$): $0.0232$ days = $0.56$ hours = **33.4 minutes**.
* **Work Balance Reconciliation:**
  * Replaced the incorrect sentence claiming an unproven equality with the exact weighted average calculation:
    $$\frac{\lambda_1 W_{q,1} + \lambda_2 W_{q,2}}{\lambda_1 + \lambda_2} = \frac{30(0.0042) + 20(0.0517)}{50} = 0.0232\text{ days} = W_q^{\text{FCFS}}$$
    confirming that under identical service rates, non-preemptive priority reallocates latency between classes without changing aggregate delay.
* **Validation Against Discrete-Event Simulation (DES):**
  * Added comparison table against a 1,200-day priority DES ($W_{q,1} \approx 3.6$ mins, $W_{q,2} \approx 25.6$ mins), explaining that the analytical heuristic provides a conservative upper bound in large multi-server systems.
* **Clinical Nuance:**
  * Removed the phrase "an 8-to-12 hour delay carries zero clinical hazard." Replaced with realistic clinical context regarding elective scheduling windows vs. emergency department disposition benchmarks.

---

## 3. Deep Dive 3: Diurnal Arrivals & Network Allocation ([`03_diurnal_staffing_and_network_deep_dive.md`](03_diurnal_staffing_and_network_deep_dive.md))

* **Jackson Network Solution & Instability Reporting:**
  * *Previous:* Contradictory, fabricated arrival rates ($[40.0, 5.203, 6.842, 22.124]$) that did not solve $(I - P^T)\vec{\Lambda} = \vec{\gamma}$ for the stated routing matrix.
  * *Corrected:* Recomputed exact solution via `solve_traffic_equations`:
    $$\vec{\Lambda} = (I - P^T)^{-1} \begin{bmatrix} 40.0 \\ 2.0 \\ 0.0 \\ 15.0 \end{bmatrix} = \begin{bmatrix} 40.000 \\ 6.229 \\ 8.538 \\ 30.126 \end{bmatrix} \quad [\text{patients / day}]$$
    Verified exact balance: $\vec{\Lambda} - P^T \vec{\Lambda} = \vec{\gamma}$ to machine precision.
  * *Station Utilizations:*
    * ED: $\rho_1 = 40.0 / 72.0 = 55.56\%$ (Stable)
    * ICU: $\rho_2 = 6.229 / 6.25 = 99.67\%$ (Marginally stable)
    * StepDown: $\rho_3 = 8.538 / 10.0 = 85.38\%$ (Stable)
    * MedSurg: $\rho_4 = 30.126 / 24.0 = \mathbf{125.52\% > 1.0}$ (**UNSTABLE**)
  * *Narrative Overhaul:* Removed previous stable-state narrative. Transparently reported that the 120-bed nominal MedSurg capacity is unstable ($\rho_4 = 1.2552$), producing infinite theoretical census ($L_{\text{total}} = \infty$) and residence time ($W_{\text{total}} = \infty$).
  * *Stabilizing Thresholds:* Derived minimum stabilizing capacity ($c_4 \ge 151$ beds) and $85\%$ occupancy target capacity ($c_4 \ge 178$ beds).
* **Fox Greedy Bed Allocation Scenario Alignment:**
  * *Previous:* Table showed $C = 230$ beds, but standalone code at the bottom used $C = 160$ beds with different loads and weights.
  * *Corrected:* Standalone script updated to run the exact $C = 230$ scenario ($a = [20, 30, 150]$, $w = [4, 2, 1]$):
    * Proportional: $\vec{c} = [24, 34, 172]$, Loss $= 0.4037$.
    * Fox Optimal: $\vec{c} = [33, 43, 154]$, Loss $= 0.0655$ (**83.8% loss reduction**).
* **Standalone Code Script Alignment:**
  * Updated standalone code to execute both the 4-station Jackson network and the 230-bed Fox allocation matching the text exactly.

---

## 4. Verification Suite Updates ([`verify_deep_dives.py`](verify_deep_dives.py))

* Replaced the legacy 3-station network test with the exact 4-station network documented in Deep Dive 3.
* Added programmatic assertion that $(I - P^T)\vec{\Lambda} = \vec{\gamma}$ holds within $10^{-5}$.
* Added assertion that system instability is correctly flagged (`all_stations_stable == False`, `bottleneck == 'MedSurg'`, $\rho_4 = 1.2552$).
* Updated Erlang-B assertions to $B(269, 269.3) = 0.0478$ and $B(293, 269.3) = 0.0091$.
* Updated priority queue assertions to $W_{q,1} = 0.0042$ days and $W_{q,2} = 0.0517$ days.
* Updated Fox allocation assertions to $C = 230$, ICU $= 33$ beds, and loss reduction $= 83.8\%$.

---

## 5. Priority DES Implementation & Claim-Audit Finalization

* **Priority Discrete-Event Simulation Engine ([`src/priority_simulation.py`](../src/priority_simulation.py)):**
  * Implemented an event-calendar (`heapq`) two-class non-preemptive multi-server priority DES engine.
  * Parameters: $c = 293$ beds, $\lambda_1 = 30.0$ emergency/day, $\lambda_2 = 20.0$ elective/day, $\mu = 0.18567\text{ days}^{-1}$.
  * Features time-based warm-up (100 days), class-specific wait tracking for completed patients, independent random number stream control, and multi-replication aggregation with Student-t 95% confidence intervals.
* **Unit Testing Suite Expansion ([`tests/test_priority_simulation.py`](../tests/test_priority_simulation.py)):**
  * Created unit tests validating single-run event processing and multi-replication aggregation, expanding test suite from 33 to 35 passing tests.
* **Multi-Replication DES Empirical Findings:**
  * Replaced single 1,200-day sample-path figures with 10 independent replications (730 days each, 100-day warmup, evaluating ~315,670 total completed patients):
    * Emergency Wait ($W_{q,1}$): $5.29 \pm 1.56$ mins ($95\%\text{ CI}: [3.73, 6.85]$ mins; range $[3.23, 11.07]$ mins; sample size: 18,890 patients/rep).
    * Elective Wait ($W_{q,2}$): $57.26 \pm 35.10$ mins ($95\%\text{ CI}: [22.16, 92.36]$ mins; range $[19.38, 193.11]$ mins; sample size: 12,677 patients/rep).
    * Overall Wait ($\bar{W}_q$): $26.21 \pm 15.15$ mins ($95\%\text{ CI}: [11.06, 41.36]$ mins; range $[9.76, 84.87]$ mins; sample size: 31,567 patients/rep).
  * Removed "conservative upper bound" assertion; clarified that high utilization ($\rho \approx 91.9\%$) creates significant multi-year sample path variance, while the heuristic point estimate comfortably resides within the 95% confidence interval.
* **Work Balance Language Refinement:**
  * Renamed section to **"Internal Consistency Check for the Heuristic"** in both `02_capacity_and_priority_deep_dive.md` and `verify_deep_dives.py`.
  * Clarified that equality between weighted heuristic delays and the FCFS baseline follows algebraically from the heuristic formulas and is not an empirical proof of Kleinrock's conservation law.
* **Scenario Distinctions and Causal Softening:**
  * Renamed "Empirical Buffer Sensitivity" to **"Model-Based Buffer Sensitivity Scenario"**.
  * Softened causal claims from "prevents ambulance diversion" to "lower modeled loss probability under the specified Erlang-B assumptions."
* **Verification Language & Dynamic Test Counts:**
  * Updated `README.md` and `verify_deep_dives.py` header:
    *"The verification script checks the documented analytical scenarios and benchmark calculations. Empirical distribution-fit statistics require the restricted SPARCS source data and original fitting pipeline."*
  * Added `check_test_suite_status()` to `verify_deep_dives.py` to dynamically discover and report test suite size (35 tests) instead of relying on hardcoded test counts.
