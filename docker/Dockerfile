FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS build-backend

COPY src/backend/ /code

# Explicitly install python in order to export it to the next stage
RUN uv python install --managed-python --install-dir /tmp/python && \
    # Save python environment
    apt update && \
    apt install jq -y --no-install-recommends && \
    mkdir -p /opt/python/ && \
    mv /tmp/python/$(uv python list --only-installed --output-format json | jq -c '.[0].key' | sed 's/"//g')/* /opt/python/ && \
    # Install python dependencies
    uv sync --no-dev --locked --project /code --python /opt/python/bin/python  && \
    # Download debian dependencies to export them to the next stage
    apt install apt-rdepends -y --no-install-recommends && \
    apt download $(apt-rdepends libpq-dev build-essential libmagic-dev | grep -v "^ " | grep -v "^libc-dev$") && \
    mkdir -p /dpkg && \
    for package in *.deb; do \
        dpkg-deb --extract $package /dpkg || exit 1; \
    done && \
    apt remove apt-rdepends jq -y && \
    apt autoremove -y && \
    apt clean -y && \
    apt autoclean -y && \
    rm -rf /var/lib/apt/lists/* && \
    # Define script to initialize database
    echo "uv run manage.py migrate" > /code/initializer.sh && \
    echo "uv run manage.py createsuperuser --no-input" >> /code/initializer.sh && \
    chmod +x /code/initializer.sh


FROM node:22.15.1-bookworm-slim AS build-frontend

COPY src/frontend /code
WORKDIR /code

RUN npm install && npm run build


FROM gcr.io/distroless/base-debian12:nonroot AS backend

ENV PATH=/opt/python/bin:$PATH
ENV REKONO_HOME=/rekono

COPY --chown=65532:65532 config.yaml /rekono/
COPY --from=build-backend --chown=65532:65532 /code /code
COPY --from=build-backend /dpkg /
COPY --from=build-backend /opt/python /opt/python
COPY --from=build-backend /usr/local/bin/uv /bin/

WORKDIR /code
EXPOSE 8000


FROM gcr.io/distroless/nodejs22-debian12:nonroot AS frontend

COPY --from=build-frontend --chown=65532:65532 /code/.output /code

WORKDIR /code
EXPOSE 3000

CMD ["server/index.mjs"]