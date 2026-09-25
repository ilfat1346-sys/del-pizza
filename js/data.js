// Del'pizza Баймак — данные сайта (демо-меню: цены и состав уточняются)
const SHOP = {
  name: "Del'pizza",
  tag: "пицца · роллы · суши",
  city: "Баймак",
  addr: "пр-т Салавата Юлаева, 28а",
  addr2: "Пекарня: ул. Карла Маркса, 1",
  hours: "Ежедневно 10:00–23:00",
  phones: ["+7 (965) 937-40-88", "+7 (937) 320-24-80"],
  wa: "79659374088",
  vk: "https://vk.com/delpizzabaimak",
  yandex: "https://yandex.ru/maps/org/del_pizza/180347199015/",
  rating: "4.2",
  reviews: "839",
  deliveryFrom: 499,     // бесплатная доставка от этой суммы
  deliveryTime: "60 минут",
  deliveryZone: "г. Баймак",
};

// ---- Тестовый режим (ФПС) ----
// testMode: заказы собираются, но никуда не уходят; оплата — демонстрационная.
// orderPhone: сюда вписать номер владельца (напр. "79659374088") — заказы пойдут в WhatsApp.
// payLink: ссылка на реальную оплату (СБП/ЮMoney) — когда появится.
const SETTINGS = {
  testMode: true,
  orderPhone: "",
  payLink: "",
  payLabel: "Тестовый режим оплаты",
};

const CATS = [
  { id: "pizza",   name: "Пиццы" },
  { id: "combo",   name: "Комбо и сеты" },
  { id: "rolls",   name: "Роллы и суши" },
  { id: "shaurma", name: "Шаурма и донеры" },
  { id: "burgers", name: "Бургеры" },
  { id: "snacks",  name: "Закуски" },
  { id: "dessert", name: "Десерты" },
  { id: "drinks",  name: "Напитки" },
  { id: "sauce",   name: "Соусы" },
];

const PRODUCTS = [
  // ---------- Пиццы (размеры 25/30/35 см) ----------
  { id: "pizza-pepperoni", cat: "pizza", name: "Пепперони", spec: "25 / 30 / 35 см",
    desc: "Пикантные колбаски пепперони, моцарелла, фирменный томатный соус",
    sizes: [[25, 419], [30, 499], [35, 599]], badge: "Хит", old: [25, 469], pop: 98 },
  { id: "pizza-margherita", cat: "pizza", name: "Маргарита", spec: "25 / 30 / 35 см",
    desc: "Моцарелла, спелые томаты, базилик, оливковое масло",
    sizes: [[25, 369], [30, 449], [35, 539]], pop: 86 },
  { id: "pizza-four-cheese", cat: "pizza", name: "Четыре сыра", spec: "25 / 30 / 35 см",
    desc: "Моцарелла, чеддер, дорблю, пармезан на сливочном соусе",
    sizes: [[25, 459], [30, 549], [35, 649]], pop: 74 },
  { id: "pizza-meat", cat: "pizza", name: "Мясная", spec: "25 / 30 / 35 см",
    desc: "Пепперони, ветчина, бекон, говядина, моцарелла",
    sizes: [[25, 479], [30, 569], [35, 669]], badge: "Хит", pop: 92 },
  { id: "pizza-hawaiian", cat: "pizza", name: "Гавайская", spec: "25 / 30 / 35 см",
    desc: "Курица, сочные кусочки ананаса, моцарелла, соус",
    sizes: [[25, 439], [30, 519], [35, 609]], pop: 63 },
  { id: "pizza-diablo", cat: "pizza", name: "Дьябло", spec: "25 / 30 / 35 см",
    desc: "Острая пепперони, халапеньо, перец чили, моцарелла",
    sizes: [[25, 459], [30, 539], [35, 639]], badge: "Острая", pop: 57 },
  { id: "pizza-caesar", cat: "pizza", name: "Цезарь", spec: "25 / 30 / 35 см",
    desc: "Курица, черри, салат айсберг, соус цезарь, пармезан",
    sizes: [[25, 439], [30, 519], [35, 609]], pop: 66 },
  { id: "pizza-del", cat: "pizza", name: "Дель'пицца — фирменная", spec: "25 / 30 / 35 см",
    desc: "Ветчина, шампиньоны, моцарелла, томаты — наша классика",
    sizes: [[25, 469], [30, 549], [35, 649]], badge: "Новинка", pop: 71 },

  // ---------- Комбо и сеты ----------
  { id: "combo-2-pizza", cat: "combo", name: "Комбо «Две по цене одной»", spec: "2 пиццы 30 см",
    desc: "Две пиццы 30 см на выбор (из списка акции) + 2 соуса", price: 979, old: 1138, badge: "-14%", pop: 95 },
  { id: "combo-friends", cat: "combo", name: "Сет «Дружеский»", spec: "4 пиццы 25 см",
    desc: "Четыре пиццы 25 см на выбор — для большой компании", price: 1349, old: 1476, badge: "-9%", pop: 88 },
  { id: "combo-rolls", cat: "combo", name: "Сет «Ролл-хит»", spec: "3 ролла + соус",
    desc: "Филадельфия, Калифорния и запечённый ролл + соус на выбор", price: 929, old: 1067, badge: "-13%", pop: 82 },
  { id: "combo-friday", cat: "combo", name: "Комбо «Пятница»", spec: "2 пиццы + крылышки + кола 1 л",
    desc: "Пицца 30 см, вторая 25 см, 6 крылышек BBQ и Кола 1 л", price: 1249, old: 1466, badge: "Хит", pop: 97 },

  // ---------- Роллы и суши ----------
  { id: "roll-philadelphia", cat: "rolls", name: "Филадельфия", spec: "8 шт · 250 г",
    desc: "Лосось, сливочный сыр, огурец", price: 439, badge: "Хит", pop: 96 },
  { id: "roll-california", cat: "rolls", name: "Калифорния", spec: "8 шт · 220 г",
    desc: "Краб, авокадо, огурец, икра тобико", price: 379, pop: 84 },
  { id: "roll-baked-salmon", cat: "rolls", name: "Запечённый с лососем", spec: "8 шт · 240 г",
    desc: "Лосось, сыр, шапка из сырно-сливочного соуса", price: 399, pop: 78 },
  { id: "roll-spicy-chicken", cat: "rolls", name: "Спайси с курицей", spec: "8 шт · 230 г",
    desc: "Курица в остром соусе, огурец, кунжут", price: 329, badge: "Острый", pop: 61 },
  { id: "roll-veg", cat: "rolls", name: "Овощной", spec: "8 шт · 180 г",
    desc: "Авокадо, огурец, болгарский перец, салат", price: 259, pop: 44 },
  { id: "roll-dragon", cat: "rolls", name: "Дракон", spec: "8 шт · 260 г",
    desc: "Угорь, авокадо, сыр, соус унаги", price: 469, pop: 69 },
  { id: "roll-maki-cucumber", cat: "rolls", name: "Маки с огурцом", spec: "6 шт · 120 г",
    desc: "Классические маки: рис, нори, огурец", price: 179, pop: 33 },
  { id: "roll-unagi", cat: "rolls", name: "Унаги с угрём", spec: "8 шт · 250 г",
    desc: "Угорь, сливочный сыр, соус унаги, кунжут", price: 449, pop: 64 },

  // ---------- Шаурма и донеры ----------
  { id: "doner-chicken", cat: "shaurma", name: "Донер с курицей", spec: "· 320 г",
    desc: "Курица, свежие овощи, соус на выбор", price: 259, badge: "Хит", pop: 91 },
  { id: "doner-beef", cat: "shaurma", name: "Донер с говядиной", spec: "· 340 г",
    desc: "Говядина, овощи, сырный соус", price: 299, pop: 73 },
  { id: "shawarma-spicy", cat: "shaurma", name: "Шаурма острая", spec: "· 330 г",
    desc: "Курица, халапеньо, острый соус, овощи", price: 279, pop: 58 },

  // ---------- Бургеры ----------
  { id: "burger-cheese", cat: "burgers", name: "Чизбургер", spec: "· 220 г",
    desc: "Говяжья котлета, чеддер, соус, огурчики", price: 229, pop: 76 },
  { id: "burger-chicken", cat: "burgers", name: "Чикенбургер", spec: "· 210 г",
    desc: "Куриная котлета, салат, соус", price: 209, pop: 68 },
  { id: "burger-double", cat: "burgers", name: "Двойной бургер", spec: "· 300 г",
    desc: "Две котлеты, двойной сыр, соус BBQ", price: 339, badge: "Новинка", pop: 55 },

  // ---------- Закуски ----------
  { id: "fries", cat: "snacks", name: "Картофель фри", spec: "· 150 г",
    desc: "Хрустящий, с солью", price: 149, pop: 80 },
  { id: "nuggets", cat: "snacks", name: "Наггетсы", spec: "6 шт",
    desc: "Куриные наггетсы с соусом на выбор", price: 199, pop: 71 },
  { id: "wings-bbq", cat: "snacks", name: "Крылышки BBQ", spec: "6 шт",
    desc: "Куриные крылышки в соусе барбекю", price: 309, badge: "Хит", pop: 89 },
  { id: "cheese-balls", cat: "snacks", name: "Сырные шарики", spec: "6 шт",
    desc: "Хрустящая панировка, тянущийся сыр", price: 249, pop: 62 },

  // ---------- Десерты ----------
  { id: "tiramisu", cat: "dessert", name: "Тирамису", spec: "· 130 г",
    desc: "Классический итальянский десерт", price: 229, pop: 59 },
  { id: "cheesecake", cat: "dessert", name: "Чизкейк", spec: "· 130 г",
    desc: "Нежный сливочный чизкейк", price: 249, pop: 66 },
  { id: "honey-cake", cat: "dessert", name: "Медовик", spec: "· 140 г",
    desc: "Домашний медовый торт", price: 209, pop: 52 },

  // ---------- Напитки ----------
  { id: "cola", cat: "drinks", name: "Кола", spec: "· 0,5 л",
    desc: "Классическая, охлаждённая", price: 119, pop: 87 },
  { id: "mors", cat: "drinks", name: "Морс домашний", spec: "· 0,5 л",
    desc: "Ягодный морс собственного приготовления", price: 139, badge: "Новинка", pop: 61 },
  { id: "cappuccino", cat: "drinks", name: "Капучино", spec: "· 300 мл",
    desc: "Кофе с молочной пенкой — можно с собой", price: 149, pop: 70 },
  { id: "latte", cat: "drinks", name: "Латте", spec: "· 300 мл",
    desc: "Мягкий кофейный вкус с молоком", price: 169, pop: 63 },
  { id: "milkshake", cat: "drinks", name: "Милкшейк ванильный", spec: "· 400 мл",
    desc: "Густой молочный коктейль", price: 219, pop: 57 },
  { id: "juice", cat: "drinks", name: "Сок в ассортименте", spec: "· 1 л",
    desc: "Апельсин, яблоко или персик", price: 149, pop: 48 },

  // ---------- Соусы ----------
  { id: "sauce-cheese", cat: "sauce", name: "Сырный соус", spec: "· 50 г", ico: "🧀",
    desc: "Тёплый сырный", price: 49, pop: 72 },
  { id: "sauce-garlic", cat: "sauce", name: "Чесночный соус", spec: "· 50 г", ico: "🧄",
    desc: "Классический чесночный", price: 39, pop: 75 },
  { id: "sauce-bbq", cat: "sauce", name: "Соус барбекю", spec: "· 50 г", ico: "🌶️",
    desc: "Копчёный, сладковатый", price: 49, pop: 58 },
];
