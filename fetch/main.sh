#!/bin/sh
python init_db.py
echo "starting fetch cron"
crontab /etc/cron.d/main.cron
crond -f