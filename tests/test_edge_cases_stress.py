"""
Comprehensive Boundary, Stress, and Edge-Case Test Suite for Hospital Patient Flow Pipeline.
Covers:
- Boundary conditions (zero loads, infinite capacity, severe overloads, heavy tails)
- Mathematical consistency (Little's Law, Erlang-B/Erlang-C relations, conservation laws)
- Stability detection (unstable queues, bottlenecks, infinite queues)
- App-level functions (PDF compilation, Fox Knapsack, Erlang-A abandonment)
- Error handling (invalid matrix dimensions, negative parameters, empty data)
"""
import io
import math
import unittest
import numpy as np
import pandas as pd

from src.queueing import (
    erlang_b,
    erlang_c,
    min_capacity_erlang_b,
    mmc_performance_metrics,
    mgc_allen_cunneen,
    mmck_finite_buffer_metrics,
    priority_queue_two_class
)
from src.jackson_network import (
    solve_traffic_equations,
    analyze_jackson_network,
    StationResult,
    NetworkResult
)
from src.bed_allocation import (
    DepartmentSpec,
    marginal_bed_allocation,
    proportional_bed_allocation,
    compute_capacity_expansion_frontier
)
from src.time_varying import (
    diurnal_arrival_rate,
    run_pointwise_stationary_approximation
)
from src.distributions import (
    compute_empirical_moments,
    fit_candidate_distributions,
    rank_distribution_models
)
from src.arrival_process import (
    index_of_dispersion_for_counts,
    diurnal_sinusoidal_rate,
    simulate_nhpp_thinning
)
from src.simulation import HospitalSimulation
from src.priority_simulation import PriorityHospitalSimulation

from src.app_engine import (
    calc_erlang_b,
    calc_erlang_c,
    calc_erlang_a,
    calc_fox_allocation,
    generate_custom_executive_pdf
)


class TestQueueingEdgeCases(unittest.TestCase):
    """Stress testing analytical queueing models under extreme boundary conditions."""

    def test_erlang_b_extreme_inputs(self):
        # c=0 -> 1.0
        self.assertEqual(erlang_b(0, 100.0), 1.0)
        # a=0 -> 0.0
        self.assertEqual(erlang_b(10, 0.0), 0.0)
        # Negative parameters should raise ValueError
        with self.assertRaises(ValueError):
            erlang_b(-1, 5.0)
        with self.assertRaises(ValueError):
            erlang_b(5, -1.0)
        # Very high capacity with small load -> virtually 0
        b_large = erlang_b(200, 20.0)
        self.assertAlmostEqual(b_large, 0.0, places=10)
        # High load with small capacity -> very close to 1
        b_overload = erlang_b(2, 500.0)
        self.assertGreater(b_overload, 0.99)

    def test_min_capacity_erlang_b_boundaries(self):
        # Target blocking 100% -> minimum capacity is 0 or 1
        c_loose = min_capacity_erlang_b(10.0, target_blocking=0.99)
        self.assertLessEqual(c_loose, 5)
        # Strict blocking requires higher capacity
        c_strict = min_capacity_erlang_b(10.0, target_blocking=0.001)
        self.assertGreater(c_strict, c_loose)
        # Offered load zero -> capacity is minimal
        c_zero = min_capacity_erlang_b(0.0, target_blocking=0.01)
        self.assertEqual(c_zero, 1)

    def test_erlang_c_instability_and_boundaries(self):
        # Unstable system (rho >= 1.0) must return 1.0
        self.assertEqual(erlang_c(c=10, arrival_rate=10.0, service_rate=1.0), 1.0)
        self.assertEqual(erlang_c(c=10, arrival_rate=15.0, service_rate=1.0), 1.0)
        # Near critical traffic (rho = 0.99)
        p_crit = erlang_c(c=10, arrival_rate=9.9, service_rate=1.0)
        self.assertGreater(p_crit, 0.8)
        self.assertLessEqual(p_crit, 1.0)
        # Invalid parameters raise ValueError
        with self.assertRaises(ValueError):
            erlang_c(c=0, arrival_rate=5.0, service_rate=1.0)
        with self.assertRaises(ValueError):
            erlang_c(c=5, arrival_rate=-1.0, service_rate=1.0)
        with self.assertRaises(ValueError):
            erlang_c(c=5, arrival_rate=5.0, service_rate=0.0)

    def test_mmc_unstable_system_returns_clean_metrics(self):
        # When rho >= 1.0, mmc_performance_metrics must return is_stable=False and inf
        res = mmc_performance_metrics(c=5, arrival_rate=6.0, service_rate=1.0)
        self.assertFalse(res["is_stable"])
        self.assertEqual(res["p_delay"], 1.0)
        self.assertEqual(res["w_q"], float("inf"))
        self.assertEqual(res["l_q"], float("inf"))
        self.assertEqual(res["l_total"], float("inf"))
        self.assertEqual(res["l_servers"], 5)

    def test_mgc_allen_cunneen_extremes(self):
        # Unstable case propagates cleanly
        unstable = mgc_allen_cunneen(c=5, arrival_rate=6.0, service_rate=1.0, cv2_service=2.0)
        self.assertFalse(unstable["is_stable"])
        # Deterministic service (cv2 = 0) reduces wait by half: factor = (1 + 0)/2 = 0.5
        det = mgc_allen_cunneen(c=10, arrival_rate=8.0, service_rate=1.0, cv2_service=0.0)
        self.assertTrue(det["is_stable"])
        self.assertAlmostEqual(det["correction_factor"], 0.5)
        self.assertAlmostEqual(det["w_q_mgc"], 0.5 * det["w_q_mmc_baseline"], places=3)
        # Extreme heavy-tail (cv2 = 10.0): factor = (1 + 10)/2 = 5.5
        heavy = mgc_allen_cunneen(c=10, arrival_rate=8.0, service_rate=1.0, cv2_service=10.0)
        self.assertAlmostEqual(heavy["correction_factor"], 5.5)
        self.assertAlmostEqual(heavy["w_q_mgc"], 5.5 * heavy["w_q_mmc_baseline"], places=3)

    def test_mmck_finite_buffer_exact_erlang_b_equivalence(self):
        # When K == c, buffer is 0 -> exact Erlang-B loss system
        mmck = mmck_finite_buffer_metrics(c=12, k_capacity=12, arrival_rate=10.0, service_rate=1.0)
        eb = erlang_b(12, 10.0)
        self.assertAlmostEqual(mmck["prob_loss_diversion"], eb, places=4)
        self.assertEqual(mmck["l_q"], 0.0)
        self.assertEqual(mmck["w_q_days"], 0.0)
        self.assertEqual(mmck["max_queue_buffer"], 0)

    def test_mmck_invalid_and_overload(self):
        # K < c must raise ValueError
        with self.assertRaises(ValueError):
            mmck_finite_buffer_metrics(c=10, k_capacity=9, arrival_rate=5.0, service_rate=1.0)
        # Negative parameters raise ValueError
        with self.assertRaises(ValueError):
            mmck_finite_buffer_metrics(c=10, k_capacity=15, arrival_rate=-5.0, service_rate=1.0)
        # Severe overload (rho = 10.0) does not crash and respects Little's Law
        overload = mmck_finite_buffer_metrics(c=2, k_capacity=10, arrival_rate=20.0, service_rate=1.0)
        self.assertGreater(overload["prob_loss_diversion"], 0.8)
        self.assertAlmostEqual(overload["l_q"], overload["effective_arrival_rate"] * overload["w_q_days"], places=3)

    def test_priority_queue_overload_behavior(self):
        # When total arrival rate >= c * mu, must report is_stable=False without ZeroDivisionError
        res = priority_queue_two_class(c=5, lambda_1=3.0, lambda_2=3.0, mu=1.0)
        self.assertFalse(res["is_stable"])
        self.assertGreaterEqual(res["rho_total"], 1.0)


class TestJacksonNetworkEdgeCases(unittest.TestCase):
    """Stress testing multi-department Jackson network models."""

    def test_single_station_network(self):
        # M=1 station
        names = ["SingleWard"]
        gamma = [10.0]
        P = np.array([[0.2]])  # 20% feedback, 80% discharge
        capacities = [20]
        los = [1.0]

        # Lambda = 10 / (1 - 0.2) = 12.5
        lam = solve_traffic_equations(np.array(gamma), P)
        self.assertAlmostEqual(lam[0], 12.5, places=3)

        net_res = analyze_jackson_network(names, gamma, P, capacities, los)
        self.assertTrue(net_res.all_stations_stable)
        self.assertEqual(net_res.bottleneck_station, "SingleWard")
        self.assertAlmostEqual(net_res.bottleneck_utilization, 12.5 / 20.0, places=3)

    def test_unstable_bottleneck_detection(self):
        # Network where station 2 is severely undersized (rho > 1.0)
        names = ["ED", "OverloadedICU"]
        gamma = [20.0, 0.0]
        P = np.array([
            [0.0, 0.8],  # 80% ED -> ICU
            [0.0, 0.0]   # ICU -> Discharge
        ])
        capacities = [30, 5]  # ICU only has 5 beds, but receives 16 pts/day with LOS 1 day -> rho = 3.2!
        los = [1.0, 1.0]

        res = analyze_jackson_network(names, gamma, P, capacities, los)
        self.assertFalse(res.all_stations_stable)
        self.assertEqual(res.bottleneck_station, "OverloadedICU")
        self.assertGreater(res.bottleneck_utilization, 1.0)
        self.assertEqual(res.mean_end_to_end_los, float("inf"))

    def test_invalid_routing_matrix_raises(self):
        # Row sum > 1.0 must raise ValueError
        with self.assertRaises(ValueError):
            solve_traffic_equations(np.array([10.0, 5.0]), np.array([[0.8, 0.5], [0.1, 0.2]]))


class TestBedAllocationEdgeCases(unittest.TestCase):
    """Testing optimal knapsack bed sizing across departments."""

    def test_exact_minimum_budget(self):
        depts = [
            DepartmentSpec("ED", offered_load=20.0, weight=1.0, min_beds=15),
            DepartmentSpec("ICU", offered_load=30.0, weight=2.0, min_beds=25),
            DepartmentSpec("Floor", offered_load=150.0, weight=0.5, min_beds=140),
        ]
        # Total beds = exact sum of minimums (180)
        res = marginal_bed_allocation(depts, total_beds=180)
        self.assertEqual(res.total_beds, 180)
        for d in res.departments:
            if d.name == "ED":
                self.assertEqual(d.beds, 15)
            elif d.name == "ICU":
                self.assertEqual(d.beds, 25)
            elif d.name == "Floor":
                self.assertEqual(d.beds, 140)

    def test_budget_below_minimum_raises(self):
        depts = [DepartmentSpec("ICU", offered_load=10.0, weight=1.0, min_beds=15)]
        with self.assertRaises(ValueError):
            marginal_bed_allocation(depts, total_beds=10)

    def test_clinical_priority_weighting(self):
        # Two identical departments, but Dept B has 100x higher clinical priority weight
        depts = [
            DepartmentSpec("LowPriority", offered_load=20.0, weight=1.0, min_beds=15),
            DepartmentSpec("HighPriority", offered_load=20.0, weight=100.0, min_beds=15),
        ]
        res = marginal_bed_allocation(depts, total_beds=40)
        beds_low = [d.beds for d in res.departments if d.name == "LowPriority"][0]
        beds_high = [d.beds for d in res.departments if d.name == "HighPriority"][0]
        self.assertGreater(beds_high, beds_low)


class TestAppMathAndExportEdgeCases(unittest.TestCase):
    """Testing algorithms embedded inside app.py and dynamic PDF briefing export."""

    def test_calc_erlang_b_zero_and_negative(self):
        self.assertEqual(calc_erlang_b(0, 10.0), 1.0)
        self.assertEqual(calc_erlang_b(10, 0.0), 0.0)
        self.assertEqual(calc_erlang_b(10, -5.0), 0.0)
        self.assertAlmostEqual(calc_erlang_b(10, 5.0), erlang_b(10, 5.0), places=5)

    def test_calc_erlang_c_zero_load_returns_zero(self):
        # Mathematical verification: 0 offered load means 0 probability of waiting
        self.assertEqual(calc_erlang_c(10, 0.0), 0.0)
        self.assertEqual(calc_erlang_c(0, 10.0), 1.0)
        self.assertEqual(calc_erlang_c(10, 15.0), 1.0)  # Overload
        self.assertAlmostEqual(calc_erlang_c(10, 8.0), erlang_c(10, 8.0, 1.0), places=4)

    def test_calc_erlang_a_abandonment_safety(self):
        # Zero load or negative rates return safe zero metrics
        res_zero = calc_erlang_a(c=10, a=0.0, theta=1.0)
        self.assertEqual(res_zero["p_wait"], 0.0)
        self.assertEqual(res_zero["walkouts_per_hour"], 0.0)
        # Normal overloaded system (rho = 1.2) self-stabilizes
        res_over = calc_erlang_a(c=10, a=12.0, theta=1.0)
        self.assertGreater(res_over["walkouts_per_hour"], 0.0)
        self.assertLessEqual(res_over["p_renege"], 1.0)

    def test_calc_fox_allocation_safeguards(self):
        loads = (24.0, 34.0, 172.0)
        # Standard budget allocation
        alloc_230 = calc_fox_allocation(230, loads)
        self.assertEqual(sum(alloc_230), 230)
        # Decreased budget
        alloc_200 = calc_fox_allocation(200, loads)
        self.assertEqual(sum(alloc_200), 200)
        self.assertLessEqual(alloc_200[0], alloc_230[0])
        # Very small budget clamped to len(loads)
        alloc_small = calc_fox_allocation(2, loads)
        self.assertEqual(sum(alloc_small), 3)

    def test_generate_custom_executive_pdf_validity(self):
        params = {
            "scenario_name": "Edge Case Academic Center",
            "lam": 50.0,
            "los": 4.8,
            "beds": 240,
            "a": 240.0,
            "rho": 100.0,
            "wait_mmc": 99.0,
            "wait_mgc": 99.0,
            "div_pct": 12.5,
            "div_daily": 60.0,
        }
        pdf_bytes = generate_custom_executive_pdf(params)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 2000)
        # Check standard PDF header and trailer magic bytes
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))
        self.assertTrue(b"%%EOF" in pdf_bytes)


class TestDistributionsAndMomentsEdgeCases(unittest.TestCase):
    """Testing empirical moment calculations and distributions."""

    def test_empty_and_single_element_moments(self):
        # Empty array
        res_empty = compute_empirical_moments(np.array([]))
        self.assertEqual(res_empty["n_samples"], 0)
        self.assertEqual(res_empty["mean"], 0.0)
        self.assertEqual(res_empty["cv2"], 0.0)
        # Single element array
        res_single = compute_empirical_moments(np.array([4.5]))
        self.assertEqual(res_single["n_samples"], 1)
        self.assertEqual(res_single["mean"], 4.5)
        self.assertEqual(res_single["variance"], 0.0)
        # All NaN or negative values
        res_nan = compute_empirical_moments(np.array([np.nan, -2.0, 0.0]))
        self.assertEqual(res_nan["n_samples"], 0)

    def test_constant_array_zero_variance(self):
        res_const = compute_empirical_moments(np.array([5.0, 5.0, 5.0, 5.0, 5.0]))
        self.assertEqual(res_const["mean"], 5.0)
        self.assertEqual(res_const["variance"], 0.0)
        self.assertEqual(res_const["cv2"], 0.0)


class TestSimulationEdgeCases(unittest.TestCase):
    """Testing simulation classes with boundary parameters."""

    def test_hospital_simulation_input_validation(self):
        with self.assertRaises(ValueError):
            HospitalSimulation(n_beds=0)
        with self.assertRaises(ValueError):
            HospitalSimulation(simulation_days=0)
        with self.assertRaises(ValueError):
            HospitalSimulation(arrival_rate_per_day=-5.0)

    def test_priority_simulation_boundary_validation(self):
        with self.assertRaises(ValueError):
            PriorityHospitalSimulation(c=0)
        with self.assertRaises(ValueError):
            PriorityHospitalSimulation(sim_days=50.0, warmup_days=60.0)
        with self.assertRaises(ValueError):
            PriorityHospitalSimulation(lambda_emergency=-1.0)


if __name__ == "__main__":
    unittest.main()
