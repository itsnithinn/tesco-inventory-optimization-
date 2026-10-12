"""Run after src/analyze.py. Checks determinism, FEFO, causality and SQLite exports."""
import sys,hashlib,sqlite3
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from generate import ROOT,generate
from analyze import fit
from simulate import simulate
import pandas as pd
before=hashlib.sha256((ROOT/'data/demand.csv').read_bytes()).hexdigest()
products,demand=generate()
assert before==hashlib.sha256((ROOT/'data/demand.csv').read_bytes()).hexdigest()
train=demand[demand.date<'2025-10-01'];hold=demand[demand.date>='2025-10-01'];params,_=fit(products,train)
one=hold[(hold.store=='London Central')&(hold.sku=='SKU001')].copy()
a,oa,_=simulate(products,one,params,'proposed')
changed=one.copy();changed.loc[changed.date>'2025-11-01','demand']*=10
b,ob,_=simulate(products,changed,params,'proposed')
pd.testing.assert_frame_equal(a[a.date<='2025-11-01'],b[b.date<='2025-11-01'])
# Previous closing is next opening; policy starts with no pipeline.
daily=pd.read_csv(ROOT/'results/daily_holdout.csv')
previous=daily.groupby(['policy','store','sku']).closing.shift()
assert (daily.loc[previous.notna(),'opening']==previous.dropna()).all()
con=sqlite3.connect(ROOT/'results/inventory.sqlite')
assert con.execute('SELECT COUNT(*) FROM daily_holdout').fetchone()[0]==33120
for query in (ROOT/'sql/analysis.sql').read_text().split(';'):
    if query.strip():con.execute(query).fetchall()
# Known expiry fixture: no demand for first 7 days means initial milk expires on day 8.
fixture=one.head(9).copy();fixture['demand']=0
x,_,_=simulate(products,fixture,params,'baseline')
assert x.iloc[7].waste>=x.iloc[0].opening
print('PASS: deterministic generation; no future-demand leakage; stock continuity; SQLite queries; expiry fixture.')
