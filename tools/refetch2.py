#!/usr/bin/env python3
"""Второй раунд: кандидаты для проблемных позиций -> img/cand2/<slug>_cN.jpg (640px).
Для 'ov' позиций сначала Openverse (дипы/напитки лучше на Flickr)."""
import json
import os
import time
import urllib.parse
import urllib.request
from io import BytesIO

from PIL import Image

OUT = os.path.join(os.getcwd(), "img", "cand2")
UA = {"User-Agent": "Mozilla/5.0 (demo-site-image-fetcher)"}
NEG = ["logo", "icon", "diagram", "map", "menu", "stamp", "poster", "coat of arms",
       "advert", "illustration", "drawing", "truck", "street", "city", "sign",
       "restaurant facade", "building"]
GEN_NEG = ["svg", ".tif", ".ogg", ".pdf", ".webm"]

# slug: (запросы, порядок [commons-first | ov-first])
TARGETS = {
    "combo-2-pizza": (["two pizzas table top view", "two whole pizzas"], "c"),
    "combo-friends": (["pizza table many pizzas top", "four pizzas on wooden table"], "c"),
    "roll-dragon": (["dragon roll sushi avocado", "sushi roll avocado on top"], "c"),
    "roll-maki-cucumber": (["maki rolls plate sushi", "cucumber maki rolls plate"], "c"),
    "roll-unagi": (["unagi eel roll sushi plate", "eel sushi roll closeup"], "c"),
    "roll-spicy-chicken": (["sushi rolls platter closeup", "sushi rolls with spicy sauce"], "c"),
    "doner-beef": (["doner kebab sandwich", "beef doner wrap sandwich"], "c"),
    "shawarma-spicy": (["shawarma roll closeup", "kebab wrap closeup"], "c"),
    "burger-double": (["double cheeseburger closeup", "double patty burger"], "c"),
    "nuggets": (["chicken nuggets plate closeup", "fried nuggets with dip"], "c"),
    "cheese-balls": (["fried cheese balls plate", "breaded cheese balls fried"], "c"),
    "wings-bbq": (["barbecue chicken wings glazed", "bbq wings plate closeup"], "c"),
    "tiramisu": (["tiramisu on plate", "tiramisu dessert closeup plate"], "c"),
    "honey-cake": (["medovik honey cake slice", "layer honey cake slice plate"], "c"),
    "cola": (["glass of cola ice cubes", "cola drink glass ice"], "c"),
    "mors": (["berry drink glass pitcher", "cranberry juice glass"], "o"),
    "latte": (["latte art cup top view", "caffe latte cup saucer"], "c"),
    "milkshake": (["vanilla milkshake tall glass", "milkshake glass straw"], "o"),
    "sauce-cheese": (["cheese dip bowl", "cheese sauce bowl dip"], "o"),
    "sauce-garlic": (["garlic aioli sauce bowl", "white sauce dip bowl"], "o"),
    "sauce-bbq": (["bbq sauce bowl ramekin", "barbecue sauce bowl"], "o"),
}


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
    raise RuntimeError("429")


def dl(url, path):
    try:
        req = urllib.request.Request(url, headers=UA)
        data = urllib.request.urlopen(req, timeout=40).read()
        if len(data) < 4000:
            return False
        im = Image.open(BytesIO(data)).convert("RGB")
        w, h = im.size
        if w < 380 or h < 240:
            return False
        im.thumbnail((640, 640), Image.LANCZOS)
        im.save(path, "JPEG", quality=80)
        return True
    except Exception:
        return False


def ok(title):
    low = title.lower()
    if any(g in low for g in GEN_NEG):
        return False
    return not any(n in low for n in NEG)


def commons(slug, queries, need):
    got = 0
    names = []
    for q in queries:
        if got >= need:
            break
        api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
            "action": "query", "format": "json", "generator": "search",
            "gsrsearch": f"filetype:bitmap {q}", "gsrnamespace": 6, "gsrlimit": 20,
            "prop": "imageinfo", "iiprop": "url|size", "iiurlwidth": 640})
        try:
            d = fetch_json(api)
        except Exception:
            time.sleep(2)
            continue
        for page in ((d.get("query") or {}).get("pages") or {}).values():
            if got >= need:
                break
            t = page.get("title", "")
            if not ok(t):
                continue
            ii = (page.get("imageinfo") or [{}])[0]
            u = ii.get("thumburl") or ii.get("url")
            if not u:
                continue
            if dl(u, os.path.join(OUT, f"{slug}_c{got}.jpg")):
                names.append("C:" + t[5:75])
                got += 1
        time.sleep(0.5)
    return got, names


def openverse(slug, queries, need, start=0):
    got = start
    names = []
    for q in queries:
        if got >= need:
            break
        api = "https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(
            {"q": q, "page_size": 15, "license_type": "commercial", "mature": "false"})
        try:
            d = fetch_json(api)
        except Exception:
            time.sleep(2)
            continue
        for res in d.get("results", []):
            if got >= need:
                break
            title = ((res.get("title") or "") + " " + (res.get("description") or ""))
            if not ok(title):
                continue
            u = res.get("url")
            if not u or u.lower().endswith((".svg", ".gif")):
                continue
            if dl(u, os.path.join(OUT, f"{slug}_c{got}.jpg")):
                names.append("O:" + title[:70].strip())
                got += 1
        time.sleep(0.4)
    return got, names


def main():
    os.makedirs(OUT, exist_ok=True)
    log = {}
    for slug, (queries, order) in TARGETS.items():
        if order == "o":
            got, names = openverse(slug, queries, 7)
            if got < 4:
                g2, n2 = commons(slug, queries, 7 - got)
                got += g2
                names += n2
        else:
            got, names = commons(slug, queries, 7)
            if got < 4:
                g2, n2 = openverse(slug, queries, 7 - got, start=got)
                got += g2
                names += n2
        log[slug] = names
        print(f"{slug}: {got}", flush=True)
    with open(os.path.join(OUT, "names.json"), "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=1)
    print("done")


if __name__ == "__main__":
    main()
