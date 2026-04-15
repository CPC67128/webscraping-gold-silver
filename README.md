# webscraping-gold-silver

Scrapes buy prices for gold and silver items from [gold-silver](https://www.achat-or-et-argent.fr) and stores them in a MariaDB database for historical tracking.

## What it tracks

Items to scrape are defined in `webscraping.conf` — no code change needed to add or remove items.

| Item | URL |
|---|---|
| 5 Francs Semeuse 1959–1969 | /argent/5-francs-semeuse-1959-1969/22 |
| Lingot 250g Argent | /argent/lingot-250g-argent/3602 |
| 20 Francs Napoléon | /or/20-francs-napoleon/6 |
| Lingot 500g Argent | /argent/lingot-500g-argent/3603 |

Each run inserts one row per item into the `ItemValueOverTime` table.

---

## Database schema (expected)

```sql
CREATE TABLE ItemValueOverTime (
    Id        INT AUTO_INCREMENT PRIMARY KEY,
    Item      VARCHAR(255),
    TypeValue VARCHAR(50),
    FloatValue VARCHAR(50),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Configuration

All settings live in `webscraping.conf` (INI format). Copy the template and fill in your values:

```bash
cp webscraping.conf.template webscraping.conf
# then edit webscraping.conf
```

`webscraping.conf` format:

```ini
[database]
user     = your_db_user
password = your_db_password
host     = 192.168.1.165
port     = 3306
database = web_scraping

[scraper]
# HTTP proxy for debugging (e.g. 127.0.0.1:8080). Leave empty to disable.
proxy =

[gold-silver]
# Format: "Item display name" = "URL to scrape"
"5 FRANCS SEMEUSE 1959-1969" = "https://www.achat-or-et-argent.fr/argent/5-francs-semeuse-1959-1969/22"
"LINGOT 250G ARGENT"         = "https://www.achat-or-et-argent.fr/argent/lingot-250g-argent/3602"
```

> `webscraping.conf` is listed in `.gitignore` and must **never** be committed to the repository.

---

## Running locally

```bash
pip install -r requirements.txt
python webscraping-gold-silver.py
```

The script looks for `webscraping.conf` in the same directory as itself.

---

## Docker

The container runs the scraper **once on startup**, then keeps running and fires again every day at **06:55** via an internal cron job. Logs are visible via `docker logs`.

### Build

```bash
docker build -t webscraping-gold-silver .
```

`webscraping.conf` must be present at build time — it is baked into the image.

### Run

```bash
docker run -d --name webscraping webscraping-gold-silver
```

### View logs

```bash
docker logs webscraping
```

---

## CI/CD — GitHub Actions

The workflow at [.github/workflows/build-and-push.yml](.github/workflows/build-and-push.yml):

- Triggers on every push to `main`
- Runs on a **self-hosted runner** (required for LAN access to the private registry at `192.168.1.192:5000`)
- Writes `webscraping.conf` from the `WEBSCRAPING_CONF_SECRET` GitHub Actions secret before building
- Builds the image with the config baked in and pushes it as `192.168.1.192:5000/webscraping-gold-silver:latest`

### Required GitHub secret

| Secret name | Content |
|---|---|
| `WEBSCRAPING_CONF_SECRET` | Full contents of `webscraping.conf` |

To add it: **Repository → Settings → Secrets and variables → Actions → New repository secret**.

---

## Project structure

```
.
├── webscraping-gold-silver.py                 # Main scraper script
├── entrypoint.sh                  # Runs initial scrape then starts cron
├── webscraping.conf               # Config and credentials (gitignored)
├── webscraping.conf.template      # Config template (committed)
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
└── .github/
    └── workflows/
        └── build-and-push.yml
```
