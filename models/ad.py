"""This module provides functionality for managing advertisements in a location-based system. It defines the `Ad` class,
which includes methods for saving ads to the database, fetching ads for specific geofences , and managing
ad data. It also ensures that ads are associated with valid geofences.
"""

from utils.db_connection import create_connection
from utils.db_connection import validate_geofence_id


class Ad:
    def __init__(self, geofence_id, title, description):
        self.geofence_id = geofence_id
        self.title = title
        self.description = description

    def save_to_db(self):
        """
        Saving the ad to the database with the validated geofence ID.
        """
        validate_geofence_id(self.geofence_id)

        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO ads (geofence_id, title, description)
            VALUES (?, ?, ?)
        """, (self.geofence_id, self.title, self.description))

        conn.commit()
        conn.close()

    @staticmethod
    def get_ads_by_geofence(geofence_id):
        """
        Fetching  all the ads for a specific geofence.
        """
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM ads WHERE geofence_id = ?
        """, (geofence_id,))
        ads = cursor.fetchall()
        conn.close()
        return ads

    @staticmethod
    def get_all_ads():
        """
        Fetching all the ads from the database.
        """
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ads")
        all_ads = cursor.fetchall()
        conn.close()
        return all_ads

    @staticmethod
    def save_ad_for_business(business_id, title, description):
        """
        Save an ad associated with the nearest geofence for a business.
        """
        conn = create_connection()
        cursor = conn.cursor()

        # Finding the most recent geofence for the business
        cursor.execute("""
            SELECT id FROM geofences
            WHERE business_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (business_id,))
        geofence = cursor.fetchone()

        if not geofence:
            raise ValueError("No geofence found for this business.")

        geofence_id = geofence[0]

        # Inserting the ad
        cursor.execute("""
            INSERT INTO ads (geofence_id, title, description)
            VALUES (?, ?, ?)
        """, (geofence_id, title, description))
        conn.commit()
        conn.close()
