FROM python:3.9

WORKDIR /usr/src/app
COPY docker-prep.sh ./
COPY . .


RUN docker-prep.sh
#    "./manage.py", "makemigrations" \
#    "./manage.py", "migrate" \
#    "./manage.py", "test"

EXPOSE 5552

#CMD ["./manage.py","runserver","5552"]
CMD ["gunicorn","django_kakaoChatbot.config.wsgi","--bind=0:5552"]
