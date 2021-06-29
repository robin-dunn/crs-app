import unittest
import geojson
from projtools import reproject

def test_reproject():
    geojson_string = '''
    {
        "type": "FeatureCollection",
        "name": "example_vector",
        "crs": { "type": "name", "properties": { "name": "epsg:4326" } },
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": { "type": "Point", "coordinates": [ -1.7071248, 52.5043046 ] }
            }
        ]
    }
    '''
    geometry = geojson.loads(geojson_string)
    reprojected_geometry = reproject(geometry, "epsg:4326", "epsg:32630")
    coords = reprojected_geometry["features"][0]["geometry"]["coordinates"]

    assert coords[0], 587753.8283029412
    assert coords[1], 5817916.448037734


if __name__ == '__main__':
    unittest.main()