FROM python:3.8.5-alpine3.12

WORKDIR /src
COPY . .
RUN pip install -r deps.txt
RUN tar zxf dockerize-alpine-linux-amd64-v0.6.1.tar.gz
RUN mkdir keys
RUN chmod +x main.sh
COPY main.cron /etc/cron.d/main.cron
RUN chmod 0644 /etc/cron.d/main.cron
RUN touch /var/log/cron.log

CMD ["./main.sh"]