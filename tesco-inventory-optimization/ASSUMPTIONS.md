# Model assumptions and data dictionary

## Experimental design
Seed 20261012. Dates: 2025-01-01 to 2025-12-31. Each of three fictional stores has 60 SKUs. Demand follows a Gamma–Poisson mixture with weekday, mild annual seasonality, store multipliers and recurring synthetic promotions. Actual supplier lead = nominal lead + 0/1/2 days with probabilities .88/.09/.03. These conditions are generated independently of the policies and keyed by order date, store and SKU. Different order dates mean different realised deliveries; the same-date conditions are shared.

Training-only policy ABC uses known demand × cost, a demand-based consumption proxy. Cumulative share before each SKU determines A (<80%), B (<95%), C (remaining), so the threshold-crossing SKU stays in the preceding class. Annual descriptive ranking instead uses fulfilled baseline sales × cost. Do not conflate the two.

Initial holdout stock is ceil(training mean × min(4, shelf life)), fresh on day one. Both pipelines are empty. The separate full-year baseline uses product base demand as a synthetic planning prior, not future realised demand. It is a descriptive series, not the holdout comparator. The Q4 reset and annual baseline discontinuity are intentional.

## Event order and batches
Opening stock → arrivals → expiry → FEFO sales → closing stock → order decision. Expiry occurs when day >= receipt day + shelf life. Fresh initial stock expires after shelf_life days. Orders are placed at end of day and can arrive no earlier than the next day. Supplier actual lead is revealed to the simulator only after the policy's quantity decision. No purchases are cancelled at the end of the horizon; orders due in January remain in orders.csv, outside the inventory ledger.

## Costs
GBP, no VAT. Unit selling price = cost × 1.38 rounded to pennies. Annual holding rate 20%, applied to daily closing stock cost / 365. Each SKU-store order costs £2, not a consolidated supplier shipment. Expiry is written off at unit cost. Lost contribution margin = lost units × (price − cost). Relevant cost adds these four terms; purchase cost and revenue are excluded. No terminal salvage or pipeline valuation. This is a policy cost proxy, not total company cost or profit.

## Files and fields
| File | Grain | Fields / meaning |
|---|---|---|
| products.csv | SKU | sku/name/category; shelf_life days at receipt; unit_cost and price GBP; base_demand generation parameter; nominal_lead days |
| demand.csv | date/store/SKU | demand units, promotion 0/1, supplier_lead realised delay for an order placed on that date |
| daily_holdout.csv | policy/date/store/SKU | opening, receipts, waste, sales, closing in units; lost = demand − sales; orders 0/1; order_qty units; inventory_value GBP at daily close; cogs GBP; writeoff GBP; lost_margin GBP |
| full_year_baseline.csv | date/store/SKU | same ledger fields, separate annual descriptive series |
| orders.csv | holdout policy/order/store/SKU | order_date, delivery_date, quantity, actual_lead, expected_lead training mean, batch_id |
| batches.csv | received holdout order | receipt_date, expiry_date, quantity at receipt, batch_id; initial stock is implicit in starting-state rule |
| recommendations.csv | store/SKU | mean/std daily demand, lead mean days, safety_stock/rop/target units, abc, cv=std/mean |
| forecast_errors.csv | model/store/SKU | summed absolute error, demand units, observation count |
| forecast_metrics.csv | model | WAPE=sum absolute error / sum actual; MAE=sum absolute error / count |
| summary.json | holdout policy | policy-level metrics; annualised turnover = holdout COGS / average stock × 365/92; inventory days = average stock / daily COGS |
| inventory.sqlite | tables | demand, products, daily_holdout, orders, batches, recommendations, full_year_baseline |
| docs/data.js | export | monthly additive facts, product metadata, training recommendations, annual descriptive totals, forecasts and supplier summaries |

Inventory reconciliation: closing = opening + receipts − expiry − sales. Unit fill rate is fulfilled units / demand, not fraction of days without stockout. Forecast WAPE is ratio of sums. Average stock is sum of daily closing inventory values divided by distinct days, summing stores and SKUs first.

## Interpretation
The baseline's seven-day cycle exceeds the shortest shelf lives; large expiry and service improvements should be expected. The comparison illustrates a mechanism, not a calibrated business case. A stronger baseline and sensitivity to delivery consolidation, order cost, service targets and lost-demand estimates are needed before deployment.
