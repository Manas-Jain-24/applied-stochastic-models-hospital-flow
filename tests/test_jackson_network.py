"""
Unit tests for Jackson Queueing Network Model.
"""

import unittest
import numpy as np

from src.jackson_network import solve_traffic_equations, analyze_jackson_network


class TestJacksonNetwork(unittest.TestCase):
    """Test Jackson queueing network solver and metrics."""

    def setUp(self):
        self.depts = ["ED", "ICU", "MedSurg"]
        self.gamma = [30.0, 5.0, 10.0]
        self.P = np.array([
            [0.0, 0.2, 0.5],
            [0.1, 0.0, 0.6],
            [0.0, 0.1, 0.0]
        ])
        self.capacities = [25, 55, 200]
        self.los_means = [0.5, 3.0, 5.0]

    def test_solve_traffic_equations_linear_system(self):
        """Verify (I - P^T) * Lambda = gamma."""
        gamma_arr = np.array(self.gamma, dtype=np.float64)
        Lambda = solve_traffic_equations(gamma_arr, self.P)

        # Reconstructed gamma should match original gamma
        gamma_recon = Lambda - self.P.T @ Lambda
        np.testing.assert_allclose(gamma_recon, gamma_arr, rtol=1e-5)
        # Lambda must be strictly greater than direct external arrivals
        self.assertTrue(np.all(Lambda >= gamma_arr))

    def test_jackson_network_metrics_and_littles_law(self):
        """Verify Jackson network stability and network Little's law: L_total = gamma_total * W_total."""
        res = analyze_jackson_network(self.depts, self.gamma, self.P, self.capacities, self.los_means)

        self.assertTrue(res.all_stations_stable)
        self.assertIn(res.bottleneck_station, self.depts)
        self.assertLess(res.bottleneck_utilization, 1.0)

        # Network-level Little's law verification
        expected_w_total = res.total_patients_in_hospital / res.total_exogenous_arrival
        self.assertAlmostEqual(res.mean_end_to_end_los, expected_w_total, places=2)

        # Station-level Little's law
        for st in res.stations:
            expected_l = st.arrival_rate * st.mean_dwell_time
            self.assertAlmostEqual(st.mean_patients, expected_l, places=2)

    def test_overloaded_station_detection(self):
        """Verify that an undersized station is flagged as unstable with infinite queue delay."""
        undersized_caps = [5, 5, 20]  # Grossly inadequate
        res = analyze_jackson_network(self.depts, self.gamma, self.P, undersized_caps, self.los_means)

        self.assertFalse(res.all_stations_stable)
        self.assertGreaterEqual(res.bottleneck_utilization, 1.0)
        self.assertEqual(res.mean_end_to_end_los, float("inf"))


if __name__ == "__main__":
    unittest.main()
