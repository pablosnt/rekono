#!/bin/bash

uv run --no-dev manage.py rename_1_x_apps
uv run --no-dev manage.py migrate
uv run --no-dev manage.py remove_deprecated_steps
uv run --no-dev manage.py update_wordlists_size
uv run --no-dev manage.py update_tools_status
uv run --no-dev manage.py createsuperuser --no-input  || true
uv run --no-dev manage.py monitor
