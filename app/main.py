import json
import logging

import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler

import database
import fetcher
from api import app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

# CONFIG_PATH could also be read from an env var
CONFIG_PATH = "config.json"


def main():
    try:
        with open(CONFIG_PATH) as f:
            config = json.load(f)
    except Exception:
        logger.exception("Failed to load config from %s", CONFIG_PATH)
        return

    # TODO: validate this are present and valid
    lat = config["location"]["lat"]
    lng = config["location"]["lng"]
    interval = config.get("interval_minutes", 60)

    database.init_db(config["db_url"])

    logger.info("Running initial fetch for (%s, %s)", lat, lng)
    fetcher.fetch_and_store(lat, lng)

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        fetcher.fetch_and_store,
        "interval",
        minutes=interval,
        args=[lat, lng],
    )
    scheduler.start()
    logger.info("Scheduler started, polling every %d mins", interval)

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
