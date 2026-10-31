"""Build a small, explicit submission ZIP without credentialed raw hospital data."""

from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import json


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "submission" / "Hospital_Patient_Flow_Submission.zip"

EXACT = [
    "README.md", "SUBMISSION_CHECKLIST.md", "requirements.txt", "app.py",
    "reports/Comprehensive_Technical_Analysis_Report.md",
    "reports/pdf/Comprehensive_Technical_Analysis_Report.pdf",
    "reports/pdf/Hospital_Patient_Flow_ASM_Submission_Report.pdf",
    "reports/pdf/Master_Combined_Stochastic_Hospital_Flow_Report.pdf",
    "reports/Master_Combined_Stochastic_Hospital_Flow_Report.md",
    "reports/slides/Hospital_Patient_Flow_Submission_Presentation_v3.pptx",
    "data/synthetic/synthetic_hospital_encounters.csv",
    "partner_repo/cms_data/cms_timely_and_effective_care_hospital.csv",
]
PATTERNS = [
    "src/*.py", "tests/test_*.py", "configs/*",
    "scripts/verify_all.py", "scripts/verify_all_math_results.py",
    "scripts/generate_submission_report.py", "scripts/create_submission_package.py",
    "data/processed/*.json", "data/processed/*.csv", "data/raw/mimic_demo/**/*.csv",
    "partner_repo/0[1-5]_*.py", "partner_repo/eicu_demo_data/*.csv",
    "partner_repo/output_tables/*.csv", "partner_repo/output_plots/*.png",
    "reports/figures/*.png", "docs/project_guidelines.txt",
]


def main():
    files = {ROOT / name for name in EXACT}
    for pattern in PATTERNS:
        files.update(ROOT.glob(pattern))
    files = sorted(path for path in files if path.is_file())
    missing = [name for name in EXACT if not (ROOT / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Required submission files missing: {missing}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    manifest = []
    with ZipFile(OUTPUT, "w", ZIP_DEFLATED, compresslevel=6) as archive:
        for path in files:
            relative = path.relative_to(ROOT).as_posix()
            if relative.startswith(("data/raw/mimic_full/", "data/raw/sparcs/")):
                raise AssertionError(f"Restricted raw path selected: {relative}")
            data = path.read_bytes()
            archive.writestr(f"ASM_Submission/{relative}", data)
            manifest.append({"path": relative, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
        archive.writestr("ASM_Submission/MANIFEST.json", json.dumps(manifest, indent=2))
    with ZipFile(OUTPUT) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("Submission ZIP integrity check failed")
    print(f"Created {OUTPUT} with {len(files)} files ({OUTPUT.stat().st_size / 1024 / 1024:.1f} MiB)")


if __name__ == "__main__":
    main()
