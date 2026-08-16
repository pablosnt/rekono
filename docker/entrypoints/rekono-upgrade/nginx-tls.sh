#!/bin/sh

# Rekono 1.x kept the nginx TLS certificate in a directory of the repository and Rekono 2.x keeps it
# in a Docker volume, so an existing certificate would be ignored and nginx would generate a new
# self-signed one. The certificate is copied to the volume to avoid that, no matter if the user
# provided it or Rekono 1.x self-signed it, since both are stored in the same place and the
# self-signed one is the certificate that the users already trusted in their browsers. This needs to
# run as root, since the certificate has to belong to the nginx user

set -eu

CERTIFICATE="certificate.crt"
PRIVATE_KEY="privatekey.key"

if [ -f "${NGINX_TLS}/${CERTIFICATE}" ] || [ -f "${NGINX_TLS}/${PRIVATE_KEY}" ]; then
    echo "[i] TLS certificate already available"
elif [ ! -f "${LEGACY_NGINX_TLS}/${CERTIFICATE}" ] || [ ! -f "${LEGACY_NGINX_TLS}/${PRIVATE_KEY}" ]; then
    # New installation
    echo "[i] No TLS certificate to be migrated"
else
    echo "[i] Migrating the TLS certificate"
    cp "${LEGACY_NGINX_TLS}/${CERTIFICATE}" "${NGINX_TLS}/${CERTIFICATE}"
    cp "${LEGACY_NGINX_TLS}/${PRIVATE_KEY}" "${NGINX_TLS}/${PRIVATE_KEY}"
    chmod 644 "${NGINX_TLS}/${CERTIFICATE}"
    chmod 600 "${NGINX_TLS}/${PRIVATE_KEY}"
    chown "${NGINX_UID}:${NGINX_GID}" "${NGINX_TLS}/${CERTIFICATE}" "${NGINX_TLS}/${PRIVATE_KEY}"
    echo "[i] TLS certificate migrated successfully"
fi

# This service mounts the volume before nginx does it, so the empty directory would belong to root
# and the nginx user couldn't create the self-signed certificate that it needs
chown "${NGINX_UID}:${NGINX_GID}" "${NGINX_TLS}"
