import os

DJANGO_SECRET = None
DB_USERNAME = None
DB_PASSWORD = None
DEBUG = None
IS_MAIN_SERVER = None

try:DJANGO_SECRET = os.environ(['DJANGO_SECRET'])
except:DJANGO_SECRET = os.environ.get('DJANGO_SECRET')

try:DB_USERNAME = os.environ(['DB_USERNAME'])
except:DB_USERNAME = os.environ.get('DB_USERNAME')

try:DB_PASSWORD = os.environ(['DB_PASSWORD'])
except:DB_PASSWORD = os.environ.get('DB_PASSWORD')

try:DEBUG = bool(int(os.environ(['DEBUG'])))
except:DEBUG = bool(int(os.environ.get('DEBUG')))

try:IS_MAIN_SERVER = bool(int(os.environ(['IS_MAIN_SERVER'])))
except:IS_MAIN_SERVER = bool(int(os.environ.get('IS_MAIN_SERVER')))

print(f'DEBUG : {DEBUG}')
print(f'IS_MAIN_SERVER : {IS_MAIN_SERVER}')
