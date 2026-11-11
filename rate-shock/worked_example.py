#!/usr/bin/env python3
"""Worked example for the README: one bond walked through step by step, then three PNG figures.

The bond is UST-10Y-like from data/sample_portfolio.csv. The data is hypothetical, so every number is
illustrative. The walk-through uses only the standard library. The figures need matplotlib:
    pip install -r requirements-extra.txt
    python3 worked_example.py          # prints the walk-through and writes docs/figures/*.png
"""

import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from bondshock import curve
from bondshock.portfolio import load_portfolio, market_value
from bondshock.pricing import (
    cashflow_times,
    convexity,
    macaulay_duration,
    modified_duration,
    price,
)

PORTFOLIO = os.path.join(ROOT, "data", "sample_portfolio.csv")
CURVE = os.path.join(ROOT, "data", "treasury_par_curve.csv")
FIG_DIR = os.path.join(ROOT, "docs", "figures")
EXAMPLE_ID = "UST-10Y-like"
SHOCK_BP = 100
NOTE = ("Illustrative: hypothetical sample data (data/). Clean prices on a coupon date, "
        "yields shift one-for-one, spreads fixed.")
NAVY, TEAL, SLATE, TEXT = "#1f3a5f", "#14b8a6", "#64748b", "#334155"


def walk_through(bonds):
    """Print the worked example and return its numbers."""
    b = next(x for x in bonds if x.id == EXAMPLE_ID)
    dy = SHOCK_BP / 10_000.0
    p0 = price(b)
    mv = market_value(b)
    d_mac, d_mod, cvx = macaulay_duration(b), modified_duration(b), convexity(b)
    full = market_value(b, b.yld + dy) - mv
    dur = -d_mod * mv * dy
    durcvx = mv * (-d_mod * dy + 0.5 * cvx * dy * dy)
    per = 100.0 * b.coupon / b.frequency
    print("Worked example (illustrative: hypothetical bond from data/sample_portfolio.csv)")
    print(f"\nStep 1, inputs: par ${b.par:,.0f}; coupon {b.coupon*100:.3f}%; {b.maturity:g} years, "
          f"{b.frequency} payments a year; yield {b.yld*100:.2f}%")
    print(f"Step 2, cash flow per 100 par: {per:.4f} each half-year, plus 100 at maturity "
          f"({b.periods} payments in total)")
    print("Step 3, discount each cash flow at the yield (period k, factor 1/(1+y/2)^k):")
    for k, t, cf in cashflow_times(b):
        if k in (1, 2, b.periods):
            pv = cf / (1 + b.yld / b.frequency) ** k
            print(f"        k={k:>2}  t={t:>4.1f}y  CF {cf:>8.4f}  PV {pv:>9.4f}")
    print(f"        ... sum of all PVs = price per 100 = {p0:.4f}  (market value ${mv:,.0f})")
    print(f"Step 4, risk measures: Macaulay duration {d_mac:.3f} years; modified duration "
          f"{d_mod:.3f} (= Macaulay / (1 + y/2)); convexity {cvx:.2f} years^2")
    print(f"Step 5, shock the yield by +{SHOCK_BP}bp and compare three estimates of the P&L:")
    print(f"        full repricing     ${full:>12,.0f}   ({100*full/mv:+.2f}% of market value)")
    print(f"        duration only      ${dur:>12,.0f}   (-D x MV x dy)")
    print(f"        duration + convex. ${durcvx:>12,.0f}   (MV x (-D dy + C dy^2 / 2))")
    print(f"        duration error     ${dur - full:>12,.0f}   convexity error ${durcvx - full:>10,.0f}")
    print(f"Interpretation: duration alone misses {100*abs(dur-full)/abs(full):.1f}% of the loss on a "
          f"100bp rise; adding convexity cuts the miss to {100*abs(durcvx-full)/abs(full):.2f}%.")
    return {"p0": p0, "mv": mv, "d_mod": d_mod, "cvx": cvx, "full": full, "dur": dur, "durcvx": durcvx,
            "bond": b}


def make_figures(bonds, out_dir=FIG_DIR):
    """Write three PNGs. Raises ImportError if matplotlib is missing."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(out_dir, exist_ok=True)
    tenors, par = curve.load_par_curve(CURVE)
    written = []

    def style(ax, title, xlabel, ylabel):
        ax.set_title(title, color=TEXT, fontweight="bold")
        ax.set_xlabel(xlabel, color=TEXT)
        ax.set_ylabel(ylabel, color=TEXT)
        ax.tick_params(colors=TEXT)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)

    def save(fig, name):
        fig.text(0.01, 0.01, NOTE, fontsize=7.5, color=SLATE)
        fig.tight_layout(rect=(0, 0.04, 1, 1))
        path = os.path.join(out_dir, name + ".png")
        fig.savefig(path, dpi=150)
        plt.close(fig)
        written.append(path)

    # 1. Price-yield curve with the duration tangent and the duration + convexity estimate
    b = next(x for x in bonds if x.id == EXAMPLE_ID)
    y0, p0, d, c = b.yld, price(b), modified_duration(b), convexity(b)
    ys = [y0 + i * 0.0005 for i in range(-60, 61)]  # +/-300bp, where convexity shows
    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.plot([100 * y for y in ys], [price(b, y) for y in ys], color=NAVY, lw=2.4, label="Full repricing")
    ax.plot([100 * y for y in ys], [p0 * (1 - d * (y - y0)) for y in ys], color=SLATE, lw=1.8, ls="--",
            label="Duration only (tangent)")
    ax.plot([100 * y for y in ys], [p0 * (1 - d * (y - y0) + 0.5 * c * (y - y0) ** 2) for y in ys],
            color=TEAL, lw=1.8, ls=":", label="Duration + convexity")
    for sign in (-1, 1):
        ax.plot(100 * (y0 + sign * SHOCK_BP / 1e4), price(b, y0 + sign * SHOCK_BP / 1e4), "o", color=NAVY)
    ax.plot(100 * y0, p0, "o", color=TEXT)
    ax.annotate(f"Base: yield {100*y0:.2f}%, price {p0:.2f}", (100 * y0, p0), xytext=(-200, -70),
                textcoords="offset points", color=TEXT, fontsize=9,
                arrowprops={"arrowstyle": "-", "color": SLATE})
    style(ax, f"Price-Yield Curve, {EXAMPLE_ID} ({b.maturity:g}y, {100*b.coupon:.3f}% coupon)",
          "Yield (% a year, semiannual)", "Price (per 100 par)")
    ax.legend(frameon=False)
    save(fig, "price_yield_tangent")

    # 2. Curve scenario P&L for the whole sample portfolio, full repricing
    names = list(curve.SCENARIOS)
    pnl = [curve.scenario_pnl(bonds, tenors, par, curve.SCENARIOS[n]) / 1e6 for n in names]
    colors = [TEAL if v >= 0 else NAVY for v in pnl]
    fig, ax = plt.subplots(figsize=(9, 5.2))
    bars = ax.bar(names, pnl, color=colors, width=0.6)
    for bar, v in zip(bars, pnl):
        ax.text(bar.get_x() + bar.get_width() / 2, v, f"{v:+.2f}", ha="center",
                va="bottom" if v >= 0 else "top", color=TEXT, fontsize=9)
    ax.axhline(0, color=TEXT, lw=0.8)
    style(ax, "Curve Scenario P&L, Full Repricing (sample portfolio, $ millions)", "Scenario",
          "P&L ($ millions)")
    ax.tick_params(axis="x", labelrotation=15)
    save(fig, "scenario_pnl_bars")

    # 3. Full-repricing P&L by bond and parallel shock
    shocks = list(range(-300, 301, 50))
    ids = [x.id for x in bonds]
    grid = [[(market_value(x, x.yld + s / 1e4) - market_value(x)) / 1e6 for x in bonds] for s in shocks]
    peak = max(abs(v) for row in grid for v in row)
    fig, ax = plt.subplots(figsize=(9, 5.8))
    im = ax.imshow(grid, cmap="RdBu", vmin=-peak, vmax=peak, aspect="auto")
    ax.set_xticks(range(len(ids)), ids, rotation=30, ha="right", color=TEXT)
    ax.set_yticks(range(len(shocks)), [f"{s:+d}" for s in shocks], color=TEXT)
    for i, row in enumerate(grid):
        for j, v in enumerate(row):
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=7.5,
                    color="white" if abs(v) > 0.6 * peak else TEXT)
    fig.colorbar(im, ax=ax, label="P&L ($ millions)")
    style(ax, "Full-Repricing P&L by Bond and Parallel Shock ($ millions)", "Bond (sample portfolio)",
          "Parallel yield shock (bp)")
    save(fig, "shock_pnl_heatmap")
    return written


def main():
    bonds = load_portfolio(PORTFOLIO)
    walk_through(bonds)
    try:
        files = make_figures(bonds)
    except ImportError:
        print("\nmatplotlib is not installed, so no figures were written. Install the optional extra with: "
              "pip install -r requirements-extra.txt", file=sys.stderr)
        return 1
    print("\nWrote figures:")
    for f in files:
        print("  " + os.path.relpath(f, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
