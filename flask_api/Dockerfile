FROM python:3.6-alpine

MAINTAINER "Bruno Trindade" <bruuno.trindade@gmail.com>

WORKDIR /usr/src/app

RUN apk --update add build-base mysql-dev

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

RUN pip install --upgrade pip
COPY ../requirements.txt .
RUN pip install -r requirements.txt

ENTRYPOINT flask run --host=0.0.0.0