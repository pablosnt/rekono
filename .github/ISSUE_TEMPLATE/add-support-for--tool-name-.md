---
name: Add support for [TOOL NAME]
about: Add support for a new hacking tool
title: ''
labels: enhancement
assignees: ''

---

**Steps to follow**
- [ ] Define the hacking tools in the [tools/fixture](https://github.com/pablosnt/rekono/tree/main/rekono/tools/fixtures) files
- [ ] Implement the [parser](https://github.com/pablosnt/rekono/tree/main/rekono/tools/tools) to obtain findings from the tool results
- [ ] Implement unit tests to check the parser correct working
- [ ] Add the tool reference in the [README.md](https://github.com/pablosnt/rekono#supported-tools).
- [ ] Add tool installation to the [Kali Linux Dockerfile](https://github.com/pablosnt/rekono/blob/main/docker/kali/Dockerfile)
- [ ] Add tool installation to the [Rekono CLI](https://github.com/pablosnt/rekono-cli/blob/main/rekono/installation/tools.py)
