from fastapi import FastAPI
from mongo import make_mongo_client

# Instantiate a FastApi as app
app = FastAPI()


# FastAPI Decorator that associates a path
# with the function defined immediately after it
@app.get('/drinks')
async def get_drinks():
    # get a MongoClient object in order work with the db
    client = make_mongo_client()
    # access the barkeep database
    db = client.barkeep
    # access the drinks collection within the barkeep db
    coll = db.drinks
    # create list to hold our query results
    drinks = []
    # iterate through the cursor that is the results of:
    #   - find 10 documents
    #   - with no query filter
    #   - omit the `_id` field in the results
    for drink in coll.find({}, {'_id': 0}).limit(10):
        # add each drink to the drinks list
        drinks.append(drink)
    # return a dict with a single key 'drinks'
    # and the drinks list as its value
    return {'drinks': drinks}
