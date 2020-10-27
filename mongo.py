from t import MONGO_URI
from pymongo import MongoClient


def make_mongo_client():
    client = MongoClient(MONGO_URI)
    return client
