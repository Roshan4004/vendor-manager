FROM python:3.10-alpine

ENV PYTHONBUFFERVALUE = 1

RUN apk update
RUN apk add gcc
RUN apk add python3-dev
RUN apk add musl-dev

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt