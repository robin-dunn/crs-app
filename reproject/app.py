import functools

from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import passlib.hash
import pyproj
import geojson
import datetime
import jwt

app = Flask(__name__)
cors = CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SECRET_KEY']='004f2af45d3a4e161a7dd2d17fdae47f'

# There's username and passwords already in db.sqlite:
#   user1 / password1
#   user2 / password2

def encrypt_password(password: str) -> str:
  return passlib.hash.pbkdf2_sha256.hash(password)


def verify_password(password: str, encypted_password: str) -> str:
  return passlib.hash.pbkdf2_sha256.verify(password, encypted_password)


@app.route('/login', methods = ['POST'])
@cross_origin("*")
def login():
  print(request.json)
  # TODO: get user from database
  token = jwt.encode({
    "iss" : "GSI-CRS-APP",
    "iat" : datetime.datetime.utcnow(),
    "exp" : datetime.datetime.utcnow() + datetime.timedelta(minutes=45),
    "sub" : request.json["username"] },
    app.config['SECRET_KEY'],
    "HS256")
  return jsonify(token=token)


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
    app.run(host= '0.0.0.0', debug=True)
