"""
Automated verification script for all three Deep Dive modules.
Executes the mathematical models and checks numerical tolerances against the exact
parameters, tables, and narrative documented in deep_dives/.
"""
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np


def verify_deep_dive_1():
    print("[Deep Dive 1] Verifying Heavy-Tail Service & Allen-Cunneen Multiplier...")
    # Empirical SPARCS parameters
    E_S = 5.386
    Var_S = 57.771
    cv2 = Var_S / (E_S ** 2)
    multiplier = (1.0 + cv2) / 2.0
    
    assert abs(cv2 - 1.9915) < 0.001, f"cv2 mismatch: {cv2}"
    assert abs(multiplier - 1.4958) < 0.001, f"multiplier mismatch: {multiplier}"
    print(f"  PASS: cv2 = {cv2:.4f}, Allen-Cunneen Multiplier = {multiplier:.4f} (+{(multiplier-1)*100:.1f}% delay estimate).")


def verify_deep_dive_2():
    print("[Deep Dive 2] Verifying Bed Capacity Sizing & Priority Queue Metrics...")
    from src.queueing import erlang_b, priority_queue_two_class

    a = 269.3
    # Check c=269 (100% avg load) has 4.78% blocking
    p_block_269 = erlang_b(269, a)
    assert abs(p_block_269 - 0.0478) < 0.001, f"p_block_269 mismatch: {p_block_269}"
    
    # Check c=293 achieves <= 1% blocking (0.91%)
    p_block_293 = erlang_b(293, a)
    assert abs(p_block_293 - 0.0091) < 0.001, f"p_block_293 mismatch: {p_block_293}"
    assert p_block_293 <= 0.010, f"p_block_293 must be <= 0.01: {p_block_293}"
    
    # Square-root staffing check: c* approx a + beta * sqrt(a)
    beta = 1.45
    c_sqrt = a + beta * np.sqrt(a)
    assert abs(c_sqrt - 293.1) < 0.5, f"Square-root staffing mismatch: {c_sqrt}"

    # Priority queue metrics (c = 293, lambda1 = 30, lambda2 = 20, mu = 0.18567)
    c = 293
    res_prio = priority_queue_two_class(c, 30.0, 20.0, 0.18567)
    
    w1_days = res_prio["w_q_class1_emergency"]
    w2_days = res_prio["w_q_class2_elective"]
    wm_days = res_prio["total_mean_wait"]
    
    assert abs(w1_days - 0.0042) < 0.0005, f"Emergency wait mismatch: {w1_days}"
    assert abs(w2_days - 0.0517) < 0.0010, f"Elective wait mismatch: {w2_days}"
    assert abs(wm_days - 0.0232) < 0.0010, f"Mean wait mismatch: {wm_days}"
    
    # Verify aggregate work balance: (lambda1*W1 + lambda2*W2) / lambda_tot == Wm
    weighted_mean = (30.0 * w1_days + 20.0 * w2_days) / 50.0
    assert abs(weighted_mean - wm_days) < 1e-4, "Aggregate work balance violated"
    
    print(f"  PASS: Sizing c* = 293 (Buffer = +23.7 beds, B = {p_block_293*100:.2f}%).")
    print(f"  PASS: Priority queue heuristic: Emer = {w1_days*24*60:.1f}m ({w1_days*24:.2f}h), Elec = {w2_days*24*60:.1f}m ({w2_days*24:.2f}h), Mean = {wm_days*24*60:.1f}m.")


def verify_deep_dive_3():
    print("[Deep Dive 3] Verifying Diurnal PSA, 4-Station Jackson Network & Fox Allocation...")
    # 1. Diurnal peak-to-trough surge
    lam_bar = 2.0833
    amp = 1.1667
    lam_max = lam_bar + amp
    lam_min = lam_bar - amp
    ratio = lam_max / lam_min
    assert abs(ratio - 3.545) < 0.05, f"Peak-to-trough ratio mismatch: {ratio}"

    # 2. 4-Station Jackson Network (matching exact parameters in Deep Dive 3 document)
    from src.jackson_network import solve_traffic_equations, analyze_jackson_network
    jn_depts = ["ED", "ICU", "StepDown", "MedSurg"]
    jn_gamma = np.array([40.0, 2.0, 0.0, 15.0])
    jn_P = np.array([
        [0.00, 0.08, 0.12, 0.15],
        [0.00, 0.00, 0.60, 0.30],
        [0.00, 0.05, 0.00, 0.85],
        [0.00, 0.02, 0.00, 0.00]
    ])
    jn_capacities = [12, 25, 30, 120]
    jn_los_means = [1.0/6.0, 4.0, 3.0, 5.0]

    Lambda = solve_traffic_equations(jn_gamma, jn_P)
    
    # Assert traffic-balance equation: (I - P^T) * Lambda = gamma
    balance_recon = Lambda - jn_P.T @ Lambda
    assert np.allclose(balance_recon, jn_gamma, atol=1e-5), "Traffic balance equation violated"
    
    # Assert exact solved arrival rates
    assert abs(Lambda[0] - 40.000) < 0.001
    assert abs(Lambda[1] - 6.229) < 0.005
    assert abs(Lambda[2] - 8.538) < 0.005
    assert abs(Lambda[3] - 30.126) < 0.005

    jn_res = analyze_jackson_network(jn_depts, jn_gamma, jn_P, jn_capacities, jn_los_means)
    
    # Under nominal c_4 = 120 beds, MedSurg is overloaded (rho_4 = 1.2552 > 1.0)
    assert not jn_res.all_stations_stable, "Network should be unstable under c_4 = 120"
    assert jn_res.bottleneck_station == "MedSurg"
    assert abs(jn_res.bottleneck_utilization - 1.2552) < 0.005
    assert jn_res.total_patients_in_hospital == float("inf")
    assert jn_res.mean_end_to_end_los == float("inf")

    # 3. Fox Greedy Bed Allocation (matching C = 230 beds in Deep Dive 3 document)
    from src.bed_allocation import DepartmentSpec, marginal_bed_allocation, proportional_bed_allocation
    alloc_depts = [
        DepartmentSpec("ICU", 20.0, 4.0, 21),
        DepartmentSpec("Emergency", 30.0, 2.0, 31),
        DepartmentSpec("MedSurg", 150.0, 1.0, 151)
    ]
    opt_alloc = marginal_bed_allocation(alloc_depts, 230)
    prop_alloc = proportional_bed_allocation(alloc_depts, 230)
    
    # Verify exact optimal allocations
    assert opt_alloc.departments[0].beds == 33, f"ICU allocation mismatch: {opt_alloc.departments[0].beds}"
    assert opt_alloc.departments[1].beds == 43, f"ED allocation mismatch: {opt_alloc.departments[1].beds}"
    assert opt_alloc.departments[2].beds == 154, f"MedSurg allocation mismatch: {opt_alloc.departments[2].beds}"
    
    # Verify proportional allocations
    assert prop_alloc.departments[0].beds == 24, f"Proportional ICU mismatch: {prop_alloc.departments[0].beds}"
    assert prop_alloc.departments[1].beds == 34, f"Proportional ED mismatch: {prop_alloc.departments[1].beds}"
    assert prop_alloc.departments[2].beds == 172, f"Proportional MedSurg mismatch: {prop_alloc.departments[2].beds}"
    
    # Verify weighted losses
    assert abs(opt_alloc.total_weighted_blocking - 0.0655) < 0.001
    assert abs(prop_alloc.total_weighted_blocking - 0.4037) < 0.001
    
    loss_reduction = (1.0 - opt_alloc.total_weighted_blocking / prop_alloc.total_weighted_blocking) * 100.0
    assert abs(loss_reduction - 83.8) < 0.2

    print(f"  PASS: Peak-to-trough surge = {ratio:.2f}x.")
    print(f"  PASS: 4-station Jackson traffic balance verified (Lambda = [40.000, 6.229, 8.538, 30.126]).")
    print(f"  PASS: System instability correctly identified (MedSurg rho = {jn_res.bottleneck_utilization*100:.2f}% > 100%, Census = inf).")
    print(f"  PASS: Fox Allocation (C = 230): ICU = 33 beds (B = {opt_alloc.departments[0].blocking_prob*100:.2f}%), Loss reduction = {loss_reduction:.1f}%.")


if __name__ == "__main__":
    print("=" * 70)
    print(">>> VERIFYING DEEP-DIVE EXPANSIONS (EXACT DOCUMENTED SCENARIOS) <<<")
    print("=" * 70)
    verify_deep_dive_1()
    verify_deep_dive_2()
    verify_deep_dive_3()
    print("=" * 70)
    print(">>> ALL DEEP-DIVE CALCULATIONS MATHEMATICALLY VALIDATED <<<")
    print("=" * 70)
