FROM python:3.12.2-slim

WORKDIR /service

COPY ./requirements.txt /service/requirements.txt
RUN pip install --default-timeout=500 --no-cache-dir --upgrade -r requirements.txt

COPY ./app /service/app
