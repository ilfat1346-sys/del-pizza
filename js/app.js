// Del'pizza — логика сайта (рендер каталога, корзина, оформление, тестовый режим оплаты)
(() => {
  "use strict";

  // ---------- helpers ----------
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const fmt = (n) => new Intl.NumberFormat("ru-RU").format(Math.round(n)) + " ₽";
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const byId = (id) => PRODUCTS.find((p) => p.id === id);
  const basePrice = (p, size) => (p.sizes ? (p.sizes.find((s) => s[0] === size) || p.sizes[0])[1] : p.price);
  const oldPrice = (p, size) => {
    if (!p.old) return null;
    return p.sizes ? ((p.old.find((s) => s[0] === size) || [0, null])[1]) : p.old;
  };
  const PLACEHOLDER = "data:image/svg+xml;utf8," + encodeURIComponent(
    `<svg xmlns='http://www.w3.org/2000/svg' width='400' height='300'><rect width='400' height='300' fill='#31363f'/><text x='200' y='158' font-size='64' text-anchor='middle'>🍕</text></svg>`);

  // ---------- toasts ----------
  const toasts = $("#toasts");
  function toast(msg, good = false) {
    const t = document.createElement("div");
    t.className = "toast" + (good ? " good" : "");
    t.textContent = msg;
    toasts.appendChild(t);
    setTimeout(() => { t.style.opacity = "0"; t.style.transition = ".3s"; }, 2300);
    setTimeout(() => t.remove(), 2700);
  }

  // ---------- cart ----------
  let cart = [];
  try { cart = JSON.parse(localStorage.getItem("dp_cart") || "[]") || []; } catch { cart = []; }
  const saveCart = () => localStorage.setItem("dp_cart", JSON.stringify(cart));
  const keyOf = (it) => it.id + (it.size ? ":" + it.size : "");
  const cartCount = () => cart.reduce((s, i) => s + i.qty, 0);
  const cartSum = () => cart.reduce((s, i) => { const p = byId(i.id); return p ? s + basePrice(p, i.size) * i.qty : s; }, 0);

  function addToCart(id, size, qty = 1, silent = false) {
    const p = byId(id); if (!p) return;
    if (p.sizes && !size) size = p.sizes[0][0];
    const k = keyOf({ id, size });
    const ex = cart.find((i) => keyOf(i) === k);
    if (ex) ex.qty += qty; else cart.push({ id, size: p.sizes ? size : null, qty });
    saveCart(); renderCart(); bumpCartBtn();
    if (!silent) toast(`Добавлено: ${p.name}${p.sizes ? " (" + size + " см)" : ""}`, true);
  }
  function setQty(k, d) {
    const i = cart.find((x) => keyOf(x) === k); if (!i) return;
    i.qty += d;
    if (i.qty <= 0) cart = cart.filter((x) => keyOf(x) !== k);
    saveCart(); renderCart();
  }
  function bumpCartBtn() {
    const b = $("#cartBtn");
    b.animate([{ transform: "scale(1)" }, { transform: "scale(1.09)" }, { transform: "scale(1)" }], { duration: 260 });
  }

  // ---------- render: categories & catalog ----------
  let activeCat = "all";
  let sortMode = "pop";
  let query = "";

  function renderCats() {
    const wrap = $("#cats");
    wrap.innerHTML = [{ id: "all", name: "Все блюда" }, ...CATS].map((c) =>
      `<button class="chip ${c.id === activeCat ? "on" : ""}" data-cat="${c.id}">${esc(c.name)}</button>`).join("");
    wrap.onclick = (e) => {
      const b = e.target.closest(".chip"); if (!b) return;
      activeCat = b.dataset.cat; renderCats(); renderCatalog();
    };
    $$("[data-cat-link]").forEach((l) => l.onclick = (e) => {
      e.preventDefault(); activeCat = l.dataset.catLink; renderCats(); renderCatalog();
      $("#menu")?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }

  function prodCard(p) {
    const badges = [];
    if (p.badge === "Хит") badges.push('<span class="badge b-hit">Хит</span>');
    else if (p.badge === "Новинка") badges.push('<span class="badge b-new">Новинка</span>');
    else if (p.badge === "Острая" || p.badge === "Острый") badges.push('<span class="badge b-spicy">Острое</span>');
    else if (p.badge) badges.push(`<span class="badge b-sale">${esc(p.badge)}</span>`);
    const price = basePrice(p);
    const oldp = oldPrice(p);
    const sizesHtml = p.sizes ? `<div class="sz">` + p.sizes.map(([cm, pr], i) =>
      `<label title="${fmt(pr)}"><input type="radio" name="s-${p.id}" value="${cm}" ${i === 0 ? "checked" : ""} data-pid="${p.id}"><span>${cm} см</span></label>`).join("") + `</div>` : "";
    return `<article class="card" data-id="${p.id}">
      <div class="ph" data-open="${p.id}">${badges.join("")}${p.ico ? `<div class="ph-ico">${p.ico}</div>` : `<img loading="lazy" src="img/${p.id}.jpg" alt="${esc(p.name)}" onerror="this.onerror=null;this.src='${PLACEHOLDER}'">`}</div>
      <div class="bd">
        <div class="nm" data-open="${p.id}">${esc(p.name)}</div>
        <div class="sp">${esc(p.spec || "")}</div>
        <div class="ds">${esc(p.desc)}</div>
        ${sizesHtml}
        <div class="pr">
          <div class="price" data-price="${p.id}">${oldp ? `<s>${fmt(oldp)}</s>` : ""}${fmt(price)}</div>
          <button class="add-btn" data-add="${p.id}" title="В корзину">+</button>
        </div>
      </div>
    </article>`;
  }

  function renderCatalog() {
    let list = PRODUCTS.slice();
    if (activeCat !== "all") list = list.filter((p) => p.cat === activeCat);
    if (query) { const q = query.toLowerCase(); list = list.filter((p) => (p.name + " " + p.desc).toLowerCase().includes(q)); }
    if (sortMode === "pop") list.sort((a, b) => (b.pop || 0) - (a.pop || 0));
    else if (sortMode === "cheap") list.sort((a, b) => basePrice(a) - basePrice(b));
    else if (sortMode === "expensive") list.sort((a, b) => basePrice(b) - basePrice(a));
    $("#grid").innerHTML = list.map(prodCard).join("") || `<div class="dr-empty"><div class="em">🔍</div>Ничего не нашлось</div>`;
    $("#foundCount").textContent = list.length;
  }

  // hits rail
  function renderHits() {
    const hits = PRODUCTS.slice().sort((a, b) => (b.pop || 0) - (a.pop || 0)).slice(0, 8);
    $("#hits").innerHTML = hits.map(prodCard).join("");
  }

  // events for catalog + hits (delegation)
  function bindCatalogEvents(root) {
    root.addEventListener("click", (e) => {
      const add = e.target.closest("[data-add]");
      if (add) {
        const p = byId(add.dataset.add);
        const size = p && p.sizes ? +($(`input[name="s-${p.id}"]:checked`)?.value || p.sizes[0][0]) : null;
        addToCart(add.dataset.add, size);
        return;
      }
      const op = e.target.closest("[data-open]");
      if (op) openProduct(op.dataset.open);
    });
    root.addEventListener("change", (e) => {
      const r = e.target;
      if (r.matches('input[type="radio"][data-pid]')) {
        const p = byId(r.dataset.pid);
        const pr = basePrice(p, +r.value);
        const op = oldPrice(p, +r.value);
        const box = $(`[data-price="${p.id}"]`);
        if (box) box.innerHTML = (op ? `<s>${fmt(op)}</s>` : "") + fmt(pr);
      }
    });
  }

  // ---------- product modal ----------
  let mQty = 1, mSize = null, mPid = null;
  function openProduct(id) {
    const p = byId(id); if (!p) return;
    mPid = id; mQty = 1;
    mSize = p.sizes ? p.sizes[0][0] : null;
    const mi = $("#mImg"), ic = $("#mIco");
    if (p.ico) { mi.style.display = "none"; ic.style.display = "flex"; ic.textContent = p.ico; }
    else {
      mi.style.display = ""; ic.style.display = "none";
      mi.src = `img/${p.id}.jpg`;
      mi.onerror = function () { this.onerror = null; this.src = PLACEHOLDER; };
      mi.alt = p.name;
    }
    $("#mName").textContent = p.name;
    $("#mSpec").textContent = p.spec || "";
    $("#mDesc").textContent = p.desc;
    $("#mSizes").innerHTML = p.sizes ? `<div class="sz" style="max-width:330px">` + p.sizes.map(([cm, pr], i) =>
      `<label title="${fmt(pr)}"><input type="radio" name="ms" value="${cm}" ${i === 0 ? "checked" : ""}><span>${cm} см</span></label>`).join("") + `</div>` : "";
    updateMPrice();
    $("#mQty").textContent = mQty;
    openModal("#mProduct");
  }
  function updateMPrice() {
    const p = byId(mPid); if (!p) return;
    const pr = basePrice(p, mSize), op = oldPrice(p, mSize);
    $("#mPrice").innerHTML = (op ? `<s>${fmt(op)}</s>` : "") + fmt(pr * mQty);
  }
  $("#mSizes").addEventListener("change", (e) => { if (e.target.name === "ms") { mSize = +e.target.value; updateMPrice(); } });
  $("#mPlus").onclick = () => { mQty = Math.min(20, mQty + 1); $("#mQty").textContent = mQty; updateMPrice(); };
  $("#mMinus").onclick = () => { mQty = Math.max(1, mQty - 1); $("#mQty").textContent = mQty; updateMPrice(); };
  $("#mAdd").onclick = () => { addToCart(mPid, mSize, mQty); closeModal("#mProduct"); };

  // ---------- modals ----------
  function openModal(sel) { $(sel).classList.add("on"); document.body.style.overflow = "hidden"; }
  function closeModal(sel) { $(sel).classList.remove("on"); document.body.style.overflow = ""; }
  $$("[data-close]").forEach((b) => b.onclick = () => closeModal("#" + b.dataset.close));
  $$(".modal .m-bg").forEach((bg) => {
    bg.onclick = () => { bg.closest(".modal").classList.remove("on"); document.body.style.overflow = ""; };
  });

  // ---------- cart drawer ----------
  const drawer = $("#drawer"), ovBg = $("#ovBg");
  function openDrawer() { drawer.classList.add("on"); ovBg.classList.add("on"); }
  function closeDrawer() { drawer.classList.remove("on"); ovBg.classList.remove("on"); }
  $("#cartBtn").onclick = openDrawer;
  $("#drClose").onclick = closeDrawer;
  ovBg.onclick = () => { closeDrawer(); $$(".modal").forEach((m) => m.classList.remove("on")); };

  function renderCart() {
    const body = $("#drBody");
    if (!cart.length) {
      body.innerHTML = `<div class="dr-empty"><div class="em">🛒</div>Корзина пока пустая.<br>Добавьте что-нибудь вкусное!</div>`;
    } else {
      body.innerHTML = cart.map((i) => {
        const p = byId(i.id); if (!p) return "";
        const k = keyOf(i);
        const pr = basePrice(p, i.size);
        return `<div class="ci">
          ${p.ico ? `<div class="ci-ico">${p.ico}</div>` : `<img src="img/${p.id}.jpg" alt="" onerror="this.onerror=null;this.src='${PLACEHOLDER}'">`}
          <div class="ci-b">
            <div class="ci-n">${esc(p.name)}${i.size ? ` · ${i.size} см` : ""}</div>
            <div class="ci-s">${esc(p.spec || "")}</div>
            <div class="ci-r">
              <div class="stepper">
                <button data-dec="${k}">−</button><i>${i.qty}</i><button data-inc="${k}">+</button>
              </div>
              <div class="price">${fmt(pr * i.qty)}</div>
            </div>
          </div>
          <button class="ci-x" data-del="${k}" title="Убрать">✕</button>
        </div>`;
      }).join("");
    }
    const sum = cartSum();
    const count = cartCount();
    $("#drCount").textContent = count ? ` · ${count} шт` : "";
    $("#cartBadge").textContent = count; $("#cartBadge").hidden = !count;
    $("#cartSum").textContent = fmt(sum);
    $("#drSum").textContent = fmt(sum);
    const left = SHOP.deliveryFrom - sum;
    $("#drHint").hidden = !(cart.length);
    $("#drHint").innerHTML = left > 0
      ? `🚚 До бесплатной доставки осталось <b>${fmt(left)}</b> (от ${fmt(SHOP.deliveryFrom)})`
      : `🚚 Доставка бесплатная!`;
    $("#toCheckout").disabled = !cart.length;
  }
  $("#drBody").addEventListener("click", (e) => {
    const inc = e.target.closest("[data-inc]"), dec = e.target.closest("[data-dec]"), del = e.target.closest("[data-del]");
    if (inc) setQty(inc.dataset.inc, 1);
    else if (dec) setQty(dec.dataset.dec, -1);
    else if (del) { cart = cart.filter((x) => keyOf(x) !== del.dataset.del); saveCart(); renderCart(); }
  });

  // ---------- checkout ----------
  let promo = null; // {code, pct}
  const PROMOS = { "DEL15": 15, "PIZZA10": 10 };
  function orderTotals() {
    const sum = cartSum();
    const disc = promo ? Math.round(sum * promo.pct / 100) : 0;
    const deliv = $("#fDelivery")?.checked ? (sum - disc >= SHOP.deliveryFrom ? 0 : 150) : 0;
    return { sum, disc, deliv, total: sum - disc + deliv };
  }
  function renderCheckout() {
    if (!cart.length) { closeModal("#mCheckout"); openDrawer(); return; }
    const t = orderTotals();
    $("#coItems").innerHTML = cart.map((i) => {
      const p = byId(i.id);
      return `<div class="sum-line"><span>${esc(p.name)}${i.size ? ` · ${i.size} см` : ""} × ${i.qty}</span><b>${fmt(basePrice(p, i.size) * i.qty)}</b></div>`;
    }).join("");
    $("#coSum").textContent = fmt(t.sum);
    $("#coDisc").textContent = "−" + fmt(t.disc);
    $("#coDiscRow").hidden = !t.disc;
    $("#coDeliv").textContent = t.deliv ? fmt(t.deliv) : "бесплатно";
    $("#coTotal").textContent = fmt(t.total);
    $("#coAddrField").hidden = !$("#fDelivery").checked;
    $("#payTestNote").hidden = !$("#payOnline").checked;
  }
  $("#fDelivery").onchange = $("#fPickup").onchange = () => renderCheckout();
  $("#payOnline").onchange = $("#payCard").onchange = () => { $("#payTestNote").hidden = !$("#payOnline").checked; };
  $("#promoBtn").onclick = () => {
    const code = ($("#promoInp").value || "").trim().toUpperCase();
    if (!code) return;
    if (PROMOS[code]) { promo = { code, pct: PROMOS[code] }; toast(`Промокод ${code}: скидка ${promo.pct}%`, true); }
    else { promo = null; toast("Промокод не найден 🤔"); }
    renderCheckout();
  };
  $("#toCheckout").onclick = () => { renderCheckout(); openModal("#mCheckout"); };
  $("#coBack").onclick = () => { closeModal("#mCheckout"); openDrawer(); };

  // order assembly & demo payment flow
  let pendingOrder = null;
  function buildOrderText(num) {
    const t = orderTotals();
    const lines = cart.map((i, n) => {
      const p = byId(i.id);
      return `${n + 1}. ${p.name}${i.size ? ` (${i.size} см)` : ""} × ${i.qty} = ${fmt(basePrice(p, i.size) * i.qty)}`;
    });
    const way = $("#fDelivery").checked ? `доставка: ${$("#fAddr").value.trim() || "адрес уточнить по телефону"}` : "самовывоз";
    const pay = $("#payOnline").checked ? "онлайн (тестовый режим)" : "при получении";
    const comment = $("#fComment").value.trim();
    return `🍕 Заказ №${num} с сайта Del'pizza\n\n${lines.join("\n")}\n` +
      (promo ? `\nПромокод ${promo.code}: −${fmt(t.disc)}` : "") +
      `\nИтого: ${fmt(t.total)} (в т.ч. доставка ${t.deliv ? fmt(t.deliv) : "бесплатно"})\n\n` +
      `Получение: ${way}\nОплата: ${pay}\nИмя: ${$("#fName").value.trim() || "—"}\nТелефон: ${$("#fPhone").value.trim() || "—"}` +
      (comment ? `\nКомментарий: ${comment}` : "");
  }

  $("#coSubmit").onclick = () => {
    const name = $("#fName").value.trim();
    const phone = $("#fPhone").value.trim();
    if (name.length < 2) { toast("Напишите имя"); $("#fName").focus(); return; }
    if (phone.replace(/\D/g, "").length < 10) { toast("Проверьте телефон"); $("#fPhone").focus(); return; }
    if ($("#fDelivery").checked && $("#fAddr").value.trim().length < 4) { toast("Укажите адрес доставки"); $("#fAddr").focus(); return; }
    if (!$("#fAgree").checked) { toast("Нужно согласие на обработку данных"); return; }
    pendingOrder = { num: Math.floor(Math.random() * 900 + 100), online: $("#payOnline").checked };
    if (pendingOrder.online) { closeModal("#mCheckout"); openModal("#mPay"); }
    else finalizeOrder();
  };

  // demo payment screen
  $("#payGo").onclick = () => {
    $("#payGo").disabled = true; $("#payGo").textContent = "Обрабатываем…";
    setTimeout(() => {
      $("#payGo").disabled = false; $("#payGo").textContent = "Оплатить (демо)";
      closeModal("#mPay"); finalizeOrder(true);
    }, 1500);
  };
  $("#payCancel").onclick = () => closeModal("#mPay");

  function finalizeOrder(paid = false) {
    const text = buildOrderText(pendingOrder.num) + (paid ? "\nОплачено онлайн (демо)" : "");
    // журнал заказов (тестовый режим)
    try {
      const log = JSON.parse(localStorage.getItem("dp_orders") || "[]");
      log.unshift({ ts: Date.now(), text });
      localStorage.setItem("dp_orders", JSON.stringify(log.slice(0, 50)));
    } catch { }

    const phone = (SETTINGS.orderPhone || "").replace(/\D/g, "");
    if (phone) {
      window.open(`https://wa.me/${phone}?text=${encodeURIComponent(text)}`, "_blank");
    }
    $("#okText").textContent = paid ? "Оплата в тестовом режиме принята. Заказ собран и сохранён." : "Заказ собран и сохранён.";
    $("#okOrder").textContent = text;
    $("#okNum").textContent = pendingOrder.num;
    $("#okSend").hidden = !!phone;
    closeModal("#mPay"); closeModal("#mCheckout"); closeDrawer();
    openModal("#mOk");
    cart = []; promo = null; saveCart(); renderCart();
    $("#promoInp").value = "";
    $("#fComment").value = "";
  }
  $("#okSend").onclick = async () => {
    const text = $("#okOrder").textContent;
    try { await navigator.clipboard.writeText(text); toast("Заказ скопирован — вставьте в WhatsApp", true); }
    catch { toast("Не удалось скопировать"); }
  };
  $("#okClose").onclick = () => closeModal("#mOk");

  // ---------- promo strip timer (до ближайшего воскресенья 23:59; если < 6ч — на след. неделю) ----------
  function tickTimer() {
    const els = [$("#tmr"), $("#tmr2")].filter(Boolean); if (!els.length) return;
    const now = new Date();
    const target = new Date(now);
    const day = now.getDay(); // 0 вс
    let add = (7 - day) % 7;
    target.setDate(now.getDate() + add);
    target.setHours(23, 59, 0, 0);
    if (target - now < 6 * 3600 * 1000) target.setDate(target.getDate() + 7);
    const d = target - now;
    const h = Math.floor(d / 3600000), m = Math.floor(d % 3600000 / 60000), s = Math.floor(d % 60000 / 1000);
    const txt = h >= 24
      ? `${Math.floor(h / 24)} д ${String(h % 24).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`
      : `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
    els.forEach((el) => el.textContent = txt);
  }
  setInterval(tickTimer, 1000);

  // ---------- nav / ui ----------
  const burger = $("#burger");
  burger && (burger.onclick = () => {
    const nav = $("#nav");
    const open = nav.dataset.open === "1";
    nav.dataset.open = open ? "0" : "1";
    if (open) { nav.style.cssText = ""; } else {
      nav.style.cssText = "display:flex;flex-direction:column;position:fixed;top:64px;left:0;right:0;background:var(--bg2);border-bottom:1px solid var(--line);padding:10px 18px 16px;z-index:60;box-shadow:var(--sh)";
    }
  });
  $$("#nav a").forEach((a) => a.addEventListener("click", () => { const nav = $("#nav"); nav.dataset.open = "0"; nav.style.cssText = ""; }));
  const up = $("#fabUp");
  addEventListener("scroll", () => { up.classList.toggle("on", scrollY > 600); });
  up.onclick = () => scrollTo({ top: 0, behavior: "smooth" });

  // FAQ
  $$(".faq-q").forEach((q) => q.onclick = () => q.closest(".faq-item").classList.toggle("open"));

  // search & sort
  $("#search").addEventListener("input", (e) => { query = e.target.value.trim(); renderCatalog(); });
  $("#sort").addEventListener("change", (e) => { sortMode = e.target.value; renderCatalog(); });

  // ---------- init ----------
  renderCats(); renderCatalog(); renderHits(); renderCart(); tickTimer();
  bindCatalogEvents($("#grid")); bindCatalogEvents($("#hits"));
  const y = $("#year"); if (y) y.textContent = new Date().getFullYear();
})();
