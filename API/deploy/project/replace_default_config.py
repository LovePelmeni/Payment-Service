import os

try:
    from API.migrations import env
    from API import alembic
    from API.models import BaseMetaData
    from configparser import SafeConfigParser

except(ImportError):
    raise NotImplementedError


DATABASE_HOST = os.environ['POSTGRES_HOST']
DATABASE_USER = os.environ['POSTGRES_USER']
DATABASE_PASSWORD = os.environ['POSTGRES_PASSWORD']
DATABASE_PORT = os.environ['POSTGRES_PORT']
DATABASE_NAME = os.environ['POSTGRES_DB']


parser = SafeConfigParser()
DATABASE_URL = 'postgresql://%s:%s@%s:%s/%s' % (DATABASE_USER, DATABASE_PASSWORD,
DATABASE_HOST, DATABASE_PORT, DATABASE_NAME)


def replace_default_config() -> None:
    env.target_metadata = BaseMetaData.metadata
    parser.set('ALEMBIC', 'sqlalchemy.url', DATABASE_URL)

replace_default_config()