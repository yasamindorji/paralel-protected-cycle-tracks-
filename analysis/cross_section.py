"""Draw scaled cross-sections (building to building) from data/cross_sections.csv."""
from pathlib import Path
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
COLOURS = {"walk": "#d9d6cc", "bike": "#d9534f", "buffer": "#f2f1ec", "parking": "#9fa6b2",
           "traffic": "#5f6670", "median": "#7fb069", "platform": "#c9b27c"}
TITLES = {"before": "Existing section", "after": "Proposed section (typical)", "after_bus_stop": "Proposed section at a bus stop"}


def draw(section, rows, ax):
    x = 0.0
    sec = sorted((r for r in rows if r["section"] == section), key=lambda r: int(r["order"]))
    for r in sec:
        w = float(r["width_m"])
        ax.add_patch(FancyBboxPatch((x + 0.04, 0), w - 0.08, 1, boxstyle="square,pad=0",
                                    facecolor=COLOURS[r["mode"]], edgecolor="white", linewidth=1.5))
        dark = r["mode"] in ("traffic", "bike", "median", "parking")
        label = r["element"].split(" (")[0]
        if w < 0.5:  # too narrow for a label inside: put it under the bar
            ax.text(x + w / 2, -0.06, f"{label} {w:.1f} m", ha="center", va="top", fontsize=6, color="#3d3d3a")
        else:
            ax.text(x + w / 2, 0.5, f"{label}\n{w:.1f} m", ha="center", va="center", rotation=90 if w < 3.2 else 0,
                    fontsize=6.5, color="white" if dark else "#2b2b2b")
        x += w
    ax.set_xlim(-0.3, 40.3)
    ax.set_ylim(-0.3, 1.15)
    ax.axis("off")
    ax.set_title(f"{TITLES[section]}  ·  total {x:.1f} m", loc="left", fontsize=10, color="#1f1f1e")
    ax.annotate("North", (0, -0.22), fontsize=7, color="#6b6a63")
    ax.annotate("South", (40, -0.22), fontsize=7, color="#6b6a63", ha="right")


def main():
    rows = list(csv.DictReader(open(ROOT / "data" / "cross_sections.csv", encoding="utf-8")))
    for name in TITLES:
        fig, ax = plt.subplots(figsize=(11, 2.3), dpi=200)
        draw(name, rows, ax)
        fig.tight_layout()
        fig.savefig(ROOT / "figures" / f"cross_section_{name}.png")
        plt.close(fig)


if __name__ == "__main__":
    main()
