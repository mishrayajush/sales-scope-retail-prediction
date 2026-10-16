# Streamlit deployment

1. Train locally and inspect validation/test metrics. Run tests and the app.
2. Create a GitHub repository and push source, requirements and the trained
   `artifacts/model.joblib`. It is ignored by default: explicitly add it using
   `git add -f artifacts/model.joblib` only after reviewing competition rules.
   Keep raw CSVs and account credentials out of the repository.
3. Check artifact size with `Get-Item artifacts/model.joblib`. If too large for
   your repository or hosting limits, document and retrain with the 100-store
   option. Do not silently swap the model or its scope. Regenerate report/plots.
4. Sign in to https://share.streamlit.io/ and choose your repository, branch,
   and `app.py` entry point. Select Python 3.12 in advanced settings.
5. Open the resulting public URL in a fresh browser session. Confirm an open-day
   prediction, zero for a closed day, readable limitations and no exceptions.
6. Record the URL in your report and presentation. Monitor deployment logs for
   dependency or memory errors. Match the sklearn version used in training.

Do not claim deployment is complete until the public URL passes these checks.
Official instructions: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app
