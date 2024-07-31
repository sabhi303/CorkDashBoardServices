import requests
import csv
import json
from io import StringIO
from flask import Blueprint, jsonify
from database.db import get_database
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask blueprint
population_bp = Blueprint("population", __name__)

# Define a route to fetch, process, and store the CSV data as a single document
@population_bp.route('/cork_population', methods=['GET'])
def store_cork_population_data():
    url = "https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/CNA13/CSV/1.0/en"

    try:
        # Fetch the CSV data
        response = requests.get(url)
        response.raise_for_status()
        csv_data = response.text

        # Read the CSV data
        csv_reader = csv.DictReader(StringIO(csv_data))

        # Initialize the JSON structure
        cork_data = {
            "Cork": {
                "Census": [],
                "population": {
                    "Male": [],
                    "Female": [],
                    "Both sexes": []
                }
            }
        }

        # Filter the Cork city data and populate the JSON structure
        for row in csv_reader:
            if row['Province or County'] == 'Cork' and row['Statistic Label'] == 'Population':
                census_year = row['CensusYear']
                sex = row['Sex']
                value = row['VALUE']
                
                if value:  # Check if the value is not empty
                    value = int(value)
                    if census_year not in cork_data["Cork"]["Census"]:
                        cork_data["Cork"]["Census"].append(census_year)
                    
                    if sex == 'Male':
                        cork_data["Cork"]["population"]["Male"].append(value)
                    elif sex == 'Female':
                        cork_data["Cork"]["population"]["Female"].append(value)
                    elif sex == 'Both sexes':
                        cork_data["Cork"]["population"]["Both sexes"].append(value)

        # Get the database connection
        db = get_database()
        collection = db['data_themes_demographics_population']

        # Store the JSON data as a single document
        collection.insert_one(cork_data)

        logging.debug('Cork population data stored in the database.')

        return jsonify({"message": "Cork population data stored in the database"}), 200

    except requests.RequestException as e:
        logging.error("Failed to fetch CSV data", exc_info=True)
        return jsonify({"error": "Failed to fetch CSV data"}), 500
    except Exception as e:
        logging.error("An error occurred", exc_info=True)
        return jsonify({"error": "An error occurred"}), 500
