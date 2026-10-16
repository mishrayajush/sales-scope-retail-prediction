import joblib
import pandas as pd
import pytest
from web_app import create_app

@pytest.fixture
def history_client(tmp_path):
    artifact=tmp_path/'model.joblib'
    joblib.dump({'known_stores':[1,2,3],'training_end':'2015-06-19'},artifact)
    raw=tmp_path/'train.csv'
    pd.DataFrame({'Store':[1,1,1,1,1,2],'Date':['2013-01-01','2013-01-02','2013-01-08','2015-06-19','2015-06-20','2013-01-01'],'Sales':[10,20,30,40,9999,900]}).to_csv(raw,index=False)
    return create_app(artifact,raw).test_client()

@pytest.mark.parametrize('period',['week','month','year'])
def test_history_totals_and_training_cutoff(history_client,period):
    response=history_client.get(f'/api/history?store=1&period={period}')
    assert response.status_code==200
    data=response.json
    assert data['total']==100
    assert data['observed_days']==4
    assert data['end']=='2015-06-19'
    assert sum(p['sales'] or 0 for p in data['points'])==100
    assert all(p['sales']!=9999 for p in data['points'])
    assert any(p['partial'] for p in data['points'])

def test_missing_periods_and_store_isolation(history_client):
    weekly=history_client.get('/api/history?store=1&period=week').json
    assert any(p['sales'] is None and p['days']==0 for p in weekly['points'])
    yearly=history_client.get('/api/history?store=1&period=year').json
    assert [p['sales'] for p in yearly['points']]==[60,None,40]
    assert history_client.get('/api/history?store=2&period=year').json['total']==900
    assert history_client.get('/api/history?store=3').status_code==404

def test_history_validation(history_client):
    for query in ['store=999','store=bad','store=1&period=day','store=-1','period=week']:
        assert history_client.get('/api/history?'+query).status_code==400

def test_history_missing_file(tmp_path):
    artifact=tmp_path/'model.joblib'
    joblib.dump({'known_stores':[1],'training_end':'2015-06-19'},artifact)
    client=create_app(artifact,tmp_path/'missing.csv').test_client()
    assert client.get('/api/history?store=1').status_code==503
