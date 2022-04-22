FROM python:3.8-slim-buster

COPY . /app
WORKDIR /app

RUN pip3 install sqlalchemy==1.4.35
RUN pip3 install psycopg2-binary==2.9.1

CMD python3 create_tables.py
