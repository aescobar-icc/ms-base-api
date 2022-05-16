from mongoengine import connect,disconnect
from mongoengine.connection import get_connection
from pymongo import MongoClient
from lib.db.mongo.connection import MongoConnection
import os
#init mongo connection
uri="mongodb+srv://unit_test:Tks12345@cluster0.iz5q7.mongodb.net/test"
os.environ.setdefault("MONGODB_URI",uri)

MongoConnection.connect(None)
mongoClient = MongoClient(uri,maxPoolSize=1)
mongoClient.drop_database('test')