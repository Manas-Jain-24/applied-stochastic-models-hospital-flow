"""
Central configuration manager for the Hospital Stochastic Modeling project.
Resolves paths relative to the project root and parses config settings.
"""
from pathlib import Path
from typing import Any, Dict
import json

# Define project root relative to this file
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
SYNTHETIC_DATA_DIR = PROJECT_ROOT / "data" / "synthetic"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"
TABLES_DIR = PROJECT_ROOT / "reports" / "tables"

def get_project_root() -> Path:
    """Returns the absolute Path of the project root."""
    return PROJECT_ROOT

def get_path(sub_path: str) -> Path:
    """Returns absolute path for any subpath relative to project root."""
    p = PROJECT_ROOT / sub_path
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

# Default fallback configuration parameters
DEFAULT_CONFIG: Dict[str, Any] = {
    "project": {
        "name": "hospital-stochastic-flow",
        "version": "1.0.0",
        "random_seed": 42
    },
    "paths": {
        "raw_data_dir": "data/raw",
        "interim_data_dir": "data/interim",
        "processed_data_dir": "data/processed",
        "synthetic_data_dir": "data/synthetic",
        "reports_figures_dir": "reports/figures",
        "reports_tables_dir": "reports/tables"
    },
    "synthetic": {
        "n_patients": 5000,
        "simulation_days": 90,
        "arrival_rate_per_day": 55.0,
        "mean_los_days": 4.5,
        "los_shape_k": 2.0,
        "n_beds": 300,
        "emergency_ratio": 0.55,
        "elective_ratio": 0.35,
        "urgent_ratio": 0.10
    },
    "queueing": {
        "target_service_level": 0.05,
        "erlang_b_blocking_limit": 0.01
    }
}

def load_config() -> Dict[str, Any]:
    """Loads configuration dictionary from YAML if PyYAML is installed, else default."""
    config_path = PROJECT_ROOT / "configs" / "config.yaml"
    if config_path.exists():
        try:
            import yaml
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except ImportError:
            pass  # Fall back to default
    return DEFAULT_CONFIG
