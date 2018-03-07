import os

APP_NAME = 'test'
DEBUG = False
LOGGING_LEVEL = 'ERROR'

API_HOST = '0.0.0.0'
API_PORT = 9001

SRC_DIR = os.path.abspath(os.getcwd())
LOG_DIR = os.path.abspath(os.path.join(SRC_DIR, '../logs'))

MODELS_PATTERN = '**/models.py'

DATABASE = {
    'host': 'localhost',
    'port': 5432,
    'database': 'test',
    'user': 'test',
    'password': 'test',
    'minsize': 1,
    'maxsize': 10
}

LOGGERS = {}
