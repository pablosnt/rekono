FROM nginx:1.28-alpine-slim

COPY docker/nginx/entrypoint.sh /usr/local/bin/
COPY docker/nginx/nginx.conf /etc/nginx/nginx.conf

RUN apk update && \
    apk add openssl --no-cache && \
    touch /run/nginx.pid && \
    mkdir -p /etc/nginx/tls/ && \
    chmod +x /usr/local/bin/entrypoint.sh && \
    chown nginx:nginx /run/nginx.pid && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx

USER nginx
EXPOSE 80 443
ENTRYPOINT ["entrypoint.sh"]