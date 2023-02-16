#! /bin/sh

if [ ! -e /etc/nginx/tls/privatekey.key ] || [ ! -e  /etc/nginx/tls/certificate.crt ]
then
    exec openssl req -x509 \
        -nodes \
        -days 365 \
        -newkey rsa:4096 \
        -sha512 \
        -keyout /etc/nginx/tls/privatekey.key \
        -out /etc/nginx/tls/certificate.crt \
        -subj "/C=ES/ST=Spain/L=Spain/O=Rekono/OU=Security/CN=Rekono"
fi

exec nginx -g "daemon off;"