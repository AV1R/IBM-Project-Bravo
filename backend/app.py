from flask import Flask, render_template, request, url_for, redirect
from flask import jsonify,make_response
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from bson import ObjectId

load_dotenv() # load environment variables from .env file
mongo_connection_string = os.getenv('MONGO_CONNECTION_STRING')

app = Flask(__name__)

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
            # Registra al nuevo usuario en la base de datos
            users.insert_one({'email': email, 'password': password})
            return render_template('index.html', success="Registrado exitosamente")
        else:
            return render_template('index.html', error="Las contraseñas no coinciden")
    return render_template('index.html')
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

if __name__ == '__main__':
    app.run(debug=True)
