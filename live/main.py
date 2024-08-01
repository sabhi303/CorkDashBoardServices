from flask import Flask
from weather.routes import weather_bp
from transport.routes import transport_bp
from environment.routes import environment_bp
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import requests
import json
import time
import atexit

from database.db import connect_to_database

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(weather_bp, url_prefix="/weather")
app.register_blueprint(transport_bp, url_prefix="/transport")
app.register_blueprint(environment_bp, url_prefix="/environment")

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
            print(f"API {full_url} called at {datetime.now()}, response status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to call API {full_url}: {e}")
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
        scheduler.add_job(func=create_job(api), trigger="interval", **interval)
    scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

def initialize_app():
    connect_to_database()
    start_scheduler()

if __name__ == "__main__":
    initialize_app()
    app.run(debug=True)
