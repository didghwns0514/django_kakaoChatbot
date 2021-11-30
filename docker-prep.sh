pip install --upgrade pip
pip install -r requirements.txt
pip install django-cors-headers
pip install mysqlclient
pip install gunicorn

python3 manage.py collectstatic --noinput
python3 manage.py makemigrations
python3 manage.py migrate