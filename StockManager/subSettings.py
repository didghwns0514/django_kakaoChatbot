import os

DJANGO_SECRET = None
DB_USERNAME = None
DB_PASSWORD = None

try:DJANGO_SECRET = os.environ(['DJANGO_SECRET'])
except:DJANGO_SECRET = os.environ.get('DJANGO_SECRET')


try:DB_USERNAME = os.environ(['DB_USERNAME'])
except:DB_USERNAME = os.environ.get('DB_USERNAME')

try:DB_PASSWORD = os.environ(['DB_PASSWORD'])
except:DB_PASSWORD = os.environ.get('DB_PASSWORD')

