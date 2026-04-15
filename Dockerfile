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

# webscraping.conf is NOT copied here — it is injected at runtime as a Docker secret
# mounted at /run/secrets/webscraping.conf

# Run the scraper every day at 6:55 AM; redirect output to Docker logs via /proc/1/fd/1
RUN echo "55 6 * * * root python /app/webscraping.py >> /proc/1/fd/1 2>> /proc/1/fd/2" \
        > /etc/cron.d/webscraping \
    && chmod 0644 /etc/cron.d/webscraping

# cron -f keeps cron in the foreground as PID 1
CMD ["cron", "-f"]
