import geojson
import pyproj

def reproject(geometry, source_crs, target_crs):
  transformer = pyproj.Transformer.from_crs(
    source_crs,
    target_crs,
    always_xy=True,
  )

  reprojected = {
    **geojson.utils.map_tuples(
      lambda c: transformer.transform(c[0], c[1]),
      geometry,
    ),
    **{
      "crs": {
        "type": "name",
        "properties": {
          "name": target_crs
        }
      }
    }
  }
  return reprojected