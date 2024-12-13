import pytest
from utils.analytics import plot_geofence_usage


def test_plot_geofence_usage():
    """
    Test plotting geofence usage statistics.
    """
    # Mock data for geofence usage
    geofence_stats = {1: 10, 2: 5, 3: 15}

    try:
        plot_geofence_usage(geofence_stats)
        print("Geofence usage plot created successfully!")
    except Exception as e:
        pytest.fail(f"Failed to create geofence usage plot: {e}")
