# Retail Sales Prediction — Guided Capstone

## Summary
Build the project step by step in VS Code, using Rossmann daily store sales data. Complete it over four days, with explanations and review checkpoints so you can defend every major decision during evaluation.

## Implementation
- **Day 1 — Data and EDA:** Set up a Python virtual environment and Jupyter kernel. Download `train.csv` and `store.csv` from [Kaggle](https://www.kaggle.com/c/rossmann-store-sales/data), merge by store, inspect missing values and duplicates, and validate dates and sales.
- Produce at least four meaningful charts: sales over time, weekday sales patterns, promotion versus sales, and sales by store type. Explain observations without claiming promotions cause observed differences.
- **Day 2 — Models:** Use calendar, store, promotion, and holiday features known before the prediction date. Exclude same-day `Customers`. Compare Ridge regression and Random Forest regression against a training-derived store/weekday mean baseline.
- Reserve the final six weeks for testing and the preceding six weeks for validation; use earlier dates for training. Fit preprocessing only on training data. Train on open days and return zero for known closed days.
- Compare MAE, RMSE, and R², including open-day errors separately. Select the model with lowest validation MAE, refit on training plus validation, and evaluate once on the untouched test period.
- **Day 3 — Interface:** Save the complete preprocessing/model pipeline. Build a Streamlit interface accepting a known store, future date, planned opening status, promotion, and holiday indicators. Display predicted daily sales and explain forecasting limitations. Publish through Streamlit Community Cloud using a GitHub repository.
- **Day 4 — Submission:** Prepare a short report, approximately 8–12 pages, and an 8-slide presentation. Cover the problem, objectives, dataset, cleaning, EDA, algorithms, validation design, measured results, findings, limitations, applications, and future improvements.

## Deliverables and Learning
- One reproducible notebook, reusable training/prediction code, Streamlit app, dependency file, saved pipeline, dataset-source instructions, report PDF, and presentation.
- Each guided stage includes a brief conceptual explanation, implementation task, result review, and viva questions.
- Keep results and conclusions tied to actual runs; do not promise an accuracy score in advance.

## Verification and Defaults
- Verify chronological separation, absence of customer-count leakage, and consistent preprocessing between notebook and app.
- Check known closed stores, invalid inputs, unseen store rejection, nonnegative predictions, and agreement between app and saved-pipeline outputs.
- Restart the notebook kernel and run all cells; launch the app in a clean environment and verify the deployed link.
- Use Python, pandas, scikit-learn, matplotlib/seaborn, joblib, and Streamlit with a fixed random seed.
- Begin with the full dataset. If training is impractical on the available computer, use the first 100 store IDs consistently and disclose the reduced scope.
- Assume a four-day schedule and standard report format. You handle Kaggle sign-in and hosting-account authentication when required.
