#! /bin/sh

export RKN_DB_PASSWORD=$(cat /config/rkn_db_password.txt)

# Initialize configuration file
if [ ! -f $REKONO_HOME/config.yaml ]
then
    cp /code/config.yaml $REKONO_HOME/config.yaml
fi

# Set PostgreSQL data directory
if [ ! -d $PGDATA ]
then
    cp -r $(cat /config/default_pgdata.txt) $PGDATA
fi

export PGVERSION=15
# Compatibility fix for upgrades from version 1.6.5 where the PostgreSQL 16 was being used
if [ -f "$PGDATA/PG_VERSION" ]
then
    CURRENT_VERSION=$(cat $PGDATA/PG_VERSION)
    if [ "$CURRENT_VERSION" -eq "16" ]
    then
        sudo REKONO_HOME=$REKONO_HOME PGDATA=$PGDATA RKN_DB_NAME=$RKN_DB_NAME RKN_DB_USER=$RKN_DB_USER /downgrade_postgresql_16.sh
    fi
fi

# Set proper permissions to resources
sudo REKONO_HOME=$REKONO_HOME PGDATA=$PGDATA /set_permissions.sh

# Start services
sudo /etc/init.d/postgresql start $PGVERSION
sudo /etc/init.d/redis-server start

# Migrate database
python /code/manage.py migrate

# Run backend
python /code/manage.py runserver 0.0.0.0:8000 &

# Run RQ workers
python /code/manage.py rqworker tasks-queue &
for worker in $(seq 1 $EXECUTION_WORKERS)
do
    python /code/manage.py rqworker executions-queue &
done
python /code/manage.py rqworker findings-queue &
python /code/manage.py rqworker emails-queue &

# Run Telegram bot
python /code/manage.py telegram_bot &

# Run Desktop app
/usr/bin/rekono --no-sandbox

sudo /etc/init.d/postgresql stop $PGVERSION
sudo /etc/init.d/redis-server stop