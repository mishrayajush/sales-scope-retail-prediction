from datetime import date, timedelta
from pathlib import Path
import joblib
import pytest
from web_app import create_app
from retail.core import predict_one

@pytest.fixture
def client():
    path=Path('artifacts/model.joblib')
    if not path.exists():
        pytest.skip('Train the model before running real-artifact API checks.')
    app=create_app(path)
    app.config['TESTING']=True
    return app.test_client()

def test_page_and_prediction_parity(client):
    response=client.get('/')
    assert response.status_code==200
    assert b'How much could your' in response.data
    bundle=joblib.load('artifacts/model.joblib')
    tomorrow=max(date.today(),date.fromisoformat(bundle['training_end']))+timedelta(days=1)
    payload=dict(store=bundle['known_stores'][0],date=tomorrow.isoformat(),open=True,promo=False,holiday='0',school_holiday=False)
    result=client.post('/api/predict',json=payload)
    assert result.status_code==200
    assert result.json['value']==pytest.approx(predict_one(bundle,payload['store'],tomorrow,1,0,'0',0))
    payload['open']=False
    assert client.post('/api/predict',json=payload).json['value']==0

def test_invalid_requests(client):
    valid=dict(store=1,date='2026-10-17',open=True,promo=False,holiday='0',school_holiday=False)
    for change in [dict(store=99999),dict(store='1'),dict(open='false'),dict(date='2013-01-01'),dict(date='not-a-date'),dict(holiday='bad'),dict(date='2050-01-01')]:
        result=client.post('/api/predict',json={**valid,**change})
        assert result.status_code==400
        assert result.json['error']
    assert client.post('/api/predict',json=[]).status_code==400
    assert client.post('/api/predict',data='broken',content_type='application/json').status_code==400

def test_missing_model(tmp_path):
    client=create_app(tmp_path/'missing.joblib').test_client()
    assert client.get('/').status_code==503
    assert client.post('/api/predict',json={}).status_code==503
    assert client.get('/health').json['model_available'] is False
