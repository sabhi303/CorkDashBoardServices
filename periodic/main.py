from flask import Flask
from housing.routes import housing_bp
from transport.routes import transport_bp
from economy.routes import economy_bp
import asyncio
import logging

from database.db import connect_to_database, get_database

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(housing_bp, url_prefix="/housing")
app.register_blueprint(transport_bp, url_prefix="/transport")
app.register_blueprint(economy_bp, url_prefix="/economy")



async def initialize_app():
    connect_to_database()

if __name__ == "__main__":
    # Ensure the database connection is established before running the app
    asyncio.run(initialize_app())
    app.run(debug=True)
