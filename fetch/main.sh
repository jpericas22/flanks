#!/bin/sh
python init_db.py
crontab /etc/cron.d/main.cron
echo "started fetch cron"
crond -f