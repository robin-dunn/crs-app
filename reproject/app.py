import functools

from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import passlib.hash
import pyproj
import geojson
import datetime
import jwt
import sqlite3
import os

app = Flask(__name__)
cors = CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SECRET_KEY']='004f2af45d3a4e161a7dd2d17fdae47f'

# There's username and passwords already in db.sqlite:
#   user1 / password1
#   user2 / password2

def get_db_connection():
  return sqlite3.connect(os.path.dirname(__file__) + '/../db.sqlite')

def encrypt_password(password: str) -> str:
  return passlib.hash.pbkdf2_sha256.hash(password)


def verify_password(password: str, encypted_password: str) -> str:
  return passlib.hash.pbkdf2_sha256.verify(password, encypted_password)

@app.route('/login', methods = ['POST'])
@cross_origin("*")
def login():
  username = request.json["username"]
  conn = get_db_connection()
  cur = conn.cursor()
  cur.execute("select encrypted_password from user where username = ?", [username])
  user_row = cur.fetchone()

  if (user_row == None or verify_password(request.json["password"], user_row[0]) == False):
    return {"message": "Invalid username or password"}, 401

  token = jwt.encode({
    "iss" : "GSI-CRS-APP",
    "iat" : datetime.datetime.utcnow(),
    "exp" : datetime.datetime.utcnow() + datetime.timedelta(minutes=45),
    "sub" : username },
    app.config['SECRET_KEY'],
    "HS256")
  return jsonify(access_token=token)


@app.route('/projections', methods = ["GET"])
@cross_origin("*")
def projections():
  conn = get_db_connection()
  cur = conn.cursor()
  cur.execute("select epsg_code from crs")
  return jsonify(cur.fetchall())


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
