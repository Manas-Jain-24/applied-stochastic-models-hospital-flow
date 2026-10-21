"""
Analytical Queueing Theory Models for Hospital Bed Capacity and Congestion.
Implements:
1. Erlang-C (M/M/c Delay System)
2. Erlang-B (M/M/c/c Loss System)
3. Allen-Cunneen / Kingman M/G/c Heavy-Tailed Approximation
4. Multi-class Non-preemptive Priority Queueing
"""
import math
from typing import Dict, Any, Optional

def erlang_b(c: int, offered_load: float) -> float:
    """
    Computes Erlang-B blocking probability B(c, a) using numerically stable recursion:
    B(0, a) = 1
    B(k, a) = (a * B(k-1, a)) / (k + a * B(k-1, a))
    
    c: Number of servers (beds)
    offered_load: a = lambda / mu (arrival_rate / service_rate)
    """
    if c < 0 or offered_load < 0:
        raise ValueError("Capacity c and offered_load must be non-negative.")
    if c == 0:
        return 1.0
    if offered_load == 0:
        return 0.0

    b = 1.0
    for k in range(1, c + 1):
        b = (offered_load * b) / (k + offered_load * b)
    return b

def min_capacity_erlang_b(offered_load: float, target_blocking: float = 0.01, max_c: int = 2000) -> int:
    """
    Finds the minimum server capacity c* such that Erlang-B blocking probability <= target_blocking.
    """
    b = 1.0
    for k in range(1, max_c + 1):
        b = (offered_load * b) / (k + offered_load * b)
        if b <= target_blocking:
            return k
    return max_c

def erlang_c(c: int, arrival_rate: float, service_rate: float) -> float:
    """
    Computes Erlang-C delay probability P(Wait > 0) = C(c, a) where a = lambda / mu.
    Utilization rho = a / c must be strictly < 1 for steady-state stability.
    """
    if arrival_rate < 0 or service_rate <= 0 or c <= 0:
        raise ValueError("Invalid parameters for M/M/c system.")
    
    a = arrival_rate / service_rate
    rho = a / c
    
    if rho >= 1.0:
        return 1.0  # System is unstable (queue grows unbounded)
        
    # Using the relation: C(c, a) = B(c, a) / (1 - rho * (1 - B(c, a)))
    b_val = erlang_b(c, a)
    prob_delay = b_val / (1.0 - rho * (1.0 - b_val))
    return min(1.0, max(0.0, prob_delay))

def mmc_performance_metrics(c: int, arrival_rate: float, service_rate: float) -> Dict[str, Any]:
    """
    Computes all standard steady-state performance metrics for an M/M/c queue.
    
    Returns:
    - rho: Utilization (lambda / (c * mu))
    - p_delay: Erlang-C probability of waiting
    - w_q: Expected wait time in queue
    - w_total: Expected total time in hospital (W_q + 1/mu)
    - l_q: Expected queue length (lambda * W_q)
    - l_servers: Expected number of occupied beds (lambda / mu)
    - l_total: Expected total patients in hospital (L_q + L_servers)
    """
    a = arrival_rate / service_rate
    rho = a / c
    
    if rho >= 1.0:
        return {
            "is_stable": False,
            "rho": round(rho, 4),
            "p_delay": 1.0,
            "w_q": float("inf"),
            "w_total": float("inf"),
            "l_q": float("inf"),
            "l_servers": c,
            "l_total": float("inf")
        }
        
    p_delay = erlang_c(c, arrival_rate, service_rate)
    # W_q = P_delay / (c * mu * (1 - rho))
    w_q = p_delay / (c * service_rate * (1.0 - rho))
    w_total = w_q + (1.0 / service_rate)
    l_q = arrival_rate * w_q
    l_servers = a
    l_total = l_q + l_servers
    
    return {
        "is_stable": True,
        "rho": round(rho, 4),
        "p_delay": round(p_delay, 5),
        "w_q": round(w_q, 4),
        "w_total": round(w_total, 4),
        "l_q": round(l_q, 4),
        "l_servers": round(l_servers, 4),
        "l_total": round(l_total, 4)
    }

def mgc_allen_cunneen(
    c: int, 
    arrival_rate: float, 
    service_rate: float, 
    cv2_service: float, 
    cv2_arrival: float = 1.0
) -> Dict[str, Any]:
    """
    Computes the Allen-Cunneen / Kingman heavy-tail approximation for M/G/c queues:
    W_q(M/G/c) approx ((ca^2 + cv^2) / 2) * W_q(M/M/c)
    
    cv2_service: Squared coefficient of variation of service time (Var(S) / E[S]^2)
    cv2_arrival: Squared coefficient of variation of inter-arrival time (1.0 for Poisson)
    """
    mmc_res = mmc_performance_metrics(c, arrival_rate, service_rate)
    if not mmc_res["is_stable"]:
        return mmc_res
        
    correction_factor = (cv2_arrival + cv2_service) / 2.0
    w_q_mgc = correction_factor * mmc_res["w_q"]
    w_total_mgc = w_q_mgc + (1.0 / service_rate)
    l_q_mgc = arrival_rate * w_q_mgc
    l_total_mgc = l_q_mgc + mmc_res["l_servers"]
    
    return {
        "is_stable": True,
        "rho": mmc_res["rho"],
        "cv2_service": round(cv2_service, 4),
        "correction_factor": round(correction_factor, 4),
        "w_q_mgc": round(w_q_mgc, 4),
        "w_total_mgc": round(w_total_mgc, 4),
        "l_q_mgc": round(l_q_mgc, 4),
        "l_servers": mmc_res["l_servers"],
        "l_total_mgc": round(l_total_mgc, 4),
        "w_q_mmc_baseline": mmc_res["w_q"]
    }

def priority_queue_two_class(
    c: int,
    lambda_1: float,
    lambda_2: float,
    mu: float
) -> Dict[str, Any]:
    """
    Two-class non-preemptive priority queue:
    Class 1: High priority (Emergency)
    Class 2: Low priority (Elective)
    
    Both classes share identical service rate mu across c servers.
    """
    lambda_total = lambda_1 + lambda_2
    rho_1 = lambda_1 / (c * mu)
    rho_2 = lambda_2 / (c * mu)
    rho_total = lambda_total / (c * mu)
    
    if rho_total >= 1.0:
        return {"is_stable": False, "rho_total": round(rho_total, 4)}
        
    p_delay = erlang_c(c, lambda_total, mu)
    # Expected delay before priority separation
    w_0 = p_delay / (c * mu)
    
    w_q1 = w_0 / (1.0 - rho_1)
    w_q2 = w_0 / ((1.0 - rho_1) * (1.0 - rho_total))
    
    return {
        "is_stable": True,
        "rho_1": round(rho_1, 4),
        "rho_2": round(rho_2, 4),
        "rho_total": round(rho_total, 4),
        "w_q_class1_emergency": round(w_q1, 4),
        "w_q_class2_elective": round(w_q2, 4),
        "total_mean_wait": round((lambda_1 * w_q1 + lambda_2 * w_q2) / lambda_total, 4)
    }
