FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS build-backend

COPY src/backend/ /code
COPY config.yaml /rekono/

RUN mkdir -p /opt/python/ /dpkg && \
    # Explicitly install python in order to export it to the next stage
    uv python install --managed-python --install-dir /tmp/python && \
    # Save python environment
    apt update && \
    apt install --yes --no-install-recommends jq apt-rdepends && \
    mv /tmp/python/$(uv python list --only-installed --output-format json | jq -c '.[0].key' | sed 's/"//g')/* /opt/python/ && \
    # Install python dependencies
    uv sync --no-dev --locked --project /code --python /opt/python/bin/python  && \
    # Download debian dependencies to export them to the next stage
    PACKAGES="libpq-dev libmagic1 libgcc-s1" && \
    rm -rf /var/cache/apt/archives /var/lib/apt/lists && \
    apt update && \
    apt install --reinstall --download-only --yes --no-install-recommends $PACKAGES && \
    apt-rdepends --state-show=Installed --state-follow=Installed $PACKAGES | grep -vE '^( |PreDepends:|Depends:)' | sort -u | awk '{print $1}' | xargs -r apt install --reinstall --download-only --yes --no-install-recommends && \
    for package in /var/cache/apt/archives/*.deb; do dpkg-deb -x $package /dpkg; done


FROM gcr.io/distroless/base-debian12:nonroot AS backend

ENV PATH=/opt/python/bin:$PATH
ENV REKONO_HOME=/rekono

COPY --from=build-backend --chown=65532:65532 /rekono /rekono
COPY --from=build-backend --chown=65532:65532 /code /code
COPY --from=build-backend /dpkg /
COPY --from=build-backend /opt/python /opt/python
COPY --from=build-backend /usr/local/bin/uv /bin/
COPY --from=busybox:stable /bin/wget /usr/bin/wget

WORKDIR /code
EXPOSE 8000


FROM node:22.15.1-bookworm-slim AS build-frontend

COPY src/frontend /code
WORKDIR /code
RUN npm install && npm run build


FROM gcr.io/distroless/nodejs22-debian12:nonroot AS frontend

COPY --from=build-frontend --chown=65532:65532 /code/.output/ /app
COPY --from=busybox:stable /bin/wget /usr/bin/wget

WORKDIR /app
EXPOSE 3000
CMD ["server/index.mjs"]


FROM kalilinux/kali-last-release:latest AS build-worker

RUN apt update && \
    apt install --download-only --reinstall -y --no-install-recommends nmap dirsearch theharvester nikto sslscan sslyze cmseek zaproxy exploitdb metasploit-framework emailharvester joomscan gitleaks smbmap nuclei gobuster seclists dirb && \
    mkdir -p /dpkg && \
    for package in /var/cache/apt/archives/*.deb; do dpkg-deb -xv $package /dpkg; done && \
    apt autoremove -y && \
    apt clean -y && \
    apt autoclean -y && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /var/cache/apt/*


FROM debian:bookworm-slim AS worker

ENV PATH=/opt/python/bin:$PATH
ENV REKONO_HOME=/rekono

COPY --from=build-backend --chown=65532:65532 --chmod=660 /rekono /rekono
COPY --from=build-backend --chown=65532:65532 /code /code
COPY --from=build-backend /dpkg /
COPY --from=build-worker /dpkg /
COPY --from=build-backend /opt/python /opt/python
COPY --from=build-backend /usr/local/bin/uv /bin/

RUN uv tool install emailfinder && \
    uv tool install ssh-audit && \
    apt update && \
    apt install git -y --no-install-recommends && \
    mkdir -p /opt && \
    git clone https://github.com/fullhunt/log4j-scan.git /opt/log4j-scan && \
    git clone https://github.com/fullhunt/spring4shell-scan.git /opt/spring4shell-scan && \
    git clone https://github.com/internetwache/GitTools.git /opt/GitTools && \
    apt remove git -y && \
    apt autoremove -y && \
    apt clean -y && \
    apt autoclean -y && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /var/cache/apt/* && \
    uv pip install --system -r /opt/log4j-scan/requirements.txt && \
    uv pip install --system -r /opt/spring4shell-scan/requirements.txt

# TODO: Which user is running this?
WORKDIR /code
