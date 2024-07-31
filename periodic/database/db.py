import logging
from pymongo import MongoClient

# Set debug mode globally
logging.basicConfig(level=logging.DEBUG)

url = 'mongodb://localhost:27017/'
dbName = 'CorkDashboard'

db = None  # Hold the database connection

def connect_to_database():
    global db
    if db:
        return db  # If db connection is already established, return it
    try:
        client = MongoClient(url)
        db = client[dbName]  # Get the database instance from the client
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
