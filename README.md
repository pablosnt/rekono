<p align="center">
  <a href="https://github.com/pablosnt/rekono/actions/workflows/unit-testing.yml" alt="Unit testing">
    <img src="https://github.com/pablosnt/rekono/actions/workflows/unit-testing.yml/badge.svg"/>
  </a>
  <a href="https://github.com/pablosnt/rekono/actions/workflows/security-sca.yml" alt="SCA">
    <img src="https://github.com/pablosnt/rekono/actions/workflows/security-sca.yml/badge.svg"/>
  </a>
  <a href="https://github.com/pablosnt/rekono/actions/workflows/security-secrets.yml" alt="Secrets scanning">
    <img src="https://github.com/pablosnt/rekono/actions/workflows/security-secrets.yml/badge.svg"/>
  </a>
  <a href="https://github.com/pablosnt/rekono/actions/workflows/code-style.yml" alt="Code style">
    <img src="https://github.com/pablosnt/rekono/actions/workflows/code-style.yml/badge.svg"/>
  </a>
</p>

# <p align="center"><img src="rekono/frontend/public/static/logo-black.png" width="500"/></p>

**Rekono** combines other hacking tools and its results to execute complete pentesting processes against a target in an automated way. The findings obtained during the executions will be sent to the user via email or Telegram notifications and also can be reviewed directly in the platform or sent to [Defect-Dojo](https://github.com/DefectDojo/django-DefectDojo) if an advanced vulnerability management is needed. Moreover, Rekono includes a Telegram bot that can be used to perform executions easily from anywhere and using any device.


## Why?

Do you ever think about the steps that you follow when start a pentesting? Probably you start performing some OSINT tasks to gather public information about the target. Then, maybe you run hosts discovery and ports enumeration tools. When you know what the target exposes, you can execute more specific tools for each service, to get more information and maybe, some vulnerabilities. And finally, if you find the needed information, you will look for a public exploit to get you into the target machine. I know, I know, this is an utopic scenario, and in the most cases the vulnerabilities are found due to the pentester skills and not by scanning tools. But before using your skills, how many time do you spend trying to get as information as possible with hacking tools? Probably, too much.

Why not automate this process and focus on find vulnerabilities using your skills and the information that Rekono sends you?


## Quick Start

DEMO


### Features

- Combine hacking tools to create pentesting `processes`
- Execute pentesting `processes`
- Execute pentesting `tools`
- Review `findings` and receive them via `email` or `Telegram` notifications
- Use `Defect-Dojo` integration to keep the findings synchronized between the platforms
- Execute `tools` and `processes` from `Telegram Bot`
- `Wordlists` management


## Installation

### Docker

Execute the following command in the root directory of the project:

```
docker-compose up -d
```

Go to https://127.0.0.1/

> You can check the details in the [Docker](docker/README.md) documentation. Specially, the [initial user](docker/README.md#initial-rekono-user) documentation


### Using Rekono CLI

If your system is Linux, you can use [rekono-cli](https://github.com/pablosnt/rekono-cli) to install Rekono in your system:

```
pip3 install rekono-cli
rekono install
```

After that, you can manage the Rekono services using the following commands:

```
rekono services start
rekono services stop
rekono services restart
```

Go to http://127.0.0.1:3000/

> :warning: Only tested in Kali Linux.  

> :warning: Docker is advised. Only use that for local and personal usage.  


### From Source

1. Install the required technologies:
    - Python 3 & PIP
    - Node & NPM
    - Vue
    - PostgreSQL
    - Redis

2. For Kali Linux environments, you need to install the following dependencies:

    ```
    sudo apt install libpq-dev python3-dev
    ```

3. Create the `rekono` database. You can do that with `pgAdmin` or with the following commands:

    ```
    create user <db username> with encrypted password '<db password>';`
    create database rekono;
    grant all privileges on database rekono to <db username>;
    ```

    > The database credentials should be configured using environment variables (advised) or the `config.yaml` file. See the [configuration section](#configuration) 

4. Install backend requirements:

    ```
    # pwd: root directory
    pip3 install -r requirements.txt
    ```

5. Install frontend requirements:

    ```
    # pwd: rekono/frontend
    npm install
    ```

6. Initialize the environment:

    ```
    # pwd: rekono/
    python3 manage.py migrate
    python3 manage.py createsuperuser
    python3 manage.py frontend              # Parse the Rekono configuration and apply it to the frontend
    ```

7. Deploy the Rekono services:

    - Backend
        ```
        # pwd: rekono/
        python3 manage.py migrate
        ```
    - Frontend. Only for development environments, for production see the [frontend documentation](rekono/frontend/README.md)
        ```
        # pwd: rekono/frontend/
        npm run serve
        ```
    - RQ workers
        ```
        # pwd: rekono/
        python3 manage.py rqworker --with-scheduler tasks-queue
        python3 manage.py rqworker executions-queue
        python3 manage.py rqworker findings-queue
        python3 manage.py rqworker emails-queue
        ```
    - Telegram Bot
        ```
        # pwd: rekono/
        python3 manage.py telegram_bot
        ```

8. Go to http://127.0.0.1:3000/  


## Configuration

You can configure Rekono using two main methods: `config.yaml` file and environemnt variables. The properties will be obtained in the following priority:

1. From environment variables
2. From configuration file. You can use the `config.yaml` as template
3. Default value

Rekono supports the following properties:

|Environment Variable|Configuration Property|Default Value|Description|
|--------------------|----------------------|-------------|-----------|
|`REKONO_HOME`|N/A|`/opt/rekono` or where the source code lives|Path to the Rekono home|
|`RKN_FRONTEND_URL`|`frontend.url`|`http://127.0.0.1:3000`|URL used to include links to the Rekono frontend in the notifications|
|`RKN_DB_NAME`|`database.name`|`rekono`|Database name|
|`RKN_DB_USER`|`database.user`|N/A|Database user|
|`RKN_DB_PASSWORD`|`database.password`|N/A|Database password|
|`RKN_DB_HOST`|`database.host`|`127.0.0.1`|Database host|
|`RKN_DB_PORT`|`database.port`|`5432`|Database port|
|`RKN_RQ_HOST`|`rq.host`|`127.0.0.1`|Redis Queue host|
|`RKN_RQ_PORT`|`rq.port`|`6379`|Redis Queue port|
|`RKN_EMAIL_HOST`|`email.host`|`127.0.0.1`|SMTP host|
|`RKN_EMAIL_PORT`|`email.port`|`587`|SMTP port|
|`RKN_EMAIL_USER`|`email.user`|N/A|SMTP user|
|`RKN_EMAIL_PASSWORD`|`email.password`|N/A|SMTP password|
|`RKN_TELEGRAM_BOT`|`telegram.bot`|`Rekono`|Telegram Bot name to be included in the frontend|
|`RKN_TELEGRAM_TOKEN`|`telegram.token`|N/A|Telegram Bot token. [How to get one?](https://core.telegram.org/bots#6-botfather)|
|`RKN_DD_URL`|`defect-dojo.url`|`http://127.0.0.1:8080`|Defect-Dojo URL|
|`RKN_DD_API_KEY`|`defect-dojo.api-key`|N/A|Defect-Dojo API key|
|N/A|`defect-dojo.verify`|`True`|Indicate if Defect-Dojo certificate should be verified|
|N/A|`defect-dojo.tags`|[`rekono`]|Tags included in the items created by Rekono in Defect-Dojo|
|N/A|`defect-dojo.product-type`|`Rekono Project`|Product type naem related to products created by Rekono in Defect-Dojo|
|N/A|`defect-dojo.test-type`|`Rekono Findings Import`|Test type name related to tests created by Rekono in Defect-Dojo|
|N/A|`defect-dojo.test`|`Rekono Test`|Test name related to findings imported by Rekono in Defect-Dojo|
|`RKN_OTP_EXPIRATION_HOURS`|`security.otp-expiration-hours`|`24`|Expiration time in hours for One Time Passwords created by Rekono|
|`RKN_UPLOAD_FILES_MAX_MB`|`security.upload-files-max-mb`|`500`|MB limit for files uploaded to Rekono. For example, wordlists files|
|`RKN_TRUSTED_PROXY`|N/A|`False`|Indicate if Rekono is running with a trusted reverse proxy|
|`RKN_ALLOWED_HOSTS`|`security.allowed-hosts`|[`localhost`, `127.0.0.1`, `::1`]|Hosts allowed to access Rekono|
|`RKN_SECRET_KEY`|`security.secret-key`|Generated randomly|Security key used to sign JWT tokens|


## License

Rekono is licensed under the [GNU GENERAL PUBLIC LICENSE Version 3](./LICENSE.md)
