# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

- Bump `nginx` Docker image version to `1.22-alpine` (https://github.com/pablosnt/rekono/pull/25/files)
- Bump `node` Docker image version to `18.6.0-alpine` (https://github.com/pablosnt/rekono/pull/25/files)
- Bump `python-libnmap` version to `0.7.3` (https://github.com/pablosnt/rekono/pull/31)


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