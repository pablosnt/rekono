ARG LABEL_CREATED
ARG LABEL_VERSION
ARG LABEL_REVISION
ARG LABEL_URL="https://github.com/pablosnt/rekono"
ARG LABEL_SOURCE="https://github.com/pablosnt/rekono"
ARG LABEL_DOCUMENTATION="https://github.com/pablosnt/rekono/wiki"
ARG LABEL_AUTHORS="Pablo Santiago López"
ARG LABEL_LICENSES="GPL-3.0"

ARG BACKEND_DEBIAN_DEPENDENCIES="libpq-dev libmagic1 libgcc-s1"


FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS build-backend

ARG BACKEND_DEBIAN_DEPENDENCIES

COPY src/backend/ /code
COPY config.yaml /rekono/

RUN mkdir -p /opt/python/ /dpkg && \
    # Explicitly install python in order to export it to the next stage
    uv python install --managed-python --install-dir /tmp/python && \
    # Save python environment
    mv /tmp/python/cpython*/* /opt/python/ && \
    # Install python dependencies
    uv sync --no-dev --locked --project /code --python /opt/python/bin/python  && \
    # Download debian dependencies to export them to the next stage
    rm -rf /var/cache/apt/archives /var/lib/apt/lists && \
    apt update && \
    apt install --yes --no-install-recommends apt-rdepends && \
    apt install --reinstall --download-only --yes --no-install-recommends $BACKEND_DEBIAN_DEPENDENCIES && \
    apt-rdepends --state-show=Installed --state-follow=Installed $BACKEND_DEBIAN_DEPENDENCIES | grep -vE '^( |PreDepends:|Depends:)' | sort -u | awk '{print $1}' | xargs -r apt install --reinstall --download-only --yes --no-install-recommends && \
    for package in /var/cache/apt/archives/*.deb; do dpkg-deb -x $package /dpkg; done


FROM gcr.io/distroless/base-debian12:nonroot AS backend

ARG LABEL_CREATED
ARG LABEL_AUTHORS
ARG LABEL_URL
ARG LABEL_SOURCE
ARG LABEL_DOCUMENTATION
ARG LABEL_VERSION
ARG LABEL_REVISION
ARG LABEL_LICENSES
LABEL org.opencontainers.image.created=$LABEL_CREATED
LABEL org.opencontainers.image.authors=$LABEL_AUTHORS
LABEL org.opencontainers.image.url=$LABEL_URL
LABEL org.opencontainers.image.source=$LABEL_SOURCE
LABEL org.opencontainers.image.documentation=$LABEL_DOCUMENTATION
LABEL org.opencontainers.image.version=$LABEL_VERSION
LABEL org.opencontainers.image.revision=$LABEL_REVISION
LABEL org.opencontainers.image.licenses=$LABEL_LICENSES
LABEL org.opencontainers.image.title="Rekono Backend"
LABEL org.opencontainers.image.description="Rekono backend image based on a distroless debian image"

ENV PATH=/opt/python/bin:$PATH
ENV REKONO_HOME=/rekono

COPY --from=build-backend --chown=65532:65532 /rekono /rekono
COPY --from=build-backend --chown=65532:65532 /code /code
COPY --from=build-backend /dpkg /
COPY --from=build-backend /opt/python /opt/python
COPY --from=build-backend /usr/local/bin/uv /bin/
# Wget needed to perform the healthcheck
COPY --from=busybox:stable /bin/wget /usr/bin/wget

WORKDIR /code
EXPOSE 8000


FROM node:22.15.1-bookworm-slim AS build-frontend

COPY src/frontend /code
WORKDIR /code
# Build frontend for production
RUN npm install && npm run build


FROM gcr.io/distroless/nodejs22-debian12:nonroot AS frontend

ARG LABEL_CREATED
ARG LABEL_AUTHORS
ARG LABEL_URL
ARG LABEL_SOURCE
ARG LABEL_DOCUMENTATION
ARG LABEL_VERSION
ARG LABEL_REVISION
ARG LABEL_LICENSES
LABEL org.opencontainers.image.created=$LABEL_CREATED
LABEL org.opencontainers.image.authors=$LABEL_AUTHORS
LABEL org.opencontainers.image.url=$LABEL_URL
LABEL org.opencontainers.image.source=$LABEL_SOURCE
LABEL org.opencontainers.image.documentation=$LABEL_DOCUMENTATION
LABEL org.opencontainers.image.version=$LABEL_VERSION
LABEL org.opencontainers.image.revision=$LABEL_REVISION
LABEL org.opencontainers.image.licenses=$LABEL_LICENSES
LABEL org.opencontainers.image.title="Rekono Frontend"
LABEL org.opencontainers.image.description="Rekono frontend image based on a distroless debian image"

COPY --from=build-frontend --chown=65532:65532 /code/.output/ /app
# Wget needed to perform the healthcheck
COPY --from=busybox:stable /bin/wget /usr/bin/wget

WORKDIR /app
EXPOSE 3000
CMD ["server/index.mjs"]


FROM kalilinux/kali-last-release:latest AS worker

ARG BACKEND_DEBIAN_DEPENDENCIES

ARG LABEL_CREATED
ARG LABEL_AUTHORS
ARG LABEL_URL
ARG LABEL_SOURCE
ARG LABEL_DOCUMENTATION
ARG LABEL_VERSION
ARG LABEL_REVISION
ARG LABEL_LICENSES
LABEL org.opencontainers.image.created=$LABEL_CREATED
LABEL org.opencontainers.image.authors=$LABEL_AUTHORS
LABEL org.opencontainers.image.url=$LABEL_URL
LABEL org.opencontainers.image.source=$LABEL_SOURCE
LABEL org.opencontainers.image.documentation=$LABEL_DOCUMENTATION
LABEL org.opencontainers.image.version=$LABEL_VERSION
LABEL org.opencontainers.image.revision=$LABEL_REVISION
LABEL org.opencontainers.image.licenses=$LABEL_LICENSES
LABEL org.opencontainers.image.title="Rekono Worker"
LABEL org.opencontainers.image.description="Rekono worker image based on Kali Linux that includes all the hacking tools supported by Rekono"

ENV PATH=/opt/python/bin:$PATH
ENV REKONO_HOME=/rekono

COPY --from=build-backend /opt/python /opt/python
COPY --from=build-backend /usr/local/bin/uv /bin/
COPY --from=build-backend /code /code
WORKDIR /code

# Install hacking tools supported via apt
RUN apt update && \
    TOOLS="nmap theharvester nikto sslscan sslyze cmseek zaproxy exploitdb metasploit-framework emailharvester joomscan gitleaks smbmap nuclei gobuster seclists dirb" && \
    apt install --yes --no-install-recommends $TOOLS $BACKEND_DEBIAN_DEPENDENCIES libcap2-bin git ca-certificates && \
    # Grant capabilities needed to nmap in order to get it running in a rootless environment
    setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip $(which nmap) && \
    # Clean apt resources
    apt autoremove -y && \
    apt clean -y && \
    apt autoclean -y && \
    rm -rf /var/lib/apt/lists /var/cache/apt/ && \
    # Unsatisfied emailharvester dependencies
    uv pip install validators && \
    # Install hacking tools via pip
    uv pip install --system --break-system-packages emailfinder ssh-audit dirsearch && \
    # Unsatisfied dirsearch dependencies
    uv pip install --system --break-system-packages setuptools && \
    # Install hacking tools from source
    mkdir -p /opt && \
    git clone https://github.com/fullhunt/log4j-scan.git /opt/log4j-scan && \
    git clone https://github.com/fullhunt/spring4shell-scan.git /opt/spring4shell-scan && \
    git clone https://github.com/internetwache/GitTools.git /opt/GitTools && \
    uv pip install -r /opt/log4j-scan/requirements.txt && \
    uv pip install -r /opt/spring4shell-scan/requirements.txt && \
    # Update tool resources
    nuclei -update-templates && \
    searchsploit --update || true && \
    # Rootless user
    useradd --uid 65532 --create-home rekono && \
    chown -R rekono:rekono /opt && \
    chown -R rekono:rekono /code && \
    chown -R rekono:rekono /usr/share/cmseek && \
    chown -R rekono:rekono /usr/share/seclists && \
    chown -R rekono:rekono /usr/share/dirb/wordlists

COPY --from=build-backend --chown=rekono:rekono /rekono /rekono
USER rekono
