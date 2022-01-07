FROM python:3.8.10-alpine

WORKDIR /usr/src/app
COPY docker-prep.sh .
COPY docker-startup.sh .
COPY . .

ARG DJANGO_SECRET
ARG DB_USERNAME
ARG DB_PASSWORD

RUN chmod +x ./docker-prep.sh
RUN chmod +x ./docker-startup.sh
RUN ./docker-prep.sh
#    "./manage.py", "makemigrations" \
#    "./manage.py", "migrate" \
#    "./manage.py", "test"

EXPOSE 5552

#ENTRYPOINT ["./docker-startup.sh"]
#CMD ["./manage.py","runserver","5552"]
#CMD ["gunicorn","StockManager.wsgi","--bind=0:8080"]
#ENTRYPOINT ["./docker-startup.sh"]
CMD ./docker-startup.sh ; gunicorn StockManager.wsgi --bind=0:5552 --threads=4