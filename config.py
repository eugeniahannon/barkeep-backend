from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret, URL

config = Config('.env')
CONFIG = config
MONGO_URI = config('MONGO_URI', cast=URL)
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET', cast=Secret)
OPENID_CONFIG_URL = 'https://accounts.google.com/.well-known/openid-configuration'
SESSION_SECRET_KEY = config('SESSION_SECRET_KEY', cast=Secret)
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    cast=CommaSeparatedStrings
)
