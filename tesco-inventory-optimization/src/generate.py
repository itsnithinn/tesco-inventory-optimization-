"""Seeded synthetic demand and exogenous supplier conditions; no Tesco data."""
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
SEED=20261012

def generate():
    rng=np.random.default_rng(SEED)
    groups={'Dairy':(7,['Milk','Yoghurt','Cheese','Cream','Butter']), 'Bakery':(3,['Bread','Rolls','Bagels','Croissants','Muffins']), 'Produce':(5,['Apples','Bananas','Tomatoes','Salad','Carrots']), 'Beverages':(180,['Water','Juice','Tea','Coffee','Cola']), 'Frozen':(180,['Peas','Pizza','Fish','Chips','Ice cream']), 'Household':(730,['Detergent','Tissues','Soap','Bin bags','Sponges'])}
    products=[]
    for cat,(life,names) in groups.items():
        for j in range(10):
            cost=round(float(rng.uniform(.6,6)),2)
            products.append(dict(sku=f'SKU{len(products)+1:03}',name=names[j%5]+(' Standard' if j<5 else ' Family'),category=cat,shelf_life=life,unit_cost=cost,price=round(cost*1.38,2),base_demand=round(float(rng.uniform(3,22)),2),nominal_lead=int(rng.integers(1,3) if life<10 else rng.integers(2,6))))
    products=pd.DataFrame(products); rows=[]
    for si,store in enumerate(['London Central','Manchester North','Birmingham West']):
        for p in products.to_dict('records'):
            for t,date in enumerate(pd.date_range('2025-01-01','2025-12-31')):
                promo=((t//7+int(p['sku'][3:]))%13==0)
                factor=[.90,.90,.95,1,1.18,1.30,.95][date.weekday()]
                mean=p['base_demand']*[1.15,.90,1][si]*factor*(1+.10*np.sin(2*np.pi*t/365))*(1.4 if promo else 1)
                # Gamma-Poisson mixture creates overdispersion.
                demand=int(rng.poisson(rng.gamma(16,mean/16)))
                delay=int(rng.choice([0,1,2],p=[.88,.09,.03]))
                rows.append((date.date().isoformat(),store,p['sku'],demand,int(promo),p['nominal_lead']+delay))
    demand=pd.DataFrame(rows,columns=['date','store','sku','demand','promotion','supplier_lead'])
    (ROOT/'data').mkdir(exist_ok=True)
    products.to_csv(ROOT/'data/products.csv',index=False);demand.to_csv(ROOT/'data/demand.csv',index=False)
    return products,demand
if __name__=='__main__': generate()
