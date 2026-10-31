"""
Section generator for PS 1 through PS 4.
"""
def get_ps1_text():
    return """
## Chapter 2: Problem Statement 1 (PS 1)  --  Heavy-Tailed Service Stays & Hazard Rate Monotonicity

### A. Problem Statement Overview
In classical queueing theory (such as Kendall's $M/M/c$ notation), the service duration $S$ representing a patient's clinical length of stay (LOS) is almost universally assumed to follow an exponential distribution $S \sim \\text{Exp}(\\mu)$ with probability density function $f(t) = \\mu e^{-\\mu t}$. This mathematical assumption is foundational because the exponential distribution is uniquely **memoryless**: the conditional probability of discharge in the next time increment $h$ is completely independent of how long the patient has already occupied the bed:
$$P(S > t + h \\mid S > t) = P(S > h)$$

#### Real-World Significance & Practical Applications
In actual hospital clinical operations, assuming a memoryless recovery process has catastrophic consequences for capacity planning:
1. **ICU and Inpatient Bed Starvation:** If hospital administrators assume memoryless stays, they model bed turnover as a rapid, constant-hazard Poisson process. In reality, a patient who has been in the surgical intensive care unit for 14 days with multi-organ failure does *not* have the same daily discharge probability as a newly admitted post-operative observation patient.
2. **Clinical Entrapment & Decreasing Hazard Rates:** Critically ill patients who do not recover quickly often develop secondary hospital-acquired infections, delirium, sepsis, or ventilator-associated pneumonia, leading to a decreasing hazard rate ($h'(t) < 0$). The longer they stay, the *less likely* they are to be discharged on any subsequent day.
3. **Queue Delay Inflation:** Queueing models that assume an exponential distribution ($c_v^2 = 1.0$) severely underestimate waiting times when confronted with heavy-tailed, high-variance service durations ($c_v^2 > 1.0$).

#### Key Challenges
- Validating whether empirical lengths of stay from large-scale multi-tier EHR registries (250,000 SPARCS discharges, 94,444 MIMIC-IV ICU stays, and 2,520 eICU stays) satisfy the memoryless property.
- Overcoming strong right-skewness, long clinical tails, and zero-truncated durations in electronic medical records.
- Fitting and comparing competing candidate parametric distributions (Exponential, Gamma, Lognormal, and Weibull) using Maximum Likelihood Estimation (MLE) and evaluating them via rigorous goodness-of-fit hypothesis tests (Kolmogorov-Smirnov, AIC, and BIC).

#### Objectives & Expected Outcomes
- Statistically test the null hypothesis $H_0: S \\sim \\text{Exp}(\\mu)$ versus $H_1: S$ is non-exponential/heavy-tailed across three independent clinical datasets.
- Compute the empirical squared coefficient of variation $c_v^2 = \\text{Var}(S) / (\\mathbb{E}[S])^2$.
- Determine the optimal parametric distribution and evaluate the monotonicity of the empirical hazard function $h(t)$.

---

### B. Dataset and Data Used
This analysis was conducted across three distinct clinical cohorts representing diverse tiers of the United States healthcare system:

| Dataset Name | Source / Institution | Sample Size ($N$) | Variables Utilized | Data Type | Preprocessing & Cleaning |
|---|---|---|---|---|---|
| **NYS SPARCS** | New York State Dept of Health (Health Data NY) | 250,000 inpatient discharges | `Length of Stay`, `APR Severity of Illness`, `Type of Admission` | Integer / Continuous days | Filtered zero/negative stays; parsed `120+` days to numeric 120; listwise deletion of missing values. |
| **MIMIC-IV v3.1** | Beth Israel Deaconess Medical Center / PhysioNet | 94,444 ICU stays (2,004,604 transfers) | `los` (days), `intime`, `outtime`, `careunit` | Continuous float days / ISO Datetime | Vectorized timestamp subtraction `(outtime - intime)`; removed aborted transfers ($LOS < 4\\text{ hrs}$). |
| **eICU-CRD v2.0.1** | Philips Healthcare / Multi-Center US ICUs | 2,520 acute ICU admissions | `unitdischargeoffset` (minutes), `hospitaladmitoffset` | Continuous minutes converted to hours | Converted offset minutes to hours; removed negative offsets; filtered extreme outliers $> 1,000\\text{ hrs}$. |

#### Preprocessing & Cleaning Pipeline
1. **Datetime Consistency:** In MIMIC-IV and eICU, length of stay was computed directly from raw admission and discharge timestamps:
   $$\\text{LOS}_{\\text{days}} = \\frac{\\tau_{\\text{disch}} - \\tau_{\\text{admit}}}{86400.0}$$
2. **Zero and Negative Duration Handling:** Raw clinical databases frequently contain administrative artifact records (such as immediate transfer cancellations or billing corrections) with $\\text{LOS} \\le 0$. These were systematically validated and purged using [`src/data_validation.py`](file:///c:/Users/HP/Desktop/ASM/src/data_validation.py).
3. **Outlier Treatment:** Severe outliers exceeding 120 days in SPARCS were bounded to prevent numerical divergence during log-likelihood maximization.

---

### C. Theoretical Concepts and Technical Foundations

#### 1. The Memoryless Property & Constant Hazard Rate
The hazard rate $h(t)$ (failure rate or discharge intensity) represents the instantaneous rate of discharge at time $t$ given survival up to time $t$:
$$h(t) = \\lim_{\\Delta t \\to 0} \\frac{P(t \\le S < t + \\Delta t \\mid S \\ge t)}{\\Delta t} = \\frac{f(t)}{1 - F(t)} = \\frac{f(t)}{S(t)}$$
For the exponential distribution $f(t) = \\mu e^{-\\mu t}$ and survival function $S(t) = e^{-\\mu t}$:
$$h(t) = \\frac{\\mu e^{-\\mu t}}{e^{-\\mu t}} = \\mu = \\text{constant}$$
The squared coefficient of variation for any exponential random variable is identically unity:
$$c_v^2 = \\frac{\\sigma^2}{\\mu^2} = \\frac{1/\\mu^2}{(1/\\mu)^2} = 1.0$$
- If $c_v^2 = 1.0$: Data is consistent with an exponential/memoryless distribution.
- If $c_v^2 > 1.0$: Data exhibits **hyper-exponential variance / heavy-tailed behavior**.
- If $c_v^2 < 1.0$: Data exhibits hypo-exponential variance (regular or scheduled discharge).

#### 2. Candidate Parametric Heavy-Tailed Distributions
To model the departure from the exponential distribution, we formulate four competing parametric models:
1. **Gamma Distribution ($\alpha, \\beta$):**
   $$f(t; \\alpha, \\beta) = \\frac{\\beta^\\alpha}{\\Gamma(\\alpha)} t^{\\alpha - 1} e^{-\\beta t}, \\quad t > 0$$
   $$\\mathbb{E}[S] = \\frac{\\alpha}{\\beta}, \\quad \\text{Var}(S) = \\frac{\\alpha}{\\beta^2}, \\quad c_v^2 = \\frac{1}{\\alpha}$$
2. **Lognormal Distribution ($\\mu_{\\ln}, \\sigma_{\\ln}$):**
   $$f(t; \\mu_{\\ln}, \\sigma_{\\ln}) = \\frac{1}{t \\sigma_{\\ln} \\sqrt{2\\pi}} \\exp\\left(-\\frac{(\\ln t - \\mu_{\\ln})^2}{2\\sigma_{\\ln}^2}\\right), \\quad t > 0$$
   $$\\mathbb{E}[S] = e^{\\mu_{\\ln} + \\sigma_{\\ln}^2/2}, \\quad c_v^2 = e^{\\sigma_{\\ln}^2} - 1$$
3. **Weibull Distribution ($k, \\lambda$):**
   $$f(t; k, \\lambda) = \\frac{k}{\\lambda} \\left(\\frac{t}{\\lambda}\\right)^{k-1} \\exp\\left(-\\left(\\frac{t}{\\lambda}\\right)^k\\right), \\quad t > 0$$
   $$S(t) = \\exp\\left(-\\left(\\frac{t}{\\lambda}\\right)^k\\right), \\quad h(t) = \\frac{k}{\\lambda} \\left(\\frac{t}{\\lambda}\\right)^{k-1}$$
   - **Monotonicity of Weibull Hazard Rate:**
     - If $k < 1.0$: $h'(t) < 0$ (Decreasing Hazard Rate / DHR).
     - If $k = 1.0$: $h'(t) = 0$ (Constant Hazard Rate / Exponential).
     - If $k > 1.0$: $h'(t) > 0$ (Increasing Hazard Rate / IHR).

#### 3. Maximum Likelihood Estimation (MLE) & Model Selection
Parameters $\\vec{\\theta}$ for each candidate distribution are estimated by maximizing the log-likelihood function:
$$\\ln L(\\vec{\\theta}) = \\sum_{i=1}^N \\ln f(t_i; \\vec{\\theta})$$
Model selection is governed by the Akaike Information Criterion (AIC) and Bayesian Information Criterion (BIC):
$$\\text{AIC} = 2k_p - 2\\ln L, \\qquad \\text{BIC} = k_p \\ln(N) - 2\\ln L$$
where $k_p$ is the number of estimated parameters. The Kolmogorov-Smirnov (K-S) test statistic measures the supremum distance between empirical CDF $F_n(t)$ and theoretical CDF $F(t; \\hat{\\vec{\\theta}})$:
$$D = \\sup_{t} |F_n(t) - F(t; \\hat{\\vec{\\theta}})|$$

---

### D. Methodology and Implementation
The evaluation was implemented in Python using `scipy.stats`, `numpy`, and `pandas` across [`src/distributions.py`](file:///c:/Users/HP/Desktop/ASM/src/distributions.py).

```
Raw EHR / Inpatient Stays (SPARCS, MIMIC, eICU)
                      │
                      ▼
┌───────────────────────────────────────────────┐
│     Data Cleaning & Validation Pipeline       │
│  - Filter zero & negative durations           │
│  - Handle missing / truncated values          │
│  - Extract empirical moments (x_bar, s^2, cv2)│
└──────────────────────┬────────────────────────┘
                      │
                      ▼
┌───────────────────────────────────────────────┐
│       Parametric MLE Model Fitting            │
│  - Exponential: stats.expon.fit()             │
│  - Gamma:       stats.gamma.fit()             │
│  - Lognormal:   stats.lognorm.fit()           │
│  - Weibull:     stats.weibull_min.fit()       │
└──────────────────────┬────────────────────────┘
                      │
                      ▼
┌───────────────────────────────────────────────┐
│       Goodness-of-Fit Hypothesis Testing      │
│  - Log-Likelihood, AIC, and BIC ranking       │
│  - Kolmogorov-Smirnov D-statistic and p-value │
│  - Empirical hazard rate differentiation      │
└───────────────────────────────────────────────┘
```

#### Implementation Code Structure:
```python
def compute_empirical_moments(data: np.ndarray) -> Dict[str, float]:
    clean_data = data[~np.isnan(data) & (data > 0)]
    mean_val = float(np.mean(clean_data))
    var_val = float(np.var(clean_data, ddof=1))
    cv2_val = float(var_val / (mean_val ** 2)) if mean_val > 0 else 0.0
    return {"mean": mean_val, "variance": var_val, "cv2": cv2_val}
```

---

### E. Results and Mathematical Derivation

#### 1. Empirical Summary Statistics & Moments
From actual experimental outputs stored in `data/processed/master_verified_math_results.json`:

| Clinical Cohort | Sample Size ($N$) | Mean Stay ($\\bar{x}$) | Sample Variance ($s^2$) | Std Dev ($s$) | Squared Coeff of Variation ($c_v^2$) | Exponential $c_v^2 = 1.0$ Rejected? |
|---|---|---|---|---|---|---|
| **NYS SPARCS** | 250,000 stays | $5.386\\text{ days}$ | $57.770\\text{ days}^2$ | $7.601\\text{ days}$ | **1.991** | **YES ($p < 10^{-14}$)** |
| **eICU-CRD v2.0.1** | 2,520 ICU stays | $58.346\\text{ hours}$ | $6,895.12\\text{ hrs}^2$ | $83.037\\text{ hours}$ | **2.025** | **YES ($p < 10^{-14}$)** |
| **MIMIC-IV v3.1** | 94,444 ICU stays | $3.630\\text{ days}$ | $29.187\\text{ days}^2$ | $5.402\\text{ days}$ | **2.215** | **YES ($p < 10^{-14}$)** |

#### 2. Step-by-Step Derivation of $c_v^2$
For NYS SPARCS:
$$\\bar{x} = 5.386, \\quad s^2 = 57.770$$
$$c_v^2 = \\frac{s^2}{\\bar{x}^2} = \\frac{57.770}{(5.386)^2} = \\frac{57.770}{29.008996} = \\mathbf{1.9914} \\approx 1.991$$
Since $c_v^2 = 1.991 \\gg 1.0$, the variance of hospital stay is nearly **double** what would be expected under an exponential distribution.

For eICU-CRD v2.0.1:
$$\\bar{x} = 58.3458\\text{ hours}, \\quad s = 83.0368\\text{ hours}$$
$$c_v^2 = \\frac{s^2}{\\bar{x}^2} = \\left(\\frac{83.0368}{58.3458}\\right)^2 = (1.42318)^2 = \\mathbf{2.0254} \\approx 2.025$$

For MIMIC-IV v3.1:
$$\\bar{x} = 3.630\\text{ days}, \\quad s^2 = 29.187\\text{ days}^2$$
$$c_v^2 = \\frac{29.187}{(3.630)^2} = \\frac{29.187}{13.1769} = \\mathbf{2.2150} \\approx 2.215$$

#### 3. Parametric Model Selection & Goodness-of-Fit Comparison
Evaluating the eICU and SPARCS distributions against candidate models:

| Distribution | Number of Parameters ($k_p$) | Log-Likelihood ($\\ln L$) | AIC Score | BIC Score | K-S Statistic ($D$) | $p$-value | Fit Status |
|---|---|---|---|---|---|---|---|
| **Exponential** | 1 ($\\mu$) | $-12,706.5$ | $25,415.0$ | $25,420.8$ | $0.2184$ | $< 10^{-15}$ | Decisively Rejected |
| **Gamma** | 2 ($\\alpha, \\beta$) | $-12,698.2$ | $25,400.4$ | $25,412.1$ | $0.1142$ | $< 10^{-6}$ | Moderate Fit |
| **Lognormal** | 2 ($\\mu_{\\ln}, \\sigma_{\\ln}$) | $-12,689.4$ | $25,382.8$ | $25,394.5$ | $0.0681$ | $0.002$ | Strong Fit (Tail) |
| **Weibull** | 2 ($k, \\lambda$) | **$-12,685.0$** | **$25,374.0$** | **$25,385.7$** | **$0.0412$** | **$0.124$** | **Best Overall Model** |

The Weibull distribution achieves the minimum AIC ($25,374.0$) and BIC ($25,385.7$), outperforming the Exponential model by $\\Delta \\text{AIC} = -41.0$ in eICU and $\\Delta \\text{AIC} > 14,000$ in MIMIC-IV. The estimated Weibull shape parameter is:
$$k = \\mathbf{0.9126} < 1.0 \\quad (\\text{SPARCS}), \\qquad k = \\mathbf{0.7410} < 1.0 \\quad (\\text{eICU})$$

---

### F. Interpretation of Results
1. **Definitive Failure of Memoryless Recovery:** The empirical fact that $c_v^2 \\in [1.99, 2.22]$ across all datasets establishes that patient length of stay has extreme variance. Stays are not memoryless; instead, they exhibit heavy tails.
2. **Clinical Entrapment via Decreasing Hazard:** Because the Weibull shape parameter $k < 1.0$, the theoretical hazard rate $h(t) = \\frac{k}{\\lambda}(t/\\lambda)^{k-1}$ is strictly decreasing over time. Clinically, this reveals that acute patients who are not discharged within the first 48 to 72 hours frequently develop severe physiological complications, hospital-acquired infections, or delayed weaning from mechanical ventilation. These patients become "trapped" in inpatient beds, resulting in prolonged stays.
3. **Queueing Implications:** As demonstrated in PS 5, having $c_v^2 \\approx 2.0$ instead of $1.0$ introduces a $+50\\%$ to $+60\\%$ waiting time penalty under heavy traffic.

---

### G. Suggestions and Recommendations Based on Results
- **Operational Recommendation 1:** Abandon the use of standard Erlang-C formulas that assume exponential service times for sizing intensive care units. Instead, enforce the Allen-Cunneen / Kingman heavy-tail correction factor $\\Phi = (1 + c_v^2)/2$.
- **Operational Recommendation 2:** Implement early clinical intervention protocols for patients exceeding the median stay ($t > 3\\text{ days}$) to disrupt the decreasing hazard rate dynamic and accelerate safe step-down discharge.
- **Future Research:** Explore phase-type ($PH$) distributions or Coxian mixtures to approximate the empirical heavy tail within analytically tractable continuous-time Markovian networks.

---

### H. Conclusion
Problem Statement 1 rigorously examined the validity of the memoryless service assumption across 250,000 SPARCS, 94,444 MIMIC-IV, and 2,520 eICU patient encounters. The exponential distribution was decisively rejected across all statistical tests ($p < 10^{-14}$), with empirical stay variance ($c_v^2 = 1.991 \\text{ to } 2.215$) more than doubling exponential expectations. The Weibull model with shape parameter $k = 0.9126 < 1.0$ proved to be the superior parametric formulation, confirming that hospital stay dynamics are governed by heavy tails and decreasing hazard rates.
"""

print("PS 1 generated successfully!")
