"""Custom SalesScope interface. Run: python web_app.py."""
from datetime import date, timedelta
from pathlib import Path
from functools import lru_cache
import os
import joblib
import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request
from retail.core import predict_one

def create_app(model_path=None, history_path=None):
    app=Flask(__name__)
    app.config['MAX_CONTENT_LENGTH']=8192
    app.config['TEMPLATES_AUTO_RELOAD']=True
    path=Path(model_path or os.environ.get('RETAIL_MODEL_PATH',Path(__file__).parent/'artifacts/model.joblib'))
    history_file=Path(history_path or os.environ.get('RETAIL_HISTORY_PATH',Path(__file__).parent/'data/raw/train.csv'))
    @lru_cache(maxsize=1)
    def model():
        return joblib.load(path)

    @lru_cache(maxsize=1)
    def history_source():
        frame=pd.read_csv(history_file,usecols=['Store','Date','Sales'],parse_dates=['Date'])
        frame=frame[frame.Date<=pd.Timestamp(model()['training_end'])].sort_values('Date')
        if frame.duplicated(['Store','Date']).any() or not np.isfinite(frame.Sales).all() or (frame.Sales<0).any():
            raise ValueError('Historical sales data failed validation.')
        return frame

    @lru_cache(maxsize=4000)
    def store_history(store,period):
        frame=history_source()
        data=frame[frame.Store==store].copy()
        if data.empty:
            return None
        frequency={'week':'W-SUN','month':'M','year':'Y'}[period]
        data['Period']=data.Date.dt.to_period(frequency)
        groups=data.groupby('Period').Sales.agg(['sum','count'])
        groups=groups.reindex(pd.period_range(groups.index.min(),groups.index.max(),freq=frequency))
        points=[]
        for bucket,row in groups.iterrows():
            days=int(row['count']) if pd.notna(row['count']) else 0
            start,end=bucket.start_time.date(),bucket.end_time.date()
            points.append({'start':start.isoformat(),'end':end.isoformat(),'sales':float(row['sum']) if days else None,'days':days,'partial':days!=(end-start).days+1})
        return dict(store=store,period=period,points=points,start=data.Date.min().date().isoformat(),end=data.Date.max().date().isoformat(),training_end=model()['training_end'],total=float(data.Sales.sum()),observed_days=len(data))

    @app.get('/api/history')
    def history():
        if not path.exists() or not history_file.exists():
            return jsonify(error='Sales history is unavailable. Keep the original train.csv file in data/raw.'),503
        period=request.args.get('period','week')
        raw_store=request.args.get('store','')
        if period not in ['week','month','year'] or not raw_store.isdecimal():
            return jsonify(error='Choose a valid store and weekly, monthly or yearly view.'),400
        store=int(raw_store)
        if store not in model()['known_stores']:
            return jsonify(error='Choose a store from the suggestions.'),400
        try:
            result=store_history(store,period)
            return (jsonify(result),200) if result else (jsonify(error='No training-period sales history exists for this store.'),404)
        except (ValueError,KeyError):
            app.logger.exception('Invalid sales history source')
            return jsonify(error='Sales history could not be loaded. Check the original dataset.'),503

    @app.get('/')
    def index():
        if not path.exists():
            return render_template('index.html',ready=False),503
        bundle=model()
        end=date.fromisoformat(bundle['training_end'])
        return render_template('index.html',ready=True,stores=bundle['known_stores'],start=(end+timedelta(days=1)).isoformat(),maximum=(max(date.today(),end)+timedelta(days=365)).isoformat(),training_end=end.strftime('%d %B %Y'))

    @app.post('/api/predict')
    def predict():
        if not path.exists():
            return jsonify(error='The model is not trained yet. Add the dataset and run the training notebook.'),503
        payload=request.get_json(silent=True)
        if not isinstance(payload,dict):
            return jsonify(error='Provide the store, date and daily plans.'),400
        try:
            store=payload.get('store')
            if type(store) is not int:
                raise ValueError('Choose a valid store.')
            for key in ['open','promo','school_holiday']:
                if type(payload.get(key)) is not bool:
                    raise ValueError('Provide valid opening, promotion and school holiday choices.')
            raw_date=payload.get('date')
            if not isinstance(raw_date,str):
                raise ValueError('Choose a valid date.')
            chosen=date.fromisoformat(raw_date)
            if chosen.isoformat()!=raw_date or chosen>max(date.today(),date.fromisoformat(model()['training_end']))+timedelta(days=365):
                raise ValueError('Choose a date within the calendar range.')
            holiday=payload.get('holiday')
            if holiday not in ['0','a','b','c']:
                raise ValueError('Choose a valid holiday type.')
            bundle=model()
            value=predict_one(bundle,store,chosen,int(payload['open']),int(payload['promo']),holiday,int(payload['school_holiday']))
            return jsonify(value=value,store=store,date=chosen.isoformat(),opened=payload['open'],promo=payload['promo'],holiday=holiday,school_holiday=payload['school_holiday'],outside_horizon=chosen>date.fromisoformat(bundle['training_end'])+timedelta(days=42))
        except (ValueError,TypeError) as error:
            return jsonify(error=str(error)),400

    @app.get('/health')
    def health():
        return jsonify(status='ok',model_available=path.exists())
    return app

app=create_app()
if __name__=='__main__':
    from waitress import serve
    print('SalesScope is ready at http://127.0.0.1:5000',flush=True)
    serve(app,host='127.0.0.1',port=5000)
