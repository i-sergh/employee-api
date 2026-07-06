from dotenv import load_dotenv 
import os

load_dotenv( override=True)

IMG_DEFAULT = os.environ.get('IMG_DEFAULT')
IMG_DEFAULT_MINI = os.environ.get('IMG_DEFAULT_MINI')
IMG_UPLOAD_DIR = os.environ.get('IMG_UPLOAD_DIR')
STATIC_DIR=os.environ.get('STATIC_DIR')


PG_USER = os.environ.get('PG_USER')
PG_PASS = os.environ.get('PG_PASS')
PG_HOST = os.environ.get('PG_HOST')
PG_PORT = os.environ.get('PG_PORT')
PG_NAME = os.environ.get('PG_NAME')
PG_TEST_NAME = os.environ.get('PG_TEST_NAME')


def get_pg_async_link(test=False):
    if test:
        return f'postgresql+asyncpg://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_TEST_NAME}'
    return f'postgresql+asyncpg://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_NAME}'


def get_pg_alembic_link(test=False):
    if test:
        return f'postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_TEST_NAME}'
    return f'postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_NAME}'