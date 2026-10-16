# Verification status

- Eight automated tests pass on synthetic fixtures: chronological splitting,
  exclusion of Customers and Sales, imputer stability during prediction,
  training/serialization/inference parity, invalid inputs, duplicate detection,
  closed-day anomalies, four chart files and Streamlit form predictions.
- The notebook schema and Python cells pass validation. All cells also execute
  successfully in a fresh kernel against isolated synthetic fixtures.
- The local Streamlit server starts successfully. Its current state explains
  how to add source data and train the missing model.
- The report has 10 pages and the deck has 8 editable slides. Both are visually
  reviewed drafts. Real charts, scores and interpretations remain pending.
- The test suite emits three seaborn/Matplotlib deprecation warnings. They do
  not affect test results with the pinned versions.
- Real-data run-all, final model training, empirical findings and public URL
  verification require the official Kaggle CSVs and hosting authentication.

Run `python scripts/check_notebook.py` for an isolated synthetic full-notebook
check. Its outputs stay in tmp/notebook-synthetic, never in submission artifacts.
Run `python -m pytest -q` for the automated suite.
