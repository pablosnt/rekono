FROM kalilinux/kali-last-release:latest

# Environment
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV OBJC_DISABLE_INITIALIZE_FORK_SAFETY YES
ENV XDG_CONFIG_HOME /home/rekono/.config
ENV RKN_DB_HOST 127.0.0.1
ENV RKN_DB_PORT 5432
ENV RKN_DB_NAME rekono
ENV RKN_DB_USER rekono
ENV RKN_RQ_HOST 127.0.0.1
ENV RKN_RQ_PORT 6379
ENV REKONO_HOME /rekono
ENV DJANGO_SUPERUSER_EMAIL rekono@rekono.com
ENV DJANGO_SUPERUSER_USERNAME rekono
ENV DJANGO_SUPERUSER_PASSWORD rekono
ENV EXECUTION_WORKERS 5

# Install requirements
RUN apt update -y && \
    apt install python3-pip libpq-dev python3-dev libmagic1 libcap2-bin postgresql redis-server sudo libgbm-dev libasound2 -y && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    mkdir -p $REKONO_HOME /code /config && \
    chown -R postgres:postgres /config && \
    echo $RANDOM | sha256sum | head -c 50 > /config/rkn_db_password.txt

# Install Rekono
COPY rekono/ /code
COPY requirements.txt /code
COPY config.yaml /code
COPY docker/debian/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && \
    pip install -r /code/requirements.txt && \
    dpkg -i /code/frontend/dist_electron/rekono_*.deb || apt -f install -y && \
    rm -R /code/frontend/

# Initialize database
USER postgres
RUN export RKN_DB_PASSWORD=$(cat /config/rkn_db_password.txt) && \
    /etc/init.d/postgresql start && \
    echo $(psql -c "show data_directory;" | grep postgresql) > /config/default_pgdata.txt && \
    echo $(psql -c "show config_file;" | grep postgresql) > /config/postgresql_config.txt && \
    psql -c "CREATE USER ${RKN_DB_USER} WITH ENCRYPTED PASSWORD '${RKN_DB_PASSWORD}';" && \
    psql -c "CREATE DATABASE ${RKN_DB_NAME};" && \
    psql -c "GRANT ALL PRIVILEGES ON DATABASE ${RKN_DB_NAME} TO ${RKN_DB_USER};" && \
    psql ${RKN_DB_NAME} -c "GRANT ALL ON SCHEMA public TO ${RKN_DB_USER};" && \
    psql ${RKN_DB_NAME} -c "GRANT ALL ON ALL TABLES IN SCHEMA public to ${RKN_DB_USER};" && \
    psql ${RKN_DB_NAME} -c "GRANT ALL ON ALL SEQUENCES IN SCHEMA public to ${RKN_DB_USER};" && \
    psql ${RKN_DB_NAME} -c "GRANT ALL ON ALL FUNCTIONS IN SCHEMA public to ${RKN_DB_USER};"
USER root
RUN export RKN_DB_PASSWORD=$(cat /config/rkn_db_password.txt) && \
    /etc/init.d/postgresql start && \
    python /code/manage.py migrate && \
    python /code/manage.py createsuperuser --no-input

# Tools
RUN apt install nmap dirsearch theharvester nikto sslscan sslyze cmseek zaproxy exploitdb metasploit-framework emailharvester joomscan gitleaks smbmap nuclei gobuster -y && \
    rm -rf /var/lib/apt/lists/* && \
    setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip $(which nmap) && \
    git clone https://github.com/fullhunt/log4j-scan /opt/log4j-scan && \
    git clone https://github.com/fullhunt/spring4shell-scan.git /opt/spring4shell-scan && \
    git clone https://github.com/internetwache/GitTools.git /opt/GitTools && \
    pip install -r /opt/log4j-scan/requirements.txt && \
    pip install -r /opt/spring4shell-scan/requirements.txt && \
    pip install emailfinder ssh-audit

# System user
RUN adduser --disabled-password rekono && \
    touch $XDG_CONFIG_HOME && \
    chown rekono:rekono $XDG_CONFIG_HOME && \
    chown -R rekono:rekono $REKONO_HOME && \
    chown -R rekono:rekono /code && \
    chown -R rekono:rekono /config && \
    chown -R rekono:rekono /opt && \
    chown rekono:rekono /entrypoint.sh && \
    echo "rekono ALL=(ALL) NOPASSWD:/etc/init.d/postgresql,/var/run/postgresql,/etc/init.d/redis-server" >> /etc/sudoers

# Final system configuration
USER rekono
WORKDIR /code
