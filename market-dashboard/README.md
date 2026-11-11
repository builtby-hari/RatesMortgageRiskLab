# Mortgage Market Dashboard

A weekly desk check: how far is the 30-year mortgage rate above the 10-year Treasury yield, and is that gap wide or tight compared with history? It pulls six public Federal Reserve (FRED) series and writes an HTML report and a short market note.

Latest reading in the committed data (15 Oct 2026): the gap is **222 bp**, wider than 85% of weeks since 1971. (A basis point, bp, is 0.01%, so 222 bp is 2.22 percentage points.)

![Mortgage-Treasury spread against its historical band](docs/figures/spread-band.png)

## The result (15 Oct 2026, real FRED data)

- Mortgage rate **7.40%**, 10-year Treasury weekly average **5.19%**, so the spread is **222 bp**.
- That is **0.9 standard deviations** above the 1971 to 2026 average, the **85th percentile** of 2,899 weeks.
- Against the last five years it is **below** average (z = −0.46), so the spread is not stretched on a recent view.
- The 10Y−2Y curve is **+33 bp**. It has been inverted on 16% of trading days since 1976.

The same spread year by year. Each box is the middle half of that year's weeks and the whiskers are the low and high:

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/spread-by-year-dark.svg">
  <img src="docs/spread-by-year.svg" alt="Box plot of the mortgage-Treasury spread for each year from 1971 to 2026. Most years sit between 130 and 200 bp. The early 1980s, 2008 and 2022 to 2023 stand out as wide." width="760">
</picture>

The two rates behind the spread, over the last five years:

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/rates-dark.svg">
  <img src="docs/rates.svg" alt="Line chart of the 30-year mortgage rate and the 10-year Treasury weekly average from late 2021 to October 2026. Both rise from about 3% and 1.5% to 7.4% and 5.2%." width="760">
</picture>

And the shape of the Treasury curve. Long rates are normally above short rates. When that flips, the curve is inverted:

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/curve-dark.svg">
  <img src="docs/curve.svg" alt="Line chart of the 10-year minus 2-year and 10-year minus 3-month Treasury spreads since 1976, with inverted periods shaded below zero. The 10-year minus 2-year spread was last inverted in September 2024." width="760">
</picture>

## Run it

```bash
python3 cli.py --offline          # report from the committed data snapshot, no network needed
python3 cli.py                    # refresh from FRED first
python3 -m unittest discover      # tests
```

Output goes to `out/report.html` and `out/aligned.csv`. `python3 scripts/reproduce.py` re-prints the worked example and rebuilds the charts (needs matplotlib).

`python3 charts.py` redraws the SVG charts with no installs.

## How it works

```mermaid
flowchart LR
    A["FRED CSV files<br/>6 public series"] --> B["Checked local cache<br/>(or the committed snapshot)"]
    B --> C["Line up each weekly<br/>mortgage rate with that<br/>week's Treasury average"]
    C --> D["Compare with history<br/>z-score, percentile,<br/>52-week change"]
    D --> E["HTML report,<br/>market note, CSV"]
```

The mortgage survey comes out once a week and Treasury yields come out daily, so each weekly mortgage rate is matched with the average Treasury yield for the same week. The z-score is how many standard deviations today's spread sits from its long-run average. A committed snapshot lets it all run offline.

## What I fixed along the way

- The market note once claimed a primary-secondary mortgage spread the tool can't measure. It now only states what the data supports.
- FRED sometimes serves an HTML maintenance page instead of CSV. The loader now says so clearly instead of failing on a missing header.
- If one leg of the curve is stale, the report warns instead of quietly mixing dates.

Full concepts, formulas and methods: [docs/reference.md](docs/reference.md).
