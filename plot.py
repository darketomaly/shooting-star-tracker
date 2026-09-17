# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib"]
# ///

"""
Read the file in data/, make one picture, save it to out/.

    uv run plot.py

Three parts, and you will replace all three: rows() reads the file the way *your*
file needs reading, the loop in main() picks the numbers out of it, and the plot at
the bottom is the transformation you chose. Print before you plot.
"""

import csv
import random
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.image import imread
from matplotlib.transforms import Affine2D
from fetch import FILE

PICTURE = "plot.png"                           # what goes into out/, and into the README

HERE = Path(__file__).parent
DATA = HERE / "data" / FILE
OUT = HERE / "out"
SPRITE = HERE / "sprites" / "cloud.png"

def rows(path):
    """Read the hourly visibility scores from the generated CSV."""
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))

def lerp(start, end, amount):
    return start + (end - start) * amount

def main():
    table = rows(DATA)
    first = table[0]
    score = float(first["visibility_score"])
    cloud_opacity = lerp(1, 0, max(0, min(score, 100)) / 100)

    fig, ax = plt.subplots(figsize=(10, 8), facecolor="black")
    ax.set_facecolor("black")
    cloud = imread(SPRITE)
    variation = random.Random(42)
    for x in range(8):
        for y in range(6):
            jitter_x = variation.uniform(-0.15, 0.15)
            jitter_y = variation.uniform(-0.15, 0.15)
            left, bottom = x + jitter_x, y + jitter_y
            center_x, center_y = left + 0.5, bottom + 0.5
            rotation = variation.uniform(-12, 12)
            transform = (Affine2D()
                         .rotate_deg_around(center_x, center_y, rotation)
                         + ax.transData)
            ax.imshow(cloud, extent=(left, left + 1, bottom, bottom + 1),
                      transform=transform, alpha=cloud_opacity)
    ax.text(0.05, 5.95, f"Visibility score at {first['time']} -> {score:.0f}%",
            ha="left", va="top", fontsize=14, color="white")
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 6)
    ax.axis("off")
    fig.tight_layout()

    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / PICTURE, dpi=150)
    print(f"saved out/{PICTURE}")
    plt.show()

if __name__ == "__main__":
    main()