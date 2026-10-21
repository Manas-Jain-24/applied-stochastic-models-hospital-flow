"""
Parametric distribution fitting and goodness-of-fit testing for Length of Stay (LOS)
and inter-arrival times.
Supports: Exponential, Gamma, Lognormal, Weibull.
Calculates: Mean, Variance, cv^2 (Memoryless test), AIC, BIC, and K-S test statistics.
"""
from typing import Dict, Any, List, Tuple
import numpy as np
import scipy.stats as stats
import pandas as pd

def compute_empirical_moments(data: np.ndarray) -> Dict[str, float]:
    """
    Computes sample mean, variance, standard deviation, and squared coefficient of variation.
    cv^2 = Var(X) / (E[X])^2.
    If cv^2 == 1 -> Consistent with Exponential (Memoryless).
    If cv^2 > 1 -> High variance / Heavy-tailed.
    If cv^2 < 1 -> Low variance / Regular.
    """
    clean_data = data[~np.isnan(data) & (data > 0)]
    mean_val = float(np.mean(clean_data))
    var_val = float(np.var(clean_data, ddof=1))
    std_val = float(np.std(clean_data, ddof=1))
    cv2_val = float(var_val / (mean_val ** 2)) if mean_val > 0 else 0.0
    
    return {
        "n_samples": len(clean_data),
        "mean": round(mean_val, 4),
        "variance": round(var_val, 4),
        "std_dev": round(std_val, 4),
        "cv2": round(cv2_val, 4),
        "is_memoryless_candidate": bool(abs(cv2_val - 1.0) < 0.15)
    }

def fit_candidate_distributions(data: np.ndarray) -> Dict[str, Dict[str, Any]]:
    """
    Fits candidate parametric distributions using Maximum Likelihood Estimation (MLE).
    Performs Kolmogorov-Smirnov test and calculates Log-Likelihood, AIC, and BIC.
    """
    clean_data = data[~np.isnan(data) & (data > 0)]
    n = len(clean_data)
    
    candidates = {
        "Exponential": stats.expon,
        "Gamma": stats.gamma,
        "Lognormal": stats.lognorm,
        "Weibull": stats.weibull_min
    }
    
    results = {}
    
    for dist_name, dist_obj in candidates.items():
        try:
            # Fit parameters
            params = dist_obj.fit(clean_data)
            
            # Log-Likelihood
            log_lik = float(np.sum(dist_obj.logpdf(clean_data, *params)))
            k_params = len(params)
            
            # AIC and BIC
            aic = 2 * k_params - 2 * log_lik
            bic = k_params * np.log(n) - 2 * log_lik
            
            # Kolmogorov-Smirnov Goodness-of-Fit test
            ks_stat, ks_pval = stats.kstest(clean_data, dist_name.lower() if dist_name != "Exponential" else "expon", args=params)
            
            results[dist_name] = {
                "parameters": [round(float(p), 4) for p in params],
                "log_likelihood": round(log_lik, 2),
                "aic": round(float(aic), 2),
                "bic": round(float(bic), 2),
                "ks_statistic": round(float(ks_stat), 4),
                "ks_pvalue": round(float(ks_pval), 5),
                "fit_success": True
            }
        except Exception as e:
            results[dist_name] = {
                "fit_success": False,
                "error": str(e)
            }
            
    return results

def rank_distribution_models(fit_results: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
    """
    Ranks successful distribution fits by lowest AIC and BIC.
    """
    rows = []
    for dist_name, res in fit_results.items():
        if res.get("fit_success"):
            rows.append({
                "Distribution": dist_name,
                "AIC": res["aic"],
                "BIC": res["bic"],
                "KS_Stat": res["ks_statistic"],
                "KS_pValue": res["ks_pvalue"],
                "LogLik": res["log_likelihood"]
            })
            
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(by="AIC").reset_index(drop=True)
        df["AIC_Rank"] = df.index + 1
    return df
