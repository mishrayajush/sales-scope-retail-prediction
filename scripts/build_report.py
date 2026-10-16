"""Build a 10-page report draft; measured tables require artifacts/metrics.json."""
from pathlib import Path
import json
from html import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/pdf'
OUT.mkdir(parents=True,exist_ok=True)
mp=ROOT/'artifacts/metrics.json'
metrics=json.loads(mp.read_text()) if mp.exists() else None
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyRetail',fontName='Helvetica',fontSize=11,leading=17,spaceAfter=12,textColor=colors.HexColor('#243447')))
styles['Title'].fontSize=30
styles['Title'].leading=36
story=[]
def p(text): story.append(Paragraph(text,styles['BodyRetail']))
def title(text): story.append(Paragraph(text,styles['Title']));story.append(Spacer(1,20))
def heading(text):story.append(Paragraph(text,styles['Heading2']))
def page(text):
    if story:story.append(PageBreak())
    title(text)
def table(rows):
    t=Table([[Paragraph(escape(str(c)),styles['BodyRetail']) for c in row] for row in rows],repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8eff5')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),8),('LINEBELOW',(0,0),(-1,0),1,colors.HexColor('#243447'))]))
    story.append(t)
def chart(name):
    path=ROOT/f'artifacts/figures/{name}.png'
    if path.exists():story.append(Image(str(path),width=6.6*inch,height=2.94*inch))
    else:p('Chart pending: run the EDA stage with the Rossmann data. No observations are asserted in this draft.')

page('Retail Sales Prediction')
p('CAPSTONE PROJECT 2 / REGRESSION')
p('<b>DRAFT - student review required before submission.</b> '+('Measured results loaded from local training outputs.' if metrics else 'Real dataset unavailable. Training, EDA findings and performance results remain pending.'))
p('Student name: ____________________<br/>Roll number: ____________________<br/>Course / institution: ____________________<br/>Submission date: ____________________')
heading('Abstract')
p('This project implements daily retail sales forecasting from historical Rossmann observations and information available before the forecast day. The workflow validates source data, explores training-period patterns, compares Ridge regression and Random Forest with a store/weekday baseline, and evaluates the selected method on a later six-week period. A Streamlit interface uses the same saved inference code as the notebook.')
p('The intended application is support for store-level planning. A forecast provides an estimate rather than a guarantee. Historical relationships, including promotion associations, may change over time.')

page('1. Problem and objectives')
heading('Problem statement')
p('Estimate one known store\'s daily sales on a future date, given planned opening status, promotion and holiday indicators. The target is a nonnegative continuous sales value in the dataset\'s units. Same-day customer counts are excluded because they would be unknown when producing an advance forecast.')
heading('Objectives')
p('Create a reproducible data preparation and modeling workflow. Identify meaningful calendar and store patterns. Compare at least two regression algorithms with a transparent reference. Report error in sales units and demonstrate an accessible prediction interface.')
heading('Practical purpose')
p('Estimated demand can inform inventory preparation and staffing discussions. Sales prediction alone does not calculate stock quantities, account for profit margins or optimize staffing. These decisions require additional operational constraints.')
heading('Success criteria')
p('The notebook runs from a fresh kernel, all splits respect time order, test observations do not influence preprocessing or model selection, app predictions match the saved method, and the report contains measured scores and interpreted figures. Improvement over the baseline is evaluated rather than assumed.')

page('2. Dataset and provenance')
p('Source: Kaggle Rossmann Store Sales competition. The supplied problem describes historical daily sales across 1,115 stores. The implementation uses train.csv for labeled observations and store.csv for store metadata. Competition test.csv is not scored because its target labels are unavailable.')
table([['Field group','Role'],['Sales','Target only'],['Store, Date','Store identity and calendar features'],['Open, Promo, StateHoliday, SchoolHoliday','Planned scheduling information'],['StoreType, Assortment, CompetitionDistance','Store metadata'],['Customers','Excluded to avoid unavailable same-day information']])
p('The workflow deliberately excludes extended promotion and competitor-opening history fields that require additional as-of-date interpretation. Static metadata is assumed available at the forecast origin; this assumption should be checked before a real operational deployment.')
p(('Actual modeling scope: '+metrics['scope']) if metrics else 'Actual modeling scope: pending data acquisition. Full data is the default; the first 100 store IDs may be used only if resources require it.')
p('Source files stay unchanged. The training output records SHA-256 hashes for traceability. Data access and redistribution must follow competition rules. Source: https://www.kaggle.com/c/rossmann-store-sales/data')

page('3. Cleaning and preparation')
p('Parse Date explicitly and sort by date and store. Validate required columns, nonnegative finite labels and binary scheduling flags. Reject duplicate store/date keys and nonunique store metadata rather than deleting records without explanation. Merge sales and store information with a many-to-one validation.')
p('Missing labels, missing required schedules and unmatched stores stop the run with an actionable message. A known closed store must have zero recorded sales for the deterministic closure rule to be accepted. Numeric metadata missingness uses the training median. Missing categorical metadata becomes Unknown. The fitted pipeline applies the same transformations during inference.')
heading('Missing values and duplicates')
if metrics:
    missing={k:v for k,v in metrics['missing'].items() if v}
    p('Missing counts after merge: '+escape(str(missing))+'. Duplicate store/date rows: '+str(metrics['duplicates'])+'. Only selected feature columns enter the model; unused metadata can remain missing.')
else:p('Measured missing-value counts and duplicate checks remain pending. These will populate from the actual run rather than assumptions about the dataset.')
heading('Reproducibility')
p('Use the pinned dependency file, a fixed random seed of 42 and shared functions for features and inference. Preserve the date split definitions and source files. Environment versions, settings and date ranges accompany saved metrics.')

page('4. EDA: time and weekday')
chart('trend')
p('The trend uses a seven-day rolling mean of daily sales per observed store within training dates. It smooths weekday fluctuations. Changing coverage or store composition can alter this series, so it should not automatically be interpreted as same-store growth.')
chart('weekday')
p('The weekday boxplot uses open days. Monday is 1 and Sunday is 7. Review typical sales and dispersion. Add the specific strongest and weakest patterns after inspecting the actual plot.')

page('5. EDA: promotions and stores')
chart('promotion')
p('The promotion comparison includes open days and shows an association. Store mix, season and weekday may confound differences. This comparison cannot establish the incremental sales caused by a promotion.')
chart('store_type')
p('The store-type comparison summarizes sales distributions across categories. Differences can reflect location, assortment or store scale. Explain observed categories using actual figures before submission. Outlier points are hidden for display only; training retains valid observations.')

page('6. Modeling methodology')
table([['Method','Purpose and settings'],['Store/weekday mean','Reference from open training days. Fall back to store mean, then global mean.'],['Ridge regression','Additive linear model with L2 regularization; alpha=10, lsqr solver.'],['Random Forest','100 trees, maximum depth 18, minimum leaf size 5, max_features=0.8, seed=42.']])
p('Categorical features use one-hot encoding with unknown categories ignored. Numeric features include calendar trend and competition distance, with median imputation and standardization. Both model pipelines fit open days. All methods return zero for known closures and clip learned predictions to a nonnegative value.')
heading('Time separation')
p('The last 42 calendar days form test. The previous 42 days form validation, with all earlier observations forming training. Validation MAE chooses among the two ML methods and the baseline. The selected method refits on training plus validation and receives one final test evaluation. EDA uses training dates only.')
if metrics:table([['Split','Start','End','Rows']]+[[k,v['start'],v['end'],v['rows']] for k,v in metrics['splits'].items()])
else:p('Exact split dates and row counts will appear after a real training run.')
p('Calendar features allow forecasting without needing actual future sales lags. The model assumes supplied opening and promotion schedules are known. The saved artifact remains fitted through the validation end so its test evaluation stays reproducible.')

page('7. Evaluation and findings')
p('MAE is average absolute error in sales units. RMSE takes the square root of average squared error and emphasizes larger misses. R-squared compares squared error with a constant mean reference and can be negative. Report both all-day and open-day performance because predictable closures can lower aggregate errors.')
if metrics:
    table([['Validation method','MAE','RMSE','R2']]+[[n]+[f"{v['all'][k]:.3f}" for k in ['MAE','RMSE','R2']] for n,v in metrics['validation'].items()])
    p('Selected method: '+metrics['selected_model'])
    table([['Test subset','MAE','RMSE','R2']]+[[n]+[f"{v[k]:.3f}" if v[k] is not None else 'N/A' for k in ['MAE','RMSE','R2']] for n,v in metrics['test'].items()])
    p('Review errors by store and date before drawing operational conclusions. Explain the observed difference between open-day and overall error in your own words. Scores describe this held-out historical interval and do not guarantee future accuracy.')
else:
    p('<b>Results pending.</b> No real-data models have been trained. No numerical accuracy, ranking or EDA conclusion can be reported. Run the notebook after obtaining the source data, then regenerate this report.')
heading('Interpretation checklist')
p('Discuss whether either learned model improves on the baseline, whether larger misses dominate RMSE, which stores need further analysis, and whether the error magnitude suits a proposed practical use. Do not retune against the held-out test period.')

page('8. Application and deployment')
p('The Streamlit form takes a known store, a date following training, opening status, promotion and holiday indicators. The app loads the saved model bundle and the same feature/inference functions used in training. Invalid store IDs and invalid flags raise clear errors. Closed days return zero without calling the learned estimator.')
p('The interface warns when the requested date exceeds the six-week evaluation horizon. Historical Rossmann patterns cannot be assumed reliable for present-day business conditions. No calibrated confidence interval is supplied.')
heading('Deployment status')
p('Pending. A trained artifact, GitHub repository and authenticated Streamlit account are required. Publish app.py through Streamlit Community Cloud, check a fresh public browser session and record the verified URL here before submission.')
heading('Verification')
p('Automated synthetic fixtures test chronology, feature leakage exclusion, imputer stability, saved-model prediction parity, invalid inputs, known closures and EDA output. Synthetic scores are never treated as capstone findings. A real-data notebook restart/run-all and public deployment check remain necessary.')
heading('Demonstration sequence')
p('Show the dataset source, explain the chronological split, compare validation scores, present the final held-out metrics, predict an open day and demonstrate the zero-sales closure rule. State practical limitations clearly.')

page('9. Conclusion and references')
p('The implementation provides an end-to-end forecasting workflow with explicit time separation and consistent deployment inference. The empirical conclusion must depend on measured Rossmann results. Until data is supplied and the notebook runs, the project remains an implementation draft rather than a completed experimental submission.')
heading('Limitations and future work')
p('A single holdout does not measure performance over many forecast origins. Store and calendar associations may drift. Random Forest has limited trend extrapolation. Missing external factors can explain residual errors. Static store metadata requires an availability assumption. Future experiments can use rolling-origin validation, safely shifted lag features, boosted trees and calibrated uncertainty intervals.')
heading('References')
p('1. Kaggle. Rossmann Store Sales dataset and competition documentation.<br/>https://www.kaggle.com/c/rossmann-store-sales/data')
p('2. scikit-learn. Ridge regression documentation.<br/>https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html')
p('3. Streamlit. Community Cloud deployment documentation.<br/>https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app')
heading('Submission readiness')
p('Add student details, interpret the real figures, verify all reported scores, include the executed notebook and source, record a working deployment URL, and rehearse the viva. Every major step must be explainable by the student.')

def footer(canvas,doc):
    canvas.setFont('Helvetica',9)
    canvas.setFillColor(colors.HexColor('#607080'))
    canvas.drawString(45,28,'Retail Sales Prediction / DRAFT')
    canvas.drawRightString(550,28,str(doc.page))
SimpleDocTemplate(str(OUT/'Retail_Sales_Report_DRAFT.pdf'),pagesize=(595.28,841.89),rightMargin=45,leftMargin=45,topMargin=45,bottomMargin=48).build(story,onFirstPage=footer,onLaterPages=footer)
print(OUT/'Retail_Sales_Report_DRAFT.pdf')
