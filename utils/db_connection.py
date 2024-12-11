import sqlite3
import os

def create_connection():
    """
    Create a connection to the SQLite database.
    Ensures that the database.sqlite file is located in the project root directory.
    """
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database.sqlite')
    conn = sqlite3.connect(db_path)
    return conn

def initialize_database():
    """
    Create the necessary tables in the SQLite database if they don't already exist.
    """
    conn = create_connection()
    cursor = conn.cursor()

    # Create Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        user_type TEXT NOT NULL CHECK(user_type IN ('business', 'personal'))
    )
    """)

    # Create Geofences table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS geofences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        business_id INTEGER NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        radius_km REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(business_id) REFERENCES users(id)
    )
    """)

    # Create Ads table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        geofence_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(geofence_id) REFERENCES geofences(id)
    )
    """)

    conn.commit()
    conn.close()

def debug_database():
    """
    Debug function to print the names of all tables in the database.
    """
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print("Tables in the database:",