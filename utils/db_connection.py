import sqlite3

def create_connection():
    """Create a database connection."""
    conn = sqlite3.connect('database.sqlite')
    return conn

def initialize_database():
    """Create the necessary tables in the database."""
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
        FOREIGN KEY(geofence_id) REFERENCES geofences(id)
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_database()
