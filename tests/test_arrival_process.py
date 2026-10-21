"""
Unit tests for Arrival Process and Non-Homogeneous Poisson Process (NHPP) analysis.
"""
import unittest
import numpy as np
import pandas as pd
from src.arrival_process import (
    index_of_dispersion_for_counts,
    fit_diurnal_arrival_intensity,
    simulate_nhpp_thinning
)

class TestArrivalProcess(unittest.TestCase):
    def test_index_of_dispersion_poisson(self):
        # Sample from Poisson with lambda = 20 -> Var/Mean should be ~ 1.0
        rng = np.random.default_rng(42)
        poisson_counts = rng.poisson(lam=20.0, size=2000)
        res = index_of_dispersion_for_counts(poisson_counts)
        
        self.assertAlmostEqual(res["index_of_dispersion"], 1.0, delta=0.15)
        self.assertTrue(res["is_homogeneous_poisson"])

    def test_index_of_dispersion_overdispersed(self):
        # Sample with high variance -> IDC > 1.25
        rng = np.random.default_rng(42)
        overdispersed = rng.negative_binomial(n=5, p=0.2, size=2000)
        res = index_of_dispersion_for_counts(overdispersed)
        
        self.assertGreater(res["index_of_dispersion"], 1.25)
        self.assertFalse(res["is_homogeneous_poisson"])

    def test_fit_diurnal_arrival_intensity(self):
        # Generate timestamps with peak around 14:00 (2 PM)
        rng = np.random.default_rng(42)
        hours = rng.normal(loc=14.0, scale=3.0, size=1000) % 24
        dts = [pd.Timestamp("2024-01-01") + pd.Timedelta(hours=float(h)) for h in hours]
        s = pd.Series(dts)
        
        fit_res = fit_diurnal_arrival_intensity(s)
        self.assertTrue(fit_res["fit_success"])
        self.assertGreater(fit_res["baseline_rate_per_hour"], 0.0)
        self.assertAlmostEqual(fit_res["peak_hour"], 14.0, delta=2.5)

    def test_simulate_nhpp_thinning(self):
        arrivals = simulate_nhpp_thinning(
            simulation_hours=48.0,
            baseline_rate=5.0,
            amplitude=2.0,
            peak_hour=14.0,
            random_seed=42
        )
        self.assertGreater(len(arrivals), 0)
        self.assertTrue((np.diff(arrivals) >= 0).all()) # Monotonically increasing timestamps

if __name__ == "__main__":
    unittest.main()
