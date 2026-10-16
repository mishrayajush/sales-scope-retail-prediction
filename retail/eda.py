from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from retail.core import load_data, split_dates

def create_charts(raw='data/raw', output='artifacts/figures', max_stores=None):
    data,_ = load_data(raw,max_stores)
    train,_,_ = split_dates(data)
    out=Path(output)
    out.mkdir(parents=True,exist_ok=True)
    sns.set_theme(style='whitegrid')
    paths=[]
    def save(name,title,x,y):
        plt.title(title)
        plt.xlabel(x)
        plt.ylabel(y)
        plt.tight_layout()
        p=out/f'{name}.png'
        plt.savefig(p,dpi=160)
        plt.close()
        paths.append(p)
    plt.figure(figsize=(9,4))
    train.groupby('Date').Sales.mean().rolling(7).mean().plot()
    save('trend','Training period: 7-day rolling mean sales per observed store','Date','Mean daily sales (dataset units)')
    opened=train[train.Open==1].copy()
    opened['Weekday']=opened.Date.dt.dayofweek+1
    for col,name,title in [('Weekday','weekday','Open-day sales by weekday (1=Monday)'),('Promo','promotion','Open-day sales by promotion status'),('StoreType','store_type','Open-day sales by store type')]:
        plt.figure(figsize=(9,4))
        sns.boxplot(data=opened,x=col,y='Sales',showfliers=False)
        save(name,title,col,'Daily sales (dataset units)')
    return paths

if __name__=='__main__':
    create_charts()
