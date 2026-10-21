"""
Time-Varying Queueing Dynamics & Pointwise Stationary Approximation (PSA).

Models non-homogeneous Poisson arrival processes with diurnal sinusoidal rhythms:
    lambda(t) = lambda_bar * [1 + alpha * cos(2*pi*(t - t_peak) / 24)]

Evaluates hourly bed utilization, congestion probabilities, and queue delays
under constant vs. dynamic peak-demand staffing schedules.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dataclasses import dataclass
from typing import Dict, List, Any, Tuple
import numpy as np

from src.queueing import erlang_b, erlang_c, mmc_performance_metrics


@dataclass
class HourlyQueueState:
    """State of the hospital queueing system at hour t in [0, 24)."""
    hour: int
    arrival_rate_per_hour: float
    capacity: int
    service_rate_per_hour: float
    offered_load: float
    utilization: float
    is_stable: bool
    prob_delay: float
    wait_time_hours: float
    queue_length: float
    blocking_prob: float


@dataclass
class PSASimulationResult:
    """24-hour Pointwise Stationary Approximation results for a staffing schedule."""
    schedule_name: str
    hourly_states: List[HourlyQueueState]
    peak_hour: int
    peak_arrival_rate: float
    peak_utilization: float
    peak_wait_time_hours: float
    mean_wait_time_hours: float
    daily_total_arrivals: float
    total_bed_hours: int


def diurnal_arrival_rate(
    hour: float,
    mean_daily_arrivals: float = 55.0,
    amplitude_ratio: float = 0.35,
    peak_hour: float = 14.5,
) -> float:
    """
    Compute hourly arrival rate lambda(t) in patients/hour.

    Parameters
    ----------
    hour : float
        Time of day in [0, 24).
    mean_daily_arrivals : float
        Total expected patients arriving per day.
    amplitude_ratio : float
        Fractional fluctuation around mean (e.g. 0.35 = +/- 35%).
    peak_hour : float
        Hour of day corresponding to peak arrival intensity.

    Returns
    -------
    float
        Instantaneous arrival rate in patients per hour.
    """
    base_rate = mean_daily_arrivals / 24.0
    intensity = base_rate * (1.0 + amplitude_ratio * np.cos(2.0 * np.pi * (hour - peak_hour) / 24.0))
    return max(0.01, float(intensity))


def run_pointwise_stationary_approximation(
    schedule_name: str,
    hourly_capacities: List[int],
    mean_daily_arrivals: float = 55.0,
    mean_los_days: float = 5.39,
    amplitude_ratio: float = 0.35,
    peak_hour: float = 14.5,
) -> PSASimulationResult:
    """
    Run 24-hour Pointwise Stationary Approximation (PSA).

    Parameters
    ----------
    schedule_name : str
        Description of staffing policy (e.g. "Constant 285 Beds").
    hourly_capacities : List[int]
        Number of active beds/staff at each hour (length 24).
    mean_daily_arrivals : float
        Average daily admissions.
    mean_los_days : float
        Mean length of stay in days.
    amplitude_ratio : float
        Diurnal amplitude.
    peak_hour : float
        Peak hour of the day.

    Returns
    -------
    PSASimulationResult
        Hourly metrics and aggregated performance.
    """
    if len(hourly_capacities) != 24:
        raise ValueError("hourly_capacities must have length 24 (one per hour).")

    mu_per_hour = 1.0 / (mean_los_days * 24.0)
    hourly_states: List[HourlyQueueState] = []

    for h in range(24):
        lam_h = diurnal_arrival_rate(h, mean_daily_arrivals, amplitude_ratio, peak_hour)
        c_h = hourly_capacities[h]
        a_h = lam_h / mu_per_hour
        rho_h = a_h / c_h if c_h > 0 else float("inf")
        is_stable = rho_h < 1.0

        if not is_stable:
            p_delay = 1.0
            w_q = float("inf")
            l_q = float("inf")
            p_block = 1.0
        else:
            q_metrics = mmc_performance_metrics(c_h, lam_h, mu_per_hour)
            p_delay = float(q_metrics["p_delay"])
            w_q = float(q_metrics["w_q"])
            l_q = float(q_metrics["l_q"])
            p_block = erlang_b(c_h, a_h)

        hourly_states.append(
            HourlyQueueState(
                hour=h,
                arrival_rate_per_hour=round(lam_h, 3),
                capacity=c_h,
                service_rate_per_hour=round(mu_per_hour, 6),
                offered_load=round(a_h, 2),
                utilization=round(rho_h, 4),
                is_stable=is_stable,
                prob_delay=round(p_delay, 4),
                wait_time_hours=round(w_q, 4) if is_stable else float("inf"),
                queue_length=round(l_q, 3) if is_stable else float("inf"),
                blocking_prob=round(p_block, 4),
            )
        )

    # Aggregates
    arrivals = [st.arrival_rate_per_hour for st in hourly_states]
    rhos = [st.utilization for st in hourly_states]
    waits = [st.wait_time_hours for st in hourly_states if st.is_stable]

    peak_h = int(np.argmax(arrivals))
    max_rho = max(rhos)
    max_wait = max(waits) if waits else float("inf")
    mean_wait = float(np.mean(waits)) if waits else float("inf")
    tot_arrivals = sum(arrivals)
    tot_bed_hours = sum(hourly_capacities)

    return PSASimulationResult(
        schedule_name=schedule_name,
        hourly_states=hourly_states,
        peak_hour=peak_h,
        peak_arrival_rate=round(max(arrivals), 3),
        peak_utilization=round(max_rho, 4),
        peak_wait_time_hours=round(max_wait, 3),
        mean_wait_time_hours=round(mean_wait, 3),
        daily_total_arrivals=round(tot_arrivals, 2),
        total_bed_hours=tot_bed_hours,
    )


def compare_constant_vs_dynamic_staffing(
    mean_daily_arrivals: float = 55.0,
    mean_los_days: float = 5.39,
    base_beds: int = 425,
    surge_delta: int = 25,
) -> Tuple[PSASimulationResult, PSASimulationResult]:
    """
    Compare constant 24/7 staffing vs. dynamic peak-hour shift schedule
    with matching or neutral total daily bed-hours.
    """
    # Constant policy: base_beds at all 24 hours
    constant_schedule = [base_beds] * 24

    # Dynamic policy: shift surge_delta beds from quiet night (22:00-06:00, 8 hrs) to peak day (10:00-18:00, 8 hrs)
    dynamic_schedule = []
    for h in range(24):
        if 10 <= h < 18:
            dynamic_schedule.append(base_beds + surge_delta)
        elif h < 6 or h >= 22:
            dynamic_schedule.append(base_beds - surge_delta)
        else:
            dynamic_schedule.append(base_beds)

    res_const = run_pointwise_stationary_approximation(
        schedule_name=f"Constant Staffing ({base_beds} Beds 24/7)",
        hourly_capacities=constant_schedule,
        mean_daily_arrivals=mean_daily_arrivals,
        mean_los_days=mean_los_days,
    )

    res_dyn = run_pointwise_stationary_approximation(
        schedule_name=f"Dynamic Shift Staffing ({base_beds-surge_delta} to {base_beds+surge_delta} Beds)",
        hourly_capacities=dynamic_schedule,
        mean_daily_arrivals=mean_daily_arrivals,
        mean_los_days=mean_los_days,
    )

    return res_const, res_dyn


if __name__ == "__main__":
    c_res, d_res = compare_constant_vs_dynamic_staffing()
    print("=" * 60)
    print(">>> POINTWISE STATIONARY APPROXIMATION (PSA) COMPARISON <<<")
    print("=" * 60)
    print(f"Policy 1: {c_res.schedule_name}")
    print(f"  Peak Utilization: {c_res.peak_utilization*100:.1f}%")
    print(f"  Peak Wait Time:   {c_res.peak_wait_time_hours:.2f} hours")
    print(f"  Mean Wait Time:   {c_res.mean_wait_time_hours:.2f} hours")
    print("-" * 60)
    print(f"Policy 2: {d_res.schedule_name}")
    print(f"  Peak Utilization: {d_res.peak_utilization*100:.1f}%")
    print(f"  Peak Wait Time:   {d_res.peak_wait_time_hours:.2f} hours")
    print(f"  Mean Wait Time:   {d_res.mean_wait_time_hours:.2f} hours")
    improvement = (c_res.peak_wait_time_hours - d_res.peak_wait_time_hours) / c_res.peak_wait_time_hours * 100
    print(f"\nPeak Hour Delay Reduction: {improvement:.1f}% under same total bed-hours!")
