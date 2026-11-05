"""Sensitivity check: is the cycle-track width enough for different cyclist volumes?

CROW (2016) recommended widths by peak-hour cyclist volume (bikes/h):
one-way:  0-150 -> 2.00 m | 150-750 -> 2.50-3.00 m | >750 -> 3.50-4.00 m
two-way:  0-50  -> 2.50 m | 50-150  -> 2.50-3.00 m | 150-350 -> 3.50-4.00 m | >350 -> 4.50 m
No cyclist counts were available, so the check is run over a range of volumes.
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
ONE_WAY = [(150, 2.0), (750, 2.5), (float("inf"), 3.5)]
TWO_WAY = [(50, 2.5), (150, 2.5), (350, 3.5), (float("inf"), 4.5)]


def required(volume, table):
    for limit, width in table:
        if volume <= limit:
            return width


def main():
    vols = list(range(0, 801))
    one = [required(v, ONE_WAY) for v in vols]
    two = [required(v, TWO_WAY) for v in vols]
    fig, ax = plt.subplots(figsize=(8, 4), dpi=200)
    ax.step(vols, one, where="post", color="#eb6834", linewidth=2, label="CROW minimum, one-way track")
    ax.step(vols, two, where="post", color="#2a78d6", linewidth=2, label="CROW minimum, two-way path")
    ax.axhline(2.0, color="#eb6834", linestyle=":", linewidth=1.5)
    ax.axhline(2.2, color="#2a78d6", linestyle=":", linewidth=1.5)
    ax.text(805, 2.0, "proposed track 2.0 m", va="center", fontsize=8, color="#3d3d3a")
    ax.text(805, 2.2, "existing lane 2.2 m", va="center", fontsize=8, color="#3d3d3a")
    ax.set_xlim(0, 800); ax.set_ylim(0, 5)
    ax.set_xlabel("Peak-hour cyclist volume (bikes/h)", fontsize=9, color="#3d3d3a")
    ax.set_ylabel("Width (m)", fontsize=9, color="#3d3d3a")
    ax.set_title("Existing lane fails at any volume; proposed track holds up to 150 bikes/h per direction",
                 loc="left", fontsize=10, color="#1f1f1e")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.grid(color="#e8e7e1", linewidth=0.6); ax.set_axisbelow(True)
    ax.tick_params(colors="#6b6a63", labelsize=8)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(ROOT / "figures" / "crow_width_check.png", bbox_inches="tight")
    print("Existing 2.2 m two-way lane meets CROW at:", [v for v in vols if 2.2 >= required(v, TWO_WAY)][:1] or "no volume")
    print("Proposed 2.0 m one-way track meets CROW up to:", max(v for v in vols if 2.0 >= required(v, ONE_WAY)), "bikes/h")


if __name__ == "__main__":
    main()
