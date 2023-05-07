FROM nginx:1.22-alpine

# Install requirements
RUN apk update && apk add openssl

# Configure Nginx
COPY docker/nginx/nginx.conf /etc/nginx/nginx.conf
COPY docker/nginx/entrypoint.sh /entrypoint.sh
RUN mkdir /etc/nginx/tls
RUN touch /var/run/nginx.pid

# System user
RUN chown nginx:nginx /var/run/nginx.pid
RUN chown -R nginx:nginx /var/cache/nginx
RUN chown -R nginx:nginx /var/log/nginx
RUN chown -R nginx:nginx /etc/nginx/conf.d
RUN chown -R nginx:nginx /etc/nginx/tls
RUN chown nginx:nginx /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Final system configuration
USER nginx
EXPOSE 80 443
ENTRYPOINT ["/entrypoint.sh"]
