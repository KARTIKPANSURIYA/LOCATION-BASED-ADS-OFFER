from geopy.distance import geodesic
from utils.db_connection import create_connection

def is_within_geofence(user_location, geofence_location, radius_km):
    """
    Check if a user's location is within a geofence radius.

    :param user_location: (latitude, longitude) tuple of the user's location.
    :param geofence_location: (latitude, longitude) tuple of the geofence center.
    :param radius_km: Radius of the geofence in kilometers.
    :return: True if within the geofence, False otherwise.
    """
    distance = geodesic(user_location, geofence_location).km
    print(f"Calculated distance: {distance} km (Radius: {radius_km} km)")  # Debugging statement
    return distance <= radius_km

def get_relevant_ads(user_location):
    """
    Get ads for geofences that the user has entered.

    :param user_location: (latitude, longitude) tuple of the user's location.
    :return: List of relevant ads.
    """
    conn = create_connection()
    cursor = conn.cursor()

    # Fetch all geofences and their associated ads
    cursor.execute("""
    SELECT g.latitude, g.longitude, g.radius_km, a.title, a.description
    FROM geofences g
    INNER JOIN ads a ON g.id = a.geofence_id
    """)
    geofences = cursor.fetchall()

    relevant_ads = []
    for geofence in geofences:
        geofence_location = (geofence[0], geofence[1])
        radius_km = geofence[2]
        ad_title = geofence[3]
        ad_description = geofence[4]

        if is_within_geofence(user_location, geofence_location, radius_km):
            print(f"Ad '{ad_title}' is relevant.")
            relevant_ads.append({"title": ad_title, "description": ad_description})

    if not relevant_ads:
        print("No relevant ads found for this location.")

    return relevant_ads
