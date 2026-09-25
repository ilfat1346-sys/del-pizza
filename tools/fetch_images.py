#!/usr/bin/env python3
"""Скачать бесплатные фото блюд для демо-каталога Del'pizza (Wikimedia Commons -> Openverse)."""
import json
import os
import time
import urllib.parse
import urllib.request
from io import BytesIO

from PIL import Image

OUT = os.path.join(os.getcwd(), "img")
UA = {"User-Agent": "Mozilla/5.0 (demo-site-image-fetcher)"}

GENERIC_NEG = ["logo", "icon", "diagram", "patent", "drawing", "schematic", "chart",
               "symbol", "poster", "stamp", "map", "coat of arms", "certificate",
               "menu", "sign", "restaurant facade", "packaging", "advert"]

# (slug, запросы, must-слова, негативы)
ITEMS = [
    ("pizza-pepperoni", ["pepperoni pizza", "pizza pepperoni slices"], ["pizza"], []),
    ("pizza-margherita", ["pizza margherita", "margherita pizza basil"], ["pizza", "margherita"], []),
    ("pizza-four-cheese", ["four cheese pizza", "quattro formaggi pizza"], ["pizza"], ["pizza box"]),
    ("pizza-meat", ["meat pizza", "pizza with ham and bacon"], ["pizza"], []),
    ("pizza-hawaiian", ["hawaiian pizza pineapple", "pizza ham pineapple"], ["pizza"], []),
    ("pizza-diablo", ["spicy pizza chili", "pizza with jalapeno"], ["pizza"], ["pizza box"]),
    ("pizza-caesar", ["chicken caesar pizza", "pizza chicken salad"], ["pizza"], []),
    ("pizza-del", ["pizza mushrooms ham", "mushroom pizza"], ["pizza"], ["pizza box"]),
    ("combo-2-pizza", ["two pizzas table", "pizza delivery boxes open"], ["pizza"], []),
    ("combo-friends", ["pizza party table", "many pizzas party"], ["pizza"], []),
    ("combo-rolls", ["sushi set rolls", "sushi platter rolls"], ["sushi", "roll"], []),
    ("combo-friday", ["pizza and chicken wings", "pizza wings cola"], ["pizza"], []),
    ("roll-philadelphia", ["philadelphia roll salmon", "sushi roll salmon cream cheese"], ["roll", "sushi"], []),
    ("roll-california", ["california roll crab", "sushi roll crab avocado"], ["roll", "sushi"], []),
    ("roll-baked-salmon", ["baked sushi roll salmon", "baked roll sushi"], ["roll", "sushi"], []),
    ("roll-spicy-chicken", ["spicy chicken sushi roll", "sushi roll chicken spicy"], ["roll", "sushi"], []),
    ("roll-veg", ["vegetable sushi roll", "avocado cucumber maki"], ["roll", "maki", "sushi"], []),
    ("roll-dragon", ["dragon roll sushi", "sushi roll eel avocado"], ["roll", "sushi"], []),
    ("roll-maki-cucumber", ["cucumber maki", "kappa maki sushi"], ["maki", "roll", "sushi"], []),
    ("roll-unagi", ["unagi roll eel", "eel sushi roll"], ["roll", "sushi", "eel"], []),
    ("doner-chicken", ["shawarma chicken", "doner kebab chicken"], ["shawarma", "doner", "kebab"], []),
    ("doner-beef", ["beef shawarma", "doner kebab beef"], ["shawarma", "doner", "kebab"], []),
    ("shawarma-spicy", ["shawarma wrap spicy", "wrap shawarma"], ["shawarma", "wrap", "doner"], []),
    ("burger-cheese", ["cheeseburger", "cheese burger closeup"], ["burger"], []),
    ("burger-chicken", ["chicken burger", "chicken sandwich burger"], ["burger"], []),
    ("burger-double", ["double cheeseburger", "double burger"], ["burger"], []),
    ("fries", ["french fries", "fries basket"], ["fries", "chips"], []),
    ("nuggets", ["chicken nuggets", "nuggets plate"], ["nuggets", "chicken"], []),
    ("wings-bbq", ["chicken wings bbq", "barbecue chicken wings"], ["wings", "chicken"], []),
    ("cheese-balls", ["fried cheese balls", "cheese croquettes"], ["cheese", "ball", "croquette"], []),
    ("tiramisu", ["tiramisu dessert", "tiramisu slice"], ["tiramisu"], []),
    ("cheesecake", ["cheesecake slice", "cheesecake dessert"], ["cheesecake"], []),
    ("honey-cake", ["honey cake slice", "medovik cake"], ["cake", "honey"], []),
    ("cola", ["cola glass ice", "coca cola glass"], ["cola", "coke"], []),
    ("mors", ["berry juice glass", "berry drink glass"], ["juice", "drink", "berry"], ["wine"]),
    ("cappuccino", ["cappuccino cup", "cappuccino coffee cup"], ["cappuccino", "coffee"], []),
    ("latte", ["latte glass", "caffe latte cup"], ["latte", "coffee"], []),
    ("milkshake", ["milkshake vanilla", "vanilla milkshake glass"], ["milkshake", "shake"], []),
    ("juice", ["orange juice glass", "juice glass bottle"], ["juice"], ["wine"]),
    ("sauce-cheese", ["cheese sauce bowl dip", "dipping sauce bowl"], ["sauce", "dip"], []),
    ("sauce-garlic", ["garlic sauce bowl", "white sauce dip bowl"], ["sauce", "dip"], []),
    ("sauce-bbq", ["bbq sauce bowl", "barbecue sauce dish"], ["sauce", "dip"], []),
]


def fetch_json(url):
    for _ in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            if "429" in str(e):
                time.sleep(6)
                continue
            raise
    raise RuntimeError("429 persists")


def download(url):
    req = urllib.request.Request(url, headers=UA)
    data = urllib.request.urlopen(req, timeout=40).read()
    if len(data) < 5000:
        return None
    im = Image.open(BytesIO(data)).convert("RGB")
    w, h = im.size
    if w < 420 or h < 260:
        return None
    if max(w, h) > 1000:
        if w >= h:
            im = im.resize((1000, int(h * 1000 / w)), Image.LANCZOS)
        else:
            im = im.resize((int(w * 1000 / h), 1000), Image.LANCZOS)
    return im


def ok_name(name, must, neg):
    low = name.lower()
    if low.endswith(".svg"):
        return False
    if any(n in low for n in neg) or not any(m in low for m in must):
        return False
    return True


def save(slug, im, tag, note):
    im.save(os.path.join(OUT, slug + ".jpg"), "JPEG", quality=82)
    print(f"OK-{tag} {slug} <- {note}", flush=True)


def from_commons(slug, queries, must, neg):
    for q in queries:
        api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
            "action": "query", "format": "json", "generator": "search",
            "gsrsearch": f"filetype:bitmap {q}", "gsrnamespace": 6, "gsrlimit": 16,
            "prop": "imageinfo", "iiprop": "url|size", "iiurlwidth": 1000})
        try:
            d = fetch_json(api)
        except Exception:
            time.sleep(2)
            continue
        for page in ((d.get("query") or {}).get("pages") or {}).values():
            title = page.get("title", "")
            if not ok_name(title, must, neg):
                continue
            ii = (page.get("imageinfo") or [{}])[0]
            u = ii.get("thumburl") or ii.get("url")
            if not u:
                continue
            try:
                im = download(u)
            except Exception:
                continue
            if im is None:
                continue
            save(slug, im, "commons", f"[{q}] {title[5:70]}")
            return True
        time.sleep(0.5)
    return False


def from_openverse(slug, queries, must, neg):
    for q in queries:
        api = "https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(
            {"q": q, "page_size": 14, "license_type": "commercial", "mature": "false"})
        try:
            d = fetch_json(api)
        except Exception:
            time.sleep(2)
            continue
        for res in d.get("results", []):
            title = ((res.get("title") or "") + " " + (res.get("description") or "")).lower()
            if any(n in title for n in neg) or not any(m in title for m in must):
                continue
            u = res.get("url")
            if not u or u.lower().endswith(".svg"):
                continue
            try:
                im = download(u)
            except Exception:
                continue
            if im is None:
                continue
            save(slug, im, "openverse", f"[{q}] {(res.get('title') or '')[:60]}")
            return True
        time.sleep(0.4)
    return False


def main():
    os.makedirs(OUT, exist_ok=True)
    misses = []
    for slug, queries, must, neg in ITEMS:
        if os.path.exists(os.path.join(OUT, slug + ".jpg")):
            print(f"SKIP {slug} (exists)", flush=True)
            continue
        if not (from_commons(slug, queries, must, neg + GENERIC_NEG)
                or from_openverse(slug, queries, must, neg + GENERIC_NEG)):
            misses.append(slug)
    have = [f for f in os.listdir(OUT) if f.endswith(".jpg")]
    print(f"\nTotal: {len(have)} images | MISS: {misses or 'none'}")


if __name__ == "__main__":
    main()
