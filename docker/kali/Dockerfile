FROM kalilinux/kali-rolling

RUN mkdir /rekono
COPY config.yaml /rekono

RUN mkdir /code
COPY rekono/ /code
COPY requirements.txt /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update && apt install python3-pip libpq-dev python3-dev libmagic1 libcap2-bin -y
RUN ln -s /usr/bin/python3 /usr/bin/python

RUN pip install --upgrade pip
RUN pip install -r /code/requirements.txt

RUN apt install nmap dirsearch theharvester nikto sslscan sslyze cmseek zaproxy exploitdb metasploit-framework emailharvester joomscan gitleaks -y
RUN setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip $(which nmap)
RUN git clone https://github.com/cisagov/log4j-scanner.git /opt/log4j-scanner
RUN git clone https://github.com/internetwache/GitTools.git /opt/GitTools
RUN pip install -r /opt/log4j-scanner/log4-scanner/requirements.txt
RUN pip install emailfinder

RUN apt install wordlists seclists dirb -y
RUN gzip -d /usr/share/wordlists/rockyou.txt.gz

RUN adduser --disabled-password rekono
RUN chown -R rekono:rekono /code
RUN chown -R rekono:rekono /rekono
RUN chown -R rekono:rekono /usr/share/cmseek

USER rekono
WORKDIR /code