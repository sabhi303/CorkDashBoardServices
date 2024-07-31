import requests
from flask import Blueprint, jsonify
import pandas as pd
import io
import json
from database.db import get_database
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask blueprint
housing_bp = Blueprint("housing", __name__)

# Define a route to fetch, print, and store the CSV data as a single document
@housing_bp.route('/housing', methods=['GET'])
def store_json_data():
    url = "https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/HPM05/CSV/1.0/en"

    try:
        # Fetch the CSV data
        response = requests.get(url)
        response.raise_for_status()
        csv_data = response.text

        # Read the CSV data into a DataFrame
        df = pd.read_csv(io.StringIO(csv_data))

        # Drop rows with any empty values
        df = df.dropna()

        # Filter rows for "Dwelling Status" as "All Dwelling Statuses" and "Stamp Duty Event" as "Filings"
        df = df[(df['Dwelling Status'] == 'All Dwelling Statuses') & (df['Stamp Duty Event'] == 'Filings')]

        # Function to create the nested JSON structure for a given region
        def create_json_structure(df_region):
            result = {
                "Month": df_region["Month"].unique().tolist(),
                "Type of Dwelling": {}
            }

            # Get unique types of dwelling
            dwelling_types = df_region["Type of Dwelling"].unique()

            for dwelling in dwelling_types:
                result["Type of Dwelling"][dwelling] = {}

                for statistic in ["Volume of Sales", "Mean Sale Price"]:
                    # Filter the DataFrame for the current type of dwelling and statistic
                    filtered_df = df_region[(df_region["Type of Dwelling"] == dwelling) & (df_region["Statistic Label"] == statistic)]

                    # Add the unit and values for each month
                    result["Type of Dwelling"][dwelling][statistic] = {
                        "Unit": filtered_df["UNIT"].iloc[0] if not filtered_df.empty else None,
                        "Values": filtered_df["VALUE"].tolist()
                    }

            return result

        # Filter rows for Cork City and Cork County
        cork_city_df = df[df['RPPI Region'].str.lower() == 'cork city']
        cork_county_df = df[df['RPPI Region'].str.lower() == 'cork county']

        # Create the JSON structure for Cork City and Cork County
        cork_city_json = {"Cork City": create_json_structure(cork_city_df)}
        cork_county_json = {"Cork County": create_json_structure(cork_county_df)}

        # Combine both into a single dictionary
        combined_json = {**cork_city_json, **cork_county_json}

        # Get the database connection
        db = get_database()
        collection = db['data_themes_housing']

        # Store the JSON data as a single document
        collection.insert_one({"data": combined_json})

        logging.debug('JSON data stored in the database.')

        return jsonify({"message": "JSON data stored in the database"}), 200

    except requests.RequestException as e:
        logging.error("Failed to fetch CSV data", exc_info=True)
        return jsonify({"error": "Failed to fetch CSV data"}), 500
    except Exception as e:
        logging.error("An error occurred", exc_info=True)
        return jsonify({"error": "An error occurred"}), 500
