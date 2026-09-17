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
from datetime import datetime, timedelta, timezone
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.image import imread
from matplotlib.patches import Circle
from matplotlib.transforms import Affine2D
from fetch import FILE

PICTURE = "plot.png"                           # what goes into out/, and into the README

HERE = Path(__file__).parent
DATA = HERE / "data" / FILE
OUT = HERE / "out"
SPRITE = HERE / "sprites" / "cloud.png"
TIMEZONE = "HKT"

def rows(path):
    """Read hourly cloud coverage from the generated CSV."""
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))

def format_visibility(meters):
    if meters >= 1000:
        return f"{meters / 1000:.2f}".rstrip("0").rstrip(".") + " km"
    return f"{meters:.0f} m"

def main():
    table = rows(DATA)
    hkt = timezone(timedelta(hours=8))
    sunrise = datetime.fromisoformat(table[0]["sunrise"]).replace(tzinfo=hkt)
    sunset = datetime.fromisoformat(table[0]["sunset"]).replace(tzinfo=hkt)
    first = next(
        row for row in table
        if sunrise <= datetime.fromisoformat(row["time"]).replace(tzinfo=hkt) < sunset
    )
    cloud_coverage = float(first["cloud_coverage"])
    coverage_fraction = max(0, min(cloud_coverage, 100)) / 100
    hkt_time = datetime.fromisoformat(first["time"]).replace(tzinfo=hkt)
    readable_time = hkt_time.strftime("%I:%M %p").lstrip("0")
    visibility = format_visibility(float(first["visibility"]))
    sunrise = datetime.fromisoformat(first["sunrise"]).replace(tzinfo=hkt)
    sunset = datetime.fromisoformat(first["sunset"]).replace(tzinfo=hkt)

    fig, ax = plt.subplots(figsize=(10, 8), facecolor="black")
    ax.set_facecolor("black")
    if sunrise <= hkt_time < sunset:
        ax.add_patch(Circle((7, 5), 0.45, color="#ffd34e"))
    else:
        ax.add_patch(Circle((7, 5), 0.45, color="#d9d9d9"))
        ax.add_patch(Circle((7.18, 5.15), 0.45, color="black"))
    cloud = imread(SPRITE)
    variation = random.Random(42)
    positions = [(x, y) for x in range(8) for y in range(6)]
    variation.shuffle(positions)
    cloud_count = round(len(positions) * coverage_fraction)
    for x, y in positions[:cloud_count]:
            jitter_x = variation.uniform(-0.15, 0.15)
            jitter_y = variation.uniform(-0.15, 0.15)
            left, bottom = x + jitter_x, y + jitter_y
            center_x, center_y = left + 0.5, bottom + 0.5
            rotation = variation.uniform(-12, 12)
            transform = (Affine2D()
                         .rotate_deg_around(center_x, center_y, rotation)
                         + ax.transData)
            ax.imshow(cloud, extent=(left, left + 1, bottom, bottom + 1),
                      transform=transform)
    ax.text(0.05, 5.95,
            f"Time ({TIMEZONE}): {readable_time}\n"
            f"Cloud coverage: {cloud_coverage:.0f}%\n"
            f"Visibility: {visibility}",
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