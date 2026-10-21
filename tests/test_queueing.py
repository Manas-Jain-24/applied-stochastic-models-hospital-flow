"""
Unit tests for analytical queueing models using Python's built-in unittest.
"""
import unittest
from src.queueing import (
    erlang_b,
    min_capacity_erlang_b,
    erlang_c,
    mmc_performance_metrics,
    mgc_allen_cunneen,
    mmck_finite_buffer_metrics
)


class TestQueueingModels(unittest.TestCase):
    def test_erlang_b_boundary_conditions(self):
        # Zero servers -> 100% blocking
        self.assertEqual(erlang_b(0, 5.0), 1.0)
        # Zero load -> 0% blocking
        self.assertEqual(erlang_b(5, 0.0), 0.0)
        # Monotonicity: higher capacity reduces blocking
        b_5 = erlang_b(5, 4.0)
        b_6 = erlang_b(6, 4.0)
        self.assertLess(b_6, b_5)

    def test_min_capacity_erlang_b(self):
        c = min_capacity_erlang_b(10.0, target_blocking=0.01)
        self.assertGreater(c, 10)
        self.assertLessEqual(erlang_b(c, 10.0), 0.01)
        self.assertGreater(erlang_b(c - 1, 10.0), 0.01)

    def test_erlang_c_and_littles_law(self):
        metrics = mmc_performance_metrics(c=10, arrival_rate=8.0, service_rate=1.0)
        self.assertTrue(metrics["is_stable"])
        self.assertEqual(metrics["rho"], 0.8)
        self.assertGreater(metrics["p_delay"], 0.0)
        self.assertLess(metrics["p_delay"], 1.0)
        # Little's Law verification: L_q == lambda * W_q
        self.assertAlmostEqual(metrics["l_q"], 8.0 * metrics["w_q"], places=3)
        # L_total == L_q + L_servers
        self.assertAlmostEqual(metrics["l_total"], metrics["l_q"] + metrics["l_servers"], places=3)

    def test_mgc_heavy_tail_penalty(self):
        # When cv^2 > 1, M/G/c queue delay must be strictly greater than M/M/c baseline
        res = mgc_allen_cunneen(c=10, arrival_rate=8.0, service_rate=1.0, cv2_service=2.0)
        self.assertGreater(res["w_q_mgc"], res["w_q_mmc_baseline"])
        # Correction factor for cv_arrival^2=1 and cv_service^2=2 is (1 + 2)/2 = 1.5
        self.assertAlmostEqual(res["correction_factor"], 1.5, places=4)

    def test_mmck_finite_buffer(self):
        # c=5, K=8, arrival=4, service=1
        res = mmck_finite_buffer_metrics(c=5, k_capacity=8, arrival_rate=4.0, service_rate=1.0)
        self.assertGreaterEqual(res["prob_loss_diversion"], 0.0)
        self.assertLessEqual(res["prob_loss_diversion"], 1.0)
        self.assertLessEqual(res["effective_arrival_rate"], 4.0)
        # Little's Law check: L_q == lambda_eff * W_q
        self.assertAlmostEqual(res["l_q"], res["effective_arrival_rate"] * res["w_q_days"], places=3)

    def test_priority_queue_two_class(self):
        from src.queueing import priority_queue_two_class
        prio = priority_queue_two_class(c=10, lambda_1=4.0, lambda_2=4.0, mu=1.0)
        self.assertTrue(prio["is_stable"])
        # Class 1 (Emergency) delay must be strictly shorter than Class 2 (Elective) delay
        self.assertLess(prio["w_q_class1_emergency"], prio["w_q_class2_elective"])

if __name__ == "__main__":
    unittest.main()

