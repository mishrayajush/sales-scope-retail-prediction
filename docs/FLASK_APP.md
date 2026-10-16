# SalesScope custom interface

Run from the project root:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe web_app.py
```

Open http://127.0.0.1:5000. Closing a browser tab does not stop training or delete
the model. Keep the server terminal running while using the page.

The entry point is `web_app.py`, templates live in `templates/`, and browser assets
live in `static/`. The existing `app.py` remains the original Streamlit interface.
Use the new URL to see the custom design. The fonts have local fallbacks when
Google Fonts is unavailable. The interface does not require a Node build step.

The browser sends a store ID, ISO date, boolean opening/promotion/school holiday
flags and a holiday code to `POST /api/predict`. Server validation checks each
input and delegates inference to the existing shared function. The response
contains the value, submitted scenario and an out-of-horizon flag. It does not
claim a confidence interval. Estimates are calculated, not simulated in the UI.

The calendar supports future dates through one year from today. The saved model
is historical and validated only over the six-week test period. Current-date
estimates are demonstrations; this remains visible before and after prediction.

Selecting a store loads `GET /api/history?store=ID&period=week|month|year`
without needing a prediction date. The history uses the original train.csv,
filtered through the saved model's training end. The server caches that source
and period summaries. Restart after replacing either the CSV or model artifact.
The chart shows period totals, includes closed days, marks partial periods, and
leaves missing periods as gaps rather than inventing zero sales. An expandable
table provides the exact figures. Keep data/raw/train.csv available for this view,
or set RETAIL_HISTORY_PATH to the corresponding original file.

The local server binds to loopback only. For public hosting, deploy
`web_app:app` on a Python WSGI host using Waitress, set the platform's port and
host as required, and include the reviewed model artifact. Streamlit Community
Cloud hosts the old Streamlit entry point, not this Flask application. No public
deployment has been created. Test the public page and API before reporting a URL.
