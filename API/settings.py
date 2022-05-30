import os
import fastapi, pydantic
from fastapi_csrf_protect import CsrfProtect

DEBUG = True

if not DEBUG:
    DATABASE_URL = os.environ.get('DATABASE_URL')

else:
    DATABASE_URL = 'postgresql://postgres:Kirill@localhost:5434/payment_db'
    os.environ.setdefault('DATABASE_URL', DATABASE_URL)

application = fastapi.FastAPI()

class CSRFSettings(pydantic.BaseModel):
    secret_key: str

@CsrfProtect.load_config
def get_csrf_configuration():
    return CSRFSettings()

class BaseOrmSettings(pydantic.BaseSettings):

    database_url: str = pydantic.Field(env='DATABASE_URL')

orm_settings = BaseOrmSettings()
