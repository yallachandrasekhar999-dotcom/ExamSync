from json_db import db

# JSON Database instance is already created in json_db.py

def get_db():
    """Dependency to get the JSON database instance"""
    # Simply yield the db instance. No session closing needed for JSON.
    yield db
