#! /bin/sh

# Set permissions to home directory
chown -R rekono:rekono $REKONO_HOME
chmod -R 755 $REKONO_HOME

# Set permissions to data directory
chown -R postgres:postgres $PGDATA
chmod -R 750 $PGDATA
