<p align="center">
  <a href="https://github.com/pablosnt/rekono/actions/workflows/unit-testing.yml" alt="Unit testing" target="_blank">
    <img src="https://github.com/pablosnt/rekono/actions/workflows/unit-testing.yml/badge.svg"/>
  </a>
  <a href="https://github.com/pablosnt/rekono/actions/workflows/desktop-ui.yml" alt="Desktop UI" target="_blank">
    <img src="https://github.com/pablosnt/rekono/actions/workflows/desktop-ui.yml/badge.svg"/>
  </a>
  <a href="https://github.com/pablosnt/rekono/actions/workflows/security-sast.yml" alt="SAST" target="_blank">
    <img src="https://github.com/pablosnt/rekono/actions/workflows/security-sast.yml/badge.svg"/>
  </a>
  <a href="https://snyk.io/test/github/pablosnt/rekono" alt="SCA" target="_blank">
    <img src="https://badgen.net/snyk/pablosnt/rekono?label=SCA&labelColor=black&icon=https://snyk.io/wp-content/uploads/patch-white.svg">
  </a>
  <a href="https://github.com/pablosnt/rekono/actions/workflows/security-secrets.yml" alt="Secrets scanning" target="_blank">
    <img src="https://github.com/pablosnt/rekono/actions/workflows/security-secrets.yml/badge.svg"/>
  </a>
  <a href="https://github.com/pablosnt/rekono/actions/workflows/security-containers.yml" alt="Containers" target="_blank">
    <img src="https://github.com/pablosnt/rekono/actions/workflows/security-containers.yml/badge.svg"/>
  </a>
  <a href="https://github.com/pablosnt/rekono/actions/workflows/code-style.yml" alt="Code style" target="_blank">
    <img src="https://github.com/pablosnt/rekono/actions/workflows/code-style.yml/badge.svg"/>
  </a>
  <a href="https://discord.gg/Zyduu5C7M3" target="_blank">
    <img src="https://img.shields.io/badge/Discord-Join-black?style=social&logo=discord"/>
  </a>
  <a href="https://ko-fi.com/pablosnt" target="_blank">
    <img src="https://ko-fi.com/img/githubbutton_sm.svg" width="160"/>
  </a>
  <a href="https://www.buymeacoffee.com/pablosnt" target="_blank">
    <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" width="75"/>
  </a>
</p>

# <p align="center"><img src="rekono/frontend/public/static/logo-black.png" width="500"/></p>

**Rekono** combines other hacking tools and its results to execute complete pentesting processes against a target in an automated way. The findings obtained during the executions will be sent to the user via email or Telegram notifications and also can be imported in [Defect-Dojo](https://www.defectdojo.com) if an advanced vulnerability management is needed. Moreover, Rekono includes a Telegram bot that can be used to perform executions easily from anywhere and using any device.


## Why Rekono?

Do you ever think about the steps that you follow when you start pentesting? Probably you start performing some OSINT tasks to gather public information about the target. Then, maybe you run hosts discovery and ports enumeration tools. When you know what the target exposes, you can execute more specific tools for each service, to get more information and maybe, some vulnerabilities. And finally, if you find the needed information, you will look for a public exploit to get you into the target machine. I know, I know, this is an utopic scenario, and in the most cases the vulnerabilities are found due to the pentester skills and not by scanning tools. But before using your skills, how many time do you spend trying to get as information as possible with hacking tools? Probably, too much.

Why not automate this process and focus on find vulnerabilities using your skills and the information that Rekono sends you?

> The `Rekono` name comes from the Esperanto language where it means _recon_.


## Demo

[![Rekono]](https://user-images.githubusercontent.com/69458381/211694917-6738e42a-cb44-4d3a-905d-752b3fe25718.mp4)


### Telegram Bot

[![Rekono Bot]](https://user-images.githubusercontent.com/69458381/211692042-d7c38e41-19e9-44fd-842a-59a16f945b6f.mp4)


## Quick Start

### Rekono Desktop

Rekono Desktop is a standalone app that can be easily installed and executed locally. Install it on **Kali Linux** with this command:

```bash
apt install rekono-kbx
```

If you are using **Parrot OS**, you can download the Debian package from the Rekono release:

```bash
wget https://github.com/pablosnt/rekono/releases/download/1.6.4/rekono-kbx_1.6.4_amd64.deb && dpkg -i rekono-kbx_1.6.4_amd64.deb || apt -f install -y
```

> Default credentials are `rekono:rekono`. For security reasons, **password should be changed** the first time you access the account


### Docker

Execute the following commands in the root directory of the project:

```bash
docker-compose build
docker-compose up -d --scale executions-worker=5
```

Go to https://127.0.0.1/

> Default credentials are `rekono:rekono`. For security reasons, **password should be changed** the first time you access the account. Moreover default user details can be changed using [environment variables](https://github.com/pablosnt/rekono/wiki/Configuration#docker).

> The number of workers can be changed using `--scale` option. The number of `executions-worker` determines the number of tools that could be executed at the same time.


Check [**full documentation**](https://github.com/pablosnt/rekono/wiki) for more installation and configuration options, user guides, integrations, Rekono Desktop, Rekono Bot and Rekono CLI details.


## Hacking Tools

Rekono supports the execution of this hacking tools:

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


## Reach Us

You can get support, ask questions, solve doubts or solve problems using:

<p>
  <a href="https://github.com/pablosnt/rekono/issues/new?labels=help+wanted%2C+question&template=support.md" alt="GitHub Issue">
    <img src="https://github.com/fluidicon.png" width="64"/>
  </a>
  <a href="https://discord.gg/Zyduu5C7M3" alt="Discord">
    <img src="https://assets-global.website-files.com/6257adef93867e50d84d30e2/636e0a69f118df70ad7828d4_icon_clyde_blurple_RGB.svg" width="64"/>
  </a>
  <a href="mailto:rekono.project@gmail.com" alt="Mail">
    <img src="https://www.gstatic.com/images/branding/product/2x/gmail_2020q4_512dp.png" width="64"/>
  </a>
</p>

Rekono is an open source project that we really love to maintain and it's absolutely our pleasure, but we would like to offer the possibility of supporting Rekono's development via donations. At the moment, the project only needs its maintainer's time to stay up to date with new features and fix bugs. However, in the future, it could need more expensive resources like hosting, new web pages for documentation, the inclusion of premium hacking tools, etc. With the help received from our supporters, Rekono will be able to grow fastly and have the resources that it deserves. Of course, you can use the donations just to appreciate our work. Thank you for your help!

<p>
  <a href="https://ko-fi.com/pablosnt" target="_blank">
    <img src="https://storage.ko-fi.com/cdn/brandasset/kofi_s_tag_white.png" width="130"/>
  </a>
  <a href="https://www.buymeacoffee.com/pablosnt" target="_blank">
    <img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pablosnt&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"/>
  </a>
</p>

> The main differences between them are that BuyMeACoffe charges fees over each donation while Ko-fi doesn't and Ko-fi supports PayPal payments while BuyMeACoffe doesn't

## License

Rekono is licensed under the [GNU GENERAL PUBLIC LICENSE Version 3](./LICENSE.md)
