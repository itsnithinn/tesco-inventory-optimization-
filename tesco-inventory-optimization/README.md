# Tesco-Inspired Inventory Optimisation

A simulated UK grocery retail case study using Python, SQL and an interactive dashboard.

> Independent portfolio project using synthetic data. Not affiliated with or endorsed by Tesco. Results are simulated and do not represent Tesco’s actual performance.

**Author:** Nithin Narayanan. **Status:** Built and validated locally; GitHub publication pending account access. URLs below are deployment targets, not verified live links.

- Dashboard target: https://itsnithinn.github.io/tesco-inventory-optimization/
- Case study target: https://itsnithinn.github.io/tesco-inventory-optimization/case-study.html
- Repository target: https://github.com/itsnithinn/tesco-inventory-optimization

## Business problem
Balance grocery availability, working capital, expiry and replenishment workload. This independent experiment uses 60 products, three fictional UK stores and 65,700 daily demand observations for 2025. It is not a record of improvements delivered during employment.

## Reproduce
Python 3.11 or later. From the repository root:

```sh
python -m venv .venv
# Activate your virtual environment, then:
python -m pip install -r requirements.txt
python src/analyze.py
python tests/validate.py
```

Open `docs/index.html` directly in a browser. It uses a local JavaScript data export, so no API/server is required. The optional notebook uses the same modules. Jupyter is not required for the pipeline.

## Holdout results: October–December 2025

| Metric | Weekly baseline | Daily proposed |
|---|---:|---:|
| Unit fill rate | 83.38% | 99.57% |
| Lost units | 33,908 | 886 |
| Average inventory at cost | £32,012.47 | £27,231.40 |
| Waste units | 58,445 | 7,987 |
| SKU-store orders | 2,520 | 12,027 |
| Relevant simulated cost | £220,269.44 | £50,618.60 |

Average inventory falls 14.9%. These large gains reflect an intentionally weak weekly baseline, particularly for short-life bakery. Order frequency rises sharply. Do not present this as a real-world Tesco savings claim.

## Methods
Training is January–September. The holdout is never used to fit ABC classes, demand means/variance, lead-time statistics or safety stock. Both policies share identical demand, date-indexed supplier conditions, starting stock and empty pipelines. Supplier delay outcomes are applied only after an order is placed. Policies use training expected lead, not realised lead.

Daily proposed policy: reorder at mean × (lead + 1 review day) + safety stock; order to mean × (lead + 2 days) + safety stock; cap perishable targets at mean × shelf life. Safety stock uses independent demand and lead variability and A/B/C z-scores 1.96/1.645/1.282. These are heuristic protection factors, not promised unit fill rates.

Fixed-origin 92-day forecast WAPE: weekday mean 32.77%, last-training-week seasonal naive 41.95%. No holdout refitting. Replenishment uses the constant training mean; forecasts are evaluated separately.

See [assumptions and dictionary](ASSUMPTIONS.md), [SQL](sql/analysis.sql), [interview notes](INTERVIEW.md), and [publishing instructions](PUBLISHING.md).

## Repository map
- `src/generate.py`: seeded product, demand and supplier-condition generation.
- `src/simulate.py`: inventory ledger, FEFO, batch receipts and orders.
- `src/analyze.py`: training, holdout, descriptive annual baseline, database and dashboard export.
- `data/`: synthetic products and demand.
- `results/`: ledgers, recommendations, forecasts, summary, validation and SQLite.
- `docs/`: static dashboard and case study (GitHub Pages deployment output).
- `tests/validate.py`: determinism, causality, stock continuity, expiry and SQL checks.
- `notebooks/walkthrough.ipynb`: analysis walkthrough reusing modules.

## Dashboard
Filters: store, category, product and holdout month. Cards recompute ratios from aggregate numerators/denominators. Inventory divides inventory-value-days by distinct selected calendar days, not observation count. Annual Pareto is explicitly independent of Q4 filters. Recommendations are training-only. Monthly SKU-store aggregation reduces the dashboard export to 1,080 rows.

Browser screenshots are not included: a supported browser QA capability was unavailable during this build. Desktop/mobile rendering remains a publishing check. JavaScript syntax, calculations and static assets were checked locally.

## Limitations
Synthetic known demand, weak baseline, no substitution, no MOQ/pack-size/capacity constraints, no transport consolidation, no terminal stock valuation. Shelf life starts at receipt. No promotion features in forecasting. Fresh-stock target cap ignores batch ageing within inventory position. Use real-data pilots and a stronger daily-review comparator before operational decisions.

## Licence
Original code and generated synthetic data are under MIT. Tesco's name is used only to describe inspiration; no trademarks or endorsement rights are granted.
