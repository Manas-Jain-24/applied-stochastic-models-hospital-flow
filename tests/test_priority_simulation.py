"""
Unit tests for Two-Class Multi-Server Priority Discrete-Event Simulation.
"""
import unittest
from src.priority_simulation import PriorityHospitalSimulation, run_priority_replications


class TestPrioritySimulation(unittest.TestCase):
    def test_single_priority_simulation_run(self):
        """Verify single run outputs expected structure and non-negative waits."""
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

    def test_multi_replication_runner(self):
        """Verify multi-replication runner aggregates confidence intervals properly."""
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
        self.assertIn("emergency_wait_mins", summary)
        self.assertIn("elective_wait_mins", summary)
        self.assertIn("ci_95", summary["emergency_wait_mins"])
        self.assertGreater(summary["avg_patients_total"], 0)


if __name__ == "__main__":
    unittest.main()
