# Weather Forecast Tracker

Tracks weather forecasts for a particular location.

## How It Works

At a configurable interval, it fetches the hourly forecast for the next 72 hours for a particular location, (given by the longitude
and latitude values in the config file). A REST API provides the highest and lowest recorded forecast for a particular location and date/time.
Note that a dates/times are UTC.

## Configuration

The `conig.json` file contains the configuration. Here is an example:

```json
{
  "location": {
    "lat": "39.7456",
    "lng": "-97.0892"
  },
  "db_url": "postgresql://user:password@localhost:5432/forecasts",
  "interval_minutes": 60
}
```

| Field              | Description                         |
| ------------------ | ----------------------------------- |
| `location.lat`     | Latitude of the location to track   |
| `location.lng`     | Longitude of the location to track  |
| `db_url`           | DB URL (postgres)                   |
| `interval_minutes` | How often to retrieve the forecasts |

## Building and Running

### Docker Compose

```bash
# Build and run it
docker compose up --build -d

# Stop
docker compose down
```

## API

### `GET /api/v1/forecasts`

Returns the highest and lowest temperature ever recorded in the database for the given location, date, and hour (UTC).

**Query parameters:**

| Parameter | Type    | Description            |
| --------- | ------- | ---------------------- |
| `lat`     | string  | Latitude               |
| `lng`     | string  | Longitude              |
| `date`    | string  | UTC date in ISO format |
| `hour`    | integer | UTC hour of day (0–23) |

**Example request:**

```
GET http://localhost:8000/api/v1/forecasts?lat=39.7456&lng=-97.0892&date=2026-04-23&hour=15
```

**Example response:**

```json
{
  "lat": "39.7456",
  "lng": "-97.0892",
  "date": "2026-04-23",
  "hour": 15,
  "temp_high": 72,
  "temp_low": 68
}
```

Returns 404 Not Found if no data has been collected yet for the specified parameters.

### `GET /health`

Returns `{"status": "ok"}`.

## Assumptions

- US-only coverage. The weather.gov API only provides data for US locations.

- Long/Lat matches are exact. The query API matches the stored `lat` and `lng` values exactly - they won't work if they are just "nearby".

- Everything is UTC. So the forecast min and max values probably won't be correct for your timezone.

- The db is postgres.

- Needs tests!
