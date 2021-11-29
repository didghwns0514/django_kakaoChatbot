FROM python:3.8

WORKDIR /usr/src/app
COPY docker-prep.sh ./

EXPOSE 5552

CMD ["docker-prep.sh", "./manage.py","runserver","5552"]