# Hospital Patient Flow: Applied Stochastic Models

This course project studies how variable patient stays, changing arrival rates, bed limits, and ward transfers affect waiting and blocking. It combines descriptive analysis of public hospital datasets with queueing calculations, network models, and discrete-event simulations.

## Submit these files

| File | Purpose |
| --- | --- |
| [27-page submission report](reports/pdf/Hospital_Patient_Flow_ASM_Submission_Report.pdf) | Main report. Page 1 lists all 13 questions, datasets, methods, and short findings; pages 2–14 explain each question. |
| [10-slide presentation](reports/slides/Hospital_Patient_Flow_Submission_Presentation_v3.pptx) | 15-minute group presentation with speaker notes. |
| [Streamlit app](app.py) | Interactive demonstration for the presentation. |
| [Verified numerical results](data/processed/master_verified_math_results.json) | Recomputed scenario values used in the report and app. |

The course handout suggests a **10–12-page report**. This project uses a **27-page expanded report** to meet the group's stated requirement. If the instructor enforces the suggested length as a limit, confirm acceptance before submitting it.

## What the results mean

- The processed SPARCS inpatient cohort has mean stay **5.386 days** and squared coefficient of variation **1.991**. The eICU and MIMIC ICU values are **2.025** and **2.215**.
- In an illustrative Erlang-C scenario with offered load 225 Erlangs, increasing capacity from 230 to 242 beds changes the calculated mean wait from **15.55 to 1.30 hours**.
- In an Erlang-B loss scenario with offered load 150 Erlangs, **170 beds** is the first integer capacity meeting a selected 1% blocking target. That target is a planning choice, not a cited regulation.
- In a fixed 230-bed allocation scenario, the configured weighted blocking objective changes from **0.40374 to 0.06550**, a **83.8%** reduction. This is an optimization objective, not observed patient diversion.
- The repaired partner ED/ICU simulation reports **4.80%** ED abandonment at its 90-ICU-bed baseline, compared with **2.33%** in the CMS benchmark. Its external validation **fails**. Its capacity sweep cannot justify a clinical ICU expansion recommendation.
- The eICU hospital-admission offset is a **pre-ICU interval proxy**. It does not directly measure time boarding in an ED bay.
- The multiserver priority formula is a **heuristic** and has not been independently validated. Do not present its class-specific wait changes as proven benefits.

The datasets come from different institutions and are not a joint facility-level cohort. All modeled capacity and staffing effects are conditional on their stated assumptions.

## Data used

| Source | Role | Local location |
| --- | --- | --- |
| NYS SPARCS inpatient discharges | Stay-duration analysis | `data/raw/sparcs/` and `data/processed/sparcs_empirical_parameters.json` |
| MIMIC-IV | ICU stays and transfer summaries | `data/raw/mimic_full/` or demo fallback; processed JSON in `data/processed/` |
| eICU Collaborative Research Database demo | ICU stays, admission-source timing, hourly shape | `partner_repo/eicu_demo_data/` |
| CMS Timely and Effective Care extract | ED volume and external benchmark | `partner_repo/cms_data/` |

Large raw SPARCS and credentialed MIMIC files are excluded from Git. The included processed parameters and partner outputs allow the supplied report and app to open, but regenerating every empirical estimate requires the underlying authorized raw data.

## Run the project

Use Python 3.10 or newer from the repository root:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/verify_all.py
python scripts/verify_all_math_results.py
streamlit run app.py
```

To rerun the partner analysis after its local source tables are available:

```powershell
python partner_repo/01_eda_and_preprocessing.py
python partner_repo/02_nhpp_arrival_and_service_fitting.py
python partner_repo/03_markov_chain_analysis.py
python partner_repo/04_tandem_queue_simulation.py
python partner_repo/05_model_validation_and_policy.py
```

To rebuild the report:

```powershell
python scripts/generate_submission_report.py
```

The report generator uses local figures and output tables. Run the analysis scripts first if those outputs are missing.

## Verification status

`python scripts/verify_all.py` passed **40 unit tests** and 11 pipeline stages in the prepared workspace. The partner-output checks also assert that the CMS comparison is marked as failed; a passing software suite does not mean the clinical model is externally valid.

## Project map

- `src/`: queueing, network, allocation, arrival, Markov, and simulation code.
- `partner_repo/`: eICU/CMS preprocessing, fitting, Markov analysis, tandem ED/ICU simulation, and benchmark comparison.
- `tests/`: mathematical and data-handling tests.
- `scripts/`: verification and report generation.
- `reports/pdf/`: report PDFs. The named 27-page submission report above is the current one.
- `reports/slides/`: current presentation.
- `app.py`: Streamlit companion.

Older reports in `reports/` are historical drafts with superseded numerical claims. Use the 27-page submission PDF for submission.
