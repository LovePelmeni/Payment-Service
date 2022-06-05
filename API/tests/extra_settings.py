# import os
# import databases
#
# import fastapi, pydantic
# import pytest
# from fastapi_csrf_protect import CsrfProtect
# import logging
# d
# pydantic.BaseConfig.arbitrary_types_allowed = True
# logger = logging.getLogger(__name__)
#
# APP_DEBUG = False
#
# application = fastapi.FastAPI(debug=True)
#
# if not APP_DEBUG:
#
#     TESTING = True
#
#     FRONTEND_APPLICATION_SERVICE_HOST = os.environ.get('FRONTEND_APPLICATION_SERVICE_HOST')
#     SONG_APPLICATION_SERVICE_HOST = os.environ.get('SONG_APPLICATION_SERVICE_HOST')
#     SUBSCRIPTION_SERVICE_HOST = os.environ.get('SUBSCRIPTION_SERVICE_HOST')
#
#     ALLOWED_ORIGINS = ["http://%s:3000" % FRONTEND_APPLICATION_SERVICE_HOST,
#     "http://%s:8000" % SONG_APPLICATION_SERVICE_HOST, "http://%s:8076" % SUBSCRIPTION_SERVICE_HOST]
#     ALLOWED_METHODS = ['PUT', 'POST', 'GET', 'OPTIONS', 'DELETE']
#     ALLOWED_HEADERS = ["*"]
#
#     DATABASE_NAME = os.environ.get('POSTGRES_DB')
#     DATABASE_USER = os.environ.get('POSTGRES_USER')
#     DATABASE_PORT = os.environ.get('POSTGRES_PORT')
#     DATABASE_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
#     DATABASE_HOST = os.environ.get('POSTGRES_HOST')
#
#     STRIPE_API_SECRET = os.environ.get('STRIPE_API_SECRET')
#     STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')
#
#     DATABASE_URL = 'postgresql://%s:%s@%s:%s/%s' % (DATABASE_USER, DATABASE_PASSWORD,
#     DATABASE_HOST, DATABASE_PORT, DATABASE_NAME)
#
#     TEST_DATABASE_USER = os.environ.get('TEST_DATABASE_USER')
#     TEST_DATABASE_PASSWORD = os.environ.get('TEST_DATABASE_PASSWORD')
#     TEST_DATABASE_NAME = os.environ.get('TEST_DATABASE_NAME')
#     TEST_DATABASE_HOST = os.environ.get('TEST_DATABASE_HOST')
#     TEST_DATABASE_PORT = os.environ.get('TEST_DATABASE_PORT')
#
#     TEST_DATABASE_URL = 'postgresql://%s:%s@%s:%s/%s' % (
#     TEST_DATABASE_USER, TEST_DATABASE_PASSWORD, TEST_DATABASE_HOST, TEST_DATABASE_PORT, TEST_DATABASE_NAME)
#
#     assert DATABASE_URL, TEST_DATABASE_URL
#
# else:
#     TESTING = False
#     ALLOWED_ORIGINS = ["*"]
#     ALLOWED_METHODS = ['PUT', 'POST', 'GET', 'OPTIONS', 'DELETE']
#     ALLOWED_HEADERS = ["*"]
#
#     DATABASE_HOST = 'localhost'
#     DATABASE_PORT = '5434'
#
#     STRIPE_API_KEY = 'pk_test_51KbRPhBlXqCTWmcHsFZwLrEBFIuQGGmDmXol9YMB66mSmoJM0OKsOcNQC4aPGxJ3xpRrfRMbDxF1GuFrsgUmX59Z006uU7xcuq'
#     STRIPE_API_SECRET = 'sk_test_51KbRPhBlXqCTWmcH0ByNRrTQgKwsodAmpUfReugFtuxeAtMBe4ABVab2gaNvbDzGMAsnJcG1ANcZ8PcHnNI0c4Co00eRdg7s1O'
#
#     DATABASE_URL = 'postgresql://postgres:Kirill@localhost:5434/payment_db'
#     os.environ.setdefault('DATABASE_URL', DATABASE_URL)
#
#     TEST_DATABASE_USER = 'postgres'
#     TEST_DATABASE_PASSWORD = 'Kirill'
#     TEST_DATABASE_NAME = 'test_payment_db'
#     TEST_DATABASE_HOST = 'localhost'
#     TEST_DATABASE_PORT = '5434'
#
#     TEST_DATABASE_URL = 'postgresql://%s:%s@%s:%s/%s' % (
#     TEST_DATABASE_USER, TEST_DATABASE_PASSWORD, TEST_DATABASE_HOST, TEST_DATABASE_PORT, TEST_DATABASE_NAME)
#
#     assert DATABASE_URL, TEST_DATABASE_URL
#
#
# from fastapi.middleware.cors import CORSMiddleware
#
# application.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS,
# allow_methods=ALLOWED_METHODS, allow_headers=ALLOWED_HEADERS, allow_credentials=True)
#
#
# SUCCESS_SESSION_URL = 'http://localhost:8000/healthcheck/'
# CANCEL_SESSION_URL = 'http://localhost:8081/healthcheck/'
#
# def get_database_uri() -> str:
#     if TESTING:
#         return TEST_DATABASE_URL
#     else:
#         return DATABASE_URL
#
# class BaseOrmSettings(pydantic.BaseSettings):
#
#     database_url: str = pydantic.Field(get_database_uri())
#
# orm_settings = BaseOrmSettings()
#
# database = databases.Database(url=orm_settings.database_url)
# application.state.database = database
#
# from alembic.config import Config
#
# INI_FILE_ROOT = './alembic.ini'
# alembic_cfg = Config(INI_FILE_ROOT)
# alembic_cfg.set_main_option("script_location", "migrations")
# alembic_cfg.set_main_option("sqlalchemy.url", orm_settings.database_url)
#
#
# class CSRFSettings(pydantic.BaseModel):
#     secret_key: str = 'payment_secret_key'
#
# @CsrfProtect.load_config
# def get_csrf_configuration():
#     return CSRFSettings()
#
#
#
