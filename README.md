# SalesScope

## Retail Sales Forecasting

An individual regression capstone with a chronological forecasting evaluation,
two ML algorithms, a baseline and a Streamlit interface.

**Current status:** the full Rossmann dataset has been loaded and training is
complete for all 1,115 stores. Ridge won validation selection. On the held-out
test period, MAE is 852.09 sales units, RMSE is 1,280.96, and R² is 0.882.
Open-day test MAE is 990.60 sales units. R² is not an accuracy percentage.
The custom Flask interface is now the primary app. The original Streamlit app
remains available as a fallback. Public deployment
is pending. Documents marked DRAFT must be regenerated with the measured outputs
and reviewed before submission. Synthetic test scores are software checks only.

## Start in VS Code

1. Open this folder. Install Microsoft's **Python** and **Jupyter** extensions.
2. Select `.venv/Scripts/python.exe` with **Python: Select Interpreter**.
3. Open `Retail_Sales_Prediction.ipynb`, select the same environment as its kernel.
4. Download `train.csv` and `store.csv` from https://www.kaggle.com/c/rossmann-store-sales/data
   after signing in and accepting its rules. Put both in `data/raw/`.
5. Run notebook cells from top to bottom. Read the checkpoints and write your own observations.

The local `.venv` uses the bundled Python runtime available on this computer.
For another computer, install Python 3.12 and create a fresh environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Activation is optional. These commands work without changing PowerShell policy:

```powershell
.\.venv\Scripts\python.exe -m retail.eda
.\.venv\Scripts\python.exe -m retail.train
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe web_app.py
.\.venv\Scripts\python.exe scripts/build_report.py
```

Open http://127.0.0.1:5000 for the custom SalesScope interface. Keep the terminal
running. The custom app uses Flask, HTML/CSS and JavaScript, with Waitress as its
server. A browser theme button switches light/dark and remembers the choice.
The form calls `POST /api/predict`; both interfaces use the same trained artifact
and `predict_one` function. No retraining is needed to change the interface.
The old Streamlit interface can still be launched with
`python -m streamlit run app.py`, but it does not show the custom design.

Full data is the default. If memory or runtime is impractical, run
`python -m retail.train --max-stores 100`, and use the same `MAX_STORES=100`
in the notebook's EDA cell. The report records the training scope. A forest
with 100 trees and depth 18 may take considerable time on the full dataset.

## Method and outputs

The last 42 calendar days form the test period, and the previous 42 form validation.
EDA uses training dates only. Both algorithms fit only open days. Known closed
days return zero. Customers and Sales never enter the feature matrix. Numeric
imputation, scaling and categorical encoding live in the saved sklearn pipeline.

Validation MAE selects among Ridge, Random Forest and the baseline. If the
baseline wins, keep and discuss that result. Refit the selected method on train
plus validation, then evaluate once on test. The saved model ends before test
to keep its reported score reproducible. No post-test full-data refit is implicit.
No lagged target features or retrospective promotion metadata are used.

`artifacts/metrics.json` records splits, scope, metrics, settings and dataset hashes.
`artifacts/test_predictions.csv` holds test predictions. `artifacts/model.joblib`
holds the pipeline, baseline and store lookup. Only load artifacts you produced.
The app rejects unknown stores and dates on or before the model's training end.
Its forecasts use dataset sales units, without asserting an undocumented currency.

## Four-day learning checkpoints

**Day 1:** Inspect schema, missingness and duplicates. Review four EDA plots.
Explain why changing store coverage can affect a sales trend and why promotion
association does not prove causation. Add specific observations from the plots.

**Day 2:** Explain Ridge regularization, forest interactions, one-hot encoding,
the baseline, leakage and chronological validation. Compare all-day and open-day
metrics. Explain why RMSE penalizes large misses more heavily than MAE.

**Day 3:** Run the app. Predict an open day and a closed day. Explain why a
forecast requires known promotion and opening plans. Verify model/app parity.

**Day 4:** Regenerate the report and slides, add student details and your own
findings, rehearse the demo, restart the kernel and run all cells once.

## Deployment

See `docs/DEPLOYMENT.md`. Publishing needs your GitHub and Streamlit login and
a trained artifact. No repository or deployment has been created automatically.

## Submission checklist

- Executed notebook and source code with pinned requirements.
- Dataset source, access instructions and scope disclosure.
- Report PDF with real metrics and interpreted EDA.
- Eight-slide presentation with measured results.
- Working app URL, or local demonstration if your instructor permits it.
- Your name, roll number and course details added before submission.

Historical Rossmann patterns may not generalize to current stores or distant
dates. No calibrated uncertainty interval or causal promotion effect is estimated.
Future work can compare boosted trees, add safely shifted sales history, use
rolling-origin validation and monitor forecast error as new labels arrive.
