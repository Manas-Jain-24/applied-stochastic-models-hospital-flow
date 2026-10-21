"""
Unit tests for MIMIC Data Ingestion & Calibration Adapter.
"""

import unittest
from pathlib import Path
import json

from src.mimic_adapter import calibrate_mimic_parameters
from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR


class TestMIMICAdapter(unittest.TestCase):
    """Test MIMIC demo ingestion and parameter outputs."""

    def setUp(self):
        self.mimic_dir = RAW_DATA_DIR / "mimic_demo"

    def test_mimic_demo_exists_and_calibrates(self):
        """Test that MIMIC demo data exists and produces expected stochastic parameters."""
        if not self.mimic_dir.exists():
            self.skipTest("MIMIC demo folder not found, skipping calibration test.")

        params = calibrate_mimic_parameters(self.mimic_dir, PROCESSED_DATA_DIR)
        self.assertIn("admissions", params)
        self.assertIn("ward_transfer_matrix", params)
        self.assertIn("icu_specific", params)
        self.assertIn("ed_triage_acuity", params)

        # Validate admissions metrics
        adm = params["admissions"]
        self.assertGreater(adm["total_encounters"], 50)
        self.assertGreater(adm["mean_los_days"], 1.0)
        self.assertGreater(adm["cv2_los"], 0.1)

        # Validate transfer matrix
        trans = params["ward_transfer_matrix"]
        depts = trans["departments"]
        self.assertIn("ICU", depts)
        self.assertIn("Emergency", depts)
        self.assertIn("MedSurg", depts)

        # Validate row stochasticity (sum <= 1.0)
        probs = trans["routing_probabilities"]
        for src, row in probs.items():
            row_sum = sum(row.values())
            self.assertAlmostEqual(row_sum, 1.0, places=3, msg=f"Row {src} probabilities do not sum to 1.0")

        # Check saved JSON
        json_path = PROCESSED_DATA_DIR / "mimic_empirical_parameters.json"
        self.assertTrue(json_path.exists())
        with open(json_path) as f:
            saved_data = json.load(f)
        self.assertEqual(saved_data["dataset"], "MIMIC-IV")


if __name__ == "__main__":
    unittest.main()
