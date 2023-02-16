# Rekono Docker environment

## Docker Images

### Kali

Dockerfile used for executions-queue worker. This Docker image is created from `kalilinux` image and includes all the [supported tools](../docs/TOOLS.md) and the required resources.


### Nginx

Dockerfile used to create a reverse proxy to forward Rekono requests to the backend or the frontend. This Docker image is created from `nginx` image.

You can configure the TLS connection setting up your `certificate.crt` and `privatekey.key` files in the [nginx/tls/](nginx/tls/) directory. If you don't, a self-signed certificate will be generated automatically on Nginx start.

You can check the Nginx configuration [here](nginx/nginx.conf).


### Rekono

#### Backend

Dockerfile used to deploy the Rekono backend. This Docker image is created from `python` image.


#### Frontend

Dockerfile used to deploy the Rekono frontend. This Docker image is created from `node` image.


## Configuration

### Initial Rekono user

You can configure the intial user data establishing the following environment variables before deploy Docker:

- `RKN_EMAIL`: User email address. If not set, `rekono@rekono.com` will be used.
- `RKN_USERNAME`: Username. If not set, `rekono` will be used.
- `RKN_PASSWORD`: User password. If not set, `rekono` will be used.


### SMTP configuration

By default, the Docker environment will use the `catatnight/postfix` image to send emails, but emails sent using this method can be ignored by some email services due to security reasons. So, you can configure your own SMTP server using the following environment variables:

- `RKN_EMAIL_HOST`
- `RKN_EMAIL_PORT`
- `RKN_EMAIL_USER`
- `RKN_EMAIL_PASSWORD`


## Deployment

You can follow [this steps](../README.md#docker) to deploy Rekono in Docker.
