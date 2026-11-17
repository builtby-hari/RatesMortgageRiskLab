# Changelog

## 1.0.0 (2026-11-17)

First tagged release.

- Four models in one repo, each with its own README and tests:
  - `market-dashboard`: mortgage rate spread over the 10-year Treasury, from FRED, with history and percentiles.
  - `delinquency-drivers`: what moves the mortgage delinquency rate, as a regression with diagnostics and scenarios.
  - `mbs-cashflow`: cash flows, prepayments, OAS, duration and convexity for a sample mortgage bond.
  - `rate-shock`: what a bond portfolio or a bank's balance sheet loses when rates rise, fall, steepen or flatten.
- One command (`run_tests.py`) runs every test suite.
- Tests run on GitHub Actions for every push and pull request.
- Contributing guide and issue templates.
