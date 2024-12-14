"""
Below code provides functions for managing geofences and retrieving ads based on geolocation data. It includes
methods to check user location within a geofence, fetch relevant ads, manage geofences, and assign geofences to ads.
"""

from geopy.distance import geodesic
from utils.db_connection import create_connection


def is_within_geofence(user_location, geofence_location, radius_km):
    """
    Checking if a user's location is within a geofence radius.

    Args:
        user_location (tuple): (latitude, longitude) of the user.
        geofence_location (tuple): (latitude, longitude) of the geofence.
        radius_km (float): Radius of the geofence in kilometers.

    Returns:
        bool: True if within the geofence, False otherwise.
    """
    distance = geodesic(user_location, geofence_location).km
    print(f"Calculated distance: {distance} km (Radius: {radius_km} km)")  # Debugging statement
    return distance <= radius_km


def get_relevant_ads(user_lat, user_lon):
    """
    Fetching relevant ads based on user's location.

    Args:
        user_lat (float): Latitude of the user.
        user_lon (float): Longitude of the user.

    Returns:
        list: List of relevant ads.
    """
    conn = create_connection()
    cursor = conn.cursor()

    # Finding the geofences within range and join with ads
    query = """
        SELECT ads.title, ads.description
        FROM ads
        JOIN geofences ON ads.geofence_id = geofences.id
        WHERE (
            6371 * acos(
                cos(radians(?)) * cos(radians(geofences.latitude)) *
                cos(radians(geofences.longitude) - radians(?)) +
                sin(radians(?)) * sin(radians(geofences.latitude))
            )
        ) <= geofences.radius_km
    """
    cursor.execute(query, (user_lat, user_lon, user_lat))
    ads = cursor.fetchall()

    conn.close()
    return ads


def get_all_geofences():
    """
    Fetching all geofences from the database.

    Returns:
        list: List of all geofences.
    """
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM geofences")
    geofences = cursor.fetchall()

    conn.close()
    return geofences


def save_geofence(business_id, latitude, longitude, radius_km):
    """
    Save a new geofence to the database.

    Args:
        business_id (int): ID of the business owner.
        latitude (float): Latitude of the geofence center.
        longitude (float): Longitude of the geofence center.
        radius_km (float): Radius of the geofence in kilometers.

    Returns:
        int: ID of the newly created geofence.
    """
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO geofences (business_id, latitude, longitude, radius_km)
        VALUES (?, ?, ?, ?)
    """, (business_id, latitude, longitude, radius_km))
    geofence_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return geofence_id


def assign_geofence_to_ad(ad_id, user_lat, user_lon):
    """
    Assigning a geofence to an ad based on proximity to the user's location.

    Args:
        ad_id (int): ID of the ad to assign.
        user_lat (float): Latitude of the user's location.
        user_lon (float): Longitude of the user's location.

    Returns:
        bool: True if assignment is successful, False otherwise.
    """
    conn = create_connection()
    cursor = conn.cursor()

    # Finding the nearest geofence to the user's location
    query = """
        SELECT id, (
            6371 * acos(
                cos(radians(?)) * cos(radians(latitude)) *
                cos(radians(longitude) - radians(?)) +
                sin(radians(?)) * sin(radians(latitude))
            )
        ) AS distance_km
        FROM geofences
        ORDER BY distance_km ASC
        LIMIT 1
    """
    cursor.execute(query, (user_lat, user_lon, user_lat))
    nearest_geofence = cursor.fetchone()

    if nearest_geofence:
        geofence_id = nearest_geofence[0]
        # Updated the ad with the nearest geofence ID
        cursor.execute("""
            UPDATE ads SET geofence_id = ? WHERE id = ?
        """, (geofence_id, ad_id))
        conn.commit()
        conn.close()
        return True

    conn.close()
    return False
