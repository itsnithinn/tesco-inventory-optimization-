"""Run all generation, training, holdout evaluation, SQL export and dashboard export."""
import json,math,sqlite3,hashlib
import numpy as np
import pandas as pd
from generate import generate,ROOT
from simulate import simulate
DISCLOSURE='Independent portfolio project using synthetic data. Not affiliated with or endorsed by Tesco. Results are simulated and do not represent Tesco’s actual performance.'

def fit(products,train):
    consumption=train.merge(products,on='sku');consumption['value']=consumption.demand*consumption.unit_cost
    abc=consumption.groupby('sku').value.sum().sort_values(ascending=False)
    prior=abc.cumsum().shift(fill_value=0)/abc.sum()
    classes={s:('A' if prior[s]<.8 else 'B' if prior[s]<.95 else 'C') for s in abc.index}
    params={}; recommendations=[]
    for (store,sku),g in train.groupby(['store','sku']):
        mu=float(g.demand.mean());sd=float(g.demand.std()); lead=float(g.supplier_lead.mean());ls=float(g.supplier_lead.std())
        z={'A':1.96,'B':1.645,'C':1.282}[classes[sku]]
        ss=z*math.sqrt((lead+1)*sd**2+mu**2*ls**2)
        q=dict(mean=mu,std=sd,lead=lead,safety_stock=math.ceil(ss),rop=math.ceil(mu*(lead+1)+ss),target=math.ceil(mu*(lead+2)+ss),abc=classes[sku],cv=sd/mu)
        params[(store,sku)]=q;recommendations.append(dict(store=store,sku=sku,**q))
    return params,pd.DataFrame(recommendations)

def summarize(df):
    n=df.date.nunique(); cogs=float(df.cogs.sum()); inv=float(df.inventory_value.sum()/n)
    holding=float(df.inventory_value.sum()*.20/365);order=float(df.orders.sum()*2)
    cost=holding+order+float(df.writeoff.sum())+float(df.lost_margin.sum())
    return dict(days=n,demand=int(df.demand.sum()),sales=int(df.sales.sum()),fill_rate=float(df.sales.sum()/df.demand.sum()),lost_units=int(df.lost.sum()),average_inventory=inv,holding_cost=holding,waste_units=int(df.waste.sum()),writeoff=float(df.writeoff.sum()),orders=int(df.orders.sum()),ordering_cost=order,lost_margin=float(df.lost_margin.sum()),total_cost=cost,annualized_turnover=cogs/inv*365/n,days_inventory=inv/(cogs/n))

def main():
    products,demand=generate(); train=demand[demand.date<'2025-10-01'];hold=demand[demand.date>='2025-10-01']
    params,recs=fit(products,train)
    runs=[simulate(products,hold,params,p) for p in ['baseline','proposed']]
    daily=pd.concat([r[0] for r in runs],ignore_index=True);orders=pd.concat([r[1] for r in runs],ignore_index=True);batches=pd.concat([r[2] for r in runs],ignore_index=True)
    # Full-year descriptive baseline is separate from Q4 policy evaluation.
    # Jan parameters are an explicit synthetic planning prior; never used in holdout fitting.
    initial={ (s,p.sku):dict(mean=p.base_demand,lead=p.nominal_lead) for s in demand.store.unique() for p in products.itertuples() }
    full,fullorders,fullbatches=simulate(products,demand,initial,'baseline')
    # Fixed-origin 92-day forecasts: training weekday means vs last training week.
    errors=[]
    for key,g in train.groupby(['store','sku']):
        target=hold[(hold.store==key[0])&(hold.sku==key[1])].copy();gd=g.copy();gd['dow']=pd.to_datetime(gd.date).dt.dayofweek
        means=gd.groupby('dow').demand.mean();last=gd.tail(7).set_index('dow').demand
        dow=pd.to_datetime(target.date).dt.dayofweek
        for model,pred in [('weekday_mean',dow.map(means)),('seasonal_naive',dow.map(last))]:
            errors.append(dict(store=key[0],sku=key[1],model=model,abs_error=float(np.abs(target.demand.to_numpy()-pred.to_numpy()).sum()),units=int(target.demand.sum()),n=len(target)))
    forecasts=pd.DataFrame(errors); fm=forecasts.groupby('model')[['abs_error','units','n']].sum();fm['wape']=fm.abs_error/fm.units;fm['mae']=fm.abs_error/fm.n
    summary={p:summarize(g) for p,g in daily.groupby('policy')}
    out=ROOT/'results';out.mkdir(exist_ok=True)
    for name,df in [('daily_holdout',daily),('orders',orders),('batches',batches),('recommendations',recs),('forecast_errors',forecasts),('forecast_metrics',fm.reset_index()),('full_year_baseline',full)]:df.to_csv(out/f'{name}.csv',index=False)
    con=sqlite3.connect(out/'inventory.sqlite')
    for name,df in [('products',products),('demand',demand),('daily_holdout',daily),('orders',orders),('batches',batches),('recommendations',recs),('full_year_baseline',full)]:df.to_sql(name,con,if_exists='replace',index=False)
    con.close()
    # Monthly SKU-store aggregates: all dashboard filters use these additive facts.
    daily['month']=daily.date.str[:7]
    fields=['demand','sales','lost','waste','orders','inventory_value','cogs','writeoff','lost_margin']
    monthly=daily.groupby(['policy','month','store','sku'])[fields].sum().reset_index()
    monthly['days']=monthly.month.map({'2025-10':31,'2025-11':30,'2025-12':31})
    full['annual_value']=full.sales*full.sku.map(products.set_index('sku').unit_cost)
    annual=full.groupby('sku')[['sales','annual_value']].sum().reset_index()
    supplier=orders.groupby(['policy','store','sku']).agg(order_count=('quantity','size'),mean_lead=('actual_lead','mean')).reset_index()
    payload=dict(disclosure=DISCLOSURE,summary=summary,products=products.to_dict('records'),recommendations=recs.to_dict('records'),monthly=monthly.round(6).to_dict('records'),annual=annual.round(2).to_dict('records'),forecast=fm.reset_index().to_dict('records'),supplier=supplier.to_dict('records'))
    (ROOT/'docs/data.js').write_text('window.INVENTORY_DATA='+json.dumps(payload,separators=(',',':'))+';')
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    # Meaningful invariants and equivalent starting state.
    assert (daily.opening+daily.receipts-daily.waste-daily.sales==daily.closing).all()
    assert (daily[['closing','sales','lost','waste']]>=0).all().all()
    assert (daily.sales<=daily.demand).all() and (daily.sales<=daily.opening+daily.receipts-daily.waste).all()
    starts=daily[daily.date=='2025-10-01'].pivot(index=['store','sku'],columns='policy',values='opening');assert starts.baseline.equals(starts.proposed)
    for p,g in monthly.groupby('policy'):
        assert int(g.sales.sum())==summary[p]['sales']
        assert abs(g.inventory_value.sum()/92-summary[p]['average_inventory'])<.01
    fingerprint=hashlib.sha256((ROOT/'data/demand.csv').read_bytes()).hexdigest()
    (out/'validation.json').write_text(json.dumps(dict(status='passed',rows=len(daily),demand_sha256=fingerprint,checks=['mass balance','nonnegative inventory','sales constraints','equivalent initial stock and empty pipeline','dashboard reconciliation']),indent=2))
    print(json.dumps(dict(summary=summary,forecast=fm.to_dict('index')),indent=2))
if __name__=='__main__':main()
