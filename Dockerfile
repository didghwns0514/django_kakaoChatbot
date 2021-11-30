FROM python:3.9

WORKDIR /usr/src/app
COPY docker-prep.sh ./

EXPOSE 5552

#RUN "docker-prep.sh" \
#    "./manage.py", "makemigrations" \
#    "./manage.py", "migrate" \
#    "./manage.py", "test"

COPY . .

CMD ["./manage.py","runserver","5552"]