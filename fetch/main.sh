#!/bin/sh
echo "starting fetch cron"
crontab /etc/cron.d/main.cron
crond -f