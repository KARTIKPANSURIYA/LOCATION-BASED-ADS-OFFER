from utils.db_connection import create_connection

class Ad:
    def __init__(self, geofence_id, title, description):
        self.geofence_id = geofence_id
        self.title = title
        self.description = description

    def save_to_db(self):
        """
        Saveing the ad to the database.
        """
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
        Fetching all ads associated with a specific geofence.
        """
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM ads WHERE geofence_id = ?", (geofence_id,))
        ads = cursor.fetchall()

        conn.close()
        return ads
