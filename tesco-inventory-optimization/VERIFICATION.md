# Verification record

Passed locally:
- 65,700 demand observations; 33,120 holdout inventory rows.
- Seeded demand regenerated with matching SHA-256.
- Daily stock balance, nonnegative stock, constrained sales and stock continuity.
- Equal starting inventory and empty pipelines.
- Future-demand perturbation leaves earlier ledger and ordering decisions unchanged.
- Expiry fixture.
- SQLite query execution and exported dashboard totals reconcile.
- JavaScript syntax and DOM-harness execution across store/category/month filters and empty selections.
- Case-study/dashboard relative assets and local links exist.
- Portfolio patch whitespace validation.

Not verified: visual desktop/mobile rendering, live GitHub Pages URLs, remote deployment. Supported browser QA and authenticated GitHub access were unavailable.

Run `python src/analyze.py`, `python tests/validate.py`, and `node tests/dashboard.cjs` to repeat the checks. Node is only needed for the dashboard test, not website hosting.
