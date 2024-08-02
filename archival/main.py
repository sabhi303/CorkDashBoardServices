from flask import Flask
from population.routes import population_bp
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import asyncio
import requests
import json
import logging
import atexit

from database.db import connect_to_database

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Register Blueprints
app.register_blueprint(population_bp, url_prefix="/demographics")

# Load scheduler configuration
with open('scheduler_config.json') as config_file:
    config = json.load(config_file)

scheduler = BackgroundScheduler()

# Variable to store the base URL
base_url = "http://localhost:5000"

def create_job(api):
    def job():
        full_url = f"{base_url.rstrip('/')}/{api['url'].lstrip('/')}"
        try:
            response = requests.get(full_url)
            logger.info(f"API {full_url} called at {datetime.now()}, response status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to call API {full_url}: {e}")
    return job

# Map the configuration unit to APScheduler unit keywords
time_units = {
    'seconds': 'seconds',
    'minutes': 'minutes',
    'hours': 'hours',
    'days': 'days',
    'weeks': 'weeks'
}

def start_scheduler():
    # Set up jobs based on config
    for api in config['apis']:
        interval = {time_units[api['unit']]: api['interval']}
        # Schedule the job with an initial delay of 15 seconds
        scheduler.add_job(
            func=create_job(api),
            trigger='interval',
            **interval,
            start_date=datetime.now() + timedelta(seconds=60)
        )
    scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

async def initialize_app():
    connect_to_database()
    start_scheduler()

if __name__ == "__main__":
    asyncio.run(initialize_app())
    app.run(debug=True)
