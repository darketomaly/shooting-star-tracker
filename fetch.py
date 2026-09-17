# /// script
# requires-python = ">=3.10"
# dependencies = ["requests", "astral"]
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
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

from astral import Observer
from astral.moon import elevation

# Fetch hourly cloud cover data from Open-Meteo for your coordinates
# Hong Kong coords (22.3193, 114.1694)
lat, lon = 22.3193, 114.1694
URL = (
    f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
    "&hourly=cloud_cover,visibility&daily=sunrise,sunset"
    "&forecast_days=1&timezone=Asia%2FHong_Kong"
)

FILE = "hk-hourly-coud-cover.csv"                         
MAX_CLEAR_VISIBILITY_METERS = 10_000
SYNODIC_MONTH_DAYS = 29.530588853
REFERENCE_NEW_MOON = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
HERE = Path(__file__).parent
DATA = HERE / "data"

def moon_phase(time_text):
    hkt = datetime.fromisoformat(time_text).replace(
        tzinfo=timezone(timedelta(hours=8))
    )
    days_since_new_moon = (hkt.astimezone(timezone.utc) - REFERENCE_NEW_MOON).total_seconds() / 86400
    return (days_since_new_moon / SYNODIC_MONTH_DAYS) % 1

def moon_phase_name(phase):
    names = (
        "New Moon", "Waxing crescent", "First quarter", "Waxing gibbous",
        "Full Moon", "Waning gibbous", "Last quarter", "Waning crescent",
    )
    return names[int((phase + 1 / 16) * 8) % 8]

def fetch(url, path):
    """Fetch the file and replace any existing copy in data/."""
    import requests

    DATA.mkdir(exist_ok=True)
    print(f"asking {url}")
    reply = requests.get(url, timeout=60, headers={"User-Agent": "SD5913 PolyU student"})
    reply.raise_for_status()
    response = reply.json()

    cloud_coverage = response["hourly"]["cloud_cover"][:24]
    hours = response["hourly"]["time"][:24]
    visibility = response["hourly"]["visibility"][:24]
    sunrise = response["daily"]["sunrise"][0]
    sunset = response["daily"]["sunset"][0]
    moon_phases = [moon_phase(hour) for hour in hours]
    moon_illuminations = [
        (1 - math.cos(2 * math.pi * phase)) * 50
        for phase in moon_phases
    ]
    observer = Observer(latitude=lat, longitude=lon)
    moon_altitudes = [
        elevation(
            observer,
            datetime.fromisoformat(hour).replace(
                tzinfo=timezone(timedelta(hours=8))
            ),
        )
        for hour in hours
    ]
    moon_names = [moon_phase_name(phase) for phase in moon_phases]
    stargaze_score = [
        min(visibility_meters / MAX_CLEAR_VISIBILITY_METERS * 100, 100)
        * (1 - cloud / 100)
        * (
            1
            - moon_illumination / 100
            * max(0, math.sin(math.radians(moon_altitude)))
        )
        if not (
            datetime.fromisoformat(hour) >= datetime.fromisoformat(sunrise)
            and datetime.fromisoformat(hour) < datetime.fromisoformat(sunset)
        )
        else 0
        for hour, cloud, visibility_meters, moon_illumination, moon_altitude in zip(
            hours, cloud_coverage, visibility, moon_illuminations, moon_altitudes
        )
    ]

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "time", "cloud_coverage", "visibility", "stargaze_score",
            "sunrise", "sunset", "moon_phase", "moon_illumination",
            "moon_altitude", "moon_name",
        ])
        writer.writerows(
            zip(hours, cloud_coverage, visibility, stargaze_score,
                [sunrise] * len(hours), [sunset] * len(hours), moon_phases,
                moon_illuminations, moon_altitudes, moon_names)
        )

    print(f"saved data/{path.name} ({path.stat().st_size // 1024} KB). Now: git add data")
    return path

if __name__ == "__main__":
    fetch(URL, DATA / FILE)