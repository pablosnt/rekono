#! /bin/sh

sed -i 's:/var/lib/postgresql/16/main:'"$PGDATA"':' /etc/postgresql/16/main/postgresql.conf
/etc/init.d/postgresql start 16
mkdir -p $REKONO_HOME/backup
chown -R postgres:postgres $REKONO_HOME/backup
sudo -u postgres /usr/lib/postgresql/16/bin/pg_dump --clean --dbname=$RKN_DB_NAME --port=5433 --role=$RKN_DB_USER -f $REKONO_HOME/backup/backup.sql
/etc/init.d/postgresql stop 16
sed -i 's:'"$PGDATA"':/var/lib/postgresql/16/main:' /etc/postgresql/16/main/postgresql.conf
mv $PGDATA $REKONO_HOME/backup/data
cp -r $(cat /config/default_pgdata.txt) $PGDATA
chown -R postgres:postgres $PGDATA
/etc/init.d/postgresql start 15
sudo -u postgres psql rekono < $REKONO_HOME/backup/backup.sql
/etc/init.d/postgresql stop 15
rm -R $REKONO_HOME/backup