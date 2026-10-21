"""
Data validation module.
Verifies column schemas, timestamp logic, missingness, impossible values, and duplicates.
"""
from typing import List, Dict, Any, Tuple
import pandas as pd
import numpy as np

class DataValidationError(Exception):
    """Custom exception raised when data violates critical validation rules."""
    pass

def validate_schema(df: pd.DataFrame, required_columns: List[str]) -> Tuple[bool, List[str]]:
    """
    Checks if all required columns are present in the DataFrame.
    Returns (is_valid, missing_columns).
    """
    missing = [col for col in required_columns if col not in df.columns]
    return (len(missing) == 0, missing)

def check_missingness(df: pd.DataFrame, threshold: float = 0.5) -> Dict[str, Any]:
    """
    Evaluates missing values per column and flags any exceeding the threshold ratio.
    """
    null_counts = df.isnull().sum()
    null_ratios = null_counts / len(df) if len(df) > 0 else null_counts
    exceeded = null_ratios[null_ratios > threshold].to_dict()
    return {
        "null_counts": null_counts.to_dict(),
        "null_ratios": null_ratios.to_dict(),
        "columns_exceeding_threshold": exceeded
    }

def check_duplicates(df: pd.DataFrame, subset: List[str] = None) -> int:
    """
    Counts duplicate rows based on subset or entire dataframe.
    """
    return int(df.duplicated(subset=subset).sum())

def validate_positive_durations(df: pd.DataFrame, duration_col: str) -> Tuple[bool, int]:
    """
    Ensures durations (e.g., Length of Stay) are strictly positive (>= 0).
    Returns (is_valid, count_of_invalid_values).
    """
    if duration_col not in df.columns:
        raise DataValidationError(f"Column '{duration_col}' not found in DataFrame.")
    
    numeric_vals = pd.to_numeric(df[duration_col], errors='coerce')
    invalid_mask = numeric_vals.isnull() | (numeric_vals < 0)
    invalid_count = int(invalid_mask.sum())
    return (invalid_count == 0, invalid_count)

def validate_timestamp_ordering(df: pd.DataFrame, start_col: str, end_col: str) -> Tuple[bool, int]:
    """
    Ensures end_timestamp >= start_timestamp.
    Returns (is_valid, count_of_violations).
    """
    if start_col not in df.columns or end_col not in df.columns:
        raise DataValidationError(f"Timestamp columns '{start_col}' or '{end_col}' missing.")
    
    start_dt = pd.to_datetime(df[start_col], errors='coerce')
    end_dt = pd.to_datetime(df[end_col], errors='coerce')
    
    violations = (end_dt < start_dt).sum()
    return (violations == 0, int(violations))

def run_full_validation(df: pd.DataFrame, 
                        required_cols: List[str], 
                        duration_col: str = None, 
                        start_col: str = None, 
                        end_col: str = None) -> Dict[str, Any]:
    """
    Executes a comprehensive validation report.
    """
    report = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "schema_valid": True,
        "missing_columns": [],
        "duplicate_rows": check_duplicates(df),
        "missingness": check_missingness(df),
        "duration_valid": True,
        "duration_violations": 0,
        "timestamp_valid": True,
        "timestamp_violations": 0
    }
    
    schema_ok, missing = validate_schema(df, required_cols)
    report["schema_valid"] = schema_ok
    report["missing_columns"] = missing
    
    if duration_col and duration_col in df.columns:
        dur_ok, dur_viol = validate_positive_durations(df, duration_col)
        report["duration_valid"] = dur_ok
        report["duration_violations"] = dur_viol
        
    if start_col and end_col and start_col in df.columns and end_col in df.columns:
        ts_ok, ts_viol = validate_timestamp_ordering(df, start_col, end_col)
        report["timestamp_valid"] = ts_ok
        report["timestamp_violations"] = ts_viol
        
    return report
