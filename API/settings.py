import os

import databases
import fastapi, pydantic
from fastapi_csrf_protect import CsrfProtect
import logging


pydantic.BaseConfig.arbitrary_types_allowed = True

# logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


DEBUG = True

application = fastapi.FastAPI(debug=DEBUG)

if not DEBUG:

    FRONTEND_APPLICATION_SERVICE_HOST = os.environ.get('FRONTEND_APPLICATION_SERVICE_HOST')
    SONG_APPLICATION_SERVICE_HOST = os.environ.get('SONG_APPLICATION_SERVICE_HOST')
    SUBSCRIPTION_SERVICE_HOST = os.environ.get('SUBSCRIPTION_SERVICE_HOST')

    ALLOWED_ORIGINS = ["http://%s:3000" % FRONTEND_APPLICATION_SERVICE_HOST,
    "http://%s:8000" % SONG_APPLICATION_SERVICE_HOST, "http://%s:8076" % SUBSCRIPTION_SERVICE_HOST]
    ALLOWED_METHODS = ['PUT', 'POST', 'GET', 'OPTIONS', 'DELETE']
    ALLOWED_HEADERS = ["*"]

    DATABASE_PORT = os.environ.get('DATABASE_PORT')
    DATABASE_HOST = os.environ.get('DATABASE_HOST')

    STRIPE_API_SECRET = os.environ.get('STRIPE_API_SECRET')
    STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')

    DATABASE_URL = os.environ.get('DATABASE_URL')

else:

    ALLOWED_ORIGINS = ["*"]
    ALLOWED_METHODS = ['PUT', 'POST', 'GET', 'OPTIONS', 'DELETE']
    ALLOWED_HEADERS = ["*"]

    DATABASE_HOST = 'localhost'
    DATABASE_PORT = '5434'

    STRIPE_API_SECRET = 'sk_test_51KbRPhBlXqCTWmcH0ByNRrTQgKwsodAmpUfReugFtuxeAtMBe4ABVab2gaNvbDzGMAsnJcG1ANcZ8PcHnNI0c4Co00eRdg7s1O'
    STRIPE_API_KEY = 'pk_test_51KbRPhBlXqCTWmcHsFZwLrEBFIuQGGmDmXol9YMB66mSmoJM0OKsOcNQC4aPGxJ3xpRrfRMbDxF1GuFrsgUmX59Z006uU7xcuq'
    DATABASE_URL = 'postgresql://postgres:Kirill@localhost:5434/payment_db'
    os.environ.setdefault('DATABASE_URL', DATABASE_URL)

from fastapi.middleware.cors import CORSMiddleware

application.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS,
allow_methods=ALLOWED_METHODS, allow_headers=ALLOWED_HEADERS, allow_credentials=True)

database = databases.Database(url=DATABASE_URL)
application.state.database = database

SUCCESS_SESSION_URL = 'http://localhost:8000/healthcheck/'
CANCEL_SESSION_URL = 'http://localhost:8081/healthcheck/'

class CSRFSettings(pydantic.BaseModel):
    secret_key: str = 'payment_secret_key'

@CsrfProtect.load_config
def get_csrf_configuration():
    return CSRFSettings()

class BaseOrmSettings(pydantic.BaseSettings):

    database_url: str = pydantic.Field(env='DATABASE_URL')

orm_settings = BaseOrmSettings()




