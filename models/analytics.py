from geopy.distance import geodesic
import folium
import matplotlib.pyplot as plt

# Plot geofences on a map
def plot_geofences_on_map(geofences, user_locations):
    """
    Plots geofences and user locations on an interactive map.
    """
    map_center = geofences[0][:2] if geofences else (0, 0)
    map_ = folium.Map(location=map_center, zoom_start=13)

    # Geofences
    for geofence in geofences:
        latitude, longitude, radius_km = geofence
        folium.Circle(
            location=(latitude, longitude),
            radius=radius_km * 1000,
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.3
        ).add_to(map_)

    # User Locations
    for user_location in user_locations:
        folium.Marker(location=user_location, icon=folium.Icon(color='red', icon='user')).add_to(map_)

    map_.save("geofence_map.html")
    print("Map saved as geofence_map.html")


# Count users in geofences
def count_users_in_geofences(geofences, user_locations):
    """
    Counts the number of users within each geofence.
    """
    user_count = {i: 0 for i in range(len(geofences))}
    for i, geofence in enumerate(geofences):
        center, radius = geofence[:2], geofence[2]
        for user_location in user_locations:
            if geodesic(center, user_location).km <= radius:
                user_count[i] += 1
    return user_count


# Plot geofence user counts
def plot_user_geofence_counts(user_counts):
    """
    Plots a bar chart of users in each geofence.
    """
    plt.bar(user_counts.keys(), user_counts.values(), color='blue', alpha=0.7)
    plt.xlabel('Geofence ID')
    plt.ylabel('Number of Users')
    plt.title('Number of Users in Each Geofence')
    plt.show()

def plot_ad_views(ad_views):
    """
    Plots a bar chart showing the number of views for each ad.

    Args:
        ad_views (list): List of tuples (ad_title, view_count).
    """
    ad_titles = [ad[0] for ad in ad_views]
    view_counts = [ad[1] for ad in ad_views]

    plt.figure(figsize=(10, 6))
    plt.bar(ad_titles, view_counts, color='green', alpha=0.7)
    plt.xlabel('Ad Title')
    plt.ylabel('Number of Views')
    plt.title('Ad Views for Your Ads')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()
