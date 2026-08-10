#!/bin/bash

uv run --no-dev manage.py rename_1_x_apps
uv run --no-dev manage.py migrate
uv run --no-dev manage.py createsuperuser --no-input  || true
uv run --no-dev manage.py monitor