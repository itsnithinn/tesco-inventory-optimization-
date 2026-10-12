# Interview and CV notes

## Two accurate CV bullets
- Built a reproducible Python and SQLite inventory simulation covering 60 SKUs, three fictional UK stores and 65,700 daily synthetic demand observations, with FEFO fulfilment, supplier variability and expiry tracking.
- Developed an interactive dashboard comparing replenishment policies on a 92-day holdout; achieved 14.9% lower average inventory and 99.6% unit fill rate in the simulation, while documenting increased ordering workload and baseline limitations.

## 60-second explanation
I built an independent grocery inventory project inspired by my Tesco operations experience. All the data is synthetic. The business question was how to improve availability without carrying too much stock or increasing waste. I generated a year of demand for 60 products across three stores, used nine months to estimate demand and supplier variability, and evaluated the remaining three months. I compared weekly ordering with a daily policy using safety stock and shelf-life limits. The daily policy improved simulated fill rate from 83.4% to 99.6% and reduced average inventory by 14.9%, but required many more orders. The important lesson is that fresh products need different replenishment rules. The gains are large because the baseline is deliberately basic; I would validate against real data and realistic delivery costs before recommending implementation.

## Five likely questions
**1. How did you avoid data leakage?** All policy parameters are fitted before October 1. Both policies see the same holdout demand and exogenous supplier conditions. A test changes future demand and verifies earlier decisions remain unchanged.

**2. Why not use sales as demand?** Stockouts censor sales. Since I generated the data, I know unmet demand separately. Real-world deployment would need an estimation approach for lost sales.

**3. What is safety stock?** A buffer for variation in demand and delivery lead time. I combine their variances, include one review day, and use ABC-based z-scores. The normal approximation is a heuristic, so I measure achieved service separately.

**4. What is the biggest weakness?** The weekly baseline is poor for three-day bakery items and overstates the opportunity relative to a mature retailer. Costs also assume separate £2 SKU-store orders, ignoring delivery consolidation.

**5. What would you do next?** Test a stronger daily-review baseline, use actual batch ageing and supplier pack sizes, run rolling temporal validation and sensitivity analysis, and pilot a small SKU group with operations staff.
