"""
Download MIMIC-IV Clinical Demo v2.2 and MIMIC-IV-ED Demo v2.2
from PhysioNet (Open Access, no credentials required).

This provides real, de-identified clinical records matching the exact
schema of the full MIMIC-IV database.
"""

import os
import urllib.request
import gzip
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MIMIC_DIR = BASE_DIR / "data" / "raw" / "mimic_demo"

DEMO_FILES = {
    "hosp_admissions": {
        "url": "https://physionet.org/files/mimic-iv-demo/2.2/hosp/admissions.csv.gz",
        "dest": MIMIC_DIR / "hosp" / "admissions.csv.gz",
    },
    "hosp_transfers": {
        "url": "https://physionet.org/files/mimic-iv-demo/2.2/hosp/transfers.csv.gz",
        "dest": MIMIC_DIR / "hosp" / "transfers.csv.gz",
    },
    "icu_icustays": {
        "url": "https://physionet.org/files/mimic-iv-demo/2.2/icu/icustays.csv.gz",
        "dest": MIMIC_DIR / "icu" / "icustays.csv.gz",
    },
    "ed_edstays": {
        "url": "https://physionet.org/files/mimic-iv-ed-demo/2.2/ed/edstays.csv.gz",
        "dest": MIMIC_DIR / "ed" / "edstays.csv.gz",
    },
    "ed_triage": {
        "url": "https://physionet.org/files/mimic-iv-ed-demo/2.2/ed/triage.csv.gz",
        "dest": MIMIC_DIR / "ed" / "triage.csv.gz",
    },
}


def download_mimic_demo(uncompress: bool = True):
    """Download demo files and optionally uncompress to .csv."""
    MIMIC_DIR.mkdir(parents=True, exist_ok=True)
    print("=" * 60)
    print(">>> DOWNLOADING MIMIC-IV & MIMIC-IV-ED DEMO (PHYSIONET) <<<")
    print("=" * 60)

    for name, item in DEMO_FILES.items():
        url = item["url"]
        dest_gz = item["dest"]
        dest_gz.parent.mkdir(parents=True, exist_ok=True)

        csv_path = dest_gz.with_suffix("")  # remove .gz

        if csv_path.exists() and csv_path.stat().st_size > 0:
            print(f"[SKIP] Already exists: {csv_path.name} ({csv_path.stat().st_size // 1024} KB)")
            continue

        print(f"[FETCH] Downloading {dest_gz.name} from {url}...")
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ASM-Hospital-Project/1.0"}
            )
            with urllib.request.urlopen(req, timeout=30) as response, open(dest_gz, "wb") as out_file:
                shutil.copyfileobj(response, out_file)
            print(f"  -> Saved {dest_gz.name} ({dest_gz.stat().st_size // 1024} KB)")

            if uncompress:
                print(f"  -> Decompressing to {csv_path.name}...")
                with gzip.open(dest_gz, "rb") as f_in, open(csv_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
                print(f"  -> Uncompressed size: {csv_path.stat().st_size // 1024} KB")

        except Exception as e:
            print(f"  [ERROR] Failed to download {url}: {e}")

    print("\nDownload complete! Files ready in data/raw/mimic_demo/")


if __name__ == "__main__":
    download_mimic_demo(uncompress=True)
