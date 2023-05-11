from flask import Flask, render_template, request, url_for, redirect
from flask import jsonify,make_response
from pymongo import MongoClient
from dotenv import load_dotenv
import bcrypt
import os
import jwt
from functools import wraps
from datetime import datetime, timedelta
import requests
from bson import ObjectId

load_dotenv() # load environment variables from .env file
mongo_connection_string = os.getenv('MONGO_CONNECTION_STRING')

app = Flask(__name__)
key = 'max'
app.config['SECRET_KEY'] = 'max'

#Local database with mongo
client = MongoClient('localhost', 27017)
#Example
#database name= flask_db
db = client.flask_db
#.todos is a collection from db
todos = db.todos
#end 


#Cloud database with mongo
client2 = MongoClient(mongo_connection_string)
db2 = client2["ibm-app"]
#Get dashboard collection
dash = db2.dashboard
#Get users collection
users = db2.users
#end

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f( *args, **kwargs)
    
    return decorated

@app.route('/')
def home():
    return redirect(url_for('userSignUpApi'))
    
#GET AND POST EXAMPLE WITH MONGO ATLAS DATABASE
@app.route('/signup', methods=('GET','POST'))
def userSignUpApi():
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']
        password1 = request.form['password1']

        # Busca si el usuario ya existe en la base de datos
        existing_user = users.find_one({'email': email})

        if existing_user:
            return render_template('index.html', error="El usuario ya existe en la base de datos")
        elif password == password1:
            # Hacemos un hash con la contraseña
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            # Decode hashed password to UTF-8
            hashed_password = hashed_password.decode('utf-8')
            # Registra al nuevo usuario en la base de datos
            users.insert_one({'email': email, 'password': hashed_password})
            return render_template('index.html', success="Registrado exitosamente")
        else:
            return render_template('index.html', error="Las contraseñas no coinciden")
    return render_template('index.html')


@app.route('/login', methods=('GET','POST'))
def userLoginApi():
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']

        # Find user in the database by email
        user = users.find_one({'email': email})

        if user:
            # Check if password is correct
            if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                # Password is correct, generate JWT token
                token = jwt.encode({'email': email, 'exp': datetime.utcnow() + timedelta(minutes=15)}, app.config['SECRET_KEY'])
                return jsonify({'token': token})
            else:
                # Password is incorrect, return error message
                return render_template('loginTest.html', error="La contrasena es incorrecta")
        else:
            # User not found in the database, return error message
            return render_template('loginTest.html', error=" El usuario no existe")

    return render_template('loginTest.html')

#endpoint for frontend
@app.route('/dash-api')
def dashboardApi():
    data = list(dash.find())  # retrieve all objects and convert to a list
    # convert ObjectId instances to strings
    for item in data:
        item['_id'] = str(item['_id'])
    # convert data list to JSON string
    data={"dashboard": data}
    obj = jsonify(data) # convert data list to JSON string
    response = make_response(obj)
    response.headers['Content-Type'] = 'application/json'
    response.headers['X-My-Header'] = 'My custom header value'
    response.status_code = 200
    return response


#endpoint for frontend
@app.route('/users')
def usersApi():
    data = list(users.find())  # retrieve all objects and convert to a list
    # convert ObjectId instances to strings
    for item in data:
        item['_id'] = str(item['_id'])
    # convert data list to JSON string
    obj = jsonify(data) # convert data list to JSON string
    response = make_response(obj)
    response.headers['Content-Type'] = 'application/json'
    response.headers['X-My-Header'] = 'My custom header value'
    response.status_code = 200
    return response

@app.route('/protected')
@token_required
def protected():
    return jsonify({'message': 'This is only valid to people with tokens'})

@app.route('/unprotected')
def unprotected():
    return jsonify({'message': 'Everyone can see this'})