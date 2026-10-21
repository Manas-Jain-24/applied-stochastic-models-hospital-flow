"""
Unit tests for Optimal Bed Allocation Optimizer.
"""

import unittest

from src.bed_allocation import (
    DepartmentSpec,
    marginal_bed_allocation,
    proportional_bed_allocation,
    compute_capacity_expansion_frontier,
)


class TestBedAllocation(unittest.TestCase):
    """Test Fox greedy allocation and proportional comparison."""

    def setUp(self):
        self.depts = [
            DepartmentSpec(name="ICU", offered_load=20.0, weight=4.0, min_beds=21),
            DepartmentSpec(name="Emergency", offered_load=30.0, weight=2.0, min_beds=31),
            DepartmentSpec(name="MedSurg", offered_load=150.0, weight=1.0, min_beds=151),
        ]
        self.total_beds = 230

    def test_marginal_allocation_satisfies_constraints(self):
        """Verify allocation satisfies total capacity and minimum department constraints."""
        opt = marginal_bed_allocation(self.depts, self.total_beds)

        allocated_total = sum(d.beds for d in opt.departments)
        self.assertEqual(allocated_total, self.total_beds)

        for d, orig in zip(opt.departments, self.depts):
            self.assertGreaterEqual(d.beds, orig.min_beds)
            self.assertGreaterEqual(d.safety_buffer, 0)
            self.assertLessEqual(d.blocking_prob, 0.10)

    def test_optimal_outperforms_proportional(self):
        """Verify optimal allocation achieves lower weighted blocking than proportional."""
        opt = marginal_bed_allocation(self.depts, self.total_beds)
        prop = proportional_bed_allocation(self.depts, self.total_beds)

        self.assertEqual(sum(d.beds for d in prop.departments), self.total_beds)
        self.assertLessEqual(opt.total_weighted_blocking, prop.total_weighted_blocking)

    def test_capacity_expansion_frontier_monotonicity(self):
        """Verify increasing bed budget monotonically reduces total system blocking."""
        frontier = compute_capacity_expansion_frontier(self.depts, min_total_beds=215, max_total_beds=245, step=10)

        blocking_vals = [pt["optimal_weighted_blocking"] for pt in frontier]
        for i in range(len(blocking_vals) - 1):
            self.assertGreater(blocking_vals[i], blocking_vals[i + 1])


if __name__ == "__main__":
    unittest.main()
