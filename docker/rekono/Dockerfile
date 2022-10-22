FROM python:3.9.10-alpine as backend

RUN mkdir /rekono
COPY config.yaml /rekono

RUN mkdir /code
COPY rekono/ /code
COPY requirements.txt /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && apk add curl postgresql-dev gcc python3-dev musl-dev libmagic --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community

RUN pip install --upgrade pip
RUN pip install -r /code/requirements.txt

RUN adduser --disabled-password rekono
RUN chown -R rekono:rekono /code
RUN chown -R rekono:rekono /rekono

USER rekono
WORKDIR /code

ENV REKONO_HOME /rekono


FROM node:18.9.1-alpine as frontend

RUN mkdir /frontend
COPY --from=backend /code/frontend /frontend

RUN apk update && apk add curl

ENV NODE_OPTIONS --openssl-legacy-provider

WORKDIR /frontend
RUN npm install -g serve
RUN npm install

RUN adduser --disabled-password rekono
RUN chown -R rekono /frontend
USER rekono