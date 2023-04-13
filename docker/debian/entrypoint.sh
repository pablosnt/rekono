#! /bin/sh

export RKN_DB_PASSWORD=$(cat /data/rkn_db_password.txt)

# Set configuration file
if [ ! -f $REKONO_HOME/config.yaml ]
then
    cp /code/config.yaml $REKONO_HOME/config.yaml
fi

# Set PostgreSQL data directory
export DEFAULT_PGDATA=$(cat /data/default_pgdata.txt) 
export PGDATA="$REKONO_HOME/data"
sed -i 's:'"$DEFAULT_PGDATA"':'"$PGDATA"':' $(cat /data/postgresql_config.txt)
if [ ! -d $PGDATA ]
then
    cp $DEFAULT_PGDATA $PGDATA
fi

# Start services
sudo /etc/init.d/postgresql start
sudo /etc/init.d/redis-server start

# Migrate database to update resources data
python /code/manage.py migrate

# Backend
python /code/manage.py runserver 0.0.0.0:8000 &

# RQ workers
python /code/manage.py rqworker tasks-queue &
for worker in $(seq 1 $EXECUTION_WORKERS)
do
    python /code/manage.py rqworker executions-queue &
done
python /code/manage.py rqworker findings-queue &
python /code/manage.py rqworker emails-queue &

# Telegram bot
python /code/manage.py telegram_bot &

# Desktop app
/usr/bin/rekono --no-sandbox