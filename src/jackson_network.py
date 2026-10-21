"""
Jackson Open Queueing Network Model for Hospital Patient Flow.

Implements Jackson's Theorem for multi-station open queueing networks
where patients transition between specialized hospital wards
(e.g., Emergency -> ICU -> Step-Down -> Med/Surg -> Discharge).

Solves the traffic equations:
    (I - P^T) * Lambda = gamma
and evaluates per-station and network-wide dwell times, queue lengths,
and bottleneck utilization.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np

from src.queueing import erlang_c, mmc_performance_metrics


@dataclass
class StationResult:
    """Performance metrics for an individual hospital ward / queueing station."""
    name: str
    arrival_rate: float        # Total arrival rate Lambda_j (patients/day)
    exogenous_rate: float      # Direct external arrivals gamma_j (patients/day)
    capacity: int              # Number of beds c_j
    los_mean: float            # Mean length of stay 1/mu_j (days)
    service_rate: float        # Discharge rate mu_j (patients/day/bed)
    offered_load: float        # a_j = Lambda_j / mu_j (bed-days)
    utilization: float         # rho_j = Lambda_j / (c_j * mu_j)
    is_stable: bool            # rho_j < 1.0
    prob_delay: float          # P(Wait > 0) via Erlang-C
    mean_queue_length: float   # L_q: Expected patients waiting for bed
    mean_wait_time: float      # W_q: Expected wait time in queue (days)
    mean_dwell_time: float     # W_j: Total time in department (W_q + 1/mu) (days)
    mean_patients: float       # L_j: Total patients in station (L_q + a_j)
    visit_ratio: float         # V_j = Lambda_j / sum(gamma): Expected visits per patient


@dataclass
class NetworkResult:
    """Network-wide performance metrics for the connected hospital system."""
    stations: List[StationResult]
    total_exogenous_arrival: float  # Total patient admission rate gamma_total
    total_patients_in_hospital: float  # Expected total patients across all wards L_total
    mean_end_to_end_los: float      # Expected end-to-end hospital stay W_total (days)
    bottleneck_station: str         # Ward with highest utilization rho
    bottleneck_utilization: float   # Maximum rho_j
    all_stations_stable: bool       # True if rho_j < 1 for all j


def solve_traffic_equations(
    gamma: np.ndarray,
    P: np.ndarray,
) -> np.ndarray:
    """
    Solve the linear traffic equations for an open Jackson network:
        Lambda = gamma + P^T * Lambda  <=>  (I - P^T) * Lambda = gamma

    Parameters
    ----------
    gamma : np.ndarray, shape (M,)
        Exogenous arrival rates to each department.
    P : np.ndarray, shape (M, M)
        Routing probability matrix where P[i, j] is probability that
        a patient completing stay at department i transitions to department j.
        Sum of each row sum(P[i, :]) <= 1.0 (with exit probability d_i = 1 - sum).

    Returns
    -------
    Lambda : np.ndarray, shape (M,)
        Total effective arrival rates at each department.
    """
    gamma = np.asarray(gamma, dtype=np.float64)
    P = np.asarray(P, dtype=np.float64)
    M = len(gamma)

    if P.shape != (M, M):
        raise ValueError(f"Matrix P shape {P.shape} must match gamma length {M}.")

    # Check row sums <= 1.0
    row_sums = P.sum(axis=1)
    if np.any(row_sums > 1.0 + 1e-9):
        raise ValueError("Routing matrix row sums cannot exceed 1.0.")

    # (I - P^T) * Lambda = gamma
    A = np.eye(M) - P.T
    try:
        Lambda = np.linalg.solve(A, gamma)
    except np.linalg.LinAlgError as err:
        raise ValueError("Traffic equations matrix is singular. Ensure network is open (spectral radius < 1).") from err

    if np.any(Lambda < -1e-9):
        raise ValueError("Computed negative arrival rates; verify matrix P and gamma.")

    return np.maximum(Lambda, 0.0)


def analyze_jackson_network(
    station_names: List[str],
    gamma: List[float],
    P: np.ndarray,
    capacities: List[int],
    los_means: List[float],
) -> NetworkResult:
    """
    Analyze an open Jackson queueing network of hospital departments.

    Parameters
    ----------
    station_names : List[str]
        Labels for each department (e.g. ['ED', 'ICU', 'MedSurg', 'StepDown']).
    gamma : List[float]
        Exogenous arrival rates (direct admissions from outside) in patients/day.
    P : np.ndarray, shape (M, M)
        Internal transfer probability matrix.
    capacities : List[int]
        Number of beds c_j in each department.
    los_means : List[float]
        Mean length of stay 1/mu_j (in days) in each department.

    Returns
    -------
    NetworkResult
        Comprehensive per-station and network-level metrics.
    """
    M = len(station_names)
    gamma_arr = np.array(gamma, dtype=np.float64)
    P_arr = np.array(P, dtype=np.float64)

    # 1. Solve traffic equations
    Lambda = solve_traffic_equations(gamma_arr, P_arr)
    gamma_total = float(np.sum(gamma_arr))

    station_results: List[StationResult] = []
    all_stable = True
    max_rho = -1.0
    bottleneck = ""

    for j in range(M):
        name = station_names[j]
        lam_j = float(Lambda[j])
        c_j = int(capacities[j])
        mean_los = float(los_means[j])
        mu_j = 1.0 / mean_los if mean_los > 0 else 1.0

        q_metrics = mmc_performance_metrics(c_j, lam_j, mu_j)
        offered_load = lam_j * mean_los
        rho_j = float(q_metrics["rho"])
        is_stable = bool(q_metrics["is_stable"])

        if not is_stable:
            all_stable = False
            p_delay = 1.0
            l_q = float("inf")
            w_q = float("inf")
            w_j = float("inf")
            l_j = float("inf")
        else:
            p_delay = float(q_metrics["p_delay"])
            l_q = float(q_metrics["l_q"])
            w_q = float(q_metrics["w_q"])
            w_j = float(q_metrics["w_total"])
            l_j = float(q_metrics["l_total"])


        if rho_j > max_rho:
            max_rho = rho_j
            bottleneck = name

        visit_ratio = lam_j / gamma_total if gamma_total > 0 else 0.0

        station_results.append(
            StationResult(
                name=name,
                arrival_rate=round(lam_j, 3),
                exogenous_rate=round(float(gamma_arr[j]), 3),
                capacity=c_j,
                los_mean=round(mean_los, 3),
                service_rate=round(mu_j, 4),
                offered_load=round(offered_load, 3),
                utilization=round(rho_j, 4),
                is_stable=is_stable,
                prob_delay=round(p_delay, 4),
                mean_queue_length=round(l_q, 3) if is_stable else float("inf"),
                mean_wait_time=round(w_q, 4) if is_stable else float("inf"),
                mean_dwell_time=round(w_j, 4) if is_stable else float("inf"),
                mean_patients=round(l_j, 3) if is_stable else float("inf"),
                visit_ratio=round(visit_ratio, 3),
            )
        )

    # Network-wide metrics via Little's Law
    if all_stable and gamma_total > 0:
        total_l = sum(st.mean_patients for st in station_results)
        w_total = total_l / gamma_total
    else:
        total_l = float("inf")
        w_total = float("inf")

    return NetworkResult(
        stations=station_results,
        total_exogenous_arrival=round(gamma_total, 3),
        total_patients_in_hospital=round(total_l, 3) if all_stable else float("inf"),
        mean_end_to_end_los=round(w_total, 3) if all_stable else float("inf"),
        bottleneck_station=bottleneck,
        bottleneck_utilization=round(max_rho, 4),
        all_stations_stable=all_stable,
    )
