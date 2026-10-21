"""
Two-Class Non-Preemptive Multi-Server Priority Discrete-Event Simulation (DES).
Models acute inpatient hospital beds under non-preemptive triage priority:
Class 1 (Emergency) patients take priority over Class 2 (Elective) patients
when beds become available.

Includes a separated arrival horizon and queue drain phase to eliminate right-censoring
of queued patients at the simulation boundary.
"""
import heapq
from typing import Dict, Any, List, Optional
import numpy as np
from scipy import stats


class PriorityHospitalSimulation:
    """
    Simulates a multi-server queue with two priority classes under non-preemptive FCFS discipline.
    Separates the arrival horizon from the observation/drain period so that every patient
    who arrived post-warmup is observed entering service without right-censoring.
    """
    def __init__(
        self,
        c: int = 293,
        lambda_emergency: float = 30.0,
        lambda_elective: float = 20.0,
        mu: float = 0.18567,
        sim_days: float = 730.0,
        warmup_days: float = 100.0,
        seed: int = 42
    ):
        # Input validation
        if isinstance(c, bool) or not isinstance(c, (int, np.integer)) or c <= 0:
            raise ValueError(f"Bed capacity c must be a positive integer, got {c}")
        if lambda_emergency <= 0:
            raise ValueError(f"lambda_emergency must be positive, got {lambda_emergency}")
        if lambda_elective <= 0:
            raise ValueError(f"lambda_elective must be positive, got {lambda_elective}")
        if mu <= 0:
            raise ValueError(f"Service rate mu must be positive, got {mu}")
        if warmup_days < 0:
            raise ValueError(f"warmup_days must be non-negative, got {warmup_days}")
        if sim_days <= warmup_days:
            raise ValueError(f"sim_days ({sim_days}) must be strictly greater than warmup_days ({warmup_days})")

        self.c = int(c)
        self.l1 = float(lambda_emergency)
        self.l2 = float(lambda_elective)
        self.mu = float(mu)
        self.sim_days = float(sim_days)
        self.warmup_days = float(warmup_days)
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    def run(self) -> Dict[str, Any]:
        """
        Executes a single simulation run. Arrivals are generated only until sim_days
        (the arrival horizon). The simulation then drains until every patient who arrived
        in the post-warmup observation window has begun service, preventing right-censoring.
        """
        current_time = 0.0
        occupied_beds = 0
        q_emergency: List[tuple] = []
        q_elective: List[tuple] = []
        
        events: List[tuple] = []  # (event_time, event_type, patient_id)
        # Event types: 0: Emergency arrival, 1: Elective arrival, 2: Departure
        first_arr1 = self.rng.exponential(1.0 / self.l1)
        if first_arr1 <= self.sim_days:
            heapq.heappush(events, (first_arr1, 0, 1))
            
        first_arr2 = self.rng.exponential(1.0 / self.l2)
        if first_arr2 <= self.sim_days:
            heapq.heappush(events, (first_arr2, 1, 2))
        
        waits_emergency: List[float] = []
        waits_elective: List[float] = []
        patient_counter = 2

        post_warmup_arrivals_emergency = 0
        post_warmup_arrivals_elective = 0
        observed_service_starts_emergency = 0
        observed_service_starts_elective = 0
        drain_end_time = self.sim_days

        while events:
            t, ev_type, p_id = heapq.heappop(events)
            current_time = t

            if ev_type == 0:  # Emergency arrival
                # Schedule next emergency arrival only if within arrival horizon
                next_arr = current_time + self.rng.exponential(1.0 / self.l1)
                if next_arr <= self.sim_days:
                    patient_counter += 1
                    heapq.heappush(events, (next_arr, 0, patient_counter))

                if current_time >= self.warmup_days:
                    post_warmup_arrivals_emergency += 1

                if occupied_beds < self.c:
                    occupied_beds += 1
                    if current_time >= self.warmup_days:
                        waits_emergency.append(0.0)
                        observed_service_starts_emergency += 1
                    heapq.heappush(events, (current_time + self.rng.exponential(1.0 / self.mu), 2, p_id))
                else:
                    q_emergency.append((current_time, p_id))

            elif ev_type == 1:  # Elective arrival
                # Schedule next elective arrival only if within arrival horizon
                next_arr = current_time + self.rng.exponential(1.0 / self.l2)
                if next_arr <= self.sim_days:
                    patient_counter += 1
                    heapq.heappush(events, (next_arr, 1, patient_counter))

                if current_time >= self.warmup_days:
                    post_warmup_arrivals_elective += 1

                if occupied_beds < self.c:
                    occupied_beds += 1
                    if current_time >= self.warmup_days:
                        waits_elective.append(0.0)
                        observed_service_starts_elective += 1
                    heapq.heappush(events, (current_time + self.rng.exponential(1.0 / self.mu), 2, p_id))
                else:
                    q_elective.append((current_time, p_id))

            elif ev_type == 2:  # Departure
                # When a bed becomes free, prioritize waiting emergency patients over elective patients
                if q_emergency:
                    arr_t, next_id = q_emergency.pop(0)
                    if arr_t >= self.warmup_days:
                        waits_emergency.append(current_time - arr_t)
                        observed_service_starts_emergency += 1
                    if current_time > self.sim_days:
                        drain_end_time = max(drain_end_time, current_time)
                    heapq.heappush(events, (current_time + self.rng.exponential(1.0 / self.mu), 2, next_id))
                elif q_elective:
                    arr_t, next_id = q_elective.pop(0)
                    if arr_t >= self.warmup_days:
                        waits_elective.append(current_time - arr_t)
                        observed_service_starts_elective += 1
                    if current_time > self.sim_days:
                        drain_end_time = max(drain_end_time, current_time)
                    heapq.heappush(events, (current_time + self.rng.exponential(1.0 / self.mu), 2, next_id))
                else:
                    occupied_beds -= 1

                # Stop draining once past arrival horizon and all queued patients have begun service
                if current_time >= self.sim_days and len(q_emergency) == 0 and len(q_elective) == 0:
                    break

        censored_emergency = post_warmup_arrivals_emergency - observed_service_starts_emergency
        censored_elective = post_warmup_arrivals_elective - observed_service_starts_elective
        censored_total = censored_emergency + censored_elective

        m1 = float(np.mean(waits_emergency)) if waits_emergency else 0.0
        m2 = float(np.mean(waits_elective)) if waits_elective else 0.0
        all_waits = waits_emergency + waits_elective
        mtot = float(np.mean(all_waits)) if all_waits else 0.0

        return {
            "arrival_horizon_days": self.sim_days,
            "drain_end_days": round(drain_end_time, 4),
            "post_warmup_arrivals_emergency": post_warmup_arrivals_emergency,
            "post_warmup_arrivals_elective": post_warmup_arrivals_elective,
            "observed_service_starts_emergency": observed_service_starts_emergency,
            "observed_service_starts_elective": observed_service_starts_elective,
            "censored_patients_emergency": censored_emergency,
            "censored_patients_elective": censored_elective,
            "censored_patients_total": censored_total,
            "n_emergency": observed_service_starts_emergency,
            "n_elective": observed_service_starts_elective,
            "n_total": len(all_waits),
            "wq_emergency_days": m1,
            "wq_elective_days": m2,
            "wq_total_days": mtot,
            "wq_emergency_mins": m1 * 1440.0,
            "wq_elective_mins": m2 * 1440.0,
            "wq_elective_hours": m2 * 24.0,
            "wq_total_mins": mtot * 1440.0,
        }


def run_priority_replications(
    n_replications: int = 10,
    c: int = 293,
    lambda_emergency: float = 30.0,
    lambda_elective: float = 20.0,
    mu: float = 0.18567,
    sim_days: float = 730.0,
    warmup_days: float = 100.0,
    base_seed: int = 1000
) -> Dict[str, Any]:
    """
    Executes multiple independent replications of the priority DES with arrival horizon
    and post-horizon queue drain. Reports means, standard deviations, and 95% Student-t
    confidence intervals for all post-warmup arrivals.
    """
    if isinstance(n_replications, bool) or not isinstance(n_replications, (int, np.integer)) or n_replications <= 0:
        raise ValueError(f"n_replications must be a positive integer, got {n_replications}")

    reps = []
    for i in range(n_replications):
        sim = PriorityHospitalSimulation(
            c=c,
            lambda_emergency=lambda_emergency,
            lambda_elective=lambda_elective,
            mu=mu,
            sim_days=sim_days,
            warmup_days=warmup_days,
            seed=base_seed + i
        )
        reps.append(sim.run())

    w1_vals = [r["wq_emergency_mins"] for r in reps]
    w2_vals = [r["wq_elective_mins"] for r in reps]
    wt_vals = [r["wq_total_mins"] for r in reps]
    n1_vals = [r["observed_service_starts_emergency"] for r in reps]
    n2_vals = [r["observed_service_starts_elective"] for r in reps]
    arr1_vals = [r["post_warmup_arrivals_emergency"] for r in reps]
    arr2_vals = [r["post_warmup_arrivals_elective"] for r in reps]
    drain_end_vals = [r["drain_end_days"] for r in reps]
    censored_vals = [r["censored_patients_total"] for r in reps]

    t_crit = stats.t.ppf(0.975, n_replications - 1) if n_replications > 1 else 1.96

    def get_stats(arr):
        mean = float(np.mean(arr))
        std = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0
        se = float(stats.sem(arr)) if len(arr) > 1 else 0.0
        ci = se * t_crit
        return {
            "mean": round(mean, 2),
            "std": round(std, 2),
            "se": round(se, 2),
            "ci_95": round(ci, 2),
            "ci_lower": round(mean - ci, 2),
            "ci_upper": round(mean + ci, 2),
            "min": round(float(np.min(arr)), 2),
            "max": round(float(np.max(arr)), 2),
        }

    return {
        "n_replications": n_replications,
        "arrival_horizon_days": sim_days,
        "sim_days_per_rep": sim_days,
        "warmup_days_per_rep": warmup_days,
        "avg_drain_end_days": round(float(np.mean(drain_end_vals)), 2),
        "max_drain_end_days": round(float(np.max(drain_end_vals)), 2),
        "total_censored_patients": int(np.sum(censored_vals)),
        "post_warmup_arrivals_emergency": round(float(np.mean(arr1_vals)), 0),
        "post_warmup_arrivals_elective": round(float(np.mean(arr2_vals)), 0),
        "observed_service_starts_emergency": round(float(np.mean(n1_vals)), 0),
        "observed_service_starts_elective": round(float(np.mean(n2_vals)), 0),
        "avg_patients_emergency": round(float(np.mean(n1_vals)), 0),
        "avg_patients_elective": round(float(np.mean(n2_vals)), 0),
        "avg_patients_total": round(float(np.mean(n1_vals)) + float(np.mean(n2_vals)), 0),
        "emergency_wait_mins": get_stats(w1_vals),
        "elective_wait_mins": get_stats(w2_vals),
        "elective_wait_hours": get_stats([w / 60.0 for w in w2_vals]),
        "total_wait_mins": get_stats(wt_vals),
        "individual_replications": reps
    }
