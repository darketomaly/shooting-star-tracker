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
from pathlib import Path

import matplotlib.pyplot as plt
from fetch import FILE

PICTURE = "plot.png"                           # what goes into out/, and into the README

HERE = Path(__file__).parent
DATA = HERE / "data" / FILE
OUT = HERE / "out"

def rows(path):
    """Read the hourly visibility scores from the generated CSV."""
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))

def main():
    table = rows(DATA)
    entries = "\n".join(
        f"{row['time']}  {row['visibility_score']}%"
        for row in table
    )

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.text(0.05, 0.95, f"Hourly visibility scores\n\n{entries}",
            ha="left", va="top", fontsize=11, family="monospace")
    ax.axis("off")
    fig.tight_layout()

    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / PICTURE, dpi=150)
    print(f"saved out/{PICTURE}")
    plt.show()

if __name__ == "__main__":
    main()