"""Execute all notebook cells in an isolated SYNTHETIC workspace, never real scores."""
from pathlib import Path
import json
import os
import sys
import nbformat
from nbclient import NotebookClient
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
work=ROOT/'tmp/notebook-synthetic'
(work/'data/raw').mkdir(parents=True,exist_ok=True)
(work/'retail').mkdir(exist_ok=True)
rows=[]
for date in pd.date_range('2013-01-01',periods=180):
    for store in [1,2]:
        opened=int(date.dayofweek!=6)
        rows.append(dict(Store=store,Date=date,Sales=opened*(1200+store*100+date.day*5),Customers=999,Open=opened,Promo=int(date.dayofweek<3),SchoolHoliday=0,StateHoliday='0'))
pd.DataFrame(rows).to_csv(work/'data/raw/train.csv',index=False)
pd.DataFrame(dict(Store=[1,2],StoreType=['a','b'],Assortment=['a','c'],CompetitionDistance=[100,200])).to_csv(work/'data/raw/store.csv',index=False)
kernels=ROOT/'tmp/jupyter/kernels/retail-test'
kernels.mkdir(parents=True,exist_ok=True)
(kernels/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'Retail test','language':'python'}))
os.environ['JUPYTER_PATH']=str(ROOT/'tmp/jupyter')
os.environ['JUPYTER_RUNTIME_DIR']=str(ROOT/'tmp/jupyter-runtime')
Path(os.environ['JUPYTER_RUNTIME_DIR']).mkdir(exist_ok=True)
nb=nbformat.read(ROOT/'Retail_Sales_Prediction.ipynb',as_version=4)
nb.cells.insert(0,nbformat.v4.new_code_cell(f'import sys\nsys.path.insert(0, {str(ROOT)!r})\nprint("SYNTHETIC WORKFLOW CHECK ONLY")'))
NotebookClient(nb,timeout=180,kernel_name='retail-test',resources={'metadata':{'path':str(work)}}).execute()
nbformat.write(nb,work/'executed_SYNTHETIC.ipynb')
print('All notebook cells executed on synthetic fixtures. No real-data performance claim.')
