# -*- coding: utf-8 -*-
"""Self-test Del'pizza: вставляет тест-скрипт в копию index.html, гоняет headless Chrome,
парсит JSON-отчёт из #__report и проверяет наличие всех фото каталога."""
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

TEST_JS = r"""
<script>
(async () => {
  const R = { errors: [] };
  const $ = s => document.querySelector(s);
  const $$ = s => [...document.querySelectorAll(s)];
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  try {
    R.cards = $$('#grid .card').length;
    R.chips = $$('#cats .chip').length;
    R.hits = $$('#hits .card').length;
    R.foundLbl = $('#foundCount').textContent;

    // фильтр по категории
    const rollsChip = $$('#cats .chip').find(c => c.textContent.includes('Роллы'));
    rollsChip.click();
    const rc = $$('#grid .card');
    R.rollCards = rc.length;
    R.rollOk = rc.every(c => c.dataset.id.startsWith('roll'));

    // поиск
    $$('#cats .chip')[0].click();
    const s = $('#search');
    s.value = 'пепперони'; s.dispatchEvent(new Event('input'));
    R.searchCount = $$('#grid .card').length;
    s.value = ''; s.dispatchEvent(new Event('input'));

    // сортировка «сначала дешевле»
    const so = $('#sort'); so.value = 'cheap'; so.dispatchEvent(new Event('change'));
    R.firstCheap = $('#grid .card .price') ? $('#grid .card .price').textContent.trim() : '';
    so.value = 'pop'; so.dispatchEvent(new Event('change'));

    // корзина: добавить 2 позиции
    $('#grid .card [data-add]').click();
    const second = $$('#grid .card')[1].querySelector('[data-add]');
    second.click();
    R.badge = $('#cartBadge').textContent;
    R.cartSumAfterAdd = $('#cartSum').textContent;

    // корзина, промокод
    $('#cartBtn').click();
    R.drawerOpen = $('#drawer').classList.contains('on');
    R.drawerItems = $$('#drBody .ci').length;
    $('#toCheckout').click();
    R.checkoutOpen = $('#mCheckout').classList.contains('on');
    $('#promoInp').value = 'DEL15'; $('#promoBtn').click();
    R.discRowVisible = !$('#coDiscRow').hidden;
    R.disc = $('#coDisc').textContent;
    R.total = $('#coTotal').textContent;

    // оформление с онлайн-оплатой
    $('#fName').value = 'Тест'; $('#fPhone').value = '+79659374088';
    $('#fAddr').value = 'ул. Тестовая, 1';
    $('#payOnline').click();
    R.payNote = !$('#payTestNote').hidden;
    $('#fAgree').checked = true;
    $('#coSubmit').click();
    R.payModalOpen = $('#mPay').classList.contains('on');
    $('#payGo').click();
    await sleep(2200);
    R.okOpen = $('#mOk').classList.contains('on');
    R.okNum = $('#okNum').textContent;
    R.okHasText = $('#okOrder').textContent.indexOf('Заказ №') >= 0;
    R.okHasPizza = $('#okOrder').textContent.indexOf('Пепперони') >= 0;
    R.payDemoMark = $('#okOrder').textContent.indexOf('демо') >= 0;
    try { R.cartCleared = (JSON.parse(localStorage.getItem('dp_cart') || '[]').length === 0); } catch (e) { R.cartCleared = false; }
    try { R.orderLogged = (JSON.parse(localStorage.getItem('dp_orders') || '[]').length >= 1); } catch (e) { R.orderLogged = false; }

    // таймер и мелочи
    R.timer = $('#tmr').textContent;
    R.timer2 = $('#tmr2') ? $('#tmr2').textContent : '';
    R.imgs = $$('#grid img').length;
    R.brokenImgs = $$('#grid img').filter(i => i.complete && i.naturalWidth === 0).length;
  } catch (e) { R.errors.push(String(e && e.stack || e)); }
  const pre = document.createElement('pre');
  pre.id = '__report';
  pre.textContent = JSON.stringify(R);
  document.body.appendChild(pre);
})();
</script>
"""


def chrome_run(url, out=None, extra=None, budget=26000, w=1440, h=2400):
    cmd = [CHROME, "--headless=new", "--no-sandbox", "--disable-gpu",
           "--enable-unsafe-swiftshader", "--hide-scrollbars", "--force-prefers-reduced-motion",
           f"--window-size={w},{h}", f"--virtual-time-budget={budget}"]
    if out:
        cmd.append("--screenshot=" + out)
    if extra:
        cmd.extend(extra)
    cmd.append(url)
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)


def main():
    html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    test_html = html.replace("</body>", TEST_JS + "\n</body>")
    tpath = os.path.join(ROOT, "_selftest.html")
    open(tpath, "w", encoding="utf-8").write(test_html)

    url = "file:///" + tpath.replace("\\", "/")
    r = chrome_run(url, extra=["--dump-dom"])
    m = re.search(r'<pre id="__report">(.*?)</pre>', r.stdout, re.S)
    if not m:
        print("REPORT NOT FOUND. Chrome rc:", r.returncode)
        print(r.stdout[-1500:])
        sys.exit(1)
    rep = json.loads(m.group(1))
    print(json.dumps(rep, ensure_ascii=False, indent=1))

    # --- проверки ---
    fails = []
    def check(cond, name):
        if not cond:
            fails.append(name)

    check(rep["chips"] == 10, f"чипов категорий 10 (={rep['chips']})")
    check(rep["cards"] >= 40, f"карточек >= 40 (={rep['cards']})")
    check(rep["hits"] == 8, f"хитов 8 (={rep['hits']})")
    check(rep["rollCards"] == 8, f"роллов 8 (={rep['rollCards']})")
    check(rep["rollOk"], "фильтр по категории корректен")
    check(rep["searchCount"] == 1, f"поиск 'пепперони' = 1 (={rep['searchCount']})")
    check("369" in rep["firstCheap"].replace("\u00a0", ""), f"сначала дешевле (={rep['firstCheap']})")
    check(rep["badge"] == "2", f"бейдж корзины 2 (={rep['badge']})")
    check(rep["drawerOpen"] and rep["drawerItems"] == 2, f"корзина: 2 позиции (={rep['drawerItems']})")
    check(rep["checkoutOpen"], "оформление открылось")
    check(rep["discRowVisible"] and rep["disc"] != "−0 ₽", f"промокод применён (={rep['disc']})")
    check(rep["payNote"], "пометка тестового режима оплаты")
    check(rep["payModalOpen"], "экран оплаты открылся")
    check(rep["okOpen"], "экран успеха после демо-оплаты")
    check(rep["okHasPizza"], "в заказе есть позиция")
    check(rep["payDemoMark"], "в заказе пометка «демо»")
    check(rep["cartCleared"], "корзина очищена после заказа")
    check(rep["orderLogged"], "заказ сохранён в журнал")
    check(len(rep["timer"]) == 8 and rep["timer"] != "00:00:00", f"таймер идёт (={rep['timer']})")
    check(rep["brokenImgs"] == 0, f"битых фото 0 (={rep['brokenImgs']} из {rep['imgs']})")
    check(not rep["errors"], f"JS-ошибок нет: {rep['errors']}")

    # --- фото каталога ---
    data = open(os.path.join(ROOT, "js", "data.js"), encoding="utf-8").read()
    ids = re.findall(r'id:\s*"([a-z0-9-]+)"', data)
    miss = [i for i in ids if not os.path.exists(os.path.join(ROOT, "img", i + ".jpg"))]
    print(f"\nфото: {len(ids) - len(miss)}/{len(ids)}" + (f", НЕТ: {miss}" if miss else " — все на месте"))

    os.remove(tpath)
    if fails or miss:
        print("\nFAIL:")
        for f in fails:
            print(" -", f)
        if miss:
            print(" - нет фото:", miss)
        sys.exit(1)
    print("\nALL GREEN ✓")


if __name__ == "__main__":
    main()
