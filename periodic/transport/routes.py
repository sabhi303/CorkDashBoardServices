import requests
from flask import Blueprint, jsonify
from database.db import get_database
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask blueprint
transport_bp = Blueprint("transport", __name__)

# Define a route to fetch, print, and store the CSV data as a single document
@transport_bp.route('/airport_passengers', methods=['GET'])
def store_transport_data():
    url = "https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.PxAPIv1/en/6/AS/TAQ01?query=%7B%22query%22:%5B%7B%22code%22:%22C02935V03550%22,%22selection%22:%7B%22filter%22:%22item%22,%22values%22:%5B%22EICK%22%5D%7D%7D%5D,%22response%22:%7B%22format%22:%22json-stat2%22%7D%7D"

    try:
        # Fetch the JSON data
        response = requests.get(url)
        response.raise_for_status()
        json_data = response.json()

        # Get the database connection
        db = get_database()
        collection = db['data_themes_transport']

        # Update or Store the JSON data as a single document
        collection.update_one(
            {},
            {"$set": {"data": json_data}},  # Update operation
            upsert=True  # Insert document if no matching document is found
        )

        logging.debug('Transport data stored in the database.')

        return jsonify({"message": "Transport data stored in the database"}), 200

    except requests.RequestException as e:
        logging.error("Failed to fetch JSON data", exc_info=True)
        return jsonify({"error": "Failed to fetch JSON data"}), 500
    except Exception as e:
        logging.error("An error occurred", exc_info=True)
        return jsonify({"error": "An error occurred"}), 500

