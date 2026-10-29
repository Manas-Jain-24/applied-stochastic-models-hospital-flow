"""
Unit tests for Discrete-Event Simulation and Synthetic Data Generator.
"""
import unittest
from src.synthetic_generator import generate_synthetic_encounters, generate_synthetic_daily_census
from src.simulation import HospitalSimulation

class TestSimulationAndSynthetic(unittest.TestCase):
    def test_generate_synthetic_encounters(self):
        df = generate_synthetic_encounters(n_patients=500, random_seed=42)
        self.assertEqual(len(df), 500)
        self.assertIn("patient_id", df.columns)
        self.assertIn("data_provenance", df.columns)
        self.assertEqual(df["data_provenance"].iloc[0], "[SYNTHETIC_SIMULATED]")
        self.assertTrue((df["length_of_stay_days"] >= 1).all())

    def test_generate_synthetic_daily_census(self):
        df_enc = generate_synthetic_encounters(n_patients=200, random_seed=42)
        df_census = generate_synthetic_daily_census(df_enc, total_beds=50)
        self.assertGreater(len(df_census), 0)
        self.assertIn("occupied_beds", df_census.columns)
        self.assertIn("bed_utilization", df_census.columns)

    def test_hospital_simulation_run(self):
        sim = HospitalSimulation(
            n_beds=20,
            arrival_rate_per_day=4.0,
            mean_los_days=3.0,
            los_distribution="gamma",
            simulation_days=30.0,
            random_seed=42
        )
        res = sim.run()
        self.assertGreater(res["total_patients_simulated"], 0)
        self.assertGreaterEqual(res["empirical_bed_utilization"], 0.0)
        self.assertLessEqual(res["empirical_bed_utilization"], 1.0)

    def test_occupancy_uses_elapsed_time_including_final_interval(self):
        class FixedArrivals:
            def __init__(self):
                self.intervals = iter([1.0, 100.0])

            def exponential(self, scale):
                return next(self.intervals)

        sim = HospitalSimulation(
            n_beds=1, arrival_rate_per_day=1.0, mean_los_days=3.0,
            los_distribution="deterministic", simulation_days=10.0,
        )
        sim.rng = FixedArrivals()
        result = sim.run()
        # One bed is occupied from day 1 to day 4: 3 of 10 bed-days.
        self.assertEqual(result["empirical_mean_occupied_beds"], 0.3)
        self.assertEqual(result["empirical_bed_utilization"], 0.3)
        self.assertEqual(result["max_queue_depth"], 0)

if __name__ == "__main__":
    unittest.main()
