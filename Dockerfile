FROM python:3.8

WORKDIR /usr/src/app
COPY docker-prep.sh ./

EXPOSE 5552

CMD ["docker-prep.sh"]
CMD ["./manage.py", "makemigrations"]
CMD ["./manage.py", "migrate"]
CMD ["./manage.py", "test"]
CMD ["./manage.py","runserver","5552"]