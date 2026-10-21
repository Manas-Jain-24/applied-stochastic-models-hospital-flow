"""
Arrival Process Analysis and Non-Homogeneous Poisson Process (NHPP) Modeling.
Implements:
1. Index of Dispersion for Counts (IDC) test for homogeneous Poisson validity
2. Diurnal (circadian) arrival intensity curve fitting lambda(t)
3. Lewis-Shedler Thinning Algorithm for exact NHPP simulation
"""
from typing import Dict, Any, Tuple, List
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

def index_of_dispersion_for_counts(counts: np.ndarray) -> Dict[str, Any]:
    """
    Computes the Index of Dispersion for Counts (IDC) = Var(N) / E[N].
    For a homogeneous Poisson process, IDC = 1.0.
    If IDC > 1.0 -> Overdispersion (clustering / time-varying arrival rate).
    If IDC < 1.0 -> Underdispersion (regular / scheduled arrivals).
    """
    clean_counts = counts[~np.isnan(counts)]
    mean_count = float(np.mean(clean_counts))
    var_count = float(np.var(clean_counts, ddof=1))
    
    idc = var_count / mean_count if mean_count > 0 else 1.0
    
    # Chi-square test statistic for Poisson assumption: (n - 1) * IDC
    n = len(clean_counts)
    chi2_stat = (n - 1) * idc
    
    # Qualitative classification
    if idc > 1.25:
        regime = "Overdispersed (Non-homogeneous Poisson or Negative Binomial)"
    elif idc < 0.85:
        regime = "Underdispersed (Scheduled / Paced Arrivals)"
    else:
        regime = "Equidispersed (Consistent with Homogeneous Poisson)"
        
    return {
        "n_intervals": n,
        "mean_arrivals_per_interval": round(mean_count, 3),
        "variance_arrivals": round(var_count, 3),
        "index_of_dispersion": round(idc, 3),
        "chi2_statistic": round(chi2_stat, 2),
        "dispersion_regime": regime,
        "is_homogeneous_poisson": bool(0.85 <= idc <= 1.25)
    }

def diurnal_sinusoidal_rate(t_hours: np.ndarray, baseline_rate: float, amplitude: float, peak_hour: float) -> np.ndarray:
    """
    Sinusoidal diurnal arrival rate model:
    lambda(t) = baseline + amplitude * cos(2 * pi * (t - peak_hour) / 24)
    """
    return baseline_rate + amplitude * np.cos(2 * np.pi * (t_hours - peak_hour) / 24.0)

def fit_diurnal_arrival_intensity(hourly_timestamps: pd.Series) -> Dict[str, Any]:
    """
    Fits a diurnal intensity curve lambda(t) to observed encounter timestamps by hour of day (0..23).
    """
    dts = pd.to_datetime(hourly_timestamps)
    hours = dts.dt.hour
    
    hourly_counts = hours.value_counts().sort_index()
    # Reindex to ensure all 24 hours exist
    hourly_counts = hourly_counts.reindex(range(24), fill_value=0)
    
    # Total days in sample
    total_days = max(1, (dts.max() - dts.min()).days)
    hourly_rates = (hourly_counts / total_days).values
    
    t_span = np.arange(24)
    
    # Initial parameter guesses: baseline = mean, amp = (max-min)/2, peak = argmax
    p0 = [float(np.mean(hourly_rates)), float((np.max(hourly_rates) - np.min(hourly_rates)) / 2.0), float(np.argmax(hourly_rates))]
    
    try:
        popt, _ = curve_fit(
            diurnal_sinusoidal_rate, 
            t_span, 
            hourly_rates, 
            p0=p0,
            bounds=([0.0, 0.0, 0.0], [np.inf, np.inf, 24.0])
        )
        fitted_baseline, fitted_amp, fitted_peak = popt
        fit_success = True
    except Exception:
        fitted_baseline, fitted_amp, fitted_peak = p0[0], p0[1], p0[2]
        fit_success = False
        
    return {
        "empirical_hourly_rates": np.round(hourly_rates, 3).tolist(),
        "baseline_rate_per_hour": round(float(fitted_baseline), 3),
        "amplitude": round(float(fitted_amp), 3),
        "peak_hour": round(float(fitted_peak), 2),
        "trough_hour": round(float((fitted_peak + 12.0) % 24.0), 2),
        "peak_to_trough_ratio": round(float((fitted_baseline + fitted_amp) / max(0.01, fitted_baseline - fitted_amp)), 2),
        "fit_success": fit_success
    }

def simulate_nhpp_thinning(
    simulation_hours: float,
    baseline_rate: float,
    amplitude: float,
    peak_hour: float,
    random_seed: int = 42
) -> np.ndarray:
    """
    Simulates Non-Homogeneous Poisson Process (NHPP) arrivals using Lewis-Shedler Thinning Algorithm.
    Generates candidate arrivals at majorizing rate lambda_max, and accepts with probability lambda(t) / lambda_max.
    """
    rng = np.random.default_rng(random_seed)
    lambda_max = baseline_rate + amplitude
    
    current_time = 0.0
    accepted_arrivals: List[float] = []
    
    while current_time < simulation_hours:
        # Generate potential inter-arrival step
        dt = rng.exponential(scale=1.0 / lambda_max)
        current_time += dt
        
        if current_time >= simulation_hours:
            break
            
        # Acceptance probability
        t_hour_of_day = current_time % 24.0
        lambda_t = diurnal_sinusoidal_rate(np.array([t_hour_of_day]), baseline_rate, amplitude, peak_hour)[0]
        accept_prob = max(0.0, min(1.0, lambda_t / lambda_max))
        
        if rng.uniform(0.0, 1.0) < accept_prob:
            accepted_arrivals.append(current_time)
            
    return np.array(accepted_arrivals)
