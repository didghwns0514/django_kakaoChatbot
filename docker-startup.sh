pip list
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic --noinput
#python3 manage.py collectstatic

#python3 gunicorn StockManager.wsgi --bind=0:5552