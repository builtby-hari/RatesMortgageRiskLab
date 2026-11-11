"""Matplotlib figures for the README, written as PNGs to docs/figures/.

The core package is standard-library only. This script is an extra: it plots the
same data as mbs/charts.py. Every figure carries an "Illustrative" source note.

    pip install -r requirements-extra.txt
    python3 plots_mpl.py
"""

import os
import sys

from mbs import charts

NAVY = "#1f3a5f"
TEAL = "#14b8a6"
LIGHT_TEAL = "#5eead4"
SLATE = "#94a3b8"
GRID = "#cbd5e1"
TEXT = "#334155"

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(HERE, "docs", "figures")

FILES = ("wal_duration_vs_rate.png", "convexity_bars.png", "cashflow_profile_by_psa.png",
         "cashflow_components_100psa.png", "price_heatmap.png")

BASE = ("Illustrative: $100mm pool, 6.5% WAC, 6.0% net coupon, 360 months. "
        "Source: mbs/charts.py data helpers.")


def _style(ax, title, xlabel, ylabel):
    ax.set_title(title, fontsize=12, fontweight="bold", color=TEXT)
    ax.set_xlabel(xlabel, color=TEXT)
    ax.set_ylabel(ylabel, color=TEXT)
    ax.tick_params(colors=TEXT)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def _save(fig, path, note):
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.text(0.01, 0.015, note, fontsize=7, color=TEXT, ha="left", va="bottom", wrap=True)
    fig.savefig(path)


def main(out=DEFAULT_OUT):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib is not installed. It is an optional extra: "
              "pip install -r requirements-extra.txt", file=sys.stderr)
        return 1

    os.makedirs(out, exist_ok=True)

    # WAL and effective duration vs mortgage rate
    rates, wals, durs = charts.wal_duration_data()
    fig, ax = plt.subplots(figsize=(7.6, 4.6), dpi=150)
    ax.plot(rates, wals, color=NAVY, lw=2.2, label="WAL")
    ax.plot(rates, durs, color=TEAL, lw=2.2, label="Effective duration")
    _style(ax, "WAL and Effective Duration vs Mortgage Rate",
           "Current mortgage rate (%)", "Years")
    ax.legend(frameon=False, loc="upper right")
    _save(fig, os.path.join(out, FILES[0]),
          BASE + " Prepayments follow the illustrative refi S-curve; yield 5.5%.")
    plt.close(fig)

    # Effective vs static convexity (grouped bars)
    rates, eff, stat = charts.convexity_data()
    fig, ax = plt.subplots(figsize=(7.6, 4.6), dpi=150)
    xs = range(len(rates))
    ax.bar([x - 0.19 for x in xs], eff, width=0.36, color=NAVY, label="Effective (re-projected)")
    ax.bar([x + 0.19 for x in xs], stat, width=0.36, color=TEAL, label="Static (cash flows fixed)")
    ax.set_xticks(list(xs))
    ax.set_xticklabels([f"{r:.2f}" for r in rates])
    ax.axhline(0, color=TEXT, lw=0.8)
    _style(ax, "Convexity by Mortgage Rate: Effective vs Static",
           "Current mortgage rate (%)", "Convexity (years squared)")
    ax.legend(frameon=False, loc="upper left")
    _save(fig, os.path.join(out, FILES[1]),
          BASE + " +/-25bp shock; yield 5.5%. Effective is negative near the money.")
    plt.close(fig)

    # Monthly cash flow profile by PSA speed
    colors = {50: SLATE, 100: NAVY, 300: TEAL, 500: LIGHT_TEAL}
    fig, ax = plt.subplots(figsize=(7.6, 4.6), dpi=150)
    for psa, ys in charts.profile_data().items():
        ax.plot(range(1, len(ys) + 1), ys, color=colors[psa], lw=2.0, label=f"{psa} PSA")
    _style(ax, "Monthly Cash Flow to Investor by PSA Speed", "Month", "Cash flow ($ millions)")
    ax.legend(frameon=False, loc="upper right")
    _save(fig, os.path.join(out, FILES[2]), BASE + " Constant PSA speed, no rate response.")
    plt.close(fig)

    # Annual interest / scheduled principal / prepayment stacked bars at 100 PSA
    years, interest, sched, prepay = charts.components_data(100)
    fig, ax = plt.subplots(figsize=(7.6, 4.6), dpi=150)
    ax.bar(years, interest, color=NAVY, label="Interest")
    ax.bar(years, sched, bottom=interest, color=SLATE, label="Scheduled principal")
    base = [a + b for a, b in zip(interest, sched)]
    ax.bar(years, prepay, bottom=base, color=TEAL, label="Prepayments")
    _style(ax, "Annual Cash Flow Split at 100 PSA", "Year", "$ millions per year")
    ax.legend(frameon=False, loc="upper right")
    _save(fig, os.path.join(out, FILES[3]), BASE + " 100 PSA. Scheduled plus prepaid principal sums to the $100mm balance.")
    plt.close(fig)

    # Price heatmap: discount yield x PSA speed
    grid = charts.price_grid()
    fig, ax = plt.subplots(figsize=(7.6, 4.6), dpi=150)
    im = ax.imshow(grid[::-1], cmap="GnBu", aspect="auto")
    mid = (min(map(min, grid)) + max(map(max, grid))) / 2
    for r, row in enumerate(grid[::-1]):
        for c, v in enumerate(row):
            ax.text(c, r, f"{v:.2f}", ha="center", va="center", fontsize=8,
                    color="white" if v > mid else TEXT)
    ax.set_xticks(range(len(charts.PRICE_PSAS)))
    ax.set_xticklabels(charts.PRICE_PSAS)
    ax.set_yticks(range(len(charts.PRICE_YIELDS)))
    ax.set_yticklabels([f"{y:.1f}%" for y in charts.PRICE_YIELDS[::-1]])
    ax.set_xlabel("PSA speed (%)", color=TEXT)
    ax.set_ylabel("Discount yield (%)", color=TEXT)
    ax.set_title("Price per 100 by Discount Yield and PSA Speed", fontsize=12,
                 fontweight="bold", color=TEXT)
    fig.colorbar(im, ax=ax, label="Price per 100")
    _save(fig, os.path.join(out, FILES[4]), BASE + " Constant PSA speed, no rate response.")
    plt.close(fig)

    for name in FILES:
        print(os.path.join(out, name))
    return 0


if __name__ == "__main__":
    sys.exit(main())
