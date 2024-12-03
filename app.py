#imports
from functools import wraps
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
from datetime import timedelta

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import get_jwt
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_jwt_extended import verify_jwt_in_request

import boto3
import os

#Cargando .env
load_dotenv()

# Seteando s3 cliente
s3_client = boto3.client(
    service_name='s3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)
bucket_name = os.getenv("AWS_BUCKET_NAME")

#App
app = Flask(__name__)

# Seteando jwt-extended
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1) # Seteo la expiracion del token a 1 hora
jwt = JWTManager(app)

# Funcion que verifica si es admin
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims["is_administrator"]:
                return fn(*args, **kwargs)
            else:
                return jsonify(msg="Admins only!"), 403
        return decorator
    return wrapper


# RUTAS
#Ruta inicial donde logearse
@app.route("/", methods=["GET"])
def home():
    #Login
    return jsonify({"message":"SIRIUS CHALLENGE, please introduce your user and password"})

@app.route("/", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if username == "admin" and password == "admin":
        access_token = create_access_token(
        "admin_user", additional_claims={"is_administrator": True})
        return jsonify(access_token=access_token),200
    
    if username != "usuario1" or password != "1234":
        return jsonify({"message": "Bad username or password"}), 401
    access_token = create_access_token(identity=username, additional_claims={"is_administrator": False})
    return jsonify(access_token=access_token),200

# Ruta con los archivos subidos
@app.route("/access_granted", methods=["GET"])
@jwt_required()
def list_files():
    current_user = get_jwt_identity()
    response = s3_client.list_objects_v2(Bucket=bucket_name,Prefix=current_user)

    objects_list = []
    if 'Contents' in response:
        for key in response['Contents']:
            objects_list.append({
                    "FileName": key['Key'],
                    "LastModified": key['LastModified'].isoformat(),
                    "FileSize": key['Size']
                })
        return jsonify (objects_list), 200
    else:
        return jsonify({"message": "There is no files"}), 204

# Ruta para subir archivos
@app.route("/access_granted", methods=["POST"])
@jwt_required()
def add_file():
    current_user = get_jwt_identity()
    try:
        file = request.files["mock_file"]
        name_for_s3 = secure_filename(file.filename)
        key_bucket = os.path.join(f"{current_user}/",name_for_s3)
        s3_client.upload_fileobj(file,bucket_name, key_bucket)

    except Exception:
        return jsonify({"error":"There was a problem with the file"}), 400 # Comprende que no se elegio archivo
    except NoCredentialsError: # El rol en amazon S3 no tiene los permisos necesarios
        return jsonify({"error": "S3 credentials not available"}), 500
    return jsonify({"message":"File uploaded"}), 201

# Ruta para descargar en base al nombre
@app.route("/access_granted/<string:file_name>", methods=["GET"])
@jwt_required()
def download_file(file_name):
    current_user = get_jwt_identity()
    download_path = os.path.join("downloads/", file_name)
    key_bucket = os.path.join(f"{current_user}/",file_name)
    
    try:
        s3_client.download_file(bucket_name, key_bucket, download_path)
    except NoCredentialsError:
        return jsonify({"error": " S3 credentials not available"}), 500 # El rol en amazon S3 no tiene los permisos necesarios
    return jsonify({"message":f"File {file_name} downloaded"}),200


@app.route("/stats")
@admin_required()
def stats():
    return jsonify({"message": "All the users who upload something today"}),200

# Ruta para eliminar en base al nombre
@app.route("/access_granted/<string:file_name>", methods=["DELETE"])
def delete_file(file_name):
    return jsonify({"message":"File deleted"}),204

if __name__ == "__main__":
    app.run(debug=True)