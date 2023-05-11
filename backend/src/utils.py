from pymongo import MongoClient
client = pymongo.MongoClient('mongodb+srv://max:bravo@cluster0.jbltvjh.mongodb.net/test')
db = client['ibm-app']

connection_string = mongodb+srv://max:bravo@cluster0.jbltvjh.mongodb.net/test