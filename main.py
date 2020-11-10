#
# Import Ordering Template
#

# 1. __future__ imports
# we have none in this case

# 2. stdlib imports

# 3. third-party imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

# 4. internal imports
from config import CORS_ALLOWED_ORIGINS, SESSION_SECRET_KEY
from routers import auth, drinks, ingredients, ping


# Instantiate a FastApi as app
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=str(SESSION_SECRET_KEY))
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(CORS_ALLOWED_ORIGINS),
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(
    drinks.router,
    prefix='/drinks',
    tags=['drinks']
)


app.include_router(
    ingredients.router,
    prefix='/ingredients',
    tags=['ingredients']
)

app.include_router(
    ping.router
)


app.include_router(auth.router)

# TODO: introduce user authN/authZ to protect non-read endpoints - oauth2

# NICE_TO_HAVE: image upload to Google Cloud Storage
