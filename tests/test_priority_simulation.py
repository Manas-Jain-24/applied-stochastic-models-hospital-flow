"""
Unit tests for Two-Class Multi-Server Priority Discrete-Event Simulation.
Validates non-preemptive queueing, arrival horizon separation, queue draining,
censoring elimination, and input parameter checking.
"""
import unittest
from src.priority_simulation import PriorityHospitalSimulation, run_priority_replications


class TestPrioritySimulation(unittest.TestCase):
    def test_single_priority_simulation_run(self):
        """Verify single run outputs expected structure, drain stats, and non-negative waits."""
        sim = PriorityHospitalSimulation(
            c=20,
            lambda_emergency=3.0,
            lambda_elective=2.0,
            mu=0.30,
            sim_days=60.0,
            warmup_days=10.0,
            seed=42
        )
        res = sim.run()
        self.assertGreater(res["n_emergency"], 0)
        self.assertGreater(res["n_elective"], 0)
        self.assertGreaterEqual(res["wq_emergency_mins"], 0.0)
        self.assertGreaterEqual(res["wq_elective_mins"], 0.0)
        # Priority discipline should result in elective wait >= emergency wait
        self.assertGreaterEqual(res["wq_elective_mins"], res["wq_emergency_mins"])
        self.assertEqual(res["arrival_horizon_days"], 60.0)
        self.assertGreaterEqual(res["drain_end_days"], 60.0)
        self.assertEqual(res["censored_patients_total"], 0)

    def test_congested_drain_after_arrival_horizon(self):
        """Prove that a heavily congested queue drains remaining patients after the arrival horizon."""
        # Heavily overloaded: 2 beds, offered load a = (5.0 + 5.0) / 0.5 = 20.0 >> 2 beds
        sim = PriorityHospitalSimulation(
            c=2,
            lambda_emergency=5.0,
            lambda_elective=5.0,
            mu=0.5,
            sim_days=10.0,
            warmup_days=2.0,
            seed=999
        )
        res = sim.run()
        # Arrival horizon was 10.0 days; draining queued patients should extend past 10.0 days
        self.assertGreater(res["drain_end_days"], res["arrival_horizon_days"])
        # All post-warmup arrivals must be observed entering service after drain (0 censored)
        self.assertEqual(res["censored_patients_total"], 0)
        self.assertEqual(res["post_warmup_arrivals_emergency"], res["observed_service_starts_emergency"])
        self.assertEqual(res["post_warmup_arrivals_elective"], res["observed_service_starts_elective"])

    def test_post_warmup_arrivals_equal_wait_samples(self):
        """Verify post-warmup arrivals strictly match recorded class wait samples after draining."""
        sim = PriorityHospitalSimulation(
            c=30,
            lambda_emergency=4.0,
            lambda_elective=3.0,
            mu=0.25,
            sim_days=100.0,
            warmup_days=20.0,
            seed=777
        )
        res = sim.run()
        self.assertEqual(res["post_warmup_arrivals_emergency"], res["observed_service_starts_emergency"])
        self.assertEqual(res["post_warmup_arrivals_elective"], res["observed_service_starts_elective"])
        self.assertEqual(res["n_total"], res["post_warmup_arrivals_emergency"] + res["post_warmup_arrivals_elective"])
        self.assertEqual(res["censored_patients_emergency"], 0)
        self.assertEqual(res["censored_patients_elective"], 0)
        self.assertEqual(res["censored_patients_total"], 0)

    def test_multi_replication_runner(self):
        """Verify multi-replication runner aggregates confidence intervals and drain metrics."""
        summary = run_priority_replications(
            n_replications=3,
            c=25,
            lambda_emergency=3.0,
            lambda_elective=2.0,
            mu=0.25,
            sim_days=60.0,
            warmup_days=10.0,
            base_seed=100
        )
        self.assertEqual(summary["n_replications"], 3)
        self.assertEqual(summary["total_censored_patients"], 0)
        self.assertIn("emergency_wait_mins", summary)
        self.assertIn("elective_wait_mins", summary)
        self.assertIn("ci_95", summary["emergency_wait_mins"])
        self.assertGreater(summary["avg_patients_total"], 0)
        self.assertGreaterEqual(summary["max_drain_end_days"], summary["arrival_horizon_days"])

    def test_invalid_parameters_validation(self):
        """Verify input validation raises ValueError on illegal configurations."""
        # Non-positive or non-integer capacity c
        with self.assertRaises(ValueError):
            PriorityHospitalSimulation(c=0)
        with self.assertRaises(ValueError):
            PriorityHospitalSimulation(c=-5)
        with self.assertRaises(ValueError):
            PriorityHospitalSimulation(c=2.5)  # type: ignore

        # Non-positive arrival rates
        with self.assertRaises(ValueError):
            PriorityHospitalSimulation(lambda_emergency=0)
        with self.assertRaises(ValueError):
            PriorityHospitalSimulation(lambda_emergency=-1.0)
        with self.assertRaises(ValueError):
            PriorityHospitalSimulation(lambda_elective=0)
        with self.assertRaises(ValueError):
            PriorityHospitalSimulation(lambda_elective=-2.0)

        # Non-positive service rate
        with self.assertRaises(ValueError):
            PriorityHospitalSimulation(mu=0)
        with self.assertRaises(ValueError):
            PriorityHospitalSimulation(mu=-0.5)

        # Illegal warm-up or simulation horizon
        with self.assertRaises(ValueError):
            PriorityHospitalSimulation(warmup_days=-1.0)
        with self.assertRaises(ValueError):
            PriorityHospitalSimulation(sim_days=50.0, warmup_days=50.0)
        with self.assertRaises(ValueError):
            PriorityHospitalSimulation(sim_days=30.0, warmup_days=50.0)

        # Invalid replication count
        with self.assertRaises(ValueError):
            run_priority_replications(n_replications=0)
        with self.assertRaises(ValueError):
            run_priority_replications(n_replications=-3)
        with self.assertRaises(ValueError):
            run_priority_replications(n_replications=2.5)  # type: ignore


if __name__ == "__main__":
    unittest.main()
