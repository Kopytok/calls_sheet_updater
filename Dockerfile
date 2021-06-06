FROM python:3.8-slim

ENV FLASK_APP=app_file.py

MAINTAINER Alexander Gorodinski gorodinski.a@pm.by

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

ENTRYPOINT [ "flask", "run", "--host=0.0.0.0" ]