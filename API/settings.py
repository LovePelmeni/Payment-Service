import os
import fastapi, pydantic
from fastapi_csrf_protect import CsrfProtect
from . import routers


pydantic.BaseConfig.arbitrary_types_allowed = True

DEBUG = True

if not DEBUG:
    SUBSCRIPTION_SERVICE_HOST = 'localhost'
    DATABASE_URL = os.environ.get('DATABASE_URL')

else:
    SUBSCRIPTION_SERVICE_HOST = os.environ.get('SUBSCRIPTION_SERVICE_HOST')
    DATABASE_URL = 'postgresql://postgres:Kirill@localhost:5434/payment_db'
    os.environ.setdefault('DATABASE_URL', DATABASE_URL)

application = fastapi.FastAPI()
application.include_router(router=routers.payment_router, prefix='/payment')

application.include_router(router=routers.refund_router, prefix='/refund')
application.include_router(router=routers.customer_router, prefix='/customer')

application.include_router(router=routers.webhook_router, prefix='/webhook')
application.include_router(router=routers.healthcheck_router, prefix='/healthcheck')


class CSRFSettings(pydantic.BaseModel):
    secret_key: str = 'payment_secret_key'

@CsrfProtect.load_config
def get_csrf_configuration():
    return CSRFSettings()

class BaseOrmSettings(pydantic.BaseSettings):

    database_url: str = pydantic.Field(env='DATABASE_URL')

orm_settings = BaseOrmSettings()
