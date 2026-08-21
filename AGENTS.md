# Project: Rekono

## Overview

Offensive security platform that automates attack surface discovery and vulnerability management

## Tech Stack

- Python
- Django
- Django Rest Framework
- PostgreSQL
- Valkey
- TypeScript
- Vue.js
- Nuxt
- Nuxt UI
- React
- Docker

## Architecture

- `/backend/`: Rekono backend
- `/docker/`: Rekono Docker images and the entrypoints used by the Docker Compose deployment
- `/email-templates/`: React email templates to be used by the Rekono backend
- `/frontend/`: Rekono UI
- `config.yaml`: Rekono configuration file

## Code Style

### Backend

These commands are executed from the `/backend/` directory:

- `uvx ruff format`: Format the backend code with the `ruff` formatter
- `uvx ruff==0.15.22 check --fix`: Fix `ruff` style issues
- `uvx ruff check --select I --fix`: Fix `ruff` style issues on imports. Requires to be executed independently of the previous one
- `uvx flake8 .`: Runs Flake8 linter to detect code style issues
- `uvx pytype --disable "import-error,pyi-error,invalid-annotation" --exclude "**/migrations/*.py" --keep-going --jobs 100 .`: Runs PyType to identify Python typing issues. Don't execute this on local as its execution takes long time, and we run it on CI/CD too

### Frontend & Email Templates

These commands are executed from the `/frontend/` and the `/email-templates/` directories:

- `pnpm run prettier:fix`: Format the code with the `prettier` formatter
- `pnpm run eslint:fix`: Runs ESLint linter with `fix` option to fix the issues that are automatically fixable

## Commands

### Backend

These commands are executed from the `/backend/` directory:

- `uv run manage.py makemigrations`: Generate migrations for the latest model changes
- `uv run manage.py rename_1_x_apps`: Applies the version 2.x app names to a database created by version 1.x. To be executed before `migrate`
- `uv run manage.py migrate`: Apply migrations on the database
- `uv run manage.py migrate_1_x_config`: Migrates the version 1.x configuration file to the version 2.x schema. To be executed after `migrate`
- `uv run manage.py remove_deprecated_steps`: Removes the process steps whose configuration is deprecated. To be executed after `migrate`
- `uv run manage.py update_wordlists_size`: Updates the number of words of the wordlists. To be executed after `migrate`
- `uv run manage.py update_tools_status`: Updates the installation status and version of the tools. To be executed after `migrate`
- `uv run manage.py createsuperuser`: Creates a new Rekono user with Admin access
- `uv run manage.py runserver`: Deploys the Rekono backend
- `uv run manage.py rqworker tasks --with-scheduler`: Deploys the worker for the tasks queue. The scheduler is required to run the scheduled tasks
- `uv run manage.py rqworker-pool executions --num-workers 10`: Deploys the worker for the executions queue
- `uv run manage.py rqworker findings`: Deploys the worker for the findings queue
- `uv run manage.py rqworker monitor --with-scheduler`: Deploys the worker for the monitor queue. The scheduler is required to run the monitor jobs
- `uv run manage.py monitor`: Enqueues the first monitor job, since each monitor job only schedules the next one. To be executed on every deployment
- `uv run manage.py telegram_bot`: Deploys the Rekono Telegram bot
- `uv run coverage run --concurrency=multiprocessing,thread manage.py test --parallel 50`: Runs the unit tests. They use an in-memory SQLite database, so only a Valkey server is required to run them
- `uv run coverage combine && uv run coverage report -m --skip-covered`: Shows the coverage of the last unit tests execution

### Frontend

These commands are executed from the `/frontend/` directory:

- `pnpm run dev`: Deploys the Rekono frontend in development mode, with hot reload
- `pnpm run build`: Builds the Nuxt application

### Email Templates

These commands are executed from the `/email-templates/` directory:

- `pnpm run dev`: Deploys the React Email preview server, to check how the templates look before building them
- `pnpm run build`: Builds the templates and places the email templates in HTML in `/backend/platforms/email/templates/`, from where they will be used by the backend

## Debug

### Local Environment

If the application is running locally from source, the following resources are useful to research and debug issues:

- `/`: Root directory of the repository acts as Rekono home when the application runs locally from source, so all the directories listed below are created there
- `logs/rekono.log`: this file contains the logs from all the application components (except the frontend), so if the bug was found during some user or testing activity, this file will contain what actually was executed and what happened
- `reports/`: raw report files written by the tool executions. Each one is named with a random UUID that is saved in the `output_file` field of the related `Execution`, so the report of a specific execution can be found from the database. Some tools also get a temporary directory here, named with a random UUID as well
- `reports/generated/`: reports generated by the users from the reporting feature. Each one is named with a random UUID that is saved in the `path` field of the related `Report`. If a report stays `PENDING` forever, or its file is missing, check `logs/rekono.log` since reports are generated in a raw thread
- `wordlists/`: wordlist files uploaded by the users, named with a random UUID. The default wordlists are not stored here, because they point to the paths where they are installed in the system. In both cases the full path is saved in the `path` field of the related `Wordlist`
- `uv run manage.py shell`: this command allows to run the Django shell in interactive mode, which is helpful to directly test backend features, explore data about recent activity in the database, etc. It requires to pass the local database credentials via environment variables `RKN_DB_USER` and `RKN_DB_PASSWORD`, like any other backend command that accesses the database

### Docker Compose Environment

If the application is running in the docker compose environment, these commands are executed from the root directory of the repository:

- `docker compose logs`: Shows the logs of all the services
- `docker compose exec backend uv run --no-dev manage.py shell`: Runs the Django shell in interactive mode inside the backend container. The database credentials are already set in the container environment, so they don't need to be passed. Any other management command can be executed in the same way

## Important Notes

- Don't run `git add`, `git commit` or `git push`, only work in the local git repository and I will review and test any change manually before contributing it to the repository
- Don't duplicate code, always reuse existing code if possible
- Don't create overcomplicated code, keep it simple and scalable
- Don't add comments to frontend code, as they would expose information to the users
- Don't run linters, formatters or type checks if the user didn't request it explicitly. They take valued time, and are usually useless if changes are not definitive
- Rekono is a cybersecurity project, don't introduce vulnerabilities in the code
- Always use NuxtUI components in the frontend when possible, don't write native HTML or CSS code if it's not needed
