from geopy.distance import geodesic
from utils.db_connection import create_connection


def is_within_geofence(user_location, geofence_location, radius_km):
    """
    Check if a user's location is within a geofence radius.

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
    Fetch relevant ads based on user's location.

    Args:
        user_lat (float): Latitude of the user.
        user_lon (float): Longitude of the user.

    Returns:
        list: List of relevant ads.
    """
    conn = create_connection()
    cursor = conn.cursor()

    # Find geofences within range and join with ads
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
        ) <= ge