#!/bin/bash

nuclei -update-templates
sudo /usr/local/sbin/update-tooling.sh &
uv run --no-dev manage.py rqworker executions