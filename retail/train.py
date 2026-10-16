"""Run with python -m retail.train; real data required."""
import argparse
import hashlib
import json
from pathlib import Path
import joblib
import pandas as pd
import sklearn
from retail.core import load_data, split_dates, features, make_model, fit_baseline, baseline_predict, model_predict, score

def train(raw='data/raw', output='artifacts', max_stores=None, trees=100):
    out = Path(output)
    out.mkdir(parents=True,exist_ok=True)
    data, stores = load_data(raw,max_stores)
    a,b,c = split_dates(data)
    baseline = fit_baseline(a)
    validation = {'Baseline':score(b,baseline_predict(baseline,b))}
    for name in ['Ridge','RandomForest']:
        model = make_model(name,trees)
        opened = a[a.Open==1]
        model.fit(features(opened),opened.Sales)
        validation[name] = score(b,model_predict(model,b))
    winner = min(validation,key=lambda n:validation[n]['all']['MAE'])
    development = pd.concat([a,b])
    opened = development[development.Open==1]
    final_baseline = fit_baseline(development)
    final_model = None
    if winner != 'Baseline':
        final_model = make_model(winner,trees)
        final_model.fit(features(opened),opened.Sales)
    predictions = baseline_predict(final_baseline,c) if winner=='Baseline' else model_predict(final_model,c)
    bundle = {'name':winner,'pipeline':final_model,'baseline':final_baseline,'stores':stores,'known_stores':sorted(opened.Store.unique().tolist()),'training_end':str(development.Date.max().date()),'sklearn_version':sklearn.__version__}
    metrics = {'selected_model':winner,'validation':validation,'test':score(c,predictions),'scope':f'{data.Store.nunique()} stores; '+('full dataset' if max_stores is None else f'first {max_stores} store IDs'),'splits':{label:{'start':str(d.Date.min().date()),'end':str(d.Date.max().date()),'rows':len(d)} for label,d in zip(['train','validation','test'],[a,b,c])}, 'missing':data.isna().sum().to_dict(),'duplicates':int(data.duplicated(['Store','Date']).sum()),'source':'https://www.kaggle.com/c/rossmann-store-sales/data','versions':{'sklearn':sklearn.__version__,'pandas':pd.__version__},'settings':{'seed':42,'trees':trees,'ridge_alpha':10,'forest_max_depth':18,'forest_min_samples_leaf':5},'sha256':{name:hashlib.sha256((Path(raw)/name).read_bytes()).hexdigest() for name in ['train.csv','store.csv']}}
    joblib.dump(bundle,out/'model.joblib')
    (out/'metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
    c[['Store','Date','Sales','Open']].assign(Prediction=predictions).to_csv(out/'test_predictions.csv',index=False)
    print(json.dumps({'selected_model':winner,'test':metrics['test']},indent=2))
    return metrics

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw',default='data/raw')
    parser.add_argument('--output',default='artifacts')
    parser.add_argument('--max-stores',type=int)
    parser.add_argument('--trees',type=int,default=100)
    args = parser.parse_args()
    if args.max_stores is not None and args.max_stores < 1:
        parser.error('--max-stores must be positive')
    train(args.raw,args.output,args.max_stores,args.trees)
