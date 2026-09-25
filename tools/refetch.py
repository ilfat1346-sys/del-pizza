#!/usr/bin/env python3
"""Кандидаты фото для проблемных позиций: пачкой в img/cand/<slug>_cN.jpg (640px).
После прогона — контакт-лист и ручной выбор."""
import json
import os
import time
import urllib.parse
import urllib.request
from io import BytesIO

from PIL import Image

OUT = os.path.join(os.getcwd(), "img", "cand")
UA = {"User-Agent": "Mozilla/5.0 (demo-site-image-fetcher)"}
NEG = ["logo", "icon", "diagram", "map", "menu", "stamp", "poster", "coat of arms",
       "advert", "illustration", "drawing", "svg"]

TARGETS = {
    "pizza-four-cheese": ["quattro formaggi pizza", "four cheese pizza", "cheese pizza whole"],
    "pizza-hawaiian": ["hawaiian pizza", "pineapple pizza slice", "pizza pineapple ham"],
    "pizza-meat": ["salami pizza", "meat pizza whole", "pizza sausage"],
    "roll-philadelphia": ["sushi roll salmon cream cheese", "philadelphia sushi roll", "salmon avocado roll"],
    "roll-california": ["california roll sushi", "crab maki roll", "sushi roll avocado crab"],
    "combo-friday": ["pizza chicken wings", "pizza and chicken", "chicken wings cola"],
    "burger-cheese": ["cheeseburger closeup", "cheeseburger molten cheese", "hamburger cheese"],
    "doner-chicken": ["doner kebab plate", "shawarma chicken plate", "chicken wrap plate"],
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
    if low.endswith((".svg", ".tif", ".tiff", ".ogg", ".stl", ".webm", ".pdf", ".gif")):
        return False
    return not any(n in low for n in NEG)


def main():
    os.makedirs(OUT, exist_ok=True)
    log = {}
    for slug, queries in TARGETS.items():
        got = 0
        names = []
        for q in queries:
            if got >= 8:
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
                if got >= 8:
                    break
                t = page.get("title", "")
                if not ok(t):
                    continue
                ii = (page.get("imageinfo") or [{}])[0]
                u = ii.get("thumburl") or ii.get("url")
                if not u:
                    continue
                p = os.path.join(OUT, f"{slug}_c{got}.jpg")
                if dl(u, p):
                    names.append(t[5:80])
                    got += 1
            time.sleep(0.5)
        log[slug] = names
        print(f"{slug}: {got} кандидатов", flush=True)
    with open(os.path.join(OUT, "names.json"), "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=1)
    print("done")


if __name__ == "__main__":
    main()
