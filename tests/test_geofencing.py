from models.geofence import Geofence
from models.ad import Ad
from utils.geofence_logic import is_within_geofence, get_relevant_ads

def test_is_within_geofence():
    """
    Test if a user's location is correctly identified as being within or outside a geofence.
    """
    user_location = (40.730610, -73.935242)  # New York City
    geofence_location = (40.7128, -74.0060)  # Geofence: Lower Manhattan
    radius_km = 5.0

    # Case 1: User is outside the geofence
    assert not is_within_geofence(user_location, geofence_location, radius_km), "User should be outside the geofence"
    print("User is correctly identified as outside the geofence.")

    # Case 2: Adjust the radius to include the user
    radius_km = 7.0
    assert is_within_geofence(user_location, geofence_location, radius_km), "User should be within the geofence"
    print("User is correctly identified as within the geofence.")


def test_get_relevant_ads():
    """
    Test fetching relevant ads based on user location.
    """
    user_lat, user_lon = 40.56595508198959, -74.30868876094596  # User is in the Metropark iselin geofence
    ads = get_relevant_ads(user_lat, user_lon)

    assert len(ads) > 0, "No ads found for the user's location."
    print("Relevant ads:", ads)


def test_geofence_creation():
    """
    Testing the creation of a geofence and saving to the database.
    """
    geofence = Geofence(1, 40.56595508198959, -74.30868876094596, 5.0)  # Business ID: 1, Lat/Long: Metropark, Radius: 5km
    geofence.save_to_db()
    print("Geofence created successfully!")


def test_ad_creation():
    """
    Testing the creation of an ad and saving to the database.
    """
    ad = Ad(1, "50% Off!", "Get 50% off all items this weekend.")  # Geofence ID: 1
    ad.save_to_db()
    print("Ad created successfully!")


def test_fetch_geofences_and_ads():
    """
    Testing fetching geofences and ads from the database.
    """
    geofences = Geofence.get_all_geofences()
    print("All Geofences:", geofences)

    ads = Ad.get_ads_by_geofence(1)  # Assuming Geofence ID: 1
    print("Ads for Geofence 1:", ads)


if __name__ == "__main__":
    test_geofence_creation()
    test_ad_creation()
    test_fetch_geofences_and_ads()
    test_is_within_geofence()
    test_get_relevant_ads()
