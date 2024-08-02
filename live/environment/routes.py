import requests
from flask import Blueprint, jsonify
from database.db import get_database
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask blueprint
environment_bp = Blueprint("environment", __name__)

# Define a route to fetch, filter, and store the water level data
@environment_bp.route('/water_levels', methods=['GET'])
def store_water_level_data():
    json_url = "https://waterlevel.ie/geojson/latest/"
    try:
        # Fetch the JSON data
        response = requests.get(json_url, verify=False)
        response.raise_for_status()
        json_data = response.json()

        # Extract the relevant parts of the GeoJSON
        geojson_type = json_data.get('type', 'FeatureCollection')
        crs = json_data.get('crs', {})
        features = json_data.get('features', [])

        # Filter records by region_id 6 and 15
        filtered_features = [feature for feature in features
                             if feature.get('properties', {}).get('region_id') in [6, 15]]

        # Construct the filtered GeoJSON
        filtered_geojson = {
            'type': geojson_type,
            'crs': crs,
            'features': filtered_features
        }

        # Print the filtered data for debugging
        # logging.debug("Filtered GeoJSON Data:\n" + str(filtered_geojson))

        # Get the database connection
        db = get_database()
        collection = db['data_environment_water_levels']

        # Update or store the filtered GeoJSON data as a single document
        collection.update_one(
            {},
            {"$set": {"water_levels": filtered_geojson}},  # Update operation
            upsert=True  # Insert document if no matching document is found
        )

        logging.debug('Filtered water level data stored in the database.')

        return jsonify({"message": "Filtered water level data stored in the database"}), 200

    except requests.RequestException as e:
        logging.error("Failed to fetch water level data", exc_info=True)
        return jsonify({"error": "Failed to fetch water level data"}), 500
    except Exception as e:
        logging.error("An error occurred", exc_info=True)
        return jsonify({"error": "An error occurred"}), 500
