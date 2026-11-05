"""Before/after indicators for the Av. del Paral·lel cycle-track proposal.

Reads data/cross_sections.csv (Streetmix widths, building to building) and writes
results/indicators.md plus figures/space_allocation.png.

Usage:  python analysis/indicators.py
"""
from pathlib import Path
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
CROW_ONE_WAY_MIN = 2.0   # m, one-way cycle track, up to 150 bikes/h (CROW 2016)
CROW_TWO_WAY_MIN = 2.5   # m, two-way cycle path, up to 50 bikes/h (CROW 2016)
MODES = ["walk", "bike", "buffer", "traffic", "parking", "median"]
LABELS = {"walk": "Walking", "bike": "Cycling", "buffer": "Buffer", "traffic": "Traffic lanes",
          "parking": "Parking / loading", "median": "Median / divider"}


def load():
    rows = list(csv.DictReader(open(ROOT / "data" / "cross_sections.csv", encoding="utf-8")))
    for r in rows:
        r["width_m"] = float(r["width_m"])
    return rows


def summarise(rows, section):
    sec = [r for r in rows if r["section"] == section]
    total = sum(r["width_m"] for r in sec)
    by_mode = {m: sum(r["width_m"] for r in sec if r["mode"] == m) for m in MODES}
    bike = [r for r in sec if r["mode"] == "bike"]
    two_way = len(bike) == 1
    per_dir = bike[0]["width_m"] / 2 if two_way else min(r["width_m"] for r in bike)
    crow_ok = (bike[0]["width_m"] >= CROW_TWO_WAY_MIN) if two_way else (per_dir >= CROW_ONE_WAY_MIN)
    return total, by_mode, per_dir, two_way, crow_ok


def main():
    rows = load()
    res = {s: summarise(rows, s) for s in ("before", "after")}  # typical sections
    for s, (total, *_rest) in res.items():
        assert abs(total - 40.0) < 0.05, f"{s} section does not add up to 40 m ({total})"

    lines = ["# Indicators – Av. del Paral·lel (typical section, 40 m)", "",
             "| Indicator | Before | After |", "|---|---|---|"]
    b, a = res["before"], res["after"]
    lines.append(f"| Cycling width per direction | {b[2]:.2f} m ({'two-way' if b[3] else 'one-way'}) | {a[2]:.2f} m ({'two-way' if a[3] else 'one-way'}) |")
    lines.append(f"| Meets CROW minimum width | {'yes' if b[4] else 'no'} | {'yes' if a[4] else 'no'} |")
    for m in MODES:
        lines.append(f"| Share of street: {LABELS[m]} | {100*b[1][m]/b[0]:.1f}% ({b[1][m]:.1f} m) | {100*a[1][m]/a[0]:.1f}% ({a[1][m]:.1f} m) |")
    change = 100 * (a[2] - b[2]) / b[2]
    lines += ["", f"Cycling width per direction changes by {change:+.0f}%."]
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    (out / "indicators.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))

    # Figure: share of the 40 m street per mode, before vs after
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=200)
    y = range(len(MODES))
    h = 0.36
    bv = [100 * b[1][m] / b[0] for m in MODES]
    av = [100 * a[1][m] / a[0] for m in MODES]
    ax.barh([i - h / 2 - 0.01 for i in y], bv, height=h, color="#2a78d6", label="Before")
    ax.barh([i + h / 2 + 0.01 for i in y], av, height=h, color="#eb6834", label="After")
    for i, (vb, va) in enumerate(zip(bv, av)):
        ax.text(vb + 0.6, i - h / 2, f"{vb:.1f}%", va="center", fontsize=8, color="#3d3d3a")
        ax.text(va + 0.6, i + h / 2, f"{va:.1f}%", va="center", fontsize=8, color="#3d3d3a")
    ax.set_yticks(list(y), [LABELS[m] for m in MODES], fontsize=9, color="#3d3d3a")
    ax.invert_yaxis()
    ax.set_xlabel("Share of the 40 m street (%)", fontsize=9, color="#3d3d3a")
    ax.set_title("Space allocation on Av. del Paral·lel, before and after", fontsize=11, loc="left", color="#1f1f1e")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.spines["left"].set_color("#c3c2b7"); ax.spines["bottom"].set_color("#c3c2b7")
    ax.tick_params(colors="#6b6a63", labelsize=8)
    ax.grid(axis="x", color="#e8e7e1", linewidth=0.6); ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    fig.tight_layout()
    fig.savefig(ROOT / "figures" / "space_allocation.png")


if __name__ == "__main__":
    main()
