<p align="center">
  <a href="https://github.com/pablosnt/rekono/actions/workflows/unit-testing.yml" alt="Unit testing">
    <img src="https://github.com/pablosnt/rekono/actions/workflows/unit-testing.yml/badge.svg"/>
  </a>
  <a href="https://snyk.io/test/github/pablosnt/rekono" alt="SCA">
    <img src="https://badgen.net/snyk/pablosnt/rekono?label=Vulnerabilities&labelColor=black&icon=https://snyk.io/wp-content/uploads/patch-white.svg">
  </a>
  <a href="https://snyk.io/test/github/pablosnt/rekono">
  <a href="https://github.com/pablosnt/rekono/actions/workflows/security-secrets.yml" alt="Secrets scanning">
    <img src="https://github.com/pablosnt/rekono/actions/workflows/security-secrets.yml/badge.svg"/>
  </a>
  <a href="https://github.com/pablosnt/rekono/actions/workflows/code-style.yml" alt="Code style">
    <img src="https://github.com/pablosnt/rekono/actions/workflows/code-style.yml/badge.svg"/>
  </a>
</p>

# <p align="center"><img src="rekono/frontend/public/static/logo-black.png" width="500"/></p>

**Rekono** combines other hacking tools and its results to execute complete pentesting processes against a target in an automated way. The findings obtained during the executions will be sent to the user via email or Telegram notifications and also can be imported in [Defect-Dojo](https://github.com/DefectDojo/django-DefectDojo) if an advanced vulnerability management is needed. Moreover, Rekono includes a Telegram bot that can be used to perform executions easily from anywhere and using any device.


## Why Rekono?

Do you ever think about the steps that you follow when you start pentesting? Probably you start performing some OSINT tasks to gather public information about the target. Then, maybe you run hosts discovery and ports enumeration tools. When you know what the target exposes, you can execute more specific tools for each service, to get more information and maybe, some vulnerabilities. And finally, if you find the needed information, you will look for a public exploit to get you into the target machine. I know, I know, this is an utopic scenario, and in the most cases the vulnerabilities are found due to the pentester skills and not by scanning tools. But before using your skills, how many time do you spend trying to get as information as possible with hacking tools? Probably, too much.

Why not automate this process and focus on find vulnerabilities using your skills and the information that Rekono sends you?

> The `Rekono` name comes from the Esperanto language where it means _recon_.


## Demo

[![Rekono]](https://user-images.githubusercontent.com/69458381/165973356-47666e33-e96c-4aee-b4a3-dd99fffe73bd.mp4)

### Telegram Bot

[![Rekono Bot]](https://user-images.githubusercontent.com/69458381/165973380-0f3308b6-f5f9-46a7-8d5b-ab89580eb840.mp4)


## Supported tools

- [theHarvester](https://github.com/laramies/theHarvester)
- [EmailHarvester](https://github.com/maldevel/EmailHarvester)
- [EmailFinder](https://github.com/Josue87/EmailFinder)
- [Nmap](https://nmap.org/)
- [Sslscan](https://github.com/rbsec/sslscan)
- [SSLyze](https://nabla-c0d3.github.io/sslyze/documentation/)
- [SSH Audit](https://github.com/jtesta/ssh-audit)
- [SMBMap](https://github.com/ShawnDEvans/smbmap)
- [Dirsearch](https://github.com/maurosoria/dirsearch)
- [Gobuster](https://github.com/OJ/gobuster)
- [GitLeaks](https://github.com/zricethezav/gitleaks) & [GitDumper](https://github.com/internetwache/GitTools/tree/master/Dumper)
- [Log4j Scan](https://github.com/fullhunt/log4j-scan)
- [Spring4Shell Scan](https://github.com/fullhunt/spring4shell-scan)
- [CMSeeK](https://github.com/Tuhinshubhra/CMSeeK/)
- [OWASP JoomScan](https://github.com/OWASP/joomscan)
- [OWASP ZAP](https://www.zaproxy.org/)
- [Nikto](https://github.com/sullo/nikto)
- [Nuclei](https://github.com/projectdiscovery/nuclei)
- [SearchSploit](https://www.exploit-db.com/searchsploit)
- [Metasploit](https://www.metasploit.com/)

Thanks to all the contributors of these amazing tools!


## Installation

### Docker

Execute the following commands in the root directory of the project:

```
docker-compose build
docker-compose up -d
```

If you need more than one tool running at the same time, you can set the number of executions-worker instances:

```
docker-compose up -d --scale executions-worker=5
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

> :warning: Only for Linux environments.  

> :warning: Docker is advised. Only use that for local and personal usage.


### From Source

Check the installation from source in [Rekono Wiki](https://github.com/pablosnt/rekono/wiki/Installation#from-source)


## Integrations

### Telegram Bot

You can follow this steps to deploy the Telegram bot:

1. Create a new bot in Telegram using this [guide](https://core.telegram.org/bots#how-do-i-create-a-bot) and the [@BotFather](https://t.me/botfather)
2. The [@BotFather](https://t.me/botfather) will send you an authentication token
3. Configure the token value in the `Settings` page or ask your administrator for doing it.
4. Restart the Telegram bot container (Docker) or the Telegram bot service (CLI).


### Defect-Dojo

You can configure your Defect-Dojo details in the `Settings` page or ask your administrator for doing it. The following properties can be configured:

- Defect-Dojo URL (`/api/` endpoints will be appended to make API requests)
- Defect-Dojo API key to authenticate API requests
- Tag to be assigned to every items created by Rekono in Defect-Dojo
- Product type name of the products created by Rekono in Defect-Dojo
- Test type name related to Rekono executions imported in Defect-Dojo
- Test name related to Rekono executions imported in Defect-Dojo


## Configuration

Check the configuration options in [Rekono Wiki](https://github.com/pablosnt/rekono/wiki/Configuration)


## License

Rekono is licensed under the [GNU GENERAL PUBLIC LICENSE Version 3](./LICENSE.md)


## Support

If you need help you can create a new support [Issue](https://github.com/pablosnt/rekono/issues/new?assignees=&labels=help+wanted%2C+question&template=support.md, mail rekono.project@gmail.com or join the Rekono community on [Discord](https://discord.gg/Zyduu5C7M3)
