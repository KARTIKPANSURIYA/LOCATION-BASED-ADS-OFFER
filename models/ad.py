from utils.db_connection import create_connection
from utils.db_connection import validate_geofence_id


class Ad:
    def __init__(self, geofence_id, title, description):
        self.geofence_id = geofence_id
        self.title = title
        self.description = description

    def save_to_db(self):
        """
        Save the ad to the database with the validated geofence ID.
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
        Fetch all ads for a specific geofence.
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
        Fetch all ads from the database.
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

        # Find the most recent geofence for the business
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

        # Insert the ad
        cursor.execute("""
            INSERT INTO ads (geofence_id, title, description)
            VALUES (?, ?, ?)
        """, (geofence_id, title, description))
        conn.commit()
        conn.close()
