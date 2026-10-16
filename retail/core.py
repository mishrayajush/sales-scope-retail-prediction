"""Shared data, feature, model and inference contracts."""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

CAT = ['Store', 'StoreType', 'Assortment', 'DayOfWeek', 'Month', 'StateHoliday']
NUM = ['Year', 'Day', 'WeekOfYear', 'Trend', 'Promo', 'SchoolHoliday', 'CompetitionDistance']
FEATURES = CAT + NUM

def load_data(raw='data/raw', max_stores=None):
    raw = Path(raw)
    missing = [f for f in ['train.csv', 'store.csv'] if not (raw / f).exists()]
    if missing:
        raise FileNotFoundError(f"Download {', '.join(missing)} from Kaggle into {raw.resolve()}. See data/raw/README.md.")
    sales = pd.read_csv(raw / 'train.csv', dtype={'StateHoliday': str})
    stores = pd.read_csv(raw / 'store.csv')
    required = {'Store','Date','Sales','Open','Promo','StateHoliday','SchoolHoliday'}
    if not required.issubset(sales):
        raise ValueError(f'Missing sales columns: {required - set(sales)}')
    if not {'Store','StoreType','Assortment','CompetitionDistance'}.issubset(stores):
        raise ValueError('store.csv is missing required store metadata.')
    sales['Date'] = pd.to_datetime(sales['Date'], errors='raise')
    if sales[['Store','Date','Sales','Open','Promo','StateHoliday','SchoolHoliday']].isna().any().any():
        raise ValueError('Missing required labels or scheduling values. Investigate before training.')
    if sales.duplicated(['Store','Date']).any() or stores.Store.duplicated().any():
        raise ValueError('Duplicate store/date rows or duplicate store metadata. Investigate before training.')
    if not np.isfinite(sales.Sales).all() or (sales.Sales < 0).any():
        raise ValueError('Sales must be finite and nonnegative.')
    for col in ['Open','Promo','SchoolHoliday']:
        if not sales[col].isin([0,1]).all():
            raise ValueError(f'{col} must be 0 or 1.')
    if not sales.StateHoliday.isin(['0','a','b','c']).all():
        raise ValueError('Unknown StateHoliday code.')
    if ((sales.Open == 0) & (sales.Sales != 0)).any():
        raise ValueError('Closed stores have nonzero sales. Investigate the zero-sales rule.')
    if not sales.Store.isin(stores.Store).all():
        raise ValueError('Missing store metadata.')
    if max_stores:
        sales = sales[sales.Store.isin(sorted(sales.Store.unique())[:max_stores])]
    data = sales.merge(stores, on='Store', validate='many_to_one').sort_values(['Date','Store']).reset_index(drop=True)
    return data, stores[stores.Store.isin(data.Store.unique())].copy()

def features(data):
    x = data.copy()
    dates = pd.to_datetime(x['Date'], errors='raise')
    x['DayOfWeek'] = dates.dt.dayofweek + 1
    x['Month'], x['Year'], x['Day'] = dates.dt.month, dates.dt.year, dates.dt.day
    x['WeekOfYear'] = dates.dt.isocalendar().week.astype(int)
    x['Trend'] = (dates - pd.Timestamp('2013-01-01')).dt.days
    for col in CAT:
        x[col] = x[col].fillna('Unknown').astype(str)
    return x[FEATURES]

def split_dates(data):
    end = data.Date.max().normalize()
    test_start = end - pd.Timedelta(days=41)
    val_start = test_start - pd.Timedelta(days=42)
    parts = (data[data.Date < val_start], data[(data.Date >= val_start) & (data.Date < test_start)], data[data.Date >= test_start])
    if any(p.empty or not (p.Open == 1).any() for p in parts):
        raise ValueError('Need more than 84 days and open-day observations in each split.')
    return parts

def make_model(name, trees=100):
    prep = ColumnTransformer([
        ('categorical', OneHotEncoder(handle_unknown='ignore', sparse_output=True), CAT),
        ('numeric', Pipeline([('impute',SimpleImputer(strategy='median', keep_empty_features=True)), ('scale',StandardScaler())]), NUM)
    ])
    if name == 'Ridge':
        estimator = Ridge(alpha=10.0, solver='lsqr')
    elif name == 'RandomForest':
        estimator = RandomForestRegressor(n_estimators=trees, max_depth=18, min_samples_leaf=5, max_features=0.8, n_jobs=-1, random_state=42)
    else:
        raise ValueError(f'Unknown model {name}')
    return Pipeline([('preprocess',prep), ('model',estimator)])

def fit_baseline(train):
    d = train[train.Open == 1].copy()
    d['weekday'] = d.Date.dt.dayofweek
    return {'pairs':d.groupby(['Store','weekday']).Sales.mean().to_dict(), 'stores':d.groupby('Store').Sales.mean().to_dict(), 'global':float(d.Sales.mean())}

def baseline_predict(baseline, data):
    return np.array([0.0 if r.Open == 0 else baseline['pairs'].get((r.Store,r.Date.dayofweek),baseline['stores'].get(r.Store,baseline['global'])) for r in data.itertuples()])

def model_predict(model, data):
    result = np.zeros(len(data))
    mask = data.Open.to_numpy() == 1
    if mask.any():
        result[mask] = np.maximum(0, model.predict(features(data.loc[mask])))
    return result

def score(data, pred):
    result = {}
    for label, mask in [('all',np.ones(len(data),dtype=bool)), ('open',data.Open.to_numpy()==1)]:
        y, p = data.Sales.to_numpy()[mask], pred[mask]
        result[label] = {'MAE':float(mean_absolute_error(y,p)), 'RMSE':float(np.sqrt(mean_squared_error(y,p))), 'R2':float(r2_score(y,p)) if len(y)>1 else None, 'rows':len(y)}
    return result

def predict_one(bundle, store, date, opened, promo, state_holiday, school_holiday):
    if store not in bundle['known_stores']:
        raise ValueError('Select a store with open-day training history.')
    for value in [opened,promo,school_holiday]:
        if value not in [0,1]:
            raise ValueError('Opening, promotion and school holiday flags must be 0 or 1.')
    if state_holiday not in ['0','a','b','c']:
        raise ValueError('Unknown state holiday code.')
    date = pd.Timestamp(date)
    if pd.isna(date) or date.tzinfo is not None:
        raise ValueError('Provide a valid date without a timezone.')
    date = date.normalize()
    if date <= pd.Timestamp(bundle['training_end']):
        raise ValueError('Forecast date must be later than the final training date.')
    row = bundle['stores'].loc[bundle['stores'].Store == store].copy()
    row = row.assign(Date=date,Open=opened,Promo=promo,StateHoliday=state_holiday,SchoolHoliday=school_holiday)
    if bundle['name'] == 'Baseline':
        return float(baseline_predict(bundle['baseline'], row)[0])
    return float(model_predict(bundle['pipeline'],row)[0])
