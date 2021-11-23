FROM python:3.8

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install django-cors-headers

COPY . .

EXPOSE 5552

CMD ["./manage.py","runserver","5552"]