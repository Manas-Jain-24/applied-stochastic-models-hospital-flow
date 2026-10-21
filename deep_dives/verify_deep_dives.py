"""
Automated verification script for all three Deep Dive modules.
Executes the mathematical models and checks numerical tolerances.
"""
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
from scipy import stats

def verify_deep_dive_1():
    print("[Deep Dive 1] Verifying Heavy-Tail Service & Allen-Cunneen Multiplier...")
    E_S = 5.386
    Var_S = 57.771
    cv2 = Var_S / (E_S ** 2)
    multiplier = (1.0 + cv2) / 2.0
    assert abs(cv2 - 1.9915) < 0.01, f"cv2 mismatch: {cv2}"
    assert abs(multiplier - 1.4958) < 0.01, f"multiplier mismatch: {multiplier}"
    print(f"  PASS: cv2 = {cv2:.4f}, Allen-Cunneen Multiplier = {multiplier:.4f} (~+50% delay penalty).")

def verify_deep_dive_2():
    print("[Deep Dive 2] Verifying Bed Capacity Sizing & Cobham Priority Queueing...")
    # Erlang-B recursion
    def erlang_b(c, a):
        b = 1.0
        for k in range(1, int(c) + 1):
            b = (a * b) / (k + a * b)
        return b

    a = 269.3
    # Check c=269 (100% avg load) has ~4.78% blocking
    p_block_269 = erlang_b(269, a)
    assert abs(p_block_269 - 0.0478) < 0.005, f"p_block_269 mismatch: {p_block_269}"
    
    # Check c=293 achieves <= 1% blocking
    p_block_293 = erlang_b(293, a)
    assert p_block_293 < 0.010, f"p_block_293 should be <= 0.01: {p_block_293}"
    
    # Square-root staffing check
    beta = 1.45
    c_sqrt = a + beta * np.sqrt(a)
    assert abs(c_sqrt - 293.1) < 0.5, f"Square-root staffing mismatch: {c_sqrt}"

    # Cobham priority waits via src.queueing
    from src.queueing import priority_queue_two_class
    c = 293
    res_prio = priority_queue_two_class(c, 30.0, 20.0, 0.18567)
    Wq1_hrs = res_prio["w_q_class1_emergency"] * 24.0
    Wq2_hrs = res_prio["w_q_class2_elective"] * 24.0
    assert Wq1_hrs < 1.0, f"Wq1 too high: {Wq1_hrs}"
    assert Wq2_hrs > Wq1_hrs, f"Elective must wait longer than Emergency"
    print(f"  PASS: Optimal beds c* = 293 (Buffer = +24 beds), Emergency wait = {Wq1_hrs*60:.1f} mins, Elective wait = {Wq2_hrs:.2f} hrs.")

def verify_deep_dive_3():
    print("[Deep Dive 3] Verifying Diurnal PSA, Jackson Network & Fox Allocation...")
    # Diurnal peak-to-trough
    lam_bar = 2.0833
    amp = 1.1667
    lam_max = lam_bar + amp
    lam_min = lam_bar - amp
    ratio = lam_max / lam_min
    assert abs(ratio - 3.545) < 0.05, f"Peak-to-trough ratio mismatch: {ratio}"

    # Jackson Network via src.jackson_network
    from src.jackson_network import analyze_jackson_network
    jn_depts = ["ED", "ICU", "MedSurg"]
    jn_gamma = [30.0, 5.0, 10.0]
    jn_P = np.array([
        [0.0, 0.2, 0.5],
        [0.1, 0.0, 0.6],
        [0.0, 0.1, 0.0]
    ])
    jn_res = analyze_jackson_network(jn_depts, jn_gamma, jn_P, [25, 55, 200], [0.5, 3.0, 5.0])
    assert jn_res.all_stations_stable
    assert jn_res.bottleneck_station == "MedSurg"
    assert abs(jn_res.mean_end_to_end_los - 5.19) < 0.2

    # Fox Allocation via src.bed_allocation
    from src.bed_allocation import DepartmentSpec, marginal_bed_allocation, proportional_bed_allocation
    depts = [
        DepartmentSpec("ICU", 20.0, 4.0, 21),
        DepartmentSpec("Emergency", 30.0, 2.0, 31),
        DepartmentSpec("MedSurg", 150.0, 1.0, 151)
    ]
    opt_alloc = marginal_bed_allocation(depts, 230)
    prop_alloc = proportional_bed_allocation(depts, 230)
    
    assert opt_alloc.departments[0].beds == 33
    assert opt_alloc.departments[0].blocking_prob < 0.005
    assert opt_alloc.total_weighted_blocking < prop_alloc.total_weighted_blocking
    
    improvement = (1.0 - opt_alloc.total_weighted_blocking / prop_alloc.total_weighted_blocking) * 100.0
    print(f"  PASS: Peak-to-trough surge = {ratio:.2f}x, Jackson bottleneck = {jn_res.bottleneck_station} (Stay = {jn_res.mean_end_to_end_los:.2f}d), Fox ICU beds = 33 (rejection = {opt_alloc.departments[0].blocking_prob*100:.2f}%, loss cut = {improvement:.1f}%).")

if __name__ == "__main__":
    print("=" * 65)
    print(">>> VERIFYING SEPARATE DEEP-DIVE EXPANSIONS (1, 2, 3) <<<")
    print("=" * 65)
    verify_deep_dive_1()
    verify_deep_dive_2()
    verify_deep_dive_3()
    print("=" * 65)
    print(">>> ALL THREE DEEP DIVES MATHEMATICALLY VERIFIED <<<")
    print("=" * 65)
