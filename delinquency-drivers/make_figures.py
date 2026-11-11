"""Worked example and figures for the README. Needs matplotlib (see requirements-extra.txt).

Writes PNGs to docs/figures/ and prints the worked example (model M4, one-quarter unemployment shock).
All results are illustrative: they come from FRED data in data/ and a one-quarter stylized shock.

Usage: python3 make_figures.py [--out docs/figures]
"""

import argparse
import math
import os

from analysis import MODELS, PANDEMIC, build_panel, run_model
from scenario import Z95, compute, model_by_id

FIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "figures")
NAVY, TEAL, GREY, TEXT = "#1f3a5f", "#14b8a6", "#cbd5e1", "#334155"
ASSUMPTION = ("Illustrative. FRED data in data/ (quarterly, 1991Q2-2026Q2). OLS with Newey-West SE (4 lags). "
              "Associations, not causal.")


def worked_example(rows, model_id="M4", d_unemp=1.0, d_rate=0.0, roll=0.20, lgd=0.25, portfolio=10000.0):
    """One quarter: unemployment rises d_unemp pp, mortgage rate changes d_rate pp, both vs the prior quarter."""
    title, xcols, excl, window = model_by_id(model_id)
    res = run_model(rows, xcols, excl, window)
    last = rows[-1]
    b, V, s2 = res["coef"], res["cov"], res["sigma2"]
    x = [1.0, d_unemp, d_rate]
    pred = sum(bi * xi for bi, xi in zip(b, x))
    xvx = sum(x[i] * V[i][j] * x[j] for i in range(3) for j in range(3))
    se = math.sqrt(xvx + s2)
    level0 = last["delinquency"]
    level1 = level0 + pred
    loss_pct = max(level1, 0.0) * roll * lgd
    return {"title": title, "n": res["n"], "coef": dict(zip(res["names"], b)), "se_coef": dict(zip(res["names"], res["se"])),
            "x": x, "pred": pred, "coef_var": xvx, "sigma2": s2, "se": se, "lo": level1 - Z95 * se,
            "hi": level1 + Z95 * se, "level0": level0, "level1": level1, "q0": last["quarter"],
            "loss_pct": loss_pct, "loss_mm": loss_pct / 100 * portfolio, "roll": roll, "lgd": lgd,
            "portfolio": portfolio, "unemp0": last_unemp(), "rate0": last_rate()}


def last_unemp():
    from analysis import DATA_DIR, load, quarterly_mean
    return quarterly_mean(load(os.path.join(DATA_DIR, "UNRATE.csv")))["2026Q2"]


def last_rate():
    from analysis import DATA_DIR, load, quarterly_mean
    return quarterly_mean(load(os.path.join(DATA_DIR, "MORTGAGE30US.csv")))["2026Q2"]


def print_example(ex):
    print(f"Worked example (illustrative): {ex['title']}, n={ex['n']}")
    print(f"  Start: {ex['q0']} delinquency {ex['level0']:.2f}%; unemployment {ex['unemp0']:.2f}%; mortgage rate {ex['rate0']:.2f}%")
    print("  Shock: unemployment +1.00 pp in the next quarter, mortgage rate unchanged")
    print(f"  Predicted change = const + b_unemp x 1.00 + b_rate x 0.00 = {ex['coef']['const']:.4f} + "
          f"{ex['coef']['d_unemp']:.4f} x 1.00 + {ex['coef']['d_rate']:.4f} x 0.00 = {ex['pred']:.4f} pp")
    print(f"  Level after one quarter = {ex['level0']:.2f} + {ex['pred']:.4f} = {ex['level1']:.2f}%")
    print(f"  Variance = x'Vx + sigma^2 = {ex['coef_var']:.6f} + {ex['sigma2']:.6f} = {ex['coef_var'] + ex['sigma2']:.6f}; "
          f"SE = {ex['se']:.3f} pp")
    print(f"  95% band = {ex['level1']:.2f} +/- 1.96 x {ex['se']:.3f} = {ex['lo']:.2f} to {ex['hi']:.2f}%")
    print(f"  Teaching loss, one quarter: {ex['level1']:.2f}% x {ex['roll']:.0%} roll x {ex['lgd']:.0%} LGD = "
          f"{ex['loss_pct']:.3f}% of ${ex['portfolio']:,.0f}mm = ${ex['loss_mm']:.1f}mm")


def make_all(out_dir: str):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(out_dir, exist_ok=True)
    rows = build_panel()
    paths = []
    plt.rcParams.update({"font.size": 10, "axes.edgecolor": "#94a3b8", "axes.labelcolor": TEXT,
                         "xtick.color": TEXT, "ytick.color": TEXT})

    def finish(fig, ax, title, name):
        ax.set_title(title, loc="left", fontsize=12, color=TEXT, fontweight="bold")
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.grid(axis="y", color=GREY, linewidth=0.8)
        ax.set_axisbelow(True)
        fig.text(0.01, 0.01, ASSUMPTION, fontsize=7.5, color="#64748b")
        fig.tight_layout(rect=(0, 0.04, 1, 1))
        path = os.path.join(out_dir, name)
        fig.savefig(path, dpi=150)
        plt.close(fig)
        paths.append(path)

    # Figure 1: the outcome
    fig, ax = plt.subplots(figsize=(9, 4.6))
    x = list(range(len(rows)))
    ax.plot(x, [r["delinquency"] for r in rows], color=NAVY, linewidth=1.8)
    ticks = [i for i, r in enumerate(rows) if r["quarter"].endswith("Q1") and int(r["quarter"][:4]) % 5 == 0]
    ax.set_xticks(ticks)
    ax.set_xticklabels([rows[i]["quarter"][:4] for i in ticks])
    ax.set_xlabel("Quarter (year of Q1 shown)")
    ax.set_ylabel("Delinquency Rate (% of loans, seasonally adjusted)")
    finish(fig, ax, "Single-Family Mortgage Delinquency Rate, 1991Q2 to 2026Q2", "fig1_delinquency_level.png")

    # Figure 2: the drivers' change, with pre-2020 fit
    fig, ax = plt.subplots(figsize=(8, 5.6))
    pandemic = [PANDEMIC[0] <= r["quarter"] <= PANDEMIC[1] for r in rows]
    ax.scatter([r["d_unemp"] for r, p in zip(rows, pandemic) if not p],
               [r["d_delinq"] for r, p in zip(rows, pandemic) if not p], s=18, color=NAVY, alpha=0.75,
               label="Quarters outside 2020")
    ax.scatter([r["d_unemp"] for r, p in zip(rows, pandemic) if p],
               [r["d_delinq"] for r, p in zip(rows, pandemic) if p], s=26, color=TEAL, label="2020 quarters")
    fit = run_model(rows, ["d_unemp"], window=("1991Q1", "2019Q4"))
    a_, b_ = fit["coef"]
    lo, hi = -1.0, 2.0
    ax.plot([lo, hi], [a_ + b_ * lo, a_ + b_ * hi], color=TEXT, linewidth=2,
            label=f"Univariate OLS fit, 1991-2019 (slope {b_:.2f})")
    ax.axhline(0, color="#64748b", linestyle="--", linewidth=0.8)
    ax.axvline(0, color="#64748b", linestyle="--", linewidth=0.8)
    ax.set_xlabel("Change in unemployment rate vs prior quarter (pp)")
    ax.set_ylabel("Change in delinquency rate vs prior quarter (pp)")
    ax.legend(frameon=False, fontsize=9)
    finish(fig, ax, "Quarterly Change in Delinquency vs Unemployment Change", "fig2_change_scatter.png")

    # Figure 3: coefficient across samples
    fig, ax = plt.subplots(figsize=(8, 5))
    for i, (title, xcols, excl, window) in enumerate(MODELS):
        res = run_model(rows, xcols, excl, window)
        j = res["names"].index("d_unemp")
        ax.errorbar(i, res["coef"][j], yerr=2 * res["se"][j], fmt="o", color=NAVY, ecolor=NAVY,
                    capsize=5, markersize=7, linewidth=2)
        ax.annotate(f"n={res['n']}", (i, res["coef"][j]), textcoords="offset points", xytext=(10, 6), fontsize=8)
    ax.axhline(0, color="#64748b", linestyle="--", linewidth=1)
    ax.set_xticks(range(len(MODELS)))
    ax.set_xticklabels([m[0].split()[0] for m in MODELS])
    ax.set_xlabel("Model (sample and regressors in the README table)")
    ax.set_ylabel("Coefficient on unemployment change (pp per pp)")
    finish(fig, ax, "Unemployment-Change Coefficient by Model, Plus or Minus 2 Newey-West SE",
           "fig3_coefficients_by_model.png")

    # Figure 4: scenario path with band (illustrative paths)
    _, _, start, results = compute(os.path.join(os.path.dirname(os.path.abspath(__file__)), "scenarios",
                                                "illustrative.csv"), "M4")
    fig, ax = plt.subplots(figsize=(9, 4.8))
    hist = rows[-20:]
    hx = list(range(len(hist)))
    ax.plot(hx, [r["delinquency"] for r in hist], color=NAVY, linewidth=1.8, label="Observed")
    offset = len(hist)
    colors = {"baseline": TEAL, "adverse": "#f59e0b", "severely_adverse": "#b91c1c"}
    for name, r in results.items():
        px = [offset - 1] + [offset + i for i in range(len(r["proj"]))]
        ys = [start["delinquency"]] + [p["level"] for p in r["proj"]]
        lo = [start["delinquency"]] + [p["lo"] for p in r["proj"]]
        hi = [start["delinquency"]] + [p["hi"] for p in r["proj"]]
        ax.plot(px, ys, color=colors[name], linewidth=2, label=f"{name.replace('_', ' ').title()} (M4 path)")
        ax.fill_between(px, lo, hi, color=colors[name], alpha=0.12, linewidth=0)
    ax.axvline(offset - 1, color="#64748b", linestyle=":", linewidth=1)
    labels = [r["quarter"] for r in hist]
    proj_labels = [p["quarter"] for p in results["baseline"]["proj"]]
    allq = labels + proj_labels
    ticks = list(range(0, len(allq), 4))
    ax.set_xticks(ticks)
    ax.set_xticklabels([allq[i] for i in ticks], rotation=0, fontsize=8)
    ax.set_xlabel("Quarter (observed to 2026Q2, then illustrative projection)")
    ax.set_ylabel("Delinquency Rate (%)")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    finish(fig, ax, "Illustrative Scenario Paths, Model M4, With 95% Bands", "fig4_scenario_paths.png")
    return paths


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=FIG_DIR)
    args = parser.parse_args(argv)
    print_example(worked_example(build_panel()))
    try:
        import matplotlib  # noqa: F401
    except ImportError:
        print("\nmatplotlib is not installed, so no figures were written.")
        print("Install it with: pip install -r requirements-extra.txt")
        return
    print()
    for path in make_all(args.out):
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
