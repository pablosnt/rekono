#!/bin/sh

# Upgrades everything that a Rekono 1.x deployment leaves behind, so moving to Rekono 2.x only
# requires starting the new deployment. Each step checks its own state and does nothing when it
# isn't needed, which is always the case on a new installation and on every restart that follows
# a successful upgrade.
#
# The PostgreSQL image is used because upgrading the data needs the tooling of the version that
# wrote it, and it already includes everything that the rest of the steps need.

set -eu

# The home directory is upgraded first, so the Rekono user can write its logs
# This runs as root, since only root can give the home directory to the new Rekono user
sh /entrypoints/rekono-upgrade/home-ownership.sh
# PostgreSQL refuses to run as root, so the database is upgraded by the user that owns its data
exec su-exec postgres sh /entrypoints/rekono-upgrade/postgres-data.sh
