import requests
from flask import Blueprint, jsonify
from database.db import get_database
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask blueprint
transport_bp = Blueprint("transport", __name__)

# Define a route to fetch, print, and store the CSV data as a single document
@transport_bp.route('/car_parks', methods=['GET'])
def store_csv_data():
    csv_url = "https://data.corkcity.ie/datastore/dump/f4677dac-bb30-412e-95a8-d3c22134e3c0"
    try:
        # Fetch the CSV data
        response = requests.get(csv_url, verify=False)
        response.raise_for_status()
        csv_data = response.text

        # Print the CSV data
        # logging.debug("CSV Data:\n" + csv_data)

        # Get the database connection
        db = get_database()
        collection = db['data_transport_car_parks']

        # Update or Store the CSV data as a single document
        collection.update_one(
            {},
            {"$set": {"csv_data": csv_data}},  # Update operation
            upsert=True  # Insert document if no matching document is found
        )

        logging.debug('CSV data stored in the database.')

        return jsonify({"message": "CSV data stored in the database"}), 200

    except requests.RequestException as e:
        logging.error("Failed to fetch CSV data", exc_info=True)
        return jsonify({"error": "Failed to fetch CSV data"}), 500
    except Exception as e:
        logging.error("An error occurred", exc_info=True)
        return jsonify({"error": "An error occurred"}), 500
