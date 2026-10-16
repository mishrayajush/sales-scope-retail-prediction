from pathlib import Path
import datetime as dt
import os
import joblib
import pandas as pd
import streamlit as st
from retail.core import predict_one
from retail.theme import render_theme

st.set_page_config(page_title='SalesScope · Retail forecasting',page_icon='◈',layout='wide')
brand,appearance=st.columns([5,1],vertical_alignment='center')
with brand:
    st.title('SalesScope',anchor=False)
with appearance:
    render_theme()
st.subheader('Predict daily store sales',anchor=False)
st.write('Select a store and a date to estimate how much it may sell that day.')
st.divider()

MODEL_PATH=Path(os.environ.get('RETAIL_MODEL_PATH',str(Path(__file__).parent/'artifacts'/'model.joblib')))
@st.cache_resource
def load_model(path):
    return joblib.load(path)

if not MODEL_PATH.exists():
    st.info('Model is not trained yet. Add the Rossmann CSV files to data/raw and run: python -m retail.train')
    st.stop()
bundle=load_model(str(MODEL_PATH.resolve()))
end=pd.Timestamp(bundle['training_end']).date()
st.caption('Historical demo · Sales data from 2013–2015. Estimates for current dates have not been validated.')
with st.form('forecast'):
    left,right=st.columns(2,gap='large')
    with left:
        store=st.selectbox('Which store?',bundle['known_stores'],format_func=lambda value:f'Store {value}',help='Each number identifies a Rossmann branch in the historical dataset.')
    with right:
        date=st.date_input('Which date?',value=end+dt.timedelta(days=1),min_value=end+dt.timedelta(days=1),max_value=max(dt.date.today(),end)+dt.timedelta(days=365),help='The default date follows the training period. Later dates, including tomorrow, are available for demonstration.')
    st.markdown('**What is planned for that day?**')
    plans,holidays=st.columns(2,gap='large')
    with plans:
        opened=st.checkbox('Store will be open',value=True,help='A closed store always has an estimated sales value of zero.')
        promo=st.checkbox('Sale or promotion planned')
    with holidays:
        holiday=st.selectbox('Holiday type',['0','a','b','c'],format_func=lambda x:{'0':'No holiday','a':'Public holiday','b':'Easter','c':'Christmas'}[x])
        school=st.checkbox('Schools closed for a holiday')
    submit=st.form_submit_button('Estimate sales',width='stretch')
if submit:
    st.session_state.pop('last_forecast',None)
    try:
        result=predict_one(bundle,store,date,int(opened),int(promo),holiday,int(school))
        st.session_state['last_forecast']={'value':result,'store':store,'date':date,'open':opened,'promo':promo,'holiday':holiday,'school':school}
    except ValueError as error:
        st.error(str(error))
forecast=st.session_state.get('last_forecast')
if forecast:
    st.subheader('Sales estimate',anchor=False)
    st.metric('Estimated daily sales',f"{forecast['value']:,.2f}")
    st.caption(f"Store {forecast['store']} · {forecast['date'].strftime('%d %B %Y')} · Dataset sales units")
    with st.expander('View the settings used'):
        st.write(f"Store {'open' if forecast['open'] else 'closed'} · Promotion {'planned' if forecast['promo'] else 'not planned'}")
        st.write(f"State holiday: {dict(zip(['0','a','b','c'],['None','Public holiday','Easter','Christmas']))[forecast['holiday']]} · School holiday: {'yes' if forecast['school'] else 'no'}")
        st.caption('This result reflects the last submitted settings. Submit again after changing the form.')
    if not forecast['open']:
        st.caption('The store is planned to be closed, so estimated sales are zero.')
    if forecast['date']>end+dt.timedelta(days=42):
        st.warning('This date is beyond the six-week evaluation horizon. Reliability this far ahead has not been verified.')
else:
    st.caption('Choose your settings above, then select Estimate sales to see the result.')
st.divider()
with st.expander('How this estimate works'):
    st.write('SalesScope estimates daily sales from historical Rossmann store data, calendar patterns and planned promotions.')
    st.caption(f"Model: {bundle['name']} · Training data through {end.strftime('%d %B %Y')}")
    st.write('Amounts use the original dataset’s sales units. This historical model supports learning and demonstration. Business conditions can change, and distant forecasts have not been validated. Promotion associations do not establish causal effects.')
st.caption('SalesScope · Retail Sales Prediction capstone')
