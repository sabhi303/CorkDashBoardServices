import logging
import os
from pymongo import MongoClient

# Set debug mode globally
logging.basicConfig(level=logging.DEBUG)

# Retrieve MongoDB configuration from environment variables
MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'CorkDashboard')
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')

if DB_USERNAME and DB_PASSWORD:
    MONGODB_URL = f'mongodb://{DB_USERNAME}:{DB_PASSWORD}@{MONGODB_URL.split("//")[1]}'

db = None  # Hold the database connection

def connect_to_database():
    global db
    if db:
        return db  # If db connection is already established, return it
    try:
        client = MongoClient(MONGODB_URL)
        db = client[DB_NAME]  # Get the database instance from the client
        logging.debug('Connected to MongoDB')
        return db  # Return the database instance
    except Exception as error:
        logging.error('Failed to connect to MongoDB', exc_info=True)
        raise error

def get_database():
    global db
    if db is None:
        raise Exception('Database connection not initialized.')
    return db
