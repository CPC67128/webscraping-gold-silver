#!/bin/sh
echo "[$(date)] Container started — running initial scrape..."
python /app/webscraping.py
echo "[$(date)] Initial scrape done. Starting cron (next run at 06:55)..."
exec cron -f
