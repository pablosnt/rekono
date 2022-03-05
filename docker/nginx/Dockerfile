FROM nginx:1.21.6-alpine

COPY docker/nginx/nginx.conf /etc/nginx/nginx.conf

RUN touch /var/run/nginx.pid
RUN chown -R nginx:nginx /var/run/nginx.pid
RUN chown -R nginx:nginx /var/cache/nginx
RUN chown -R nginx:nginx /var/log/nginx
RUN chown -R nginx:nginx /etc/nginx/conf.d
USER nginx

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
