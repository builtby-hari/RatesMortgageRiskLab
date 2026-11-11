#!/usr/bin/env python3
"""Reproduce the README worked example and regenerate docs/figures/*.png.

Reads only the committed FRED snapshot in data/snapshot/ (no network, no cache).
Every number is an illustrative snapshot result, not live market data.
Figures need matplotlib: pip install -r requirements-extra.txt
"""

import os
import sys
from datetime import timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from mortgage_dashboard import (
    align,
    curve_spread,
    curve_stats,
    load_all,
    rate_volatility,
    spread_stats,
    weekly_last,
)

SNAPSHOT = os.path.join(ROOT, "data", "snapshot")
FIG_DIR = os.path.join(ROOT, "docs", "figures")
NAVY, TEAL, TEXT = "#1f3a5f", "#14b8a6", "#334155"
SOURCE = "Source: FRED snapshot pulled 2026-10-22 (committed in data/snapshot/). Illustrative, not live. "
NOTE_SPREAD = SOURCE + "Spread = PMMS 30Y rate minus 10Y Treasury weekly average."
NOTE_RATES = SOURCE + "Rates = Freddie Mac PMMS 30Y and 10Y weekly average, percent."
NOTE_CURVE = SOURCE + "Curve = 10Y minus 2Y, last daily print each week."


def worked_example(data):
    """Print the worked example for the latest PMMS week, step by step."""
    rows = align(data["MORTGAGE30US"], data["MORTGAGE15US"], data["DGS10"])
    s = spread_stats(rows)
    d = s["date"]
    prints = [(dt, v) for dt, v in data["DGS10"] if d - timedelta(days=6) <= dt <= d]
    t_mean = sum(v for _, v in prints) / len(prints)
    seen = {dt for dt, _ in prints}
    gaps = [dt for dt in (d - timedelta(days=k) for k in range(7)) if dt.weekday() < 5 and dt not in seen]
    gap_note = "".join(f"  (no print on {dt:%b %d}: missing from the FRED series)" for dt in gaps)
    lines = [
        f"Inputs: PMMS 30Y rate for {d:%a %b %d, %Y} = {s['mortgage30']:.2f}%",
        "Treasury prints in the 7 calendar days ending on that date:",
        "  " + ", ".join(f"{dt:%a %b %d} {v:.2f}%" for dt, v in prints) + gap_note,
        f"Step 1  T = mean of {len(prints)} prints = {t_mean:.4f}%",
        f"Step 2  S = {s['mortgage30']:.2f} - {t_mean:.4f} = {s['spread'] * 100:.1f} bp",
        (f"Step 3  z = (S - mean) / sd = ({s['spread'] * 100:.1f} - {s['spread_mean'] * 100:.1f}) / "
         f"{s['spread_stdev'] * 100:.1f} = {s['spread_z']:+.2f}  "
         f"(over {s['hist_n']:,} weeks since {s['hist_start']:%Y})"),
        f"Step 4  percentile (mid-rank) = {s['spread_pctile']:.1f}",
        f"Step 5  5-year z = {s['spread_z_5y']:+.2f}, 5-year percentile = {s['spread_pctile_5y']:.1f}",
        (f"Step 6  30Y change: {s['mortgage30_wk_chg'] * 100:+.0f} bp on the week, "
         f"{s['mortgage30_52w_chg'] * 100:+.0f} bp over 52 weeks"),
    ]
    curve = curve_spread(data["DGS10"], data["DGS2"])
    cv = curve_stats(curve)
    lines.append(f"Step 7  10Y-2Y = {cv['value'] * 100:+.0f} bp on {cv['date']:%b %d, %Y}; "
                 f"inverted on {cv['inverted_pct']:.0f}% of {cv['hist_n']:,} daily readings")
    vol = rate_volatility(data["DGS10"])
    lines.append(f"Step 8  10Y volatility = {vol:.1f} bp std dev of daily changes over 63 days")
    return lines, rows, curve


def make_figures(rows, stats, curve, out_dir):
    """Write three PNG charts. Returns the paths written."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False,
                         "axes.grid": True, "grid.color": "#cbd5e1", "grid.linewidth": 0.6})
    os.makedirs(out_dir, exist_ok=True)
    written = []

    def save(fig, name, note):
        fig.text(0.01, 0.01, note, fontsize=7.5, color=TEXT, ha="left", va="bottom")
        fig.tight_layout(rect=(0, 0.05, 1, 1))
        path = os.path.join(out_dir, name)
        fig.savefig(path, dpi=150)
        plt.close(fig)
        written.append(path)

    last = rows[-1]["date"]
    recent = [r for r in rows if r["date"] >= last - timedelta(days=365 * 5)]
    fig, ax = plt.subplots(figsize=(9, 4.6))
    dates = [r["date"] for r in recent]
    ax.plot(dates, [r["mortgage30"] for r in recent], color=NAVY, lw=1.6, label="30Y mortgage (PMMS, weekly)")
    ax.plot(dates, [r["dgs10_avg"] for r in recent], color=TEAL, lw=1.6, label="10Y Treasury, weekly average")
    ax.set_title("30Y mortgage rate vs 10Y Treasury, last 5 years (illustrative snapshot)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Percent (%)")
    ax.legend(frameon=False, loc="upper left")
    save(fig, "rates-5y.png", NOTE_RATES)

    dates = [r["date"] for r in rows]
    spread = [r["spread"] * 100 for r in rows]
    mean, sd = stats["spread_mean"] * 100, stats["spread_stdev"] * 100
    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.plot(dates, spread, color=NAVY, lw=1.0, label="Mortgage-Treasury spread (weekly)")
    ax.axhspan(mean - sd, mean + sd, color=TEAL, alpha=0.18, lw=0, label="Mean +/- 1 std dev")
    ax.axhline(mean, color=TEXT, ls="--", lw=1, label=f"Full-history mean = {mean:,.0f} bp")
    ax.scatter([last], [spread[-1]], color=NAVY, zorder=3, label=f"Latest = {spread[-1]:,.0f} bp")
    ax.set_title("Mortgage-Treasury spread since 1971, with mean and one std dev band (illustrative)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Basis points (bp)")
    ax.legend(frameon=False, loc="lower right", fontsize=8)
    save(fig, "spread-band.png", NOTE_SPREAD)

    fig, ax = plt.subplots(figsize=(9, 4.6))
    cd = weekly_last(curve)
    cdates = [d for d, _ in cd]
    cvals = [v * 100 for _, v in cd]
    ax.plot(cdates, cvals, color=NAVY, lw=1.0, label="10Y minus 2Y, weekly")
    ax.fill_between(cdates, cvals, 0, where=[v < 0 for v in cvals], color=TEXT, alpha=0.2, lw=0,
                    interpolate=True, label="Inverted (below zero)")
    ax.axhline(0, color=TEXT, lw=1)
    ax.set_title("10Y minus 2Y Treasury spread since 1976, inversions shaded (illustrative)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Basis points (bp)")
    ax.legend(frameon=False, loc="upper left", fontsize=8)
    save(fig, "curve-10y-2y.png", NOTE_CURVE)
    return written


def main(argv=None):
    data = load_all(SNAPSHOT, offline=True)
    lines, rows, curve = worked_example(data)
    print("\n".join(lines))
    stats = spread_stats(rows)
    if "--no-figures" in (argv or sys.argv[1:]):
        return 0
    try:
        paths = make_figures(rows, stats, curve, FIG_DIR)
    except ImportError:
        print("matplotlib is not installed; figures skipped. Run: pip install -r requirements-extra.txt")
        return 1
    for p in paths:
        print("wrote " + os.path.relpath(p, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
