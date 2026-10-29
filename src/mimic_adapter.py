"""
MIMIC Database Ingestion & Parameter Calibration Adapter.

Extracts stochastic patient flow parameters, ward-to-ward transition
matrices, length of stay distributions, and triage acuity levels from
standard MIMIC-IV and MIMIC-IV-ED schemas.

Supports both the open-access MIMIC-IV Demo and full credentialed MIMIC-IV datasets.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import numpy as np
import pandas as pd


def parse_mimic_admissions(file_path: Path) -> pd.DataFrame:
    """Parse admissions.csv(.gz) and compute LOS and admission streams."""
    df = pd.read_csv(file_path)
    df["admittime"] = pd.to_datetime(df["admittime"], errors="coerce")
    df["dischtime"] = pd.to_datetime(df["dischtime"], errors="coerce")
    df["los_days"] = (df["dischtime"] - df["admittime"]).dt.total_seconds() / 86400.0
    df = df[df["los_days"] > 0].copy()

    # ED boarding time (hours) if present
    if "edregtime" in df.columns and "edouttime" in df.columns:
        ed_reg = pd.to_datetime(df["edregtime"], errors="coerce")
        ed_out = pd.to_datetime(df["edouttime"], errors="coerce")
        df["ed_dwell_hours"] = (ed_out - ed_reg).dt.total_seconds() / 3600.0
    else:
        df["ed_dwell_hours"] = np.nan

    # Categorize admission stream
    if "admission_type" in df.columns:
        df["stream"] = df["admission_type"].astype(str).str.upper().apply(
            lambda x: "EMERGENCY" if ("EMER" in x or "URG" in x) else ("ELECTIVE" if "ELEC" in x else "OTHER")
        )
    else:
        df["stream"] = "GENERAL"

    return df


def parse_mimic_transfers(file_path: Path) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    """
    Parse transfers.csv(.gz), standardize care units, and build
    the empirical Markov transition matrix P_ij.
    """
    df = pd.read_csv(file_path)
    df["intime"] = pd.to_datetime(df["intime"], errors="coerce")
    df["outtime"] = pd.to_datetime(df["outtime"], errors="coerce")
    df = df.dropna(subset=["hadm_id", "intime", "careunit"]).copy()

    # Simplify careunit names into major stochastic categories
    def categorize_unit(cu: str) -> str:
        cu_upper = str(cu).upper()
        if "EMERGENCY" in cu_upper or "ED" in cu_upper:
            return "Emergency"
        elif "ICU" in cu_upper or "INTENSIVE" in cu_upper or "CCU" in cu_upper or "TSICU" in cu_upper:
            return "ICU"
        elif "STEP" in cu_upper or "INTERMEDIATE" in cu_upper or "IMC" in cu_upper:
            return "StepDown"
        elif "PACU" in cu_upper or "RECOVERY" in cu_upper:
            return "Recovery"
        else:
            return "MedSurg"

    df["ward_category"] = df["careunit"].apply(categorize_unit)
    df["stay_days"] = (df["outtime"] - df["intime"]).dt.total_seconds() / 86400.0

    # Build sequence of wards per admission hadm_id (vectorized for million-row scale)
    if len(df) > 0:
        df_sorted = df.sort_values(by=["hadm_id", "intime"]).reset_index(drop=True)
        same_hadm = df_sorted["hadm_id"] == df_sorted["hadm_id"].shift(-1)
        internal_from = df_sorted.loc[same_hadm, "ward_category"].values
        internal_to = df_sorted["ward_category"].shift(-1).loc[same_hadm].values
        discharge_from = df_sorted.loc[~same_hadm, "ward_category"].values
        discharge_to = np.full(len(discharge_from), "Discharge")

        trans_df = pd.DataFrame({
            "from_ward": np.concatenate([internal_from, discharge_from]),
            "to_ward": np.concatenate([internal_to, discharge_to]),
        })
    else:
        trans_df = pd.DataFrame(columns=["from_ward", "to_ward"])
    unique_wards = sorted(list(set(df["ward_category"].unique())))
    all_nodes = unique_wards + ["Discharge"]

    # Transition probability matrix
    P_matrix = pd.crosstab(
        trans_df["from_ward"],
        trans_df["to_ward"],
        normalize="index"
    ).reindex(index=unique_wards, columns=all_nodes, fill_value=0.0)

    return df, P_matrix, unique_wards


def parse_mimic_icustays(file_path: Path) -> pd.DataFrame:
    """Parse icustays.csv(.gz) for exact ICU length of stay in days."""
    df = pd.read_csv(file_path)
    if "los" in df.columns:
        df["los_days"] = pd.to_numeric(df["los"], errors="coerce")
    else:
        intime = pd.to_datetime(df["intime"], errors="coerce")
        outtime = pd.to_datetime(df["outtime"], errors="coerce")
        df["los_days"] = (outtime - intime).dt.total_seconds() / 86400.0
    return df[df["los_days"] > 0].copy()


def parse_mimic_triage(file_path: Path) -> pd.DataFrame:
    """Parse triage.csv(.gz) for Emergency Severity Index (ESI) acuity levels."""
    df = pd.read_csv(file_path)
    if "acuity" in df.columns:
        df["acuity"] = pd.to_numeric(df["acuity"], errors="coerce")
    return df


def calibrate_mimic_parameters(
    mimic_dir: Path,
    output_dir: Path,
    fallback_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Calibrate hospital stochastic parameters from MIMIC directory
    and export JSON and summary tables. Optionally fall back to a
    secondary directory (e.g. demo) for any unsupplied tables.
    """
    mimic_dir = Path(mimic_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    def find_file(pattern: str) -> Optional[Path]:
        cands = list(mimic_dir.glob(pattern))
        if cands:
            return cands[0]
        if fallback_dir and Path(fallback_dir).exists():
            fb_cands = list(Path(fallback_dir).glob(pattern))
            if fb_cands:
                return fb_cands[0]
        return None

    params: Dict[str, Any] = {"dataset": "MIMIC-IV"}

    # 1. Admissions & Overall LOS
    adm_path = find_file("**/admissions.csv*")
    if adm_path:
        adm_df = parse_mimic_admissions(adm_path)
        los = adm_df["los_days"].values

        mean_los = float(np.mean(los))
        var_los = float(np.var(los, ddof=1)) if len(los) > 1 else 0.0
        cv2_los = float(var_los / (mean_los ** 2)) if mean_los > 0 else 1.0

        stream_counts = adm_df["stream"].value_counts(normalize=True).to_dict()
        mortality_rate = float(adm_df["hospital_expire_flag"].mean()) if "hospital_expire_flag" in adm_df.columns else 0.0

        params["admissions"] = {
            "source_file": str(adm_path.name),
            "total_encounters": len(adm_df),
            "mean_los_days": round(mean_los, 3),
            "variance_los": round(var_los, 3),
            "cv2_los": round(cv2_los, 3),
            "stream_proportions": {k: round(v, 4) for k, v in stream_counts.items()},
            "in_hospital_mortality_rate": round(mortality_rate, 4),
        }

    # 2. Transfers & Network Routing Matrix
    trans_path = find_file("**/transfers.csv*")
    if trans_path:
        trans_df, P_matrix, unique_wards = parse_mimic_transfers(trans_path)

        # Department-specific LOS
        ward_los = {}
        for ward, grp in trans_df.groupby("ward_category"):
            valid_stays = grp["stay_days"].dropna().values
            valid_stays = valid_stays[valid_stays > 0]
            if len(valid_stays) > 0:
                m_los = float(np.mean(valid_stays))
                v_los = float(np.var(valid_stays, ddof=1)) if len(valid_stays) > 1 else 0.0
                ward_los[ward] = {
                    "mean_days": round(m_los, 3),
                    "variance_days": round(v_los, 3),
                    "cv2": round(v_los / (m_los ** 2), 3) if m_los > 0 else 1.0,
                    "count": len(valid_stays),
                }

        params["ward_transfer_matrix"] = {
            "source_file": str(trans_path.name),
            "total_transfers": len(trans_df),
            "departments": unique_wards,
            "routing_probabilities": {
                row: {col: round(float(P_matrix.loc[row, col]), 4) for col in P_matrix.columns}
                for row in P_matrix.index
            },
            "ward_los": ward_los,
        }

    # 3. ICU-specific metrics
    icu_path = find_file("**/icustays.csv*")
    if icu_path:
        icu_df = parse_mimic_icustays(icu_path)
        icu_los = icu_df["los_days"].dropna().values
        if len(icu_los) > 0:
            m_icu = float(np.mean(icu_los))
            v_icu = float(np.var(icu_los, ddof=1)) if len(icu_los) > 1 else 0.0
            params["icu_specific"] = {
                "source_file": str(icu_path.name),
                "total_icu_stays": len(icu_los),
                "mean_los_days": round(m_icu, 3),
                "variance_los": round(v_icu, 3),
                "cv2_los": round(v_icu / (m_icu ** 2), 3) if m_icu > 0 else 1.0,
            }

    # 4. ED Triage Acuity
    triage_path = find_file("**/triage.csv*")
    if triage_path:
        triage_df = parse_mimic_triage(triage_path)
        if "acuity" in triage_df.columns:
            acuity_counts = triage_df["acuity"].value_counts(normalize=True).sort_index().to_dict()
            params["ed_triage_acuity"] = {
                f"ESI_{int(k)}": round(float(v), 4) for k, v in acuity_counts.items() if not np.isnan(k)
            }

    # Save to JSON
    out_json = output_dir / "mimic_empirical_parameters.json"
    with open(out_json, "w") as f:
        json.dump(params, f, indent=2)

    print(f"Calibration successful! Output saved to {out_json}")
    return params


if __name__ == "__main__":
    from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR
    mimic_full = RAW_DATA_DIR / "mimic_full"
    mimic_demo = RAW_DATA_DIR / "mimic_demo"
    if mimic_full.exists():
        print("Calibrating from full MIMIC dataset with demo fallback...")
        res = calibrate_mimic_parameters(mimic_full, PROCESSED_DATA_DIR, fallback_dir=mimic_demo)
        print("Calibrated MIMIC parameters summary:")
        print(json.dumps(res, indent=2))
    elif mimic_demo.exists():
        res = calibrate_mimic_parameters(mimic_demo, PROCESSED_DATA_DIR)
        print("Calibrated MIMIC parameters summary:")
        print(json.dumps(res, indent=2))
    else:
        print(f"MIMIC directory not found. Run download_mimic_demo.py first.")
