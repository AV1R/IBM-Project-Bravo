from flask import Flask, render_template, request, url_for, redirect
from flask import jsonify, make_response
from pymongo import MongoClient
from dotenv import load_dotenv
import bcrypt
import os
import jwt
from functools import wraps
from datetime import datetime, timedelta
import json

load_dotenv()  # load environment variables from .env file
mongo_connection_string = os.getenv("MONGO_CONNECTION_STRING")

app = Flask(__name__)
key = "max"
app.config["SECRET_KEY"] = "max"

# Local database with mongo
client = MongoClient("localhost", 27017)
# Example
# database name= flask_db
db = client.flask_db
# .todos is a collection from db
todos = db.todos
# end


# Cloud database with mongo
client2 = MongoClient(mongo_connection_string)
db2 = client2["ibm-app"]
# Get dashboard collection
dash = db2.certificates
# Get users collection
users = db2.users
# end


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get("token")
        if not token:
            return jsonify({"message": "Token is missing!"}), 401
        try:
            data = jwt.decode(token, app.config["SECRET_KEY"])
        except:
            return jsonify({"message": "Token is invalid!"}), 401

        return f(*args, **kwargs)

    return decorated


@app.route("/register", methods=["POST"])
def register():
    new_user = request.get_json()  # store the json body request
    # Checking if user already exists
    existinguser = users.find_one({"email": new_user["email"]})  # check if user exist
    # If not exists than create one
    if existinguser:
        return jsonify({"msg": "Email already exists"}), 409
    elif new_user["password"] == new_user["password1"]:
        # Creating user
        hashed_password = bcrypt.hashpw(
            new_user["password"].encode("utf-8"), bcrypt.gensalt()
        )
        # Decode hashed password to UTF-8
        hashed_password = hashed_password.decode("utf-8")
        # Registra al nuevo usuario en la base de datos
        users.insert_one(
            {
                "email": new_user["email"],
                "password": hashed_password,
                "first_name": new_user["first_name"],
                "second_name": new_user["second_name"],
            }
        )
        existinguser = users.find_one({"email": new_user["email"]})
        user_id = str(existinguser["_id"])
        token = jwt.encode(
            {
                "id": user_id,
                "email": new_user["email"],
                "first_name": new_user["first_name"],
                "second_name": new_user["second_name"],
                "exp": datetime.utcnow() + timedelta(minutes=60),
            },
            app.config["SECRET_KEY"],
        )

        response = {
            "token": token.decode("utf-8"),
            "msg": "User created successfully",
        }  # Assuming `token` is the bytes object
        return json.dumps(response), 200, {"Content-Type": "application/json"}
        # users.insert_one(new_user)
        # return jsonify({"msg": "User created successfully"}), 201
    else:
        return jsonify({"msg": "Server error"}), 500


@app.route("/login", methods=["POST"])
def login():
    reqUser = request.get_json()
    email = reqUser["email"]
    password = reqUser["password"]
    # Find user in the database by email
    existingUser = users.find_one({"email": email})
    if existingUser:
        # Check if password is correct
        if bcrypt.checkpw(
            password.encode("utf-8"), existingUser["password"].encode("utf-8")
        ):
            # Password is correct, generate JWT token
            user_id = str(existingUser["_id"])
            token = jwt.encode(
                {
                    "id": user_id,
                    "email": existingUser["email"],
                    "first_name": existingUser["first_name"],
                    "second_name": existingUser["second_name"],
                    "exp": datetime.utcnow() + timedelta(minutes=60),
                },
                app.config["SECRET_KEY"],
            )
            response = {
                "token": token.decode("utf-8")
            }  # Assuming `token` is the bytes object
            return json.dumps(response), 200, {"Content-Type": "application/json"}

            # return jsonify({"token": token})
        else:
            # Password is incorrect, return error message
            return jsonify({"msg": "Incorrect password"}), 409
    else:
        # User not found in the database, return error message
        return jsonify({"msg": "User doesn´t exists"}), 400


# endpoint for frontend
@app.route("/dash")
def dashboardApi():
    reqUser = request.get_json()
    userEmail = reqUser["email"]
    try:
        data = list(
            dash.find({"owner": userEmail})
        )  # retrieve all objects and convert to a list
        # convert ObjectId instances to strings
        if not data:
            return jsonify({"error": "No certificates found"}), 404

        for item in data:
            item["_id"] = str(item["_id"])
        # convert data list to JSON string
        data = {"dashboard": data}
        obj = jsonify(data)  # convert data list to JSON string
        response = make_response(obj)
        response.headers["Content-Type"] = "application/json"
        response.headers["X-My-Header"] = "My custom header value"
        response.status_code = 200
        return response
    except Exception:
        data = {"status": "error"}
        response = make_response(obj)
        response.headers["Content-Type"] = "application/json"
        response.status_code = 500
        return response


# endpoint for frontend
# @app.route("/users")
# def usersApi():
#     data = list(users.find())  # retrieve all objects and convert to a list
#     # convert ObjectId instances to strings
#     for item in data:
#         item["_id"] = str(item["_id"])
#     # convert data list to JSON string
#     obj = jsonify(data)  # convert data list to JSON string
#     response = make_response(obj)
#     response.headers["Content-Type"] = "application/json"
#     response.headers["X-My-Header"] = "My custom header value"
#     response.status_code = 200
#     return response
