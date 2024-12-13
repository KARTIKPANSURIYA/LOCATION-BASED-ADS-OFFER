import pytest
from utils.map_view import generate_map

def test_generate_map():
    """
    Test generating an interactive map with geofences.
    """
    geofences = [
        {'latitude': 40.7128, 'longitude': -74.0060, 'radius_km': 5.0},
        {'latitude': 40.730610, 'longitude': -73.935242, 'radius_km': 3.0},
    ]

    try:
        map_file = generate_map(geofences, output_file='test_map.html')
        assert map_file == 'test_map.html', "Map file name mismatch."
        print("Interactive map generated successfully!")
    except Exception as e:
        pytest.fail(f"Failed to generate map: {e}")
