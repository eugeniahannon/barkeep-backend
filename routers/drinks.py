# 1. __future__ imports
# we have none in this case

# 2. stdlib imports
from typing import List, Optional

# 3. third-party imports
from bson import ObjectId
from fastapi import APIRouter, Depends
from pydantic import BaseModel

# 4. internal imports
from mongo import get_barkeep_coll
from roles import UserHasAccessToLevel, RoleLevel


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


router = APIRouter()


# @app is a FastAPI Decorator that associates a path
# with the function defined immediately after it
###
# Define the /drinks GET API endpoint functionality
@router.get('/')
async def get_drinks(
    limit: int = 0,
    authorized: bool = Depends(UserHasAccessToLevel(RoleLevel.EDITOR))
):
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
@router.get('/{id}')
async def get_drink(
    id: str,
    authorized: bool = Depends(UserHasAccessToLevel(RoleLevel.EDITOR))
):
    # get a pymongo Collection object in order work with the db
    coll = get_barkeep_coll('drinks')
    # find a cocktail from the database that matches a given _id
    drink = coll.find_one({'_id': ObjectId(id)})
    # delete the _id k/v pair from the drink dict
    # because ObjectId is not serializable
    del drink['_id']
    # send the drink dict back to the client
    return drink


# Define the /drink POST API endpoint functionality
@router.post('/')
async def insert_drink(
    drink: Drink,
    access: bool = Depends(UserHasAccessToLevel(RoleLevel.EDITOR))
):
    # get a pymongo Collection object in order work with the db
    coll = get_barkeep_coll('drinks_test')
    # check if a drink with this name already exists
    if coll.find({'name': drink.dict()['name']}):
        return {
            'err': 'Please choose a different name. '
            f'A drink called {drink.dict()["name"]} already exists.'
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
@router.patch('/')
async def modify_drink(
    drink: Drink,
    access: bool = Depends(UserHasAccessToLevel(RoleLevel.EDITOR))
):
    # get a pymongo Collection object in order work with the db
    coll = get_barkeep_coll('drinks_test')
    # find a doc in the collection with the same _id as
    # the supplied drink and replace
    db_res = coll.find_one_and_replace(
        # find the matching drink in the db
        {'_id': ObjectId(drink.dict()['id'])},
        # replace the matching db doc with the drink dict supplied
        drink.dict()
    )
    # delete the _id k/v pair from the drink dict because
    # ObjectId is not serializable
    del db_res['_id']
    # send the pre-modification drink (if it was modified) back to the client
    return db_res


# Define the /drink DELETE API endpoint functionality
@router.delete('/{id}')
async def mark_drink_deleted(
    id: str,
    access: bool = Depends(UserHasAccessToLevel(RoleLevel.ADMIN))
):
    # get a pymongo Collection object in order work with the db
    coll = get_barkeep_coll('drinks_test')
    # update the doc in the collection with the id supplied
    db_res = coll.update_one(
            {'_id': ObjectId(id)},
            {'$set': {'is_deleted': True}}
    )
    return {
        'matched_count': db_res.matched_count,
        'modified_count': db_res.modified_count
    }


# Defined the /search POST API endpoint for searching on cocktail name
# TODO: make this more flexible so that the filters can be more granular
@router.post('/search')
async def search_for_drink(
    drink: Drink,
    access: bool = Depends(UserHasAccessToLevel(RoleLevel.EDITOR))
):
    # extract the cocktail name from the supplied drink
    cocktail_name = drink.dict()['name']
    # get a pymongo Collection object in order work with the db
    coll = get_barkeep_coll('drinks')
    # create an empty list to hold the cursor results
    matching_drinks = []
    # define the aggregation pipeline
    pipeline = [{
                    '$search': {
                      'text': {
                          'query': cocktail_name,
                          'path': 'name'
                      }
                    }
                },
                {
                    '$project': {
                        '_id': 0,
                        'name': 1,
                        'ingredients': 1,
                        'detritus': 1,
                        'method': 1,
                        'history': 1,
                        'glassware': 1,
                        'ice': 1,
                        'garnish': 1,
                        'id': {
                            '$toString': '$_id'
                        },
                        'score': {
                            '$meta': 'searchScore'
                        }
                    }
               }]
    # execute the aggregation and assign the resulting cursor to db_res
    db_res = coll.aggregate(pipeline)
    # iterate through the cursor object
    for drink in db_res:
        # append each drink to the matching_drinks list
        matching_drinks.append(drink)
    return matching_drinks
