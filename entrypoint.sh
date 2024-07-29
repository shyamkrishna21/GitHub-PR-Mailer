#!/bin/bash

# Activate virtual environment for any interactive commands
source /venv/bin/activate

# Add cron job
echo "*/3 * * * * /venv/bin/python /app/main.py >> /var/log/cron.log 2>&1" > /etc/cron.d/github-pr-cron
chmod 0644 /etc/cron.d/github-pr-cron
crontab /etc/cron.d/github-pr-cron

# Create log directory and file
mkdir -p /var/log
touch /var/log/cron.log

# Start cron service in the foreground
cron -f
