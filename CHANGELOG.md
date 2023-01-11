# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2023-01-11

### Added

- Support for authenticated scans using different authentication types (https://github.com/pablosnt/rekono/pull/95)
- Replace `TargetTechnology` and `TargetVulnerability` entities by `InputTechnology` and `InputVulnerability` entities (https://github.com/pablosnt/rekono/pull/97)
- New popup for the management of target details: target ports, authentication, input technologies and vulnerabilities (https://github.com/pablosnt/rekono/pull/97)
- Support for `Nuclei` tool (https://github.com/pablosnt/rekono/pull/100)
- Support for `Spring4Shell Scan` tool (https://github.com/pablosnt/rekono/pull/102)
- Support for `Gobuster` tool (https://github.com/pablosnt/rekono/pull/106)
- New default wordlists (https://github.com/pablosnt/rekono/pull/109)
- Save default wordlists `size` after database migration (https://github.com/pablosnt/rekono/pull/109)
- Save the reason of skipped executions in `output_plain` field (https://github.com/pablosnt/rekono/pull/121)

### Changed

- Remove `TargetEndpoint` entity because they are useless for all tools (https://github.com/pablosnt/rekono/pull/92)
- Optimize API handlers to reduce duplicated code (https://github.com/pablosnt/rekono/pull/96)
- Remove password wordlists because they are useless for all tools (https://github.com/pablosnt/rekono/pull/101)
- Replace `cisagov/log4j-scanner` tool by `fullhunt/log4j-scan` (https://github.com/pablosnt/rekono/pull/103)
- Move `stage` parameter from `Tool` entity to `Configuration` to allow configurations of the same tool to belong to different stages (https://github.com/pablosnt/rekono/pull/108)
- Improve favourities filters on web interface (https://github.com/pablosnt/rekono/pull/110)
- Upgrade `requests` to version `2.28.1` (https://github.com/pablosnt/rekono/pull/114)

### Fixed

- Deploy Telegram bot automatically after configuring the Telegram token (https://github.com/pablosnt/rekono/pull/93)
- Allow the creation of tasks without specific wordlist from the Telegram bot (https://github.com/pablosnt/rekono/pull/98)
- Only apply input parameters for tool executions (https://github.com/pablosnt/rekono/pull/99)
- Filter host inputs by distinct address type to prevent errors in tool configurations (https://github.com/pablosnt/rekono/pull/107)
- Fix icon size and resolution to improve user experience on web interface (https://github.com/pablosnt/rekono/pull/111)
- Configure `CMSeeK` to don't ask user about anything (https://github.com/pablosnt/rekono/pull/115)
- Fix usage of specific environment variables for tool executions (https://github.com/pablosnt/rekono/pull/119) 

### Security

- Validate target addresses to prevent scannings of the internal Rekono infrastructure (https://github.com/pablosnt/rekono/pull/94)
- Upgrade `setuptools` to version `65.6.3` (https://github.com/pablosnt/rekono/pull/105)


## [1.3.0] - 2022-11-19

### Added

- Popup to manage the target ports details (https://github.com/pablosnt/rekono/pull/87)
- Improve user experience while the findings are obtained via API Rest (https://github.com/pablosnt/rekono/pull/88)

### Security

- Upgrade `node` Docker image version to `19.0.1-alpine` (https://github.com/pablosnt/rekono/pull/85)
- Upgrade `djangorestframework-simplejwt` version to `5.2.2` (https://github.com/pablosnt/rekono/pull/84)


## [1.2.0] - 2022-11-01

### Added

- `Settings` page to configure Defect-Dojo, Telegram and security properties (https://github.com/pablosnt/rekono/pull/71)

### Fixed

- Docker environment deployment using privileged users (https://github.com/pablosnt/rekono/pull/71)
- Optimize the frontend build in Docker environment (https://github.com/pablosnt/rekono/pull/72) 

### Security

- Use `sessionStorage` to store access and refresh tokens in the frontend (https://github.com/pablosnt/rekono/pull/74)
- Upgrade `node` Docker image version to `18.9.1-alpine` (https://github.com/pablosnt/rekono/pull/72)


## [1.1.0] - 2022-10-16

### Added

- Create multiple targets at the same time (https://github.com/pablosnt/rekono/pull/49)
- Execute tasks against multiple targets at the same time (https://github.com/pablosnt/rekono/pull/55)
- Show executions duration in task page (https://github.com/pablosnt/rekono/pull/54)

### Fixed

- Show Defect-Dojo fields only when it is configured (https://github.com/pablosnt/rekono/pull/53)

### Changed

- Upgrade `axios` version to `0.27.2` (https://github.com/pablosnt/rekono/pull/62)
- Upgrade `vue-router` version to `3.6.5` (https://github.com/pablosnt/rekono/pull/61)
- Upgrade `core-js` version to `3.25.2` (https://github.com/pablosnt/rekono/pull/60)
- Upgrade `vue` version to `2.7.10` (https://github.com/pablosnt/rekono/pull/59)
- Upgrade `sass` version to `1.55.0` (https://github.com/pablosnt/rekono/pull/58)

### Security

- Upgrade `Django` version to `3.2.16` (https://github.com/pablosnt/rekono/pull/50)


## [1.0.1] - 2022-09-20

### Fixed

- Retry requests to Defect-Dojo API after unexpected errors (https://github.com/pablosnt/rekono/pull/39)
- Retry requests to NVD NIST API to avoid blocks by the API rate limit and after unexpected errors (https://github.com/pablosnt/rekono/pull/39)
- Save unique exploits based on its `reference` instead of `edb_id` (https://github.com/pablosnt/rekono/pull/30)
- Prevent unexpected errors parsing malformed Sslscan reports (https://github.com/pablosnt/rekono/pull/27)

### Changed

- Optimize calculation of executions from previous findings to make process executions faster (https://github.com/pablosnt/rekono/pull/27)
- Allow parentheses in text values like names and descriptions (https://github.com/pablosnt/rekono/pull/29)

### Security

- Upgrade `nginx` Docker image version to `1.22-alpine` (https://github.com/pablosnt/rekono/pull/25/files)
- Upgrade `node` Docker image version to `18.6.0-alpine` (https://github.com/pablosnt/rekono/pull/25/files)
- Upgrade `python-libnmap` version to `0.7.3` (https://github.com/pablosnt/rekono/pull/31)


## [1.0.0] - 2022-08-19

### Added

- Execution of `hacking tools`
- Execution of `pentesting processes` combining different hacking tools automatically
- Execution of `scheduled tasks`
- Search of projects and processes by `tags`
- `Like` features for tools, processes and wordlists
- `Defect-Dojo integration` to import findings from Rekono
- `User notifications` by email and Telegram
- Management of `Projects`, `Targets`, `Wordlist` and `Users`
- Execution of tools and processes from `Telegram Bot`
- Initial `web UI`