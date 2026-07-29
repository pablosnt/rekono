# Project: Rekono

## Overview

Offensive security platform that automates attack surface discovery and vulnerability management

## Tech Stack

- Python
- Django
- Django Rest Framework
- Vue.js
- Nuxt
- Nuxt UI
- React

## Architecture

- `/backend/`: Rekono backend
- `/docker/`: Rekono Docker images
- `/email-templates/`: React email templates to be used by the Rekono backend
- `/frontend/`: Rekono UI

## Code Style

### Backend

- `uvx ruff format`: Format the backend code with the `ruff` formatter
- `uvx ruff==0.15.22 check --fix`: Fix `ruff` style issues
- `uvx ruff check --select I --fix`: Fix `ruff` style issues on imports. Requires to be executed independently of the previous one
- `uvx flake8 .`: Runs Flake8 linter to detect code style issues
- `uvx pytype --disable "import-error,pyi-error,invalid-annotation" --keep-going --jobs 100 .`: Runs PyType to identify Python typing issues. Don't execute this on local as its execution takes long time, and we run it on CI/CD too

### Frontend

- `pnpm run prettier:fix`: Format the frontend and email-templates code with the `prettier` formatter
- `pnpm run eslint:fix`: Runs ESLint linter with `fix` option to fix the issues that are automatically fixable in the frontend and email-templates code

## Commands

### Backend

- `uv run manage.py makemigrations`: Generate migrations for the latest model changes
- `uv run manage.py migrate`: Apply migrations on the database
- `uv run manage.py createsuperuser`: Creates a new Rekono user with Admin access
- `uv run manage.py runserver`: Deploys the Rekono backend
- `uv run manage.py rqworker tasks`: Deploys the worker for the tasks queue
- `uv run manage.py rqworker executions`: Deploys the worker for the executions queue
- `uv run manage.py rqworker findings`: Deploys the worker for the findings queue
- `uv run manage.py rqworker monitor`: Deploys the worker for the monitor queue
- `uv run manage.py telegram_bot`: Deploys the Rekono Telegram bot

### Frontend

- `pnpm run dev`: Deploys the Rekono frontend
- `pnpm run build`: In the email-templates, build the templates and place the email templates in HTML in `/backend/platforms/email/templates/` from where they will be used by the backend

## Debug

If the application is running locally from source, the following resources are useful to research and debug issues:

- `logs/rekono.log`: this file contains the logs from all the application components (except the frontend), so if the bug was found during some user or testing activity, this file will contain what actually was executed and what happened
- `uv run manage.py shell`: this command allows to run the Django shell in interactive mode, which is helpful to directly test backend features, explore data about recent activity in the database, etc. It requires to pass the local database credentials via environment variables `RKN_DB_USER` and `RKN_DB_PASSWORD`

If the application is running in the docker compose environment, logs are accesible with `docker compose logs` command.

## Important Notes

- Don't run `git add`, `git commit` or `git push`, only work in the local git repository and I will review and test any change manually before contributing it to the repository
- Don't duplicate code, always reuse existing code if possible
- Don't add comments to frontend code, as they would expose information to the users
- Don't run linters, formatters or type checks if the user didn't request it. They take valued time, and are usually useless if changes are not definitive
- Rekono is a cybersecurity project, don't introduce vulnerabilities in the code
- Always use NuxtUI components in the frontend, don't write native HTML or CSS code if it's not needed
