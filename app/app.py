import functools

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS, cross_origin
import passlib.hash
import pyproj
import geojson
import datetime
import jwt
import sqlite3
import os
import os.path

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

@app.route('/', defaults={'path': ''}, methods=["GET"])
@app.route('/<string:path>', methods=["GET"])
@app.route('/<path:path>', methods=["GET"])
def static_proxy(path):
  public_dir = os.path.dirname(os.path.abspath(__file__)) + "/../ui/dist/crs-app/";
  if os.path.isfile(public_dir + path):
      return send_from_directory(public_dir, path)
  else:
      return send_from_directory(public_dir, "index.html")

@app.route('/login', methods = ['POST'])
@cross_origin("*")
def login():
  username = request.json["username"]
  conn = get_db_connection()
  cur = conn.cursor()
  cur.execute("select user_id, encrypted_password from user where username = ?", [username])
  user_row = cur.fetchone()

  if (user_row == None or verify_password(request.json["password"], user_row[1]) == False):
    return {"message": "Invalid username or password"}, 401

  token = jwt.encode({
    "iss" : "GSI-CRS-APP",
    "iat" : datetime.datetime.utcnow(),
    "exp" : datetime.datetime.utcnow() + datetime.timedelta(minutes=45),
    "sub" : user_row[0] },
    app.config['SECRET_KEY'],
    "HS256")
  return jsonify(access_token=token)


@app.route('/projections', methods = ["GET"])
@cross_origin("*")
def projections():
  authHeader = request.headers.get('Authorization')
  authToken = authHeader.split()[1]
  decodedToken = jwt.decode(authToken, app.config["SECRET_KEY"], "HS256")
  #TODO: check auth token valid
  
  conn = get_db_connection()
  cur = conn.cursor()
  cur.execute("""
  select crs.epsg_code
  from
  user join user_crs on user.user_id = user_crs.user_id
  join crs on crs.crs_id = user_crs.crs_id
  where user.user_id = ?
  """, [decodedToken['sub']])
  items = map(lambda item: item[0], cur.fetchall())
  return jsonify(list(items))


@app.route('/vector/reproject', methods=["POST"])
def vector_reproject():

  #TODO: check auth token valid
  requestBody = request.get_json()
  target_crs = requestBody["targetProjection"]
  geometry = geojson.loads(geojson.dumps(requestBody["geojson"]))

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
  return reprojected


if __name__ == '__main__':
  # Bind on all interfaces so that we can easily
  # map ports when running in a docker container
  app.run(host= '0.0.0.0', debug=True)
