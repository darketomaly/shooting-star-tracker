# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib", "numpy"]
# ///

"""
Read the file in data/, make one picture, save it to out/.

    uv run plot.py

Three parts, and you will replace all three: rows() reads the file the way *your*
file needs reading, the loop in main() picks the numbers out of it, and the plot at
the bottom is the transformation you chose. Print before you plot.
"""

import csv
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.image import imread
from matplotlib.patches import Circle
from matplotlib.transforms import Affine2D
import numpy as np
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

def lerp_color(start, end, amount):
    return tuple(
        start_channel + (end_channel - start_channel) * amount
        for start_channel, end_channel in zip(start, end)
    )

def moon_image(phase):
    coordinates = np.linspace(-1, 1, 100)
    x, y = np.meshgrid(coordinates, coordinates)
    disk = x**2 + y**2 <= 1
    z = np.sqrt(np.maximum(0, 1 - x**2 - y**2))
    angle = 2 * math.pi * phase
    illuminated = x * math.sin(angle) + z * math.cos(angle) > 0
    image = np.zeros((100, 100, 4))
    image[..., :3] = (0.85, 0.85, 0.85)
    image[..., 3] = disk & illuminated
    return image

def main():
    table = rows(DATA)
    hkt = timezone(timedelta(hours=8))
    sunrise = datetime.fromisoformat(table[0]["sunrise"]).replace(tzinfo=hkt)
    sunset = datetime.fromisoformat(table[0]["sunset"]).replace(tzinfo=hkt)
    first = next(
        (row for row in table
         if datetime.fromisoformat(row["time"]).hour == 1),
        table[0],
    )
    cloud_coverage = float(first["cloud_coverage"])
    coverage_fraction = max(0, min(cloud_coverage, 100)) / 100
    hkt_time = datetime.fromisoformat(first["time"]).replace(tzinfo=hkt)
    readable_time = hkt_time.strftime("%I:%M %p").lstrip("0")
    visibility = format_visibility(float(first["visibility"]))
    visibility_score = float(first["visibility_score"])
    moon_phase = float(first["moon_phase"])
    daylight_progress = (
        (hkt_time - sunrise).total_seconds()
        / (sunset - sunrise).total_seconds()
    )
    daylight_brightness = (
        math.sin(math.pi * daylight_progress)
        if 0 <= daylight_progress <= 1
        else 0
    )
    background = lerp_color((0.01, 0.02, 0.10), (0.35, 0.70, 0.95),
                            daylight_brightness)

    fig, ax = plt.subplots(figsize=(10, 8), facecolor=background)
    ax.set_facecolor(background)
    if sunrise <= hkt_time < sunset:
        ax.add_patch(Circle((7, 5), 0.45, color="#ffd34e"))
    else:
        ax.imshow(moon_image(moon_phase), extent=(6.55, 7.45, 4.55, 5.45))
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
            f"Visibility: {visibility}\n"
            f"Good stargaze probability: {visibility_score:.0f}%",
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