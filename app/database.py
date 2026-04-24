from sqlalchemy import create_engine, text

_engine = None


def init_db(db_url: str) -> None:
    global _engine
    _engine = create_engine(db_url)
    with _engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS forecast (
                id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                lat TEXT NOT NULL,
                lng TEXT NOT NULL,
                forecast_at TIMESTAMP NOT NULL,
                temp REAL NOT NULL,
                created_at TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'utc')
            )
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_forecast_lookup
            ON forecast (lat, lng, forecast_at)
        """))
        conn.commit()


def insert_forecast(periods: list[dict]) -> None:
    with _engine.connect() as conn:
        conn.execute(
            text("""
                INSERT INTO forecast (lat, lng, forecast_at, temp)
                VALUES (:lat, :lng, :forecast_at, :temp)
            """),
            periods,
        )
        conn.commit()


# TODO: doesn't deal with timezones (i.e. get high and low for 8pm PT)
def query_min_max(lat: str, lng: str, date_str: str, hour: int):
    with _engine.connect() as conn:
        row = conn.execute(
            text("""
                SELECT MAX(temp), MIN(temp)
                FROM forecast
                WHERE lat = :lat AND lng = :lng
                  AND TO_CHAR(forecast_at, 'YYYY-MM-DD') = :date_str
                  AND EXTRACT(HOUR FROM forecast_at) = :hour
            """),
            {"lat": lat, "lng": lng, "date_str": date_str, "hour": hour},
        ).fetchone()
    return row
