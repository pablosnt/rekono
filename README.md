<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="frontend/public/logo-dark.png">
    <img src="frontend/public/logo-light.png" width="450" alt="Rekono">
  </picture>
</p>

**Automate the recon, keep your time for the part that actually needs a hacker**

Think about how an assessment really starts. You gather public information about the target. You discover its hosts, enumerate their ports and identify the services behind them. Then you run a more specific tool against each service, scan for known vulnerabilities and look for public exploits. It's almost the same sequence every time, it takes hours of watching terminals waiting for executions to finish and copying results from one tool into the next, and none of it is the part where your skills make the difference.

Rekono does that work for you. You define a target and it chains the hacking tools by itself: what one tool discovers becomes the input of the ones that come next. So, the ports found by a port scanner are attacked by the right service tools, the technologies detected are checked for known vulnerabilities, and the vulnerabilities found are matched against public exploit databases. Everything lands in one place, deduplicated, linked to the host and the port where it lives, and enriched with the information that you would otherwise look up by hand.

It's a platform, not a script. Projects for your engagements, roles for your team, notes to write down what you find, collaborative triage, automatic resolution of findings, metrics, reports for your deliverables, and scheduled or repeated scans to keep watching an attack surface over time.

Best of all, you don't have to wait in front of it. Rekono notifies you by email or Telegram as soon as something worth your attention shows up, so when you sit down you are starting from an attack surface that is already mapped, prioritized and full of leads.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/user-attachments/assets/a04acbdf-250d-4f9d-816c-d22981dc23cf">
    <img width="1710" height="1016" alt="screenshot" src="https://github.com/user-attachments/assets/4c9d952c-9c6f-4462-9c7d-45f43b7f5920" />
  </picture>
</p>

# Quick Start

```bash
docker compose up -d --scale executions-worker=5
```

Go to https://127.0.0.1 and log in with `rekono:rekono`. **Change that password the first time you log in**

> Upgrading from Rekono 1.x? Read the [upgrade guide](UPGRADE.md) first. The database migration runs on its own, but there are things that you should know

# Features

- **Pentesting processes**: Rekono runs a full assessment by itself, chaining the tools so that whatever one of them discovers is immediately attacked by the next one. Build your methodology once and launch it against any target with a single click.
- **One attack surface, not a pile of raw outputs**: The same finding reported by three different tools is one finding in Rekono, attached to the host, the port or the technology where it was found. You get a clean inventory of what your target exposes, instead of the output of every execution.
- **Vulnerability management**: Confirm the real vulnerabilities and dismiss the false positives once and for all. Don't waste time with findings that are gone, Rekono marks them as fixed as soon as the executions stop detecting them, brings them back with your verdict intact if they ever return, and remembers how long they were exposed.
- **Vulnerabilities with context**: Every CVE discovered is enriched with what the security community already knows about it, so you can tell how serious it really is, how likely it is to be exploited, and how to get rid of it, without opening a single browser tab. Prioritization comes for free.
- **Alerts that reach you**: Tell Rekono what you are hunting for and it will let you know the moment it shows up, wherever you are, so you never have to sit in front of the platform waiting for it.
- **Metrics that tell the story**: See how exposed a project is, where the risk is concentrated and how everything evolves over time.
- **Reports ready to deliver**: Turn a whole assessment into a deliverable in seconds, with your own template, and skip the part of the job that nobody enjoys.
- **Notes for the whole team**: Write what you found and what you plan to do next, and share it with your teammates so nobody repeats the work that is already done and everyone works with the same knowledge.
- **Customize your scans**: Decide how aggressive each scan is, send it through your own proxy and give the tools the headers and the credentials that your target expects.
- **Hack from anywhere**: The Telegram bot launches scans and delivers the findings straight to your phone, and if you need the automation of the automation, everything that Rekono does is one API call away.

# Hacking Tools

Rekono supports the execution of 19 hacking tools:

- OSINT: [theHarvester](https://github.com/laramies/theHarvester), [EmailHarvester](https://github.com/maldevel/EmailHarvester)
- Host, ports and services enumeration: [Nmap](https://nmap.org/)
- Enumeration: [Dirsearch](https://github.com/maurosoria/dirsearch), [Gobuster](https://github.com/OJ/gobuster)
- SSL and TLS: [Sslscan](https://github.com/rbsec/sslscan), [SSLyze](https://nabla-c0d3.github.io/sslyze/documentation/)
- Exposed secrets: [GitLeaks](https://github.com/zricethezav/gitleaks)
- SSH: [SSH Audit](https://github.com/jtesta/ssh-audit)
- SMB: [SMBMap](https://github.com/ShawnDEvans/smbmap)
- Web: [Log4j Scan](https://github.com/fullhunt/log4j-scan), [Spring4Shell Scan](https://github.com/fullhunt/spring4shell-scan), [CMSeeK](https://github.com/Tuhinshubhra/CMSeeK/), [OWASP JoomScan](https://github.com/OWASP/joomscan), [OWASP ZAP](https://www.zaproxy.org/), [Nikto](https://github.com/sullo/nikto)
- Vulnerability scanners: [Nuclei](https://github.com/projectdiscovery/nuclei)
- Exploits: [SearchSploit](https://www.exploit-db.com/searchsploit), [Metasploit](https://www.metasploit.com/)

# Integrations

The findings detected by the [hacking tools](#hacking-tools) are nothing if we don't enrich them with information from external sources or if we don't share them with the right people at the right time. This is why Rekono supports multiple integrations:

| Integration | Type | Purpose |
| ----------- | ---- | ------- |
| [DefectDojo](https://www.defectdojo.com/) | Vulnerability Management | Findings detected by Rekono executions are shipped to DefectDojo, to make their management and reporting easier |
| [Virus Total](https://www.virustotal.com/) | Malware Analysis | Identified hosts are verified in VirusTotal to get metadata about their reputation and malware analysis conclusions |
| [HackTricks](https://hacktricks.wiki/) | Hacking Wiki | The findings that have a related page in HackTricks will be linked to it, for auditors to get more information easily |
| [CVE Crowd](https://cvecrowd.com/) | Trending CVEs | Detected CVEs are marked as trending if CVE Crowd identifies them as so |
| [FIRST EPSS](https://first.org/epss) | EPSS provider | We get EPSS scores and percentiles for the detected CVEs from this source |
| [NVD NIST](https://nvd.nist.gov/) | CVE provider | We get updated information for the detected CVEs from this source |
| [VulnCheck NVD++](https://www.vulncheck.com/nvd2) | CVE provider | We get updated information for the detected CVEs from this source |
| [OSV](https://osv.dev/) | CVE provider | We get updated information for the detected CVEs from this source |
| [GHSA](https://github.com/advisories) | CVE provider | We get updated information for the detected CVEs from this source |
| [EU Vulnerability Database](https://euvd.enisa.europa.eu/homepage) | CVE provider | We get updated information for the detected CVEs from this source |
| SMTP | Notifications | Notifications about the user account, executions, alerts, etc |
| Telegram | Notifications | Notifications about executions and alerts |

# Get Involved

Join our community in [![](https://readmecodegen.vercel.app/api/social-icon?name=discord&size=10) Discord](https://discord.gg/Zyduu5C7M3) and follow us on [![](https://readmecodegen.vercel.app/api/social-icon?name=x&size=10)](https://x.com/rekonosec).

Rekono is an open source project with only one maintainer, working in his free time and with no external funds. You can support the project or simply appreciate our work with your donations on [![](https://readmecodegen.vercel.app/api/social-icon?name=kofi&size=10) Ko-fi](https://ko-fi.com/pablosnt) or [![](https://readmecodegen.vercel.app/api/social-icon?name=buymeacoffee&size=10) Buy me a Coffee](https://buymeacoffee.com/pablosnt).

![](https://readmecodegen.vercel.app/api/social-icon?name=github&size=10&color=ffffff) Rekono is open to suggestions and improvements, don't hesitate to create an [issue](https://github.com/pablosnt/rekono/issues) or contribute something cool to the project. Check our [CONTRIBUTING](./CONTRIBUTING.md) guidelines

> Do you want to know more? The Rekono name comes from Esperanto and it means _recon_

# License

Rekono is licensed under the [GNU GENERAL PUBLIC LICENSE Version 3](./LICENSE.txt)

# Disclaimer

Rekono is intended only for authorized security testing, education and research, so you must have explicit permission to test every target that you add to it. You are solely responsible for the use that you make of the project, which its authors, maintainers and contributors provide as is, without warranty of any kind, and for which they accept no liability for any damage or legal consequence arising from its misuse.
