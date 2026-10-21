"""
Unit tests for Time-Varying Queueing & Pointwise Stationary Approximation (PSA).
"""

import unittest
import numpy as np

from src.time_varying import (
    diurnal_arrival_rate,
    run_pointwise_stationary_approximation,
    compare_constant_vs_dynamic_staffing,
)


class TestTimeVaryingPSA(unittest.TestCase):
    """Test PSA simulation and staffing schedule evaluations."""

    def test_diurnal_rate_cycle_and_mean(self):
        """Verify 24-hour diurnal arrival curve characteristics."""
        hours = np.linspace(0, 24, 240, endpoint=False)
        rates = [diurnal_arrival_rate(h, mean_daily_arrivals=48.0, amplitude_ratio=0.30, peak_hour=14.0) for h in hours]

        # Mean rate should approximately equal 48 / 24 = 2.0 patients/hr
        self.assertAlmostEqual(float(np.mean(rates)), 2.0, places=2)

        # Peak rate should occur near 14.0
        peak_idx = int(np.argmax(rates))
        self.assertAlmostEqual(hours[peak_idx], 14.0, delta=0.5)

    def test_psa_constant_vs_dynamic_improvement(self):
        """Verify dynamic shift staffing reduces peak waiting time under equal bed-hours."""
        c_res, d_res = compare_constant_vs_dynamic_staffing(
            mean_daily_arrivals=50.0,
            mean_los_days=5.0,
            base_beds=400,
            surge_delta=20,
        )

        self.assertEqual(len(c_res.hourly_states), 24)
        self.assertEqual(len(d_res.hourly_states), 24)

        # Total bed hours should be identical
        self.assertEqual(c_res.total_bed_hours, d_res.total_bed_hours)

        # Dynamic staffing should reduce peak hour waiting time
        self.assertLess(d_res.peak_wait_time_hours, c_res.peak_wait_time_hours)
        self.assertLess(d_res.peak_utilization, c_res.peak_utilization)


if __name__ == "__main__":
    unittest.main()
