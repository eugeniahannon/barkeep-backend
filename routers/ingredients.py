from fastapi import APIRouter
from mongo import get_barkeep_coll

router = APIRouter()


# Define the /ingredients GET API endpoint to get all distinct ingredient names
@router.get('/ingredients')
async def get_distinct_ingredients(access: bool = Depends(UserHasAccessToLevel(RoleLevel.EDITOR))):
    # get a pymongo Collection object in order work with the db
    coll = get_barkeep_coll('drinks')
    # get a list of all distinct ingredient names
    db_res = coll.distinct('ingredients.ingredient')
    # remove the first element of the list
    # (which for some reason is always None)
    db_res.pop(0)
    return db_res
