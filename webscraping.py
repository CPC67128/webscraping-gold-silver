import configparser
import mechanize
from datetime import datetime
from bs4 import BeautifulSoup
import mariadb
import os
import sys

# Resolve webscraping.conf: prefer Docker secret mount, fall back to local file for dev
_CONFIG_PATHS = ["/run/secrets/webscraping.conf", os.path.join(os.path.dirname(__file__), "webscraping.conf")]
_config_file = next((p for p in _CONFIG_PATHS if os.path.isfile(p)), None)
if _config_file is None:
    print("ERROR: No webscraping.conf found. Provide it at /run/secrets/webscraping.conf or alongside this script.")
    sys.exit(1)

_db_cfg = configparser.ConfigParser()
_db_cfg.optionxform = str  # preserve key case (item names are uppercase)
_db_cfg.read(_config_file)

DB_USER     = _db_cfg["database"]["user"]
DB_PASSWORD = _db_cfg["database"]["password"]
DB_HOST     = _db_cfg["database"]["host"]
DB_PORT     = int(_db_cfg["database"]["port"])
DB_NAME     = _db_cfg["database"]["database"]

ITEMS = {k.strip('"'): v.strip('"') for k, v in _db_cfg["items"].items()}
PROXY = _db_cfg.get("scraper", "proxy", fallback="").strip()

br = mechanize.Browser()
br.set_handle_robots(False)
br.set_handle_refresh(False)
br.addheaders = [{'User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}]
if PROXY:
    br.set_proxies({"http": PROXY})

def WebScrap(item, url):
    print("> ", item, " - ", url)
    html = br.open(url).read()
    soup = BeautifulSoup(html, "html.parser")

    try:
        itemValue = soup.find_all("span", {"id": "pv"})[0].get_text().strip()
    except:
        print("Unexpected error:", sys.exc_info()[0])
        itemValue = -1

    if itemValue == -1:
        try:
            itemValue = soup.find_all("span", {"id": "tpv"})[0].get_text().strip()
        except:
            print("Unexpected error:", sys.exc_info()[0])
            itemValue = -1

    print(itemValue)

    if itemValue == -1:
        return

    try:
        conn = mariadb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    # Get Cursor
    cur = conn.cursor()

    typeValue = "Float"

    try:
        cur.execute("INSERT INTO `ItemValueOverTime` (Item,TypeValue,FloatValue) VALUES (?,?,?)", (item,typeValue,itemValue))
    except mariadb.Error as e:
        print(f"Error: {e}")

    conn.commit()

    conn.close()

for _item, _url in ITEMS.items():
    WebScrap(_item, _url)

