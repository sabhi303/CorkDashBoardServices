from flask import Flask
from weather.routes import weather_bp
from noise.routes import noise_bp
from air.routes import air_bp
from transport.routes import transport_bp
from environment.routes import environment_bp
import asyncio
import logging

from database.db import connect_to_database, get_database

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(weather_bp, url_prefix="/weather")
app.register_blueprint(noise_bp, url_prefix="/noise")
app.register_blueprint(air_bp, url_prefix="/air")
app.register_blueprint(transport_bp, url_prefix="/transport")
app.register_blueprint(environment_bp, url_prefix="/environment")


async def initialize_app():
    connect_to_database()

if __name__ == "__main__":
    # Ensure the database connection is established before running the app
    asyncio.run(initialize_app())
    app.run(debug=True)
