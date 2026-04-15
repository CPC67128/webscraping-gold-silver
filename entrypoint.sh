#!/bin/sh
echo "[$(date)] Container started — running initial scrape..."
python /app/webscraping-gold-silver.py
echo "[$(date)] Initial scrape done. Starting cron (next run at 06:55)..."
exec cron -f
