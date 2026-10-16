"""Synthetic fixtures verify software behavior, never model accuracy."""
import joblib
import numpy as np
import pandas as pd
import pytest
from retail.core import *
from retail.train import train

@pytest.fixture
def raw(tmp_path):
    folder=tmp_path/'raw'
    folder.mkdir()
    rows=[]
    for date in pd.date_range('2013-01-01',periods=180):
        for store in [1,2]:
            opened=int(date.dayofweek!=6)
            promo=int(date.dayofweek<3)
            rows.append(dict(Store=store,Date=date,Sales=opened*(1000+store*200+promo*400+date.day*5),Customers=999,Open=opened,Promo=promo,StateHoliday='0',SchoolHoliday=0))
    pd.DataFrame(rows).to_csv(folder/'train.csv',index=False)
    pd.DataFrame(dict(Store=[1,2],StoreType=['a','b'],Assortment=['a','c'],CompetitionDistance=[100,np.nan])).to_csv(folder/'store.csv',index=False)
    return folder

def test_split_features_and_training_only_imputation(raw):
    data,_=load_data(raw)
    a,b,c=split_dates(data)
    assert a.Date.max()<b.Date.min()<c.Date.min()
    assert b.Date.nunique()==c.Date.nunique()==42
    x=features(a)
    assert 'Customers' not in x and 'Sales' not in x
    assert features(a.assign(Customers=-999)).equals(x)
    model=make_model('Ridge')
    model.fit(x,a.Sales)
    before=model['preprocess'].named_transformers_['numeric']['impute'].statistics_.copy()
    model.predict(features(b.assign(CompetitionDistance=999999)))
    np.testing.assert_array_equal(before,model['preprocess'].named_transformers_['numeric']['impute'].statistics_)

def test_end_to_end_and_inference(raw,tmp_path):
    result=train(raw,tmp_path/'output',trees=3)
    bundle=joblib.load(tmp_path/'output/model.joblib')
    date=pd.Timestamp(bundle['training_end'])+pd.Timedelta(days=1)
    assert predict_one(bundle,1,date,0,0,'0',0)==0
    value=predict_one(bundle,1,date,1,1,'0',0)
    assert np.isfinite(value) and value>=0
    row=bundle['stores'].query('Store == 1').assign(Date=date,Open=1,Promo=1,StateHoliday='0',SchoolHoliday=0)
    expected=baseline_predict(bundle['baseline'],row)[0] if bundle['name']=='Baseline' else model_predict(bundle['pipeline'],row)[0]
    assert value==pytest.approx(expected)
    for params in [(999,date,1,0,'0',0),(1,date,2,0,'0',0),(1,date,1,0,'z',0),(1,bundle['training_end'],1,0,'0',0),(1,'bad-date',1,0,'0',0)]:
        with pytest.raises(ValueError): predict_one(bundle,*params)
    assert set(result['validation'])=={'Baseline','Ridge','RandomForest'}
    assert result['test']['all']['rows']==84

def test_duplicate_rejected(raw):
    d=pd.read_csv(raw/'train.csv')
    pd.concat([d,d.iloc[:1]]).to_csv(raw/'train.csv',index=False)
    with pytest.raises(ValueError,match='Duplicate'):load_data(raw)

def test_closed_day_anomaly_rejected(raw):
    d=pd.read_csv(raw/'train.csv')
    d.loc[d.Open==0,'Sales']=1
    d.to_csv(raw/'train.csv',index=False)
    with pytest.raises(ValueError,match='Closed'):load_data(raw)

def test_missing_data_message(tmp_path):
    with pytest.raises(FileNotFoundError,match='Kaggle'):load_data(tmp_path)

def test_eda(raw,tmp_path):
    from retail.eda import create_charts
    charts=create_charts(raw,tmp_path/'figures')
    assert len(charts)==4 and all(p.stat().st_size>1000 for p in charts)

def test_app_untrained():
    from streamlit.testing.v1 import AppTest
    from pathlib import Path
    if (Path('artifacts')/'model.joblib').exists():
        pytest.skip('Real model present; missing-model branch does not apply.')
    app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py')).run()
    assert not app.exception
    assert 'not trained' in app.info[0].value

def test_app_prediction(raw,tmp_path,monkeypatch):
    from streamlit.testing.v1 import AppTest
    from pathlib import Path
    train(raw,tmp_path/'app-artifacts',trees=3)
    monkeypatch.setenv('RETAIL_MODEL_PATH',str(tmp_path/'app-artifacts/model.joblib'))
    app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py')).run()
    assert not app.exception
    app.button[0].click().run()
    assert not app.exception and app.metric
    app.checkbox[0].uncheck()
    app.button[0].click().run()
    assert app.metric[0].value=='0.00'
    app.toggle[0].set_value(False).run()
    assert app.metric[0].value=='0.00'
