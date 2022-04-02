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

Do you ever think about the steps that you follow when start a pentesting? Probably you start performing some OSINT tasks to gather public information about the target. Then, maybe you run hosts discovery and ports enumeration tools. When you know what the target exposes, you can execute more specific tools for each service, to get more information and maybe, some vulnerabilities. And finally, if you find the needed information, you will look for a public exploit to get you into the target machine. I know, I know, this is an utopic scenario, and in the most cases the vulnerabilities are found due to the pentester skills and not by scanning tools. But before using your skills, how many time do you spend trying to get as information as possible with hacking tools? Probably, too much.

With Rekono, you can design your pentesting processes including the hacking tools that you need to combine, and then you can execute it directly against your target. While the full process is running, you can see the result of each tool execution and Rekono will send you notifications with the findings. So you will have the target information instantly and you can focus in find vulnerabilities on your own using your skills, while Rekono executes the boring and predictable part of the pentesting. Of course, you can review your findings in the platform and Rekono includes a Defect-Dojo integration, so if you need an advance vulnerability management you can import them in your Defect-Dojo instance.

Oh, one more thing, you can execute the entire process from anywhere using the Rekono Telegram bot.


## Quick Start

DEMO


### Main Features

- Design pentesting process
- Execute pentesting process
- Execute pentesting tools
- Finding management
- Defect-Dojo integration
- Execution from Telegram Bot
- Email and Telegram notifications


### Supported Tools

Please, review the supported tools [documentation](docs/TOOLS.md)


## Installation

### Docker

Execute the following command in the project root:

```
docker-compose up -d
```

Visit https://127.0.0.1/


### Using Rekono CLI

If your system is Linux, you can use [rekono-cli](https://github.com/pablosnt/rekono-cli) to install Rekono in your system:

```
python3 -m pip install rekono-cli
rekono install
```

After that, you can manage the Rekono services in that way:

```
rekono services start
rekono services stop
rekono services restart
```

Visit http://127.0.0.1:3000/

> :warning: Only tested in Kali Linux.  

> :warning: Only use that for local and personal usage. Otherwise Docker is advised.  


### From Source

1. Install the required technologies:
    - Python 3 & PIP
    - Node & NPM
    - PostgreSQL
    - Redis

2. Create the `rekono` database. You can do that with `pgAdmin` or with the following commands:

    ```
    create user <db username> with encrypted password '<db password>';`
    create database rekono;
    grant all privileges on database rekono to <db username>;
    ```

3. Install backend requirements:

    ```
    python3 -m pip install -r requirements.txt
    ```

4. Install frontend requirements:

    ```
    cd rekono/frontend
    npm install
    ```

5. Initialize the environment:

    ```
    cd rekono/
    export RKN_DB_USER=<db username>
    export RKN_DB_PASSWORD=<db password>
    python3 manage.py migrate
    python3 manage.py createsuperuser
    ```

6. Deploy the Rekono services:

    - Backend
        ```
        cd rekono/
        python3 manage.py migrate
        ```
    - Frontend. For production environments, see the [frontend documentation](rekono/frontend/README.md)
        ```
        cd rekono/frontend
        npm run serve       # Only for development environments
        ```
    - RQ workers
        ```
        cd rekono/
        python3 manage.py rqworker --with-scheduler tasks-queue
        python3 manage.py rqworker executions-queue
        python3 manage.py rqworker findings-queue
        python3 manage.py rqworker emails-queue
        ```
    - Telegram Bot
        ```
        cd rekono/
        export RKN_TELEGRAM_TOKEN=<telegram token>
        python3 manage.py telegram_bot
        ```

7. Visit http://127.0.0.1:3000/


## Configuration


## Contributing

Please, review the Rekono [contributing guidelines](docs/CONTRIBUTING.md)


## Security

Please, review the Rekono [security policy](docs/SECURITY.md)


## License

Rekono is licensed under the [GNU GENERAL PUBLIC LICENSE Version 3](./LICENSE.md)
