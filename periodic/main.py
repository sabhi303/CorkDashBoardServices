from flask import Flask
from housing.routes import housing_bp
from transport.routes import transport_bp
from economy.routes import economy_bp
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
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
app.register_blueprint(housing_bp, url_prefix="/housing")
app.register_blueprint(transport_bp, url_prefix="/transport")
app.register_blueprint(economy_bp, url_prefix="/economy")

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
        # Calculate the start date
        start_date = datetime.now() + timedelta(seconds=60)  # Start after 60 seconds

        scheduler.add_job(
            func=create_job(api),
            trigger='interval',
            **interval,
            start_date=start_date
        )
        # create_job(api)()
    scheduler.start()

# Register the shutdown function to be called on exit
atexit.register(lambda: scheduler.shutdown())

def initialize_app():
    # Connect to the database
    connect_to_database()
    # Start the scheduler
    start_scheduler()

if __name__ == "__main__":
    try:
        # Ensure the database connection is established before running the app
        initialize_app()
        # Run the Flask app
        app.run(debug=True)

    except Exception as e:
        logger.error(f"An error occurred: {e}")
