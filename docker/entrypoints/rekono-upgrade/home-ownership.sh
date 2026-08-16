#!/bin/sh

# Rekono 1.x ran as the user 1000 and Rekono 2.x runs as the user 65532. Docker only applies the
# ownership that the image carries to a volume that is still empty, so a home directory written by
# Rekono 1.x keeps an owner that the new user can't write, and every command fails as soon as it
# opens the log file. This needs to run as root

set -eu

# Empty volume, new installation
if [ ! -d "${REKONO_HOME}" ] || [ -z "$(ls -A "${REKONO_HOME}")" ]; then
    echo "[i] No home directory to be migrated"
    exit 0
fi
# Rekono home ownership is already correct
if [ "$(stat -c '%u' "${REKONO_HOME}")" = "${REKONO_UID}" ]; then
    echo "[i] Home directory already belongs to the Rekono user"
    exit 0
fi

echo "[i] Migrating the ownership of the home directory to the Rekono user"
chown -R "${REKONO_UID}:${REKONO_GID}" "${REKONO_HOME}"
echo "[i] Home directory ownership migrated successfully"
