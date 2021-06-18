import functools

from flask import Flask
import passlib.hash
import pyproj
import geojson

app = Flask(__name__)

# There's username and passwords already in db.sqlite:
#   user1 / password1
#   user2 / password2

def encrypt_password(password: str) -> str:
  return passlib.hash.pbkdf2_sha256.hash(password)


def verify_password(password: str, encypted_password: str) -> str:
  return passlib.hash.pbkdf2_sha256.verify(password, encypted_password)


@app.route('/login')
def login():
    raise NotImplementedError('Implement Me!')


@app.route('/projections')
def projections():
    raise NotImplementedError('Implement Me!')


@app.route('/vector/reproject')
def vector_reproject():

    raise NotImplementedError('Implement Me!')

    ## Some sample code to reproject a geojson

    # Target CRS to be read from HTTP request
    target_crs = 'epsg:3857'

    # GeoJSON to be read from HTTP request
    with open('example_vector.geojson') as geojson_file:
      geometry = geojson.load(geojson_file)

    source_crs = geometry['crs']['properties']['name']

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


if __name__ == '__main__':
    # Bind on all interfaces so that we can easily
    # map ports when running in a docker container
    app.run(host= '0.0.0.0')
