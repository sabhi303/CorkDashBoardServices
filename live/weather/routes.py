import requests
from flask import Blueprint, jsonify
from database.db import get_database
import logging
import xml.etree.ElementTree as ET

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask blueprint
weather_bp = Blueprint("weather", __name__)

# Define a route to fetch, filter, and store the weather data
@weather_bp.route('/weather_data', methods=['GET'])
def store_weather_data():
    xml_url = "https://www.met.ie/Open_Data/xml/obs_present.xml"
    try:
        # Fetch the XML data
        response = requests.get(xml_url, verify=False)
        response.raise_for_status()
        xml_data = response.text

        # Print the full XML data for debugging
        # logging.debug("Full XML Data:\n" + xml_data)

        # Parse the XML data
        root = ET.fromstring(xml_data)

        # Since the root tag is <observations>, use it directly
        observations_element = root

        # Print the <observations> element and its attributes for debugging
        # logging.debug(f"<observations> tag: {observations_element.tag}, attributes: {observations_element.attrib}")

        # Filter child <station> elements for Cork
        filtered_stations = []
        for station in observations_element.findall("station"):
            station_name = station.get("name")
            if station_name and "Cork" in station_name:
                filtered_stations.append(station)

        # Reconstruct the XML data with filtered <station> elements
        filtered_observations = ET.Element("observations", time=observations_element.get("time"))
        for station in filtered_stations:
            filtered_observations.append(station)

        # Convert the filtered XML to a string
        filtered_xml_data = ET.tostring(filtered_observations, encoding='unicode')

        # Print the filtered XML data for debugging
        # logging.debug("Filtered XML Data:\n" + filtered_xml_data)

        # Get the database connection
        db = get_database()
        collection = db['data_weather']

        # Update or Store the filtered XML data as a single document
        collection.update_one(
            {},
            {"$set": {"weather_data": filtered_xml_data}},  # Update operation
            upsert=True  # Insert document if no matching document is found
        )

        logging.debug('Filtered weather data stored in the database.')

        return jsonify({"message": "Filtered weather data stored in the database"}), 200

    except requests.RequestException as e:
        logging.error("Failed to fetch weather data", exc_info=True)
        return jsonify({"error": "Failed to fetch weather data"}), 500
    except ET.ParseError as e:
        logging.error("Failed to parse XML data", exc_info=True)
        return jsonify({"error": "Failed to parse XML data"}), 500
    except Exception as e:
        logging.error("An error occurred", exc_info=True)
        return jsonify({"error": "An error occurred"}), 500
