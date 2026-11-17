# Contributing

Thanks for taking a look. Bug reports, fixes and ideas are all welcome.

## Quick start

Python 3.9 or newer.

```bash
git clone https://github.com/builtby-hari/RatesMortgageRiskLab.git
cd RatesMortgageRiskLab
python3 run_tests.py
```

Tests run on every push and pull request, on Python 3.9 and 3.13. They need to pass before a pull request is merged.

## Ground rules

- The models use only the standard library. matplotlib is only for the optional PNG charts, so please keep it that way.
- Real numbers come from FRED or a cited source. If a number is an assumption, say so next to it.
- Add or update a test for any change to a calculation.
- Keep the README honest. If a change moves a number shown there, rerun it and update the number.

## Reporting a bug

Open an issue with the bug template. The most useful thing you can include is the exact command and a small input that shows the problem.

## Questions

Not sure if it's a bug? Ask in [Discussions](https://github.com/builtby-hari/RatesMortgageRiskLab/discussions).
