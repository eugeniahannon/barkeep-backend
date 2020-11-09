from pymongo import MongoClient
from config import MONGO_URI


def make_mongo_client():
    client = MongoClient(str(MONGO_URI))
    return client


def get_barkeep_coll(coll: str):
    # get a MongoClient object in order work with the db
    client = make_mongo_client()
    # access the barkeep database
    db = client.barkeep
    # access the drinks collection within the barkeep db
    coll = db.get_collection(coll)
    return coll
