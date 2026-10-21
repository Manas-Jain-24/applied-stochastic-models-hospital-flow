"""
Unit tests for distribution fitting using Python's built-in unittest.
"""
import unittest
import numpy as np
from src.distributions import compute_empirical_moments, fit_candidate_distributions

class TestDistributions(unittest.TestCase):
    def test_compute_empirical_moments(self):
        rng = np.random.default_rng(42)
        sample = rng.exponential(scale=4.0, size=5000)
        moments = compute_empirical_moments(sample)
        
        self.assertAlmostEqual(moments["mean"], 4.0, delta=0.2)
        self.assertAlmostEqual(moments["cv2"], 1.0, delta=0.15)
        self.assertTrue(moments["is_memoryless_candidate"])

    def test_fit_candidate_distributions(self):
        rng = np.random.default_rng(42)
        sample = rng.gamma(shape=2.5, scale=2.0, size=1000)
        fits = fit_candidate_distributions(sample)
        
        self.assertIn("Gamma", fits)
        self.assertTrue(fits["Gamma"]["fit_success"])
        self.assertGreater(fits["Gamma"]["aic"], 0)
        self.assertGreater(fits["Gamma"]["ks_pvalue"], 0.01)

if __name__ == "__main__":
    unittest.main()
