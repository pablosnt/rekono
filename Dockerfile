FROM python:3.9.6-alpine as backend

RUN mkdir rekono/
COPY rekono/ rekono/

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev libmagic --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /rekono
RUN python manage.py frontend


FROM node:17.6.0-alpine as frontend

RUN mkdir frontend/
WORKDIR /frontend
COPY --from=backend /rekono/frontend .

ENV NODE_OPTIONS --openssl-legacy-provider

RUN npm install -g serve
RUN npm install
RUN npm run build
