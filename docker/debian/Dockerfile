FROM debian:bookworm-20240423

# Environment
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV OBJC_DISABLE_INITIALIZE_FORK_SAFETY YES
ENV XDG_CONFIG_HOME /home/rekono/.config
ENV DISPLAY :0.0
ENV RKN_DB_HOST 127.0.0.1
ENV RKN_DB_PORT 5432
ENV RKN_DB_NAME rekono
ENV RKN_DB_USER rekono
ENV RKN_RQ_HOST 127.0.0.1
ENV RKN_RQ_PORT 6379
ENV REKONO_HOME /rekono
ENV PGDATA /rekono/data
ENV DJANGO_SUPERUSER_EMAIL rekono@rekono.dev
ENV DJANGO_SUPERUSER_USERNAME rekono
ENV DJANGO_SUPERUSER_PASSWORD rekono
ENV EXECUTION_WORKERS 5
ARG REKONO_VERSION

# Install requirements
RUN apt update && \
    apt install python3-pip libpq-dev python3-dev libmagic1 redis-server firefox-esr sudo libgbm-dev libasound2 postgresql-15 wget libcap2-bin -y && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    mkdir -p $REKONO_HOME $PGDATA /code /config /kaboxer && \
    chown -R postgres:postgres /config && \
    echo $RANDOM | sha256sum | head -c 50 > /config/rkn_db_password.txt && \
    echo $REKONO_VERSION > /kaboxer/version && \
    echo 1 > /kaboxer/packaging-revision

# Source code and configuration
COPY backend/ /code
COPY frontend/dist_electron/rekono_*.deb /code
COPY config.yaml /rekono
COPY docker/debian/entrypoint.sh /entrypoint.sh
COPY docker/debian/set_permissions.sh /set_permissions.sh

# Install dependencies and Desktop app
RUN pip install -r /code/requirements.txt && \
    dpkg -i /code/rekono_*.deb || apt -f install -y && \
    rm -R /code/tests/ && \
    # Install security tools
    apt install nmap dirsearch theharvester nikto sslscan sslyze cmseek zaproxy exploitdb metasploit-framework emailharvester joomscan gitleaks smbmap nuclei gobuster -y && \
    apt install seclists dirb -y && \
    apt autoremove -y && \
    apt autoclean -y && \
    apt clean -y && \
    rm -rf /var/lib/apt/lists/* && \
    setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip $(which nmap) && \
    git clone https://github.com/fullhunt/log4j-scan /opt/log4j-scan && \
    git clone https://github.com/fullhunt/spring4shell-scan.git /opt/spring4shell-scan && \
    git clone https://github.com/internetwache/GitTools.git /opt/GitTools && \
    pip install -r /opt/log4j-scan/requirements.txt && \
    pip install -r /opt/spring4shell-scan/requirements.txt && \
    pip install emailfinder ssh-audit

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

# Tools
# nosemgrep: dockerfile.security.last-user-is-root.last-user-is-root
USER root
# sudo is required at runtime so the unprivileged 'rekono' user can start the
# bundled postgresql/redis services in this all-in-one Kali desktop package. It
# is locked down to a specific command allowlist in /etc/sudoers (see below).
# nosemgrep: dockerfile.security.no-sudo-in-dockerfile.no-sudo-in-dockerfile
RUN export RKN_DB_PASSWORD=$(cat /config/rkn_db_password.txt) && \
    /etc/init.d/postgresql start 15 && \
    python /code/manage.py migrate && \
    python /code/manage.py createsuperuser --no-input && \
    # System user
    adduser --disabled-password rekono && \
    usermod -a -G postgres rekono && \
    usermod -a -G postgres root && \
    touch $XDG_CONFIG_HOME && \
    chown rekono:rekono $XDG_CONFIG_HOME && \
    chown rekono:rekono /entrypoint.sh && \
    chmod 700 /entrypoint.sh && \
    chown rekono:rekono /set_permissions.sh && \
    chmod 700 /set_permissions.sh && \
    /set_permissions.sh && \
    chown rekono:rekono /downgrade_postgresql_16.sh && \
    chmod 700 /downgrade_postgresql_16.sh && \
    chown -R rekono:rekono /code && \
    chown -R rekono:rekono /config && \
    chown -R rekono:rekono /opt && \
    chown -R rekono:rekono /home/kali && \
    chown -R rekono:rekono /usr/share && \
    echo "rekono ALL=(ALL) NOPASSWD:SETENV:/etc/init.d/postgresql,/var/run/postgresql,/etc/init.d/redis-server,/set_permissions.sh,/downgrade_postgresql_16.sh" >> /etc/sudoers && \
    export DEFAULT_PGDATA=$(cat /config/default_pgdata.txt) && \
    chown -R rekono:rekono $DEFAULT_PGDATA && \
    sed -i 's:'"$DEFAULT_PGDATA"':'"$PGDATA"':' $(cat /config/postgresql_config.txt) && \
    rm /config/postgresql_config.txt

# nosemgrep: dockerfile.security.last-user-is-root.last-user-is-root
USER root
WORKDIR /code
