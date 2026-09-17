# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///

"""
Fetch the numbers and save hourly visibility scores to data/, replacing any
existing file.

    uv run fetch.py

Change URL and FILE. The default is the Hong Kong Observatory's daily mean
temperature for 2026, so the template runs before you have touched it and you
can see what a file looks like when it arrives. It is an example, not your
phenomenon: handing it in unchanged is handing in nothing.
"""

import csv
from pathlib import Path

# Fetch hourly cloud cover data from Open-Meteo for your coordinates
# Hong Kong coords (22.3193, 114.1694)
lat, lon = 22.3193, 114.1694
URL = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=cloud_cover,visibility&forecast_days=1"

FILE = "hk-hourly-coud-cover.csv"                         
HERE = Path(__file__).parent
DATA = HERE / "data"

def fetch(url, path):
    """Fetch the file and replace any existing copy in data/."""
    import requests

    DATA.mkdir(exist_ok=True)
    print(f"asking {url}")
    reply = requests.get(url, timeout=60, headers={"User-Agent": "SD5913 PolyU student"})
    reply.raise_for_status()
    response = reply.json()

    # Calculate a "Stargazing Visibility Score" (0% = Terrible, 100% = Perfect)
    hours = response["hourly"]["time"][:24]
    cloud_cover = response["hourly"]["cloud_cover"][:24]
    visibility = response["hourly"]["visibility"][:24]
    visibility_score = [100 - cloud for cloud in cloud_cover]

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["time", "cloud_cover", "visibility", "visibility_score"])
        writer.writerows(zip(hours, cloud_cover, visibility, visibility_score))

    print(f"saved data/{path.name} ({path.stat().st_size // 1024} KB). Now: git add data")
    return path

if __name__ == "__main__":
    fetch(URL, DATA / FILE)