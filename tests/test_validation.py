"""
Unit tests for data validation module using Python's built-in unittest.
"""
import unittest
import pandas as pd
from src.data_validation import (
    validate_schema,
    check_missingness,
    check_duplicates,
    validate_positive_durations,
    validate_timestamp_ordering
)

class TestDataValidation(unittest.TestCase):
    def test_validate_schema_success(self):
        df = pd.DataFrame({"patient_id": [1, 2], "arrival_time": ["2024-01-01", "2024-01-02"]})
        valid, missing = validate_schema(df, ["patient_id", "arrival_time"])
        self.assertTrue(valid)
        self.assertEqual(len(missing), 0)

    def test_validate_schema_missing(self):
        df = pd.DataFrame({"patient_id": [1, 2]})
        valid, missing = validate_schema(df, ["patient_id", "arrival_time"])
        self.assertFalse(valid)
        self.assertEqual(missing, ["arrival_time"])

    def test_check_duplicates(self):
        df = pd.DataFrame({"patient_id": [1, 1, 2]})
        dup_count = check_duplicates(df, subset=["patient_id"])
        self.assertEqual(dup_count, 1)

    def test_validate_positive_durations(self):
        df_valid = pd.DataFrame({"los": [1, 3, 5]})
        ok, violations = validate_positive_durations(df_valid, "los")
        self.assertTrue(ok)
        self.assertEqual(violations, 0)

        df_invalid = pd.DataFrame({"los": [1, -2, 4]})
        ok, violations = validate_positive_durations(df_invalid, "los")
        self.assertFalse(ok)
        self.assertEqual(violations, 1)

    def test_validate_timestamp_ordering(self):
        df = pd.DataFrame({
            "start": ["2024-01-01 10:00", "2024-01-02 12:00"],
            "end": ["2024-01-01 14:00", "2024-01-02 11:00"] # 2nd row violates
        })
        ok, violations = validate_timestamp_ordering(df, "start", "end")
        self.assertFalse(ok)
        self.assertEqual(violations, 1)

if __name__ == "__main__":
    unittest.main()
