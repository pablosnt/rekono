# Project: Rekono

## Overview

Offensive security platform that automates attack surface discovery and vulnerability management

### Tech Stack

- Python
- Django
- Django Rest Framework
- Vue.js
- Nuxt
- Nuxt UI

## Architecture

- `/backend/`: Rekono backend
- `/docker/`: Rekono Docker images
- `/frontend/`: Rekono UI

## Code Style

- `uvx ruff format`: Format the backend code with the `ruff` formatter
- `uvx ruff check --fix`: Fix `ruff` style issues
- `uvx ruff check --select I --fix`: Fix `ruff` style issues on imports. Requires to be executed independently of the previous one
- `uvx flake8 .`: Runs Flake8 linter to detect code style issues
- `uvx pytype --disable "import-error,pyi-error,invalid-annotation" --keep-going --jobs 100 .`: Runs PyType to identify Python typing issues. Don't execute this on local as its execution takes long time, and we run it on CI/CD too
- `pnpm run prettier:fix`: Format the frontend code with the `prettier` formatter
- `pnpm run eslint:fix`: Runs ESLint linter with `fix` option to fix the issues that are automatically fixable

### Commands

- `uv run manage.py makemigrations`: Generate migrations for the latest model changes
- `uv run manage.py migrate`: Apply migrations on the database
- `uv run manage.py createsuperuser`: Creates a new Rekono user with Admin access
- `uv run manage.py runserver`: Deploys the Rekono backend
- `uv run manage.py rqworker tasks`: Deploys the worker for the tasks queue
- `uv run manage.py rqworker executions`: Deploys the worker for the executions queue
- `uv run manage.py rqworker findings`: Deploys the worker for the findings queue
- `uv run manage.py rqworker monitor`: Deploys the worker for the monitor queue
- `uv run manage.py telegram_bot`: Deploys the Rekono Telegram bot
- `pnpm run dev`: Deploys the Rekono frontend

### Important Notes

- Don't duplicate code, always reuse existing code if possible
- Rekono is a cybersecurity project, don't introduce vulnerabilities in the code
- Don't add comments to frontend code, as they would expose information to the users
- Always use NuxtUI components in the frontend, don't write native HTML or CSS code if it's not needed
- Reuse the @frontend/components/crud components to create new frontend pages, unlest it's not possible
