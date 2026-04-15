# webscraping-gold-silver

Scrapes buy prices for gold and silver items from [achat-or-et-argent.fr](https://www.achat-or-et-argent.fr) and stores them in a MariaDB database for historical tracking.

## What it tracks

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

Database credentials are **never hardcoded**. They are read at startup from a `webscraping.conf` file (INI format).

Copy the template and fill in your values:

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
```

> `webscraping.conf` is listed in `.gitignore` and `.dockerignore` and must **never** be committed or baked into the image.

---

## Running locally

```bash
pip install -r requirements.txt
python webscraping-goldsilver.py
```

The script looks for `webscraping.conf` next to itself when no Docker secret is present.

---

## Docker

### Build

```bash
docker build -t webscraping-gold-silver .
```

### Run (with secret file mounted)

```bash
docker run --rm \
  --mount type=bind,source=/path/to/webscraping.conf,target=/run/secrets/webscraping.conf \
  webscraping-gold-silver
```

At startup the script checks `/run/secrets/webscraping.conf` first, then falls back to a local `webscraping.conf`.

---

## CI/CD — GitHub Actions

The workflow at [.github/workflows/build-and-push.yml](.github/workflows/build-and-push.yml):

- Triggers on every push to `main`
- Runs on a **self-hosted runner** (required for LAN access to the private registry at `192.168.1.192:5000`)
- Reads `DB_CONF_SECRET` from GitHub Actions secrets, writes it to `webscraping.conf` before the build
- Builds the image and pushes it as `192.168.1.192:5000/webscraping-gold-silver:latest`

### Required GitHub secret

| Secret name | Content |
|---|---|
| `DB_CONF_SECRET` | Full contents of `webscraping.conf` |

To add it: **Repository → Settings → Secrets and variables → Actions → New repository secret**.

---

## Project structure

```
.
├── webscraping-goldsilver.py      # Main scraper script
├── webscraping.conf.template               # Config template (committed)
├── webscraping.conf                        # Actual credentials (gitignored)
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
└── .github/
    └── workflows/
        └── build-and-push.yml
```
