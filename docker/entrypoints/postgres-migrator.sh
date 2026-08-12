#!/bin/sh

# Migrates the data from the PostgreSQL version used by the previous Rekono version, since
# PostgreSQL can't read data directories written by previous major versions. Data is dumped and
# restored instead of using pg_upgrade, so the indexes are rebuilt. That's required when the base
# system of the PostgreSQL image changes, like in the migration from Rekono 1.x (Alpine, musl) to
# Rekono 2.x (Debian, glibc), because both C libraries sort text in a different way

set -eu

LEGACY_DATA="/var/lib/postgresql/data"
DUMP="/tmp/rekono-${LEGACY_PG_VERSION}.sql"
BACKUP="${LEGACY_DATA}/rekono-${LEGACY_PG_VERSION}-backup.sql.gz"

# New installation, or migration already performed in a previous execution
if [ ! -f "${LEGACY_DATA}/PG_VERSION" ]; then
    echo "[i] No PostgreSQL ${LEGACY_PG_VERSION} data to be migrated"
    exit 0
fi

legacy_version=$(cat "${LEGACY_DATA}/PG_VERSION")
if [ "${legacy_version}" != "${LEGACY_PG_VERSION}" ]; then
    echo "[!] Found a PostgreSQL ${legacy_version} database, but only PostgreSQL ${LEGACY_PG_VERSION} can be migrated automatically" >&2
    echo "[!] Check the upgrade guide: https://github.com/pablosnt/rekono/blob/main/UPGRADE.md" >&2
    exit 1
fi

# The new database is only empty before the initializer applies the Django migrations for the first time
tables=$(psql -h "${RKN_DB_HOST}" -U "${RKN_DB_USER}" -d "${RKN_DB_NAME}" -tAc "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'")
if [ "${tables}" != "0" ]; then
    echo "[i] New database already contains data"
    exit 0
fi

echo "[i] Migrating the PostgreSQL ${LEGACY_PG_VERSION} data"

pg_ctl -D "${LEGACY_DATA}" -o "-c listen_addresses='' -c unix_socket_directories=/tmp" -w start
# Dump
pg_dump -h /tmp -d "${RKN_DB_NAME}" --no-owner --no-privileges > "${DUMP}"
# Restore
psql -h "${RKN_DB_HOST}" -U "${RKN_DB_USER}" -d "${RKN_DB_NAME}" --single-transaction -v ON_ERROR_STOP=1 -f "${DUMP}"
pg_ctl -D "${LEGACY_DATA}" -m fast -w stop

# Replace the old data directory by a compressed backup to free disk space
find "${LEGACY_DATA}" -mindepth 1 -delete
gzip -c "${DUMP}" > "${BACKUP}"
rm -f "${DUMP}"

echo "[i] PostgreSQL ${LEGACY_PG_VERSION} data migrated successfully. Backup available in ${BACKUP}"
