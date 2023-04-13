FROM kalilinux/kali-last-release:latest

# Environment
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV OBJC_DISABLE_INITIALIZE_FORK_SAFETY YES
ENV XDG_CONFIG_HOME /home/rekono/.config
ENV NODE_OPTIONS --openssl-legacy-provider
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

# Update system
RUN apt update -y && apt upgrade -y && apt dist-upgrade -y

# Install requirements
RUN apt install python3-pip libpq-dev python3-dev libmagic1 libcap2-bin nodejs npm postgresql redis-server sudo libgbm-dev libasound2 -y
RUN ln -s /usr/bin/python3 /usr/bin/python

# Create directories
RUN mkdir -p $REKONO_HOME

# Source code
RUN mkdir -p /code
COPY rekono/ /code
COPY requirements.txt /code
COPY config.yaml /code

# Entrypoint
COPY docker/debian/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Install backend dependencies
RUN pip install --upgrade pip
RUN pip install -r /code/requirements.txt

# Initialize database
RUN mkdir -p /data && chown -R postgres:postgres /data
RUN echo $RANDOM | sha256sum | head -c 50 > /data/rkn_db_password.txt
USER postgres
RUN export RKN_DB_PASSWORD=$(cat /data/rkn_db_password.txt) && \
    /etc/init.d/postgresql start && \
    echo $(psql -c "show data_directory;" | grep postgresql) > /data/default_pgdata.txt && \
    echo $(psql -c "show config_file;" | grep postgresql) > /data/postgresql_config.txt && \
    psql -c "CREATE USER ${RKN_DB_USER} WITH ENCRYPTED PASSWORD '${RKN_DB_PASSWORD}';" && \
    psql -c "CREATE DATABASE ${RKN_DB_NAME};" && \
    psql -c "GRANT ALL PRIVILEGES ON DATABASE ${RKN_DB_NAME} TO ${RKN_DB_USER};" && \
    psql ${RKN_DB_NAME} -c "GRANT ALL ON SCHEMA public TO ${RKN_DB_USER};" && \
    psql ${RKN_DB_NAME} -c "GRANT ALL ON ALL TABLES IN SCHEMA public to ${RKN_DB_USER};" && \
    psql ${RKN_DB_NAME} -c "GRANT ALL ON ALL SEQUENCES IN SCHEMA public to ${RKN_DB_USER};" && \
    psql ${RKN_DB_NAME} -c "GRANT ALL ON ALL FUNCTIONS IN SCHEMA public to ${RKN_DB_USER};"
USER root
RUN export RKN_DB_PASSWORD=$(cat /data/rkn_db_password.txt) && \
    /etc/init.d/postgresql start && \
    python /code/manage.py migrate && \
    python /code/manage.py createsuperuser --no-input

# Install frontend dependencies
WORKDIR /code/frontend
RUN npm install .

# Build Desktop app
RUN echo "VUE_APP_DESKTOP_BACKEND_URL=http://127.0.0.1:8000" > .env.production
RUN npm run electron:build
RUN dpkg -i dist_electron/rekono_*.deb || apt -f install -y

# Tools
RUN apt install nmap dirsearch theharvester nikto sslscan sslyze cmseek zaproxy exploitdb metasploit-framework emailharvester joomscan gitleaks smbmap nuclei gobuster -y
RUN setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip $(which nmap)
RUN git clone https://github.com/fullhunt/log4j-scan /opt/log4j-scan
RUN git clone https://github.com/fullhunt/spring4shell-scan.git /opt/spring4shell-scan
RUN git clone https://github.com/internetwache/GitTools.git /opt/GitTools
RUN pip install -r /opt/log4j-scan/requirements.txt
RUN pip install -r /opt/spring4shell-scan/requirements.txt
RUN pip install emailfinder ssh-audit

# System user
RUN adduser --disabled-password rekono
RUN touch $XDG_CONFIG_HOME
RUN chown rekono:rekono $XDG_CONFIG_HOME
RUN chown -R rekono:rekono $REKONO_HOME
RUN chown -R rekono:rekono /code
RUN chown -R rekono:rekono /data
RUN chown -R rekono:rekono /opt
RUN chown rekono:rekono /entrypoint.sh
RUN echo "rekono ALL=(ALL) NOPASSWD:/etc/init.d/postgresql,/var/run/postgresql,/etc/init.d/redis-server" >> /etc/sudoers

# Final system configuration
USER rekono
WORKDIR /code
