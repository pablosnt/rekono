# Upgrade to Rekono 2.x

Rekono 2.0.0 changes the PostgreSQL version from 14 to 18. PostgreSQL can't read data directories written by previous major versions, so the data has to be migrated before Rekono 2.x can use it.

This guide covers the two supported installation methods. Rekono Desktop is upgraded by its own package, so it isn't covered here.

Rekono 2.0.0 also changes the data model in ways that can't always be translated from the version 1.x one. Check the [known problems](#known-problems) before upgrading, since some data is lost even when the migration succeeds.

> Take a backup of your database before upgrading, whatever installation method you use.


## Docker Compose

The migration is automatic. Update the repository and start Rekono as usual:

```bash
git pull
docker-compose up -d --scale executions-worker=5
```

The `rekono-upgrade` service prepares everything that Rekono 1.x left behind, before the Django migrations are applied. It dumps the PostgreSQL 14 data and restores it in the new PostgreSQL 18 database, it gives the home directory to the user that runs Rekono 2.x, which is a different one, and it keeps your TLS certificate, since Rekono 2.x stores it in a Docker volume instead of the `docker/nginx/tls` directory. You can check it with:

```bash
docker-compose logs rekono-upgrade
```

The migration is only performed once and it's skipped on new installations. If the migration fails, Rekono won't start. This is intentional: starting with an empty database would look like a successful new installation and would hide the loss of your data. The PostgreSQL 14 data isn't removed, so you can check the logs, fix the problem and start Rekono again.

After a successful migration, the PostgreSQL 14 data directory is replaced by a compressed backup of the migrated data, so the old database doesn't keep using disk space. Once you have verified that all your data is available in Rekono 2.x, you can also remove that backup:

```bash
docker volume rm rekono_postgres
```

If you need to recover the backup before removing it:

```bash
docker run --rm -v rekono_postgres:/backup -v $(pwd):/output alpine \
    cp /backup/rekono-14-backup.sql.gz /output/
```


## Installation from source

You have to migrate your data to PostgreSQL 18 by yourself, since Rekono doesn't manage your PostgreSQL installation. Any PostgreSQL version can be migrated using a dump.

1. Dump the data from your current database:

```bash
pg_dump --no-owner --no-privileges -d rekono > rekono.sql
```

2. Install PostgreSQL 18 and create an empty `rekono` database.

3. Restore the data:

```bash
psql -d rekono --single-transaction -v ON_ERROR_STOP=1 -f rekono.sql
```

4. Apply the Rekono migrations:

```bash
uv run --no-dev manage.py rename_1_x_apps
uv run --no-dev manage.py migrate
uv run --no-dev manage.py migrate_1_x_config
```


## Known problems

These are consequences of the changes in the data model, so they apply to every installation method, and they can't be avoided by migrating the database in a different way.

### Changes over the default processes and wordlists are undone

Rekono 2.0.0 creates its default processes and wordlists during the migration, matching the ones that already exist by name. The changes that you made over them are handled like this:

- Default processes and wordlists that you removed are created again.
- Default processes and wordlists that you renamed are kept with your name, but a new one is created with the original name, so you end up with both.
- Steps that you removed from a default process are added again. The steps that you added to it are kept.
- The path of a default wordlist is set again to the one that Rekono provides, since these files move between releases of the packages that provide them. The wordlists that you uploaded keep their path.

### Executions aren't marked as imported in Defect-Dojo anymore

Rekono 1.x only stored whether an execution had been imported in Defect-Dojo. Rekono 2.0.0 stores the identifier of the test that the execution creates in Defect-Dojo, which is a more meaningful link, but it can't be deduced from the version 1.x data. So the executions imported by Rekono 1.x are shown as not imported.

The Defect-Dojo synchronization of your projects and targets is migrated, so new executions are imported as usual.

### Input technologies and vulnerabilities of the targets are lost

Rekono 1.x assigned the input technologies and vulnerabilities to a target, so all its tasks used the same values. Rekono 2.0.0 assigns them to each task, so different scans over the same target can use different values, and there is no way to know which tasks the values of a target belonged to.

You have to set them again when you create the tasks that need them.
