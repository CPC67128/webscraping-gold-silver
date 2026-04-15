# CLAUDE.md — Project context for Claude Code

## What this project does

A Python script that scrapes gold and silver coin/bar prices from `achat-or-et-argent.fr` and persists them to a MariaDB database for historical tracking. It runs as a one-shot Docker container, scheduled externally (e.g. cron on the host or a homelab scheduler).

## Key files

| File | Role |
|---|---|
| `webscraping-goldsilver.py` | Single entry point — scrapes 4 items, writes to DB |
| `webscraping.conf` | Runtime credentials (gitignored, never in image) |
| `webscraping.conf.template` | Committed template showing required keys |
| `Dockerfile` | Builds the image; does NOT embed `webscraping.conf` |
| `requirements.txt` | Pinned Python deps |
| `.github/workflows/build-and-push.yml` | CI: build + push to private LAN registry |

## Database credentials — secret handling

- Config format: INI file read via Python's `configparser`
- At runtime the script resolves the config file in this order:
  1. `/run/secrets/webscraping.conf` (Docker secret / bind-mount)
  2. `./webscraping.conf` (local dev fallback, next to the script)
- The file is excluded from the Docker image via `.dockerignore`
- In CI (`build-and-push.yml`) the GitHub Actions secret `DB_CONF_SECRET` is echoed to `webscraping.conf` before the build (used for the run step, not baked into the image)

## Infrastructure

- **Private Docker registry**: `192.168.1.192:5000` — on the home LAN
- **MariaDB host**: `192.168.1.165` — on the home LAN
- **CI runner**: self-hosted (Linux), required because the runner needs LAN access to push to the registry

## Known issue — filename mismatch

The Dockerfile currently references `webscraping-gold-silver.py` (with hyphen) but the actual file on disk is `webscraping-goldsilver.py` (no hyphen). These must be made consistent or the image build will fail. Pick one name and apply it to both.

## Adding a new item to scrape

Add a `WebScrap("ITEM NAME", "https://...")` call at the bottom of `webscraping-goldsilver.py`. No other changes needed.

## Local development

```bash
cp webscraping.conf.template webscraping.conf   # fill in credentials
pip install -r requirements.txt
python webscraping-goldsilver.py
```

## Docker run (after build)

```bash
docker run --rm \
  --mount type=bind,source=$(pwd)/webscraping.conf,target=/run/secrets/webscraping.conf \
  192.168.1.192:5000/webscraping-gold-silver:latest
```
