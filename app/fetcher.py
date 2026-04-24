import logging
from datetime import datetime, timedelta, timezone

import requests
from dateutil import parser as dateutil_parser

import database

logger = logging.getLogger(__name__)

WEATHER_API_BASE = "https://api.weather.gov"
HEADERS = {"User-Agent": "forecast-tracker/1.0 (jim@jim.com)"}

# TODO: cache grid info per (lat, lng) to avoid redundant /points calls on every fetch


def fetch_and_store(lat: str, lng: str) -> None:
    try:
        url = f"{WEATHER_API_BASE}/points/{lat},{lng}"
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        props = resp.json()["properties"]
        grid_id, grid_x, grid_y = props["gridId"], props["gridX"], props["gridY"]

        url = f"{WEATHER_API_BASE}/gridpoints/{grid_id}/{grid_x},{grid_y}/forecast/hourly"
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()

        end_time = datetime.now(timezone.utc) + timedelta(hours=72)

        periods = []
        for p in resp.json()["properties"]["periods"]:
            start_dt = dateutil_parser.parse(p["startTime"]).astimezone(timezone.utc)
            if start_dt >= end_time:
                break
            periods.append({"lat": lat, "lng": lng, "forecast_at": start_dt.strftime("%Y-%m-%dT%H:%M:%S"), "temp": p["temperature"]})

        database.insert_forecasts(periods)
        logger.info("Got %d periods for (%s, %s)", len(periods), lat, lng)

    except Exception:
        logger.exception("Forecast fetch failed")
