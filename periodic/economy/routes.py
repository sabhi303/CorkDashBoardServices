import requests
from flask import Blueprint, jsonify
import pandas as pd
import json
import requests
from io import StringIO
from database.db import get_database
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask blueprint
economy_bp = Blueprint("economy", __name__)

# Define a route to fetch, print, and store the CSV data as a single document
@economy_bp.route('/employment', methods=['GET'])
def store_transport_data():

    try:
        # Define the API URL
        url = "https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/QLF08/CSV/1.0/en"

        # Fetch the CSV data from the API
        response = requests.get(url)
        csv_data = response.text

        # Read the CSV data into a pandas DataFrame
        df = pd.read_csv(StringIO(csv_data))

        # Define the structure for the JSON data
        json_data = {
            "Persons aged 15 years and over in Employment": {
                "Quarter": [],
                "Region": {
                    "State": [],
                    "Southern": [],
                    "South-West": []
                }
            },
            "Unemployed Persons aged 15 years and over": {
                "Quarter": [],
                "Region": {
                    "State": [],
                    "Southern": [],
                    "South-West": []
                }
            }
        }

        # Fill the JSON data with values from the DataFrame
        for statistic_label in json_data.keys():
            # Filter the DataFrame based on the statistic label
            df_filtered = df[df['Statistic Label'] == statistic_label]

            # Get the unique quarters
            unique_quarters = df_filtered['Quarter'].unique().tolist()
            json_data[statistic_label]['Quarter'] = unique_quarters

            # Get the values for each region
            for region in json_data[statistic_label]['Region'].keys():
                region_values = df_filtered[df_filtered['Region'] == region]['VALUE'].tolist()
                json_data[statistic_label]['Region'][region] = region_values


        # Get the database connection
        db = get_database()
        collection = db['data_themes_economy']

        # Store the JSON data as a single document
        collection.insert_one({"data": json_data})

        logging.debug('Economy data stored in the database.')

        return jsonify({"message": "Economy data stored in the database"}), 200

    except requests.RequestException as e:
        logging.error("Failed to fetch JSON data", exc_info=True)
        return jsonify({"error": "Failed to fetch JSON data"}), 500
    except Exception as e:
        logging.error("An error occurred", exc_info=True)
        return jsonify({"error": "An error occurred"}), 500

