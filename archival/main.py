from flask import Flask
from population.routes import population_bp
import asyncio
import logging

from database.db import connect_to_database, get_database

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(population_bp, url_prefix="/demographics")

async def initialize_app():
    connect_to_database()

if __name__ == "__main__":
    # Ensure the database connection is established before running the app
    asyncio.run(initialize_app())
    app.run(debug=True)
