from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS, cross_origin
import passlib.hash
import geojson
import datetime
import jwt
import sqlite3
import os
import os.path
from projtools import reproject

app = Flask(__name__)
cors = CORS(app)

app.config["CORS_HEADERS"] = "Content-Type"
app.config["AUTH_ISSUER"] = "GSI-CRS-APP"
app.config["SECRET_KEY"] = "004f2af45d3a4e161a7dd2d17fdae47f"

# There's username and passwords already in db.sqlite:
#   user1 / password1
#   user2 / password2

def get_db_connection():
  return sqlite3.connect(os.path.dirname(__file__) + '/../db.sqlite')

def encrypt_password(password: str) -> str:
  return passlib.hash.pbkdf2_sha256.hash(password)

def verify_password(password: str, encypted_password: str) -> str:
  return passlib.hash.pbkdf2_sha256.verify(password, encypted_password)

def decode_auth_token(request):
  try:
    authHeader = request.headers.get('Authorization')
    authToken = authHeader.split()[1]
    decodedToken = jwt.decode(authToken, app.config["SECRET_KEY"], "HS256")
    if (decodedToken["iss"].lower() != app.config["AUTH_ISSUER"].lower()):
      return False
    return decodedToken
  except jwt.ExpiredSignatureError:
    return False

def get_projections(user_id):
  conn = get_db_connection()
  cur = conn.cursor()
  cur.execute("""
  select crs.epsg_code
  from
  user join user_crs on user.user_id = user_crs.user_id
  join crs on crs.crs_id = user_crs.crs_id
  where user.user_id = ?
  """, [user_id])
  return list(map(lambda item: item[0], cur.fetchall()))

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
    "iss" : app.config["AUTH_ISSUER"],
    "iat" : datetime.datetime.utcnow(),
    "exp" : datetime.datetime.utcnow() + datetime.timedelta(minutes=45),
    "sub" : user_row[0] },
    app.config["SECRET_KEY"],
    "HS256")
  return jsonify(access_token=token)


@app.route('/projections', methods = ["GET"])
@cross_origin("*")
def projections():
  decodedToken = decode_auth_token(request)
  if (decodedToken == False): return jsonify({'message':'Unauthorised'}), 401
  return jsonify(get_projections(decodedToken["sub"]))


@app.route('/vector/reproject/json', methods=["POST"])
def vector_reproject_json():
  decodedToken = decode_auth_token(request)
  if (decodedToken == False): return jsonify({'message':'Unauthorised'}), 401
  requestBody = request.get_json()
  target_crs = requestBody["targetProjection"]

  allowed_projections = get_projections(decodedToken["sub"])
  if target_crs not in allowed_projections:
    return jsonify({'message':'Target coordinate CRS not allowed for this user.'}), 403

  geometry = geojson.loads(geojson.dumps(requestBody["geojson"]))
  source_crs = geometry['crs']['properties']['name']

  return reproject(geometry, source_crs, target_crs)


@app.route('/vector/reproject/file', methods=["POST"])
def vector_reproject_file():
  decodedToken = decode_auth_token(request)
  if (decodedToken == False): return jsonify({'message':'Unauthorised'}), 401

  target_crs = request.form.get("targetProjection")

  allowed_projections = get_projections(decodedToken["sub"])
  if target_crs not in allowed_projections:
    return jsonify({'message':'Target coordinate CRS not allowed for this user.'}), 403

  geometry = geojson.load(request.files['file'])
  source_crs = geometry['crs']['properties']['name']

  return reproject(geometry, source_crs, target_crs)


if __name__ == '__main__':
  # Bind on all interfaces so that we can easily
  # map ports when running in a docker container
  app.run(host= '0.0.0.0', debug=True)
