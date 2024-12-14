"""
This module provides functionality for managing geofences in a location-based system. It defines the Geofence class,
which includes methods for creating geofences, saving them to a database, and retrieving all geofences.
"""
from utils.db_connection import create_connection

class Geofence:
    def __init__(self, business_id, latitude, longitude, radius_km):
        self.business_id = business_id
        self.latitude = latitude
        self.longitude = longitude
        self.radius_km = radius_km

    def save_to_db(self):
        """
        Saving the geofence to the database.
        """
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO geofences (business_id, latitude, longitude, radius_km)
        VALUES (?, ?, ?, ?)
        """, (self.business_id, self.latitude, self.longitude, self.radius_km))

        conn.commit()
        conn.close()

    @staticmethod
    def get_all_geofences():
        """
        Fetching all geofences from the database.
        """
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM geofences")
        geofences = cursor.fetchall()

        conn.close()
        return geofences
