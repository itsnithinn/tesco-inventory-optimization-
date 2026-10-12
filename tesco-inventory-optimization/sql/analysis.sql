-- Holdout availability: ratio of sums, never average of SKU percentages.
SELECT policy, SUM(sales)*1.0/SUM(demand) AS unit_fill_rate,
       SUM(lost) AS lost_units, SUM(inventory_value)/COUNT(DISTINCT date) AS average_inventory_gbp
FROM daily_holdout GROUP BY policy;
-- Category inventory and waste exposure.
SELECT d.policy,p.category,SUM(d.inventory_value)/COUNT(DISTINCT d.date) AS average_inventory_gbp,
       SUM(d.writeoff) AS writeoff_gbp
FROM daily_holdout d JOIN products p USING(sku) GROUP BY d.policy,p.category;
-- Supplier realised lead performance, including orders arriving beyond the holdout.
SELECT policy,store,AVG(actual_lead) AS actual_lead_days,
       AVG(CASE WHEN actual_lead>expected_lead THEN 1.0 ELSE 0 END) AS share_above_training_mean
FROM orders GROUP BY policy,store;
-- Annual descriptive consumption value, distinct from training-only policy ABC.
SELECT p.sku,p.name,SUM(d.sales*p.unit_cost) AS annual_consumption_value
FROM full_year_baseline d JOIN products p USING(sku)
GROUP BY p.sku,p.name ORDER BY annual_consumption_value DESC;
