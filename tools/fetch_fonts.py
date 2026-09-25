# -*- coding: utf-8 -*-
"""Скачивает нужные шрифты Google Fonts (woff2) локально в fonts/ и генерирует css/fonts.css,
чтобы сайт не зависел от внешнего resources (в РФ fonts.googleapis часто недоступен)."""
import os
import re
import urllib.request

WD = r"C:\Users\ilfat\del-pizza"
FONT_DIR = os.path.join(WD, "fonts")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
CSS_URL = ("https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800"
           "&family=Open+Sans:wght@400;600;700&display=swap")


def get(url, ua=UA):
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    return urllib.request.urlopen(req, timeout=40).read()


def main():
    os.makedirs(FONT_DIR, exist_ok=True)
    css = get(CSS_URL).decode()
    # пары «/* subset */ @font-face {...}»
    pairs = re.findall(r"/\*\s*([a-z-]+)\s*\*/\s*(@font-face\s*{[^}]+})", css)
    out = ["/* локальные шрифты — сгенерировано tools/fetch_fonts.py */"]
    n = 0
    for subset, block in pairs:
        fam = re.search(r"font-family:\s*'([^']+)'", block).group(1)
        weight = re.search(r"font-weight:\s*(\d+)", block).group(1)
        m = re.search(r"url\((https://[^)]+\.woff2)\)", block)
        urange = re.search(r"unicode-range:\s*([^;]+);", block)
        if not m:
            continue
        fname = f"{fam.lower().replace(' ', '-')}-{weight}-{subset}.woff2"
        path = os.path.join(FONT_DIR, fname)
        if not os.path.exists(path):
            data = get(m.group(1))
            with open(path, "wb") as f:
                f.write(data)
        new_block = block.replace(m.group(1), f"../fonts/{fname}")
        if urange:
            new_block = new_block.replace(urange.group(1), urange.group(1).strip())
        out.append(new_block)
        n += 1
    out_css = "\n".join(out) + "\n"
    with open(os.path.join(WD, "css", "fonts.css"), "w", encoding="utf-8") as f:
        f.write(out_css)
    total = sum(os.path.getsize(os.path.join(FONT_DIR, x)) for x in os.listdir(FONT_DIR))
    print(f"fonts: {n} @font-face, files: {len(os.listdir(FONT_DIR))}, {total // 1024} KB")


if __name__ == "__main__":
    main()
