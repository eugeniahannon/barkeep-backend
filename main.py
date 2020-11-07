from typing import List, Optional

from bson import ObjectId
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mongo import make_mongo_client
from pydantic import BaseModel

# define an object model for what a drink is supposed to look like.
# this also specifies default values if fields are empty
# all fields are optional except for name
class Drink(BaseModel):
    name: str
    ingredients: List[dict] = []
    detritus: Optional[str] = None
    method: Optional[str] = None
    history: Optional[str] = None
    glassware: Optional[str] = None
    ice: Optional[str] = None
    garnish: Optional[str] = None
    id: Optional[str] = None


def get_barkeep_coll(coll: str):
    # get a MongoClient object in order work with the db
    client = make_mongo_client()
    # access the barkeep database
    db = client.barkeep
    # access the drinks collection within the barkeep db
    coll = db.get_collection(coll)
    return coll


# Instantiate a FastApi as app
app = FastAPI()
origins = ['http://localhost:3000', 'http://localhost']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# @app is a FastAPI Decorator that associates a path
# with the function defined immediately after it
###
# Define the /drinks GET API endpoint functionality
@app.get('/drinks')
async def get_drinks(limit: int = 0):
    # what happens when limit is provided as a query param
    if limit > 0:
        # this pipeline has a limit stage
        pipeline = [
            {'$limit': limit},
            {'$addFields': {'id': {'$toString': '$_id'}}},
            {'$project': {'_id': 0}}
        ]
    # what happens when limit is not provided
    if limit == 0:
        # this pipeline has no limit stage
        pipeline = [
            {'$addFields': {'id': {'$toString': '$_id'}}},
            {'$project': {'_id': 0}}
        ]
    # get a pymongo Collection object in order work with the db
    coll = get_barkeep_coll('drinks')
    # create list to hold our query results
    drinks = []
    # iterate through the cursor that is the results of:
    #   - find 10 documents
    #   - with no query filter
    #   - cast the `_id` field to a string in the results
    for drink in coll.aggregate(pipeline):
        # add each drink to the drinks list
        drinks.append(drink)
    # return a dict with a single key 'drinks'
    # and the drinks list as its value
    return {'drinks': drinks}


# Define the /drink GET API endpoint functionality
@app.get('/drink/{id}')
async def get_drink(id: str):
    # get a pymongo Collection object in order work with the db
    coll = get_barkeep_coll('drinks')
    # find a cocktail from the database that matches a given _id
    drink = coll.find_one({'_id': ObjectId(id)})
    # delete the _id k/v pair from the drink dict because ObjectId is not serializable
    del drink['_id']
    # send the drink dict back to the client
    return drink


# Define the /drink POST API endpoint functionality
@app.post('/drink')
async def insert_drink(drink: Drink):
    # get a pymongo Collection object in order work with the db
    coll = get_barkeep_coll('drinks_test')
    # check if a drink with this name already exists
    if coll.find({'name': drink.dict()['name']}):
        return {
            'err': f'Please choose a different name. A drink called {drink.dict()["name"]} already exists.'
        }
    # insert the drink into the collection
    db_res = coll.insert_one(drink.dict())
    # return to the client the acknowledged bool (i.e. did it work?)
    # and the stringified ObjectID of the inserted doc if a doc was inserted
    return {
        'acknowledged': db_res.acknowledged,
        'inserted_id': str(db_res.inserted_id)
    }


# Define the /drink PATCH API endpoint functionality
@app.patch('/drink')
async def modify_drink(drink: Drink):
    # get a pymongo Collection object in order work with the db
    coll = get_barkeep_coll('drinks_test')
    # find a doc in the collection with the same _id as the supplied drink and replace
    db_res = coll.find_one_and_replace(
        # find the matching drink in the db
        {'_id': ObjectId(drink.dict()['id'])},
        # replace the matching db doc with the drink dict supplied
        drink.dict()
    )
    # delete the _id k/v pair from the drink dict because ObjectId is not serializable
    del db_res['_id']
    # send the pre-modification drink (if it was modified) back to the client
    return db_res
