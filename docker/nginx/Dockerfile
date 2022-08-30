FROM nginx:1.22-alpine

COPY docker/nginx/nginx.conf /etc/nginx/nginx.conf

RUN apk update && apk add openssl
RUN mkdir /etc/nginx/tls
RUN openssl req -x509 \
    -nodes \
    -days 365 \
    -newkey rsa:4096 \
    -sha512 \
    -keyout /etc/nginx/tls/rekono.key \
    -out /etc/nginx/tls/rekono.crt \
    -subj "/C=ES/ST=Spain/L=Spain/O=Rekono/OU=Security/CN=Rekono"

RUN touch /var/run/nginx.pid
RUN chown nginx:nginx /var/run/nginx.pid
RUN chown -R nginx:nginx /var/cache/nginx
RUN chown -R nginx:nginx /var/log/nginx
RUN chown -R nginx:nginx /etc/nginx/conf.d
RUN chown -R nginx:nginx /etc/nginx/tls
USER nginx

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
