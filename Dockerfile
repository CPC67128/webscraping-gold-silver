FROM python:3.11-slim-bookworm

# System deps for the mariadb Python connector
RUN apt-get update && apt-get install -y --no-install-recommends \
        libmariadb-dev \
        gcc \
        cron \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY webscraping.py .
COPY webscraping.conf .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Run the scraper every day at 6:55 AM; redirect output to Docker logs via /proc/1/fd/1
RUN echo "55 6 * * * root python /app/webscraping.py >> /proc/1/fd/1 2>> /proc/1/fd/2" \
        > /etc/cron.d/webscraping \
    && chmod 0644 /etc/cron.d/webscraping

# Run an initial scrape on startup, then hand off to cron
ENTRYPOINT ["/app/entrypoint.sh"]
