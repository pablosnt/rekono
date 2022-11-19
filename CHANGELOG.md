# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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