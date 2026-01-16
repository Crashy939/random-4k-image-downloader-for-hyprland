#!/usr/bin/env python3

import os
import sys
import time
import random
import hashlib
import subprocess
import logging
import re
from pathlib import Path
from urllib.parse import urljoin
from PIL import Image
import subprocess

import requests
from bs4 import BeautifulSoup

# ================= CONFIG =================

BASE_URL = "https://4kwallpapers.com"
RANDOM_URL = "https://4kwallpapers.com/random-wallpapers/"

WALLPAPER_DIR = Path.home() / ".local/share/wallpapers/4kwallpapers"
CACHE_DIR = Path.home() / ".cache/4kwallpapers"
HASH_FILE = CACHE_DIR / "hashes.txt"

MIN_WIDTH = 1920
MIN_HEIGHT = 1080

MAX_WALLPAPERS = 20
MIN_WAIT = 60      # minutes
MAX_WAIT = 180     # minutes

BLOCK_SIZE = 1024 * 1024

# ==========================================

logging.basicConfig(level=logging.INFO, format="%(message)s")

WALLPAPER_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)
HASH_FILE.touch(exist_ok=True)



def dominant_color(path):
    img = Image.open(path).convert("RGB")
    img = img.resize((64, 64))
    pixels = img.getdata()

    r = sum(p[0] for p in pixels) // len(pixels)
    g = sum(p[1] for p in pixels) // len(pixels)
    b = sum(p[2] for p in pixels) // len(pixels)

    return r, g, b

def set_hypr_borders(img_path):
    r, g, b = dominant_color(img_path)

    active = f"rgba({r:02x}{g:02x}{b:02x}ff)"
    inactive = "rgba(aaaaaacc)"

    subprocess.run([
        "hyprctl", "keyword",
        "general:col.active_border",
        f"{active} {active}"
    ])

    subprocess.run([
        "hyprctl", "keyword",
        "general:col.inactive_border",
        inactive
    ])

# ---------- HELPERS ----------

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd):
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ---------- SWWW ----------

def ensure_swww():
    if subprocess.run(["pgrep", "-x", "swww-daemon"],
                      stdout=subprocess.DEVNULL).returncode != 0:
        run(["swww-daemon"])
        time.sleep(1)


def set_wallpaper(path):
    ensure_swww()
    run(["swww", "img", str(path)])

# ---------- HYPRLAND COLORS ----------

def update_colors(path):
    run(["wallust", "run", str(path)])

    # fallback gray border for inactive
    run([
        "hyprctl", "keyword",
        "general:col.inactive_border",
        "rgba(888888aa)"
    ])


# ---------- NOTIFY ----------

def notify(name):
    run([
        "notify-send",
        "Wallpaper actualizado",
        name
    ])


# ---------- SCRAPING ----------

def fetch_html(url):
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    return BeautifulSoup(r.text, "lxml")


def find_pages():
    soup = fetch_html(RANDOM_URL)
    for a in soup.select("a[itemprop='url']"):
        yield urljoin(BASE_URL, a["href"])


def extract_image(soup):
    link = soup.find("a", id="resolution")
    if not link:
        return None

    text = link.text.lower()

    # Extraer resolución tipo 3840 x 2160
    match = re.search(r"(\d{3,5})\s*x\s*(\d{3,5})", text)
    if not match:
        return None

    w, h = map(int, match.groups())

    if w < MIN_WIDTH or h < MIN_HEIGHT:
        return None

    href = link.get("href")
    if not href:
        return None

    return urljoin(BASE_URL, href)


def download(url):
    name = url.split("/")[-1]
    path = WALLPAPER_DIR / name

    if path.exists():
        return path

    r = requests.get(url, stream=True)
    r.raise_for_status()

    with open(path, "wb") as f:
        for chunk in r.iter_content(BLOCK_SIZE):
            f.write(chunk)

    h = sha256(path)
    hashes = HASH_FILE.read_text().splitlines()

    if h in hashes:
        path.unlink()
        return None

    with open(HASH_FILE, "a") as f:
        f.write(h + "\n")

    return path


# ---------- WALLPAPER MGMT ----------

def cleanup():
    files = sorted(WALLPAPER_DIR.glob("*"), key=os.path.getmtime)
    while len(files) > MAX_WALLPAPERS:
        files[0].unlink()
        files.pop(0)


def pick_random():
    files = list(WALLPAPER_DIR.glob("*"))
    return random.choice(files) if files else None


# ---------- MAIN LOGIC ----------

def change_wallpaper():
    for page in find_pages():
        soup = fetch_html(page)
        img = extract_image(soup)
        if not img:
            continue

        path = download(img)
        if not path:
            continue

        set_wallpaper(path)
        set_hypr_borders(path)
        update_colors(path)
        notify(path.name)
        cleanup()
        return


def daemon():
    while True:
        change_wallpaper()
        wait = random.randint(MIN_WAIT, MAX_WAIT)
        time.sleep(wait * 60)


# ---------- ENTRY ----------

if __name__ == "__main__":
    if "--next" in sys.argv:
        change_wallpaper()
    else:
        daemon()
