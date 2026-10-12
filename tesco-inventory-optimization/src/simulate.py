"""Daily FEFO inventory simulation. Policy cannot see future demand or actual lead."""
import math
import pandas as pd

def simulate(products,demand,params,policy,start=None):
    records=[]; orders=[]; batches=[]
    for (store,sku),g in demand.groupby(['store','sku'],sort=True):
        p=products.set_index('sku').loc[sku]; q=params[(store,sku)]
        mu=q['mean']; life=int(p.shelf_life)
        stock=[[life,int(math.ceil(mu*min(4,life))),f'{store}-{sku}-initial']]
        pipeline=[]
        for t,r in enumerate(g.itertuples(index=False)):
            opening=sum(b[1] for b in stock); received=0; waste=0
            for due,qty,bid in list(pipeline):
                if due==t:
                    stock.append([t+life,qty,bid]);received+=qty;pipeline.remove((due,qty,bid))
                    batches.append(dict(policy=policy,store=store,sku=sku,batch_id=bid,receipt_date=r.date,expiry_date=(pd.Timestamp(r.date)+pd.Timedelta(days=life)).date().isoformat(),quantity=qty))
            for b in stock:
                if b[0]<=t: waste+=b[1];b[1]=0
            available=sum(b[1] for b in stock); sold=min(available,r.demand); remaining=sold
            for b in sorted(stock):
                take=min(b[1],remaining); b[1]-=take;remaining-=take
            stock=[b for b in stock if b[1]]; closing=sum(b[1] for b in stock)
            position=closing+sum(x[1] for x in pipeline)
            qty=0
            if policy=='baseline':
                # Weekly review; ignores perishability and supplier variability.
                if t%7==0: qty=max(0,math.ceil(mu*(q['lead']+7))-position)
            else:
                if position<=q['rop']:
                    target=min(q['target'],mu*life) if life<10 else q['target']
                    qty=max(0,math.ceil(target)-position)
            if qty:
                bid=f'{policy}-{store}-{sku}-{t}'; actual=int(r.supplier_lead)
                pipeline.append((t+actual,qty,bid))
                orders.append(dict(policy=policy,store=store,sku=sku,order_date=r.date,delivery_date=(pd.Timestamp(r.date)+pd.Timedelta(days=actual)).date().isoformat(),quantity=qty,actual_lead=actual,expected_lead=q['lead'],batch_id=bid))
            records.append(dict(policy=policy,date=r.date,store=store,sku=sku,demand=r.demand,sales=sold,lost=r.demand-sold,opening=opening,receipts=received,waste=waste,closing=closing,orders=int(qty>0),order_qty=qty,inventory_value=closing*p.unit_cost,cogs=sold*p.unit_cost,writeoff=waste*p.unit_cost,lost_margin=(r.demand-sold)*(p.price-p.unit_cost)))
    return pd.DataFrame(records),pd.DataFrame(orders),pd.DataFrame(batches)
