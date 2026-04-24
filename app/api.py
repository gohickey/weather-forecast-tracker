from fastapi import FastAPI, HTTPException, Query

import database

app = FastAPI()


@app.get("/api/v1/forecasts")
def get_forecast(
    lat: str = Query(..., description="Latitude"),
    lng: str = Query(..., description="Longitude"),
    date: str = Query(..., description="Date (YYYY-MM-DD UTC)"),
    hour: int = Query(..., ge=0, le=23, description="Hour of day (0-23 UTC)"),
):
    row = database.query_min_max(lat, lng, date, hour)
    if row is None or row[0] is None:
        # Could also return 200 with empty or null temps
        raise HTTPException(
            status_code=404,
            detail=f"No forecast data found for ({lat}, {lng}) on {date} at hour {hour}",
        )
    return {
        "lat": lat,
        "lng": lng,
        "date": date,
        "hour": hour,
        "temp_high": row[0],
        "temp_low": row[1],
    }


@app.get("/health")
def health():
    return {"status": "ok"}
