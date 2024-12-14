"""
This code file  provides functionality for managing the SQLite database used in the location-based system. It includes
utilities for creating and validating database connections, initializing tables, and managing data for users, geofences,
and ads.
"""
import sqlite3
import os

def create_connection():
    """
    Creating a connection to the SQLite database.
    Ensures that the database.sqlite file is located in the project root directory.
    """
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database.sqlite')
    conn = sqlite3.connect(db_path)
    return conn

def initialize_database():
    """
    Creating the necessary tables in the SQLite database if they don't already exist.
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
    debug function to print the names of all tables in the database.
    """
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print("Tables in the database:", cursor.fetchall())
    conn.close()

def validate_geofence_id(geofence_id):
    """
    Validates whether the given geofence_id exists in the geofences table.

    Args:
        geofence_id (int): The geofence ID to validate.

    Raises:
        ValueError: If the geofence_id does not exist.
    """
    conn = create_connection()
    cursor = conn.cursor()

    # Validate geofence_id exists
    cursor.execute("SELECT COUNT(*) FROM geofences WHERE id = ?", (geofence_id,))
    count = cursor.fetchone()[0]

    conn.close()
    if count == 0:
        raise ValueError("Invalid geofence_id.")

def get_business_geofences_and_ads(business_id):
    """
    Fetching geofences and associated ads for a specific business.

    Args:
        business_id (int): The ID of the business.

    Returns:
        list: A list of tuples containing geofence and ad information.
    """
    conn = create_connection()
    cursor = conn.cursor()

    # Fetch geofences and associated ads
    query = """
        SELECT g.id, g.latitude, g.longitude, g.radius_km, a.title, a.description
        FROM geofences g
        LEFT JOIN ads a ON g.id = a.geofence_id
        WHERE g.business_id = ?
        ORDER BY g.created_at DESC
    """
    cursor.execute(query, (business_id,))
    results = cursor.fetchall()

    conn.close()
    return results


def save_ad(geofence_id, title, description):
    """
    Saves a new ad associated with a geofence.

    Args:
        geofence_id (int): The ID of the geofence.
        title (str): The title of the ad.
        description (str): The description of the ad.

    Returns:
        None
    """
    # Validating geofence_id before proceeding
    validate_geofence_id(geofence_id)

    conn = create_connection()
    cursor = conn.cursor()

    # Inserting the ad
    cursor.execute("""
        INSERT INTO ads (geofence_id, title, description)
        VALUES (?, ?, ?)
    """, (geofence_id, title, description))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    initialize_database()
    debug_database()
