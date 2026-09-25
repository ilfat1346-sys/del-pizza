#!/usr/bin/env python3
"""Третий раунд: combo-friends, shawarma-spicy, nuggets, honey-cake -> img/cand4/."""
import json
import os
import time
import urllib.parse
import urllib.request
from io import BytesIO

from PIL import Image

OUT = os.path.join(os.getcwd(), "img", "cand4")
UA = {"User-Agent": "Mozilla/5.0 (demo-site-image-fetcher)"}
NEG = ["logo", "icon", "diagram", "map", "menu", "stamp", "poster", "coat of arms",
       "advert", "illustration", "drawing", "truck", "street", "city", "sign", "building"]

TARGETS = {
    "sauce-cheese": (["cheese dip ramekin", "cheese sauce bowl warm", "queso dip bowl"], "c"),
    "sauce-garlic": (["garlic sauce ramekin", "aioli bowl sauce", "white sauce ramekin"], "c"),
    "sauce-bbq": (["bbq sauce ramekin", "barbecue sauce cup", "sauce ramekin"], "c"),
    "nuggets": (["chicken nuggets basket", "nuggets with ketchup plate", "chicken nuggets close up"], "c"),
    "roll-california": (["california roll top view", "sushi roll tobiko top", "california maki plate"], "c"),
    "combo-2-pizza": (["two pizzas wooden board", "two pizza pies table", "two pizzas top view"], "c"),
    "combo-friends": (["pizzas on table overhead", "several pizzas table top view", "three pizzas board"], "c"),
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
    if any(g in low for g in (".svg", ".tif", ".ogg", ".pdf", ".webm")):
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
    for slug, (queries, _) in TARGETS.items():
        got, names = commons(slug, queries, 8)
        if got < 4:
            g2, n2 = openverse(slug, queries, 8 - got, start=got)
            got += g2
            names += n2
        log[slug] = names
        print(f"{slug}: {got}", flush=True)
    with open(os.path.join(OUT, "names.json"), "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=1)
    print("done")


if __name__ == "__main__":
    main()
