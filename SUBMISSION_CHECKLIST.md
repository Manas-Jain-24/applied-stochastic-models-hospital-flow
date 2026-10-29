# Submission checklist

## Files to upload

1. `reports/pdf/Hospital_Patient_Flow_ASM_Submission_Report.pdf` — the 27-page report requested by the group.
2. `reports/slides/Hospital_Patient_Flow_Submission_Presentation_v3.pptx` — the 10-slide, 15-minute deck. Speaker notes include timing and individual contributions.
3. `submission/Hospital_Patient_Flow_Submission.zip` — source code, Streamlit app, included small datasets, processed parameters, figures, output tables, report, and slides.

If the submission portal accepts only one file, upload the ZIP. If it accepts separate report and slides, upload the PDF and PPTX directly as well.

## Before speaking

- Run `streamlit run app.py` from the project root. The live demo should show the question matrix, the 170-bed Erlang-B threshold, and the failed CMS comparison.
- Keep the 15-minute deck to about 11–13 minutes of speaking so there is room for the demo and questions.
- Explain that the SPARCS, MIMIC, eICU, and CMS records are not one matched hospital cohort.
- Say plainly that the partner ED/ICU model fails external validation: 4.80% modeled ED abandonment versus 2.33% CMS, with ED sojourn 206.7 versus 202.5 minutes.
- Describe the priority queue estimate as a heuristic. The eICU hospital-admission offset is a pre-ICU interval proxy, not measured ED boarding.

## Course guideline conflict

The supplied course handout suggests a 10–12-page report. The group's requested report is 27 pages. The PDF meets the group's requirement but exceeds that suggestion. Confirm with the instructor if 10–12 pages is enforced as a hard limit.

## Verified on this workspace

- 40 unit tests and 11 pipeline stages passed.
- The numerical verification script completed and recorded the 170-bed threshold.
- All nine Streamlit sections, the simulation button, and high-load inputs ran without exceptions in the local test runtime.
- The Streamlit server health endpoint returned `ok`.
- The 27-page PDF has all 13 questions on page 1 and the deep dives on pages 2–14.
- The 10-slide PPTX passed package and layout checks, contains four embedded figures, and includes notes on all 10 slides.

Software verification does not establish external clinical validity.
