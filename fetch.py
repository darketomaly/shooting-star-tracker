# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///

"""
Fetch the numbers and save the raw reply to data/, replacing any existing file.

    uv run fetch.py

Change URL and FILE. The default is the Hong Kong Observatory's daily mean
temperature for 2026, so the template runs before you have touched it and you
can see what a file looks like when it arrives. It is an example, not your
phenomenon: handing it in unchanged is handing in nothing.
"""

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
    path.write_bytes(reply.content)      # the raw reply, byte for byte: what arrived is what gets committed
    print(f"saved data/{path.name} ({path.stat().st_size // 1024} KB). Now: git add data")
    return path

if __name__ == "__main__":
    fetch(URL, DATA / FILE)