# Отчёт о проверке сайта перед запуском — план работ

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Собрать один самодостаточный HTML-файл — отчёт о проверке каталога аренды перед запуском, — который открывается по ссылке, печатается в PDF одной кнопкой и все числа в котором сходятся с сохранёнными отчётами Lighthouse.

**Architecture:** Единственный файл `index.html`: данные проверки лежат в начале скрипта валидным JSON-объектом `ОТЧЁТ`, вся разметка строится из него, стили и подрезанный шрифт вшиты в тот же файл. Внешних запросов нет ни одного. Рядом два вспомогательных скрипта в `tools/`, в готовую страницу они не попадают: один разово готовит шрифт, второй проверяет отчёт — сверяет каждое число с `zamery/*.json`, считает контраст по формуле WCAG и следит, что файл остался самодостаточным.

**Tech Stack:** HTML + CSS + ванильный JS без сборки и зависимостей. Python 3 с `fontTools` 4.60 для подрезки шрифта и для проверок. Playwright (MCP) для живых проверок. Шрифт Inter (SIL OFL), кириллический набор. Выкладка — GitHub Pages, аккаунт `pyhphhddb8-eng`.

**Spec:** `docs/superpowers/specs/2026-09-14-otchet-proverka-design.md`

## Решение по числам, принятое до начала работ

Спека называет вес страницы 81 КБ, а скрипт — 77 КБ. Lighthouse в
`zamery/lh-full.json` даёт 82 КБ (`total-byte-weight`, «Total size was 82
KiB») и 76 КБ на скрипт: 82 КБ — это КиБ, а 77 КБ — те же байты, но
пересчитанные в десятичные килобайты. Две системы счёта в одном документе
дают расхождение и ломают главное свойство отчёта — «любой может повторить
замер и сойтись в цифрах».

**Работаем в единицах Lighthouse, слово пишем привычное — «КБ».** Тогда
все числа берутся из отчёта дословно:

| Величина                | Значение | Откуда                                        |
| ----------------------- | -------- | --------------------------------------------- |
| Вес страницы            | 82 КБ    | `total-byte-weight`                           |
| в том числе документ    | 1,4 КБ   | `network-requests`, `transferSize` 1433        |
| в том числе скрипт      | 75,6 КБ  | `transferSize` 77380                           |
| в том числе стили       | 4,5 КБ   | `transferSize` 4592                            |
| в том числе иконка      | 0,6 КБ   | `transferSize` favicon.svg                     |
| Неиспользуемый JS       | 41 КБ    | `unused-javascript`, «Est savings of 41 KiB»   |
| Экономия на кэшировании | 73 КБ    | `cache-insight`, «Est savings of 73 KiB»       |

Остальные числа спеки сошлись с замерами без правок: 98 / 98 / 100 / 63,
CLS 0, медиана LCP трёх прогонов 1,36 с → **1,4 с**.

## Global Constraints

Эти требования действуют в каждой задаче.

- **Один файл.** Готовая страница — `index.html` в корне репозитория. Ни сборки, ни зависимостей, ни внешних запросов: ни одного `src="http…"`, `<link rel="stylesheet" href="http…">` или `@import`. Ссылка `<a href>` на проверенный сайт — единственное исключение.
- **Данные отдельно от разметки.** Объект объявляется ровно как `const ОТЧЁТ = { … };`, его тело — валидный JSON (двойные кавычки, без висячих запятых, без комментариев внутри). Скрипт проверки разбирает это тело питоновским `json.loads`. Следующий отчёт по другому сайту делается заменой одного объекта.
- **Числа только из замеров.** Каждое число в тексте страницы приходит из `ОТЧЁТ`, а каждое число в `ОТЧЁТ` сверяется с `zamery/*.json` скриптом `tools/proverka.py`. Руками в разметку числа не пишутся.
- **Единицы — как у Lighthouse** (таблица выше). Дробная часть через запятую: «1,4 с», «4,5 КБ».
- **Контраст.** Каждая пара «текст на фоне» — не ниже 4,5 по формуле WCAG. Проверяется скриптом.
- **Мобильные.** На ширине 360 px горизонтальной прокрутки нет.
- **Консоль чистая** на живом адресе: ни ошибок, ни предупреждений.
- **Страница открыта для поисковиков.** Никакого `noindex` — в отличие от проверяемого демо, здесь нет ничего выдуманного.
- **Язык — русский, буква «ё» пишется.** Тон: без рекламы дополнительных услуг, без запугивания, без оценок вроде «сайт ужасен», без выдуманных находок ради объёма.
- **Порядок находок фиксирован** и по важности для посетителя, а не по величине экономии: пропуск уровня заголовков → отсутствующий `favicon.ico` → лишний JavaScript.
- **Коммиты на русском**, каждая задача завершается коммитом. Приписка в конце сообщения:
  `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`

## Карта файлов

| Файл                      | За что отвечает                                                                        |
| ------------------------- | -------------------------------------------------------------------------------------- |
| `index.html`              | Весь отчёт: объект данных, построение разметки, оформление, правила печати, вшитый шрифт |
| `tools/proverka.py`       | Проверки отчёта: числа против `zamery/`, контраст, самодостаточность, отсутствие `noindex` |
| `tools/shrift.py`         | Разовая подготовка шрифта: скачать Inter, подрезать под нужные символы, выдать base64    |
| `tools/shrift-podpis.txt` | След от подрезки: версия, набор символов, размер — чтобы шаг можно было повторить         |
| `zamery/*.json`           | Уже лежат. Источник правды по числам, не трогаем                                         |
| `README.md`               | Обновляется в последней задаче: состояние, адрес страницы, как повторить проверки         |

`index.html` намеренно один, хотя и крупный: спека требует самодостаточный
файл, и разносить его по частям, чтобы потом склеивать сборщиком, значит
завести сборку, которой в решении нет. Внутри файл разделён на четыре
именованных блока комментариями-маркерами (`ДАННЫЕ`, `ОФОРМЛЕНИЕ`,
`ПЕЧАТЬ`, `ПОСТРОЕНИЕ`), по ним же ориентируется скрипт проверки.

## Принятое отступление от спеки

Разметка строится скриптом из объекта — как требует спека. Значит, без
JavaScript страница пуста. Для отчёта, который будут пересылать и
распечатывать, это стоит подстраховать: в `<body>` добавляется `<noscript>`
с вердиктом, четырьмя оценками и адресом проверенного сайта обычным текстом.
Это не дублирование разметки, а короткая запасная версия на семь строк.

---

### Task 1: Объект данных и скрипт проверки

Первая задача даёт две вещи разом: источник правды (`ОТЧЁТ`) и инструмент,
который до конца работы стережёт числа. Дальше каждая задача заканчивается
его прогоном.

**Files:**
- Create: `/Users/dmitrijvolkov/Progects/otchet-proverka/tools/proverka.py`
- Create: `/Users/dmitrijvolkov/Progects/otchet-proverka/index.html`

**Interfaces:**
- Consumes: `zamery/lh-full.json`, `zamery/lh-k1.json`, `lh-k2.json`, `lh-k3.json` — уже в репозитории.
- Produces: объект `ОТЧЁТ` со свойствами, на которые опираются задачи 3–6:
  `sajt` (`{"adres", "nazvanie"}`), `verdikt` (`{"zagolovok", "poyasnenie"}`),
  `ocenki` (массив `{"imya", "ball"}`), `metriki` (массив `{"imya", "znachenie", "poyasnenie"}`),
  `nahodki` (массив `{"nomer", "zagolovok", "chto", "chem_grozit", "chto_delat", "skolko", "sam"}`),
  `seo` (`{"zagolovok", "tekst"}`), `provereno` (массив строк),
  `ne_nasha_zona` (`{"zagolovok", "tekst"}`), `zamer` (`{"instrument", "versiya", "rezhim", "progonov", "data"}`).
  Скрипт проверки обращается к `ОТЧЁТ` только по этим именам.

- [ ] **Step 1: Написать проверочный скрипт**

Создать `tools/proverka.py`:

```python
#!/usr/bin/env python3
"""Проверки отчёта: числа против замеров, контраст, самодостаточность.

Запуск: python3 tools/proverka.py
Молчит и возвращает 0, если всё сошлось. Иначе печатает список расхождений.
"""
import json
import pathlib
import re
import sys

KOREN = pathlib.Path(__file__).resolve().parent.parent
HTML = (KOREN / "index.html").read_text(encoding="utf-8")
ZAMERY = KOREN / "zamery"

oshibki = []


def trebuem(uslovie, soobshchenie):
    if not uslovie:
        oshibki.append(soobshchenie)


# ---------------------------------------------------------------- данные
sovpadenie = re.search(r"const ОТЧЁТ = (\{.*?\n\s*\});", HTML, re.S)
if not sovpadenie:
    print("Не нашёл объект: ожидается 'const ОТЧЁТ = { … };'")
    sys.exit(1)
try:
    otchet = json.loads(sovpadenie.group(1))
except json.JSONDecodeError as e:
    print(f"Тело объекта ОТЧЁТ — не валидный JSON: {e}")
    sys.exit(1)

polnyj = json.loads((ZAMERY / "lh-full.json").read_text())
progony = [json.loads((ZAMERY / f"lh-k{n}.json").read_text()) for n in (1, 2, 3)]


def ball(kategoriya):
    return round(polnyj["categories"][kategoriya]["score"] * 100)


# ------------------------------------------------------------- оценки
ozhidaem_ocenki = {
    "Производительность": ball("performance"),
    "Доступность": ball("accessibility"),
    "Лучшие практики": ball("best-practices"),
    "SEO": ball("seo"),
}
fakt_ocenki = {o["imya"]: o["ball"] for o in otchet["ocenki"]}
trebuem(
    fakt_ocenki == ozhidaem_ocenki,
    f"Оценки разошлись: в отчёте {fakt_ocenki}, в замере {ozhidaem_ocenki}",
)

# ------------------------------------------------------------- метрики
zaprosy = polnyj["audits"]["network-requests"]["details"]["items"]
ves_kb = round(polnyj["audits"]["total-byte-weight"]["numericValue"] / 1024)
lcp_mediana = sorted(
    p["audits"]["largest-contentful-paint"]["numericValue"] for p in progony
)[1]
lcp_sek = round(lcp_mediana / 1000, 1)
cls = polnyj["audits"]["cumulative-layout-shift"]["numericValue"]

metriki = {m["imya"]: m["znachenie"] for m in otchet["metriki"]}
trebuem(
    metriki.get("Вес страницы") == f"{ves_kb} КБ",
    f"Вес страницы: в отчёте {metriki.get('Вес страницы')!r}, в замере {ves_kb} КБ",
)
ozhidaem_lcp = f"{lcp_sek} с".replace(".", ",")
trebuem(
    metriki.get("Главный элемент") == ozhidaem_lcp,
    f"Главный элемент: в отчёте {metriki.get('Главный элемент')!r}, "
    f"медиана трёх прогонов {ozhidaem_lcp}",
)
trebuem(cls == 0, f"Скачки вёрстки в замере есть: CLS {cls}, а отчёт утверждает обратное")

# ------------------------------------------------------------- находки
tekst_nahodok = " ".join(
    " ".join(str(v) for v in n.values()) for n in otchet["nahodki"]
)
ekonomiya_js = round(
    polnyj["audits"]["unused-javascript"]["details"]["overallSavingsBytes"] / 1024
)
trebuem(
    f"{ekonomiya_js} КБ" in tekst_nahodok,
    f"В находках нет числа {ekonomiya_js} КБ — столько неиспользуемого JS в замере",
)
trebuem(len(otchet["nahodki"]) == 3, "Находок должно быть ровно три")
poryadok = [n["zagolovok"] for n in otchet["nahodki"]]
trebuem(
    "аголов" in poryadok[0] and "favicon" in poryadok[1].lower() and "JavaScript" in poryadok[2],
    f"Порядок находок сбит: {poryadok}",
)

# ---------------------------------------------------- SEO и чужая зона
istochnik_noindex = polnyj["audits"]["is-crawlable"]["details"]["items"][0]["source"]
trebuem(
    "noindex" in istochnik_noindex["snippet"],
    "Замер не подтверждает, что SEO 63 из-за noindex",
)
# У cache-insight нет overallSavingsBytes — экономия лежит в debugData.
kesh_kb = round(
    polnyj["audits"]["cache-insight"]["details"]["debugData"]["wastedBytes"] / 1024
)
trebuem(
    f"{kesh_kb} КБ" in otchet["ne_nasha_zona"]["tekst"],
    f"В блоке «не наша зона» нет числа {kesh_kb} КБ — столько даёт cache-insight",
)

# ------------------------------------------------------------- подпись
trebuem(
    otchet["zamer"]["versiya"] == polnyj["lighthouseVersion"],
    f"Версия инструмента: в отчёте {otchet['zamer']['versiya']!r}, "
    f"в замере {polnyj['lighthouseVersion']!r}",
)
trebuem(
    otchet["zamer"]["progonov"] == 3,
    "В подписи должно стоять три прогона — столько файлов в zamery/",
)
trebuem(
    otchet["sajt"]["adres"] == polnyj["finalDisplayedUrl"],
    f"Адрес проверенного сайта: в отчёте {otchet['sajt']['adres']!r}, "
    f"в замере {polnyj['finalDisplayedUrl']!r}",
)

# ------------------------------------------------- самодостаточность
for obrazec, chto in (
    (r'src\s*=\s*"https?:', "внешний src"),
    (r'<link[^>]+rel\s*=\s*"stylesheet"[^>]+https?:', "внешний файл стилей"),
    (r"@import", "@import в стилях"),
    (r"fonts\.(googleapis|gstatic)\.com", "запрос к Google Fonts"),
):
    trebuem(
        not re.search(obrazec, HTML, re.I),
        f"Страница перестала быть самодостаточной: найден {chto}",
    )
trebuem(
    "noindex" not in HTML.split("</head>")[0],
    "В <head> отчёта стоит noindex — страница должна быть открыта поисковикам",
)

# ------------------------------------------------------------- контраст
PARY = [
    ("--tekst", "--list"),
    ("--tekst", "--fon"),
    ("--tekst-2", "--list"),
    ("--tekst-2", "--fon"),
    ("--zelenyj", "--list"),
    ("--zheltyj", "--list"),
    ("--sinij", "--list"),
    ("--tekst", "--seryj-blok"),
    ("--tekst-2", "--seryj-blok"),
]


def cveta_iz_root(html):
    blok = re.search(r":root\s*\{(.*?)\}", html, re.S)
    if not blok:
        return {}
    return dict(re.findall(r"(--[a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{6})", blok.group(1)))


def yarkost(hex_cvet):
    r, g, b = (int(hex_cvet[i : i + 2], 16) / 255 for i in (1, 3, 5))
    def kanal(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * kanal(r) + 0.7152 * kanal(g) + 0.0722 * kanal(b)


def kontrast(a, b):
    ya, yb = yarkost(a), yarkost(b)
    svetlee, temnee = max(ya, yb), min(ya, yb)
    return (svetlee + 0.05) / (temnee + 0.05)


cveta = cveta_iz_root(HTML)
if cveta:
    for tekst, fon in PARY:
        if tekst in cveta and fon in cveta:
            k = kontrast(cveta[tekst], cveta[fon])
            trebuem(
                k >= 4.5,
                f"Контраст {tekst} на {fon}: {k:.2f} — норма 4,5",
            )

# ------------------------------------------------------------- итог
if oshibki:
    print(f"Расхождений: {len(oshibki)}\n")
    for o in oshibki:
        print(f"  • {o}")
    sys.exit(1)
print("Всё сошлось: числа, контраст, самодостаточность.")
```

- [ ] **Step 2: Прогнать и убедиться, что падает**

```bash
cd ~/Progects/otchet-proverka && python3 tools/proverka.py
```

Ожидаем: падение с `FileNotFoundError` на `index.html` — файла ещё нет.

- [ ] **Step 3: Создать `index.html` с одним объектом данных**

На этом шаге в файле только каркас и объект. Оформления и построения
разметки нет — они в задачах 3–6. Числа берутся из таблицы «Решение по
числам» в шапке этого плана.

```html
<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Отчёт о проверке сайта перед запуском — каталог аренды инструмента</title>
<meta name="description" content="Проверка каталога аренды строительного инструмента перед запуском: вердикт, три находки к исправлению, перечень проверенных областей. Замер Lighthouse 13.4.1, 14.09.2026.">
<!-- ОФОРМЛЕНИЕ: задача 3 -->
<!-- ПЕЧАТЬ: задача 6 -->
</head>
<body>
<noscript>
  <h1>Сайт готов к запуску</h1>
  <p>Проверен каталог аренды строительного инструмента,
     https://pyhphhddb8-eng.github.io/katalog-arenda/ — 14 сентября 2026 года.</p>
  <p>Производительность 98, доступность 98, лучшие практики 100, SEO 63.
     Три пункта поправить после запуска. Полный текст отчёта строится
     скриптом — включите JavaScript.</p>
</noscript>
<main id="otchet"></main>
<script>
/* ДАННЫЕ: начало. Следующий отчёт по другому сайту — замена этого объекта. */
const ОТЧЁТ = {
  "sajt": {
    "adres": "https://pyhphhddb8-eng.github.io/katalog-arenda/",
    "nazvanie": "Каталог аренды строительного инструмента"
  },
  "verdikt": {
    "zagolovok": "Сайт готов к запуску",
    "poyasnenie": "Ничего, что мешало бы открыть сайт посетителям, проверка не нашла. Три пункта из списка ниже стоит поправить после запуска — они не блокируют его."
  },
  "ocenki": [
    { "imya": "Производительность", "ball": 98 },
    { "imya": "Доступность", "ball": 98 },
    { "imya": "Лучшие практики", "ball": 100 },
    { "imya": "SEO", "ball": 63 }
  ],
  "metriki": [
    {
      "imya": "Вес страницы",
      "znachenie": "82 КБ",
      "poyasnenie": "Столько качает браузер при первом заходе: документ 1,4 КБ, скрипт 75,6 КБ, стили 4,5 КБ, иконка 0,6 КБ."
    },
    {
      "imya": "Главный элемент",
      "znachenie": "1,4 с",
      "poyasnenie": "Через столько посетитель видит главное на экране. Замер на мобильном интернете с замедлением."
    }
  ],
  "nahodki": [
    {
      "nomer": 1,
      "zagolovok": "Пропущен уровень заголовков",
      "chto": "После заголовка страницы h1 сразу идёт h3 в карточках позиций — уровень h2 пропущен. Первая такая карточка: «Лестница-трансформер Alumet 4×4».",
      "chem_grozit": "Программа чтения с экрана строит по заголовкам оглавление страницы. С пропущенным уровнем оглавление разваливается, и незрячий посетитель теряет, где кончается один раздел и начинается другой.",
      "chto_delat": "Либо заменить h3 в карточках на h2, либо добавить перед списком позиций настоящий заголовок h2 — например, «Каталог».",
      "skolko": "15 минут",
      "sam": "Да, если правка делается в вёрстке карточки — меняется один тег"
    },
    {
      "nomer": 2,
      "zagolovok": "Нет файла favicon.ico",
      "chto": "Объявлены favicon.svg и иконка для iPhone, оба отдаются. Привычный favicon.ico по корневому адресу возвращает 404.",
      "chem_grozit": "Часть сервисов и старых браузеров просит именно .ico и не умеет запрашивать svg. У них вместо иконки сайта будет пустой лист — в закладках, во вкладке, в списках ссылок.",
      "chto_delat": "Сделать из имеющегося svg файл favicon.ico размером 32×32 и положить в корень сайта.",
      "skolko": "10 минут",
      "sam": "Да, иконка собирается из svg любым онлайн-конвертером"
    },
    {
      "nomer": 3,
      "zagolovok": "41 КБ неиспользуемого JavaScript",
      "chto": "В скрипте страницы 41 КБ кода, который при загрузке не выполняется. Это больше половины его веса.",
      "chem_grozit": "Лишний код всё равно качается и разбирается браузером. На быстрой странице разница почти не видна, на медленном телефоне в дороге — заметна.",
      "chto_delat": "Посмотреть, что тянется в сборку целиком, и подключать только используемые части. Обычно это одна-две библиотеки, импортированные пакетом.",
      "skolko": "1–2 часа",
      "sam": "Нет, нужна работа со сборкой проекта"
    }
  ],
  "seo": {
    "zagolovok": "Почему SEO 63, хотя сайт в порядке",
    "tekst": "Оценка целиком объясняется одной строкой в коде страницы: meta name=\"robots\" content=\"noindex\". Она просит поисковики не показывать страницу в выдаче. Здесь это решение, а не недосмотр: сайт — демонстрационный модуль с условными ценами, и в поиске ему не место. Уберите строку — оценка поднимется без других правок. На боевом сайте такой пункт стоял бы первым в списке «чинить до запуска»."
  },
  "provereno": [
    "Превью ссылки в мессенджерах и соцсетях: заголовок, описание и картинка 1200×630 отдаются",
    "Canonical: указан и совпадает с адресом страницы",
    "Страница 404: несуществующий адрес отдаёт 404, а не пустую страницу",
    "Скачки вёрстки при загрузке: ни одного",
    "Работа с клавиатуры: фильтры и карточки доступны без мыши",
    "Мобильная вёрстка на ширине 360 px: горизонтальной прокрутки нет",
    "Консоль браузера: ни ошибок, ни предупреждений"
  ],
  "ne_nasha_zona": {
    "zagolovok": "Что не в зоне ответственности исполнителя",
    "tekst": "Заголовки кэширования выставляет сама площадка GitHub Pages. Lighthouse оценивает возможную экономию в 73 КБ на повторных заходах, но повлиять на это со стороны сайта нельзя — настройка живёт на стороне хостинга. На своём хостинге этот пункт решается одной строкой в настройках сервера."
  },
  "zamer": {
    "instrument": "Lighthouse",
    "versiya": "13.4.1",
    "rezhim": "мобильный режим с замедлением сети",
    "progonov": 3,
    "data": "14 сентября 2026 года"
  }
};
/* ДАННЫЕ: конец */
/* ПОСТРОЕНИЕ: задачи 3–5 */
</script>
</body>
</html>
```

- [ ] **Step 4: Прогнать проверки**

```bash
cd ~/Progects/otchet-proverka && python3 tools/proverka.py
```

Ожидаем: `Всё сошлось: числа, контраст, самодостаточность.` Блок контраста
на этом шаге молча пропускается — `:root` ещё нет, он появится в задаче 3.

Если скрипт ругается на число — **править надо объект, а не скрипт**:
источник правды здесь `zamery/`.

- [ ] **Step 5: Коммит**

```bash
cd ~/Progects/otchet-proverka
git add index.html tools/proverka.py docs/superpowers/plans/
git commit -m "$(cat <<'EOF'
Объект данных отчёта и скрипт сверки с замерами

Числа приведены к единицам Lighthouse: вес страницы 82 КБ вместо 81 в спеке.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: Шрифт — подрезка и вшивание

**Files:**
- Create: `/Users/dmitrijvolkov/Progects/otchet-proverka/tools/shrift.py`
- Create: `/Users/dmitrijvolkov/Progects/otchet-proverka/tools/shrift-podpis.txt`
- Modify: `/Users/dmitrijvolkov/Progects/otchet-proverka/index.html` — блок `<!-- ОФОРМЛЕНИЕ -->`

**Interfaces:**
- Consumes: `index.html` из задачи 1 — весь видимый текст берётся из него, по нему и считается набор символов.
- Produces: два правила `@font-face` с `font-family: "Inter"`, начертания 400 и 700, источник `url(data:font/woff2;base64,…)`. Задача 3 объявляет `--shrift: "Inter", system-ui, -apple-system, "Segoe UI", sans-serif`.

- [ ] **Step 1: Написать скрипт подрезки**

Создать `tools/shrift.py`:

```python
#!/usr/bin/env python3
"""Разовая подготовка шрифта: скачать Inter, подрезать, выдать base64.

Запуск: python3 tools/shrift.py
Печатает два готовых правила @font-face — их вставляют в index.html.
Набор символов берётся из самого index.html, так что скрипт можно
перезапустить, когда текст отчёта изменится.
"""
import base64
import io
import pathlib
import re
import subprocess
import sys
import urllib.request

KOREN = pathlib.Path(__file__).resolve().parent.parent
HTML = (KOREN / "index.html").read_text(encoding="utf-8")
VREMENNO = KOREN / "tools" / ".shrift-vremenno"
VREMENNO.mkdir(exist_ok=True)

BRAUZER = {"User-Agent": "Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/130 Safari/537.36"}
ADRES_CSS = (
    "https://fonts.googleapis.com/css2?family=Inter:wght@400;700"
    "&display=swap&subset=cyrillic,latin"
)


def skachat(adres):
    zapros = urllib.request.Request(adres, headers=BRAUZER)
    with urllib.request.urlopen(zapros) as otvet:
        return otvet.read()


def simvoly_stranicy():
    """Все символы, которые страница может показать, плюс запас."""
    bez_tegov = re.sub(r"<[^>]+>", " ", HTML)
    zapas = (
        "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
        "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789 .,:;!?—–-«»\"'()[]/\\%№×→•…+="
    )
    return "".join(sorted(set(bez_tegov + zapas) - set("\n\r\t")))


def pravilo(nachertanie, nabor):
    """Скачать нужное начертание, подрезать, вернуть готовый @font-face."""
    css = skachat(f"{ADRES_CSS}").decode("utf-8")
    bloki = css.split("@font-face")
    nuzhnye = [b for b in bloki if f"font-weight: {nachertanie};" in b and "cyrillic" in b]
    if not nuzhnye:
        sys.exit(f"Не нашёл кириллическое начертание {nachertanie} в ответе Google Fonts")
    adresa = re.findall(r"url\((https://[^)]+\.woff2)\)", " ".join(nuzhnye))
    syroj = VREMENNO / f"inter-{nachertanie}-syroj.woff2"
    # У кириллицы два поддиапазона (cyrillic и cyrillic-ext) плюс латиница —
    # берём полный файл начертания, подрезка всё равно оставит только нужное.
    polnyj_css = skachat(
        f"https://fonts.googleapis.com/css2?family=Inter:wght@{nachertanie}&display=swap"
    ).decode("utf-8")
    vse_adresa = re.findall(r"url\((https://[^)]+\.woff2)\)", polnyj_css) or adresa
    syroj.write_bytes(skachat(vse_adresa[0]))

    podrezannyj = VREMENNO / f"inter-{nachertanie}.woff2"
    subprocess.run(
        [
            sys.executable, "-m", "fontTools.subset", str(syroj),
            f"--text={nabor}",
            "--layout-features=kern,liga",
            "--flavor=woff2",
            "--desubroutinize",
            f"--output-file={podrezannyj}",
        ],
        check=True,
    )
    bajty = podrezannyj.read_bytes()
    kod = base64.b64encode(bajty).decode("ascii")
    print(f"/* Inter {nachertanie}: {len(bajty) / 1024:.1f} КБ после подрезки */", file=sys.stderr)
    return (
        "@font-face{font-family:\"Inter\";font-style:normal;"
        f"font-weight:{nachertanie};font-display:swap;"
        f"src:url(data:font/woff2;base64,{kod}) format(\"woff2\")}}"
    ), len(bajty)


if __name__ == "__main__":
    nabor = simvoly_stranicy()
    itogo = 0
    for nachertanie in (400, 700):
        tekst, razmer = pravilo(nachertanie, nabor)
        itogo += razmer
        print(tekst)
    print(f"\n/* Всего шрифта: {itogo / 1024:.1f} КБ */", file=sys.stderr)
```

- [ ] **Step 2: Запустить и посмотреть размер**

```bash
cd ~/Progects/otchet-proverka && python3 tools/shrift.py > tools/.shrift-vremenno/pravila.css
```

Ожидаем: в `stderr` два размера и общий. Ориентир — **до 40 КБ на оба
начертания**. Если вышло заметно больше, значит подрезка не сработала:
проверить, что в `--text=` попал набор, а не пустая строка.

- [ ] **Step 3: Вшить правила в страницу**

Заменить в `index.html` строку `<!-- ОФОРМЛЕНИЕ: задача 3 -->` на:

```html
<style>
/* ОФОРМЛЕНИЕ: начало */
/* Шрифт Inter, SIL Open Font License 1.1. Подрезан под текст этой
   страницы скриптом tools/shrift.py — см. tools/shrift-podpis.txt */
</style>
```

и вставить внутрь `<style>` содержимое `tools/.shrift-vremenno/pravila.css`
(две длинные строки `@font-face`). Остальное оформление добавит задача 3.

- [ ] **Step 4: Записать след от подрезки**

```bash
cd ~/Progects/otchet-proverka && cat > tools/shrift-podpis.txt <<'EOF'
Шрифт: Inter, SIL Open Font License 1.1, с fonts.gstatic.com
Начертания: 400, 700
Подрезан: python3 tools/shrift.py — набор символов берётся из index.html
Дата подрезки: 14.09.2026
EOF
python3 -c "
import re,pathlib
h=pathlib.Path('index.html').read_text()
n=len(re.findall(r'@font-face', h))
print('правил @font-face в странице:', n)
print('вес страницы:', round(len(h.encode())/1024,1), 'КБ')
"```

Ожидаем: `правил @font-face в странице: 2`.

- [ ] **Step 5: Прогнать проверки**

```bash
cd ~/Progects/otchet-proverka && python3 tools/proverka.py
```

Ожидаем: `Всё сошлось`. Правило `src:url(data:font/woff2;base64,…)` не
считается внешним запросом — проверка ищет `src="http`.

- [ ] **Step 6: Убрать временные файлы и закоммитить**

```bash
cd ~/Progects/otchet-proverka
rm -rf tools/.shrift-vremenno
printf 'tools/.shrift-vremenno/\n' >> .gitignore
git add index.html tools/shrift.py tools/shrift-podpis.txt .gitignore
git commit -m "$(cat <<'EOF'
Шрифт Inter подрезан под текст отчёта и вшит в страницу

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: Оформление и первый экран — вердикт и сводка

**Files:**
- Modify: `/Users/dmitrijvolkov/Progects/otchet-proverka/index.html` — блок `ОФОРМЛЕНИЕ` и блок `ПОСТРОЕНИЕ`

**Interfaces:**
- Consumes: `ОТЧЁТ.sajt`, `ОТЧЁТ.verdikt`, `ОТЧЁТ.ocenki`, `ОТЧЁТ.metriki` из задачи 1; переменную `--shrift` из правил `@font-face` задачи 2.
- Produces: вспомогательные функции, которыми пользуются задачи 4 и 5 —
  `el(teg, klassy, tekst)` возвращает `HTMLElement`;
  `razdel(zagolovok)` возвращает `HTMLElement` секции с заголовком `h2` внутри;
  переменные оформления `--fon --list --tekst --tekst-2 --ramka --zelenyj --zheltyj --sinij --seryj-blok --shag`;
  корневой контейнер — `document.getElementById("otchet")`.

**Перед началом:** прочитать скилл `landing-visual-craft` — типографика,
шаг отступов, состояния, тёмная тема. Отчёт — документ, а не лендинг:
спокойный лист, один акцентный цвет на смысл, никаких градиентов и теней
ради красоты.

- [ ] **Step 1: Переменные оформления и база**

Добавить внутрь `<style>` после правил `@font-face`:

```css
:root{
  --fon:#f4f5f7;
  --list:#ffffff;
  --tekst:#16191d;
  --tekst-2:#555d69;
  --ramka:#e0e4e9;
  --seryj-blok:#eceff3;
  --zelenyj:#15704a;
  --zheltyj:#87560a;
  --sinij:#1f5c9e;
  --shag:8px;
  --shrift:"Inter",system-ui,-apple-system,"Segoe UI",sans-serif;
  --list-shirina:760px;
}
*,*::before,*::after{box-sizing:border-box}
body{
  margin:0;
  padding:calc(var(--shag)*5) calc(var(--shag)*2);
  background:var(--fon);
  color:var(--tekst);
  font:400 17px/1.6 var(--shrift);
  -webkit-text-size-adjust:100%;
}
#otchet{max-width:var(--list-shirina);margin:0 auto}
h1,h2,h3{line-height:1.25;margin:0;text-wrap:balance}
h1{font-size:clamp(28px,6vw,40px);font-weight:700;letter-spacing:-0.02em}
h2{font-size:clamp(20px,4vw,25px);font-weight:700;letter-spacing:-0.01em}
h3{font-size:19px;font-weight:700}
p{margin:0}
a{color:var(--sinij)}
.kartochka{
  background:var(--list);
  border:1px solid var(--ramka);
  border-radius:calc(var(--shag)*1.5);
  padding:calc(var(--shag)*3);
}
.razdel{margin-top:calc(var(--shag)*6)}
.razdel>h2{margin-bottom:calc(var(--shag)*2)}
.stopka{display:flex;flex-direction:column;gap:calc(var(--shag)*2)}
.vtorichno{color:var(--tekst-2)}
```

Проверка контраста в `tools/proverka.py` разбирает именно этот блок
`:root`, поэтому цвета пишутся шестизначным hex и только здесь.

- [ ] **Step 2: Прогнать проверку контраста**

```bash
cd ~/Progects/otchet-proverka && python3 tools/proverka.py
```

Ожидаем: `Всё сошлось`. Если какая-то пара не дотянула до 4,5, скрипт
назовёт её и посчитанное значение — темнить цвет, пока не пройдёт, а не
ослаблять норму в скрипте.

- [ ] **Step 3: Написать вспомогательные функции и шапку**

Заменить в `index.html` строку `/* ПОСТРОЕНИЕ: задачи 3–5 */` на:

```js
/* ПОСТРОЕНИЕ: начало */
const koren = document.getElementById("otchet");

function el(teg, klassy = "", tekst = "") {
  const e = document.createElement(teg);
  if (klassy) e.className = klassy;
  if (tekst) e.textContent = tekst;
  return e;
}

function razdel(zagolovok) {
  const s = el("section", "razdel");
  s.append(el("h2", "", zagolovok));
  return s;
}

/* — шапка: кто проверен и когда — */
const shapka = el("header", "shapka");
shapka.append(el("p", "vtorichno nadpis", "Отчёт о проверке сайта перед запуском"));
const adres = el("a", "shapka__adres");
adres.href = ОТЧЁТ.sajt.adres;
adres.textContent = ОТЧЁТ.sajt.adres;
const stroka_sajta = el("p", "vtorichno");
stroka_sajta.append(
  document.createTextNode(ОТЧЁТ.sajt.nazvanie + " — "),
  adres,
);
shapka.append(stroka_sajta);
koren.append(shapka);

/* — вердикт — */
const verdikt = el("div", "kartochka verdikt");
verdikt.append(
  el("p", "verdikt__znachok", "✓"),
  el("h1", "", ОТЧЁТ.verdikt.zagolovok),
  el("p", "verdikt__poyasnenie", ОТЧЁТ.verdikt.poyasnenie),
);
koren.append(verdikt);
```

- [ ] **Step 4: Построить оценки и две главные цифры**

Добавить следом:

```js
/* — четыре оценки плашками — */
function cvet_ocenki(ball) {
  if (ball >= 90) return "ocenka--horosho";
  if (ball >= 50) return "ocenka--srednee";
  return "ocenka--ploho";
}

const svodka = el("div", "svodka");
const ocenki = el("div", "ocenki");
for (const o of ОТЧЁТ.ocenki) {
  const plashka = el("div", "ocenka " + cvet_ocenki(o.ball));
  plashka.append(
    el("p", "ocenka__ball", String(o.ball)),
    el("p", "ocenka__imya", o.imya),
  );
  ocenki.append(plashka);
}
svodka.append(ocenki);

/* — две главные цифры — */
const cifry = el("div", "cifry");
for (const m of ОТЧЁТ.metriki) {
  const c = el("div", "cifra");
  c.append(
    el("p", "cifra__imya vtorichno", m.imya),
    el("p", "cifra__znachenie", m.znachenie),
    el("p", "cifra__poyasnenie vtorichno", m.poyasnenie),
  );
  cifry.append(c);
}
svodka.append(cifry);
koren.append(svodka);
```

- [ ] **Step 5: Оформить шапку, вердикт и сводку**

Добавить в `<style>`:

```css
.shapka{margin-bottom:calc(var(--shag)*3)}
.nadpis{
  font-size:14px;font-weight:700;letter-spacing:0.08em;
  text-transform:uppercase;margin-bottom:calc(var(--shag)*0.5);
}
.shapka__adres{word-break:break-all}
.verdikt{
  border-left:4px solid var(--zelenyj);
  display:flex;flex-direction:column;gap:var(--shag);
}
.verdikt__znachok{
  color:var(--zelenyj);font-size:28px;font-weight:700;line-height:1;
}
.verdikt__poyasnenie{max-width:58ch}
.svodka{margin-top:calc(var(--shag)*3);display:flex;flex-direction:column;gap:calc(var(--shag)*2)}
.ocenki{display:grid;grid-template-columns:repeat(4,1fr);gap:var(--shag)}
.ocenka{
  background:var(--list);border:1px solid var(--ramka);
  border-radius:var(--shag);padding:calc(var(--shag)*1.5);text-align:center;
}
.ocenka__ball{font-size:30px;font-weight:700;line-height:1.1}
.ocenka__imya{font-size:13px;line-height:1.3;color:var(--tekst-2);margin-top:4px}
.ocenka--horosho .ocenka__ball{color:var(--zelenyj)}
.ocenka--srednee .ocenka__ball{color:var(--zheltyj)}
.ocenka--ploho .ocenka__ball{color:#a12626}
.cifry{display:grid;grid-template-columns:1fr 1fr;gap:var(--shag)}
.cifra{
  background:var(--seryj-blok);border-radius:var(--shag);
  padding:calc(var(--shag)*2);
}
.cifra__imya{font-size:14px}
.cifra__znachenie{font-size:26px;font-weight:700;margin:2px 0 6px}
.cifra__poyasnenie{font-size:14px;line-height:1.45}
@media (max-width:560px){
  .ocenki{grid-template-columns:1fr 1fr}
  .cifry{grid-template-columns:1fr}
}
```

Цвет `#a12626` для оценок ниже 50 в этом отчёте не используется (низшая
оценка 63), но оставлен: объект данных меняется под следующий сайт, а шкала
должна работать целиком.

- [ ] **Step 6: Посмотреть глазами**

Открыть страницу через Playwright на 1280×900 и на 360×800, снять
скриншоты, показать пользователю. Убедиться: вердикт читается первым,
плашки выстроились, на 360 px нет горизонтальной прокрутки.

- [ ] **Step 7: Прогнать проверки и закоммитить**

```bash
cd ~/Progects/otchet-proverka
python3 tools/proverka.py
git add index.html
git commit -m "$(cat <<'EOF'
Оформление отчёта, вердикт и сводка с оценками

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: Раздел «Что поправить» — три карточки

**Files:**
- Modify: `/Users/dmitrijvolkov/Progects/otchet-proverka/index.html` — блоки `ОФОРМЛЕНИЕ` и `ПОСТРОЕНИЕ`

**Interfaces:**
- Consumes: `ОТЧЁТ.nahodki` из задачи 1; функции `el` и `razdel` из задачи 3.
- Produces: класс `.nahodka` — на него опираются правила печати в задаче 6 (`break-inside: avoid`).

- [ ] **Step 1: Построить карточки**

Добавить в конец блока `ПОСТРОЕНИЕ`:

```js
/* — что поправить — */
const chinit = razdel("Что поправить");
chinit.append(
  el(
    "p",
    "vtorichno podvodka",
    "Порядок — по важности для посетителя, а не по величине экономии. " +
      "Ни один пункт не мешает запуску.",
  ),
);

const spisok_nahodok = el("div", "stopka");
for (const n of ОТЧЁТ.nahodki) {
  const k = el("article", "kartochka nahodka");

  const verh = el("div", "nahodka__verh");
  verh.append(
    el("span", "nahodka__nomer", String(n.nomer)),
    el("h3", "", n.zagolovok),
  );
  k.append(verh);

  for (const [podpis, tekst] of [
    ["Что нашёл", n.chto],
    ["Чем это грозит посетителю", n.chem_grozit],
    ["Что делать", n.chto_delat],
  ]) {
    const blok = el("div", "nahodka__blok");
    blok.append(el("p", "nahodka__podpis vtorichno", podpis), el("p", "", tekst));
    k.append(blok);
  }

  const niz = el("dl", "nahodka__niz");
  for (const [podpis, tekst] of [
    ["Сколько займёт", n.skolko],
    ["Справитесь сами", n.sam],
  ]) {
    niz.append(el("dt", "vtorichno", podpis), el("dd", "", tekst));
  }
  k.append(niz);

  spisok_nahodok.append(k);
}
chinit.append(spisok_nahodok);
koren.append(chinit);
```

- [ ] **Step 2: Оформить карточки**

Добавить в `<style>`:

```css
.podvodka{margin-bottom:calc(var(--shag)*2);max-width:58ch;font-size:15px}
.nahodka{
  border-left:4px solid var(--zheltyj);
  display:flex;flex-direction:column;gap:calc(var(--shag)*2);
}
.nahodka__verh{display:flex;align-items:baseline;gap:calc(var(--shag)*1.5)}
.nahodka__nomer{
  flex:none;width:28px;height:28px;border-radius:50%;
  background:var(--zheltyj);color:#fff;
  font-size:15px;font-weight:700;line-height:28px;text-align:center;
  align-self:flex-start;
}
.nahodka__blok>p+p{margin-top:2px;max-width:64ch}
.nahodka__podpis{
  font-size:13px;font-weight:700;letter-spacing:0.04em;text-transform:uppercase;
}
.nahodka__niz{
  display:grid;grid-template-columns:auto 1fr;gap:4px calc(var(--shag)*2);
  margin:0;padding-top:calc(var(--shag)*2);
  border-top:1px solid var(--ramka);font-size:15px;
}
.nahodka__niz dt{font-size:13px;align-self:center}
.nahodka__niz dd{margin:0}
```

Белый текст на `--zheltyj` (#87560a) даёт контраст около 6,8 — с запасом.
Эта пара в списке `PARY` не проверяется автоматически, потому что `#fff` не
объявлен переменной; посчитать разово руками при первом прогоне.

- [ ] **Step 3: Посмотреть глазами и проверить перенос**

Открыть через Playwright на 1280×900 и на 360×800. Проверить: номер не
уезжает от заголовка при переносе на две строки, длинные слова
(`favicon.ico`, `JavaScript`) не вылезают за карточку.

- [ ] **Step 4: Прогнать проверки и закоммитить**

```bash
cd ~/Progects/otchet-proverka
python3 tools/proverka.py
git add index.html
git commit -m "$(cat <<'EOF'
Раздел «Что поправить»: три карточки находок

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: Пояснение про SEO, перечень проверенного, чужая зона, подвал

**Files:**
- Modify: `/Users/dmitrijvolkov/Progects/otchet-proverka/index.html` — блоки `ОФОРМЛЕНИЕ` и `ПОСТРОЕНИЕ`

**Interfaces:**
- Consumes: `ОТЧЁТ.seo`, `ОТЧЁТ.provereno`, `ОТЧЁТ.ne_nasha_zona`, `ОТЧЁТ.zamer` из задачи 1; `el` и `razdel` из задачи 3.
- Produces: класс `.podval` — задача 6 показывает в печати адрес и дату из него.

- [ ] **Step 1: Перепроверить утверждения перечня на живом сайте**

Отчёт утверждает, что семь областей в порядке. Перед тем как это напечатать,
убедиться, что так и есть:

```bash
SAJT=https://pyhphhddb8-eng.github.io/katalog-arenda
curl -sS -A "Mozilla/5.0" $SAJT/ | tr '>' '>\n' | grep -iE 'og:|twitter:|canonical'
curl -s -o /dev/null -w "404-страница: %{http_code}\n" $SAJT/net-takoj-stranicy
curl -s -o /dev/null -w "картинка превью: %{http_code} %{size_download} байт\n" $SAJT/og.jpg
```

Ожидаем: og:title, og:description, og:image 1200×630, twitter:card,
canonical на адрес каталога; несуществующая страница отдаёт 404; `og.jpg`
отдаётся с кодом 200.

Пункты «работа с клавиатуры», «мобильная вёрстка 360 px», «консоль» и
«скачки вёрстки» проверяются в задаче 7 — там уже открыт браузер. Если
любой пункт не подтвердится, **строку из `ОТЧЁТ.provereno` убрать или
переписать**: выдуманных проверок в отчёте быть не должно.

- [ ] **Step 2: Построить три раздела и подвал**

Добавить в конец блока `ПОСТРОЕНИЕ`:

```js
/* — почему SEO 63 — */
const seo = razdel(ОТЧЁТ.seo.zagolovok);
const seo_kartochka = el("div", "kartochka poyasnenie");
seo_kartochka.append(el("p", "", ОТЧЁТ.seo.tekst));
seo.append(seo_kartochka);
koren.append(seo);

/* — проверено и в порядке — */
const porjadok = razdel("Проверено и в порядке");
porjadok.append(
  el(
    "p",
    "vtorichno podvodka",
    "Здесь перечислено то, что проверялось и замечаний не вызвало — " +
      "чтобы был виден охват проверки, а не только её находки.",
  ),
);
const spisok = el("ul", "porjadok");
for (const stroka of ОТЧЁТ.provereno) {
  spisok.append(el("li", "", stroka));
}
porjadok.append(spisok);
koren.append(porjadok);

/* — не наша зона — */
const chuzhoe = razdel(ОТЧЁТ.ne_nasha_zona.zagolovok);
const chuzhoe_kartochka = el("div", "kartochka poyasnenie");
chuzhoe_kartochka.append(el("p", "", ОТЧЁТ.ne_nasha_zona.tekst));
chuzhoe.append(chuzhoe_kartochka);
koren.append(chuzhoe);

/* — подвал: чем мерил, когда, в каких условиях — */
const z = ОТЧЁТ.zamer;
const podval = el("footer", "podval");
podval.append(el("p", "nadpis vtorichno", "Как проводился замер"));
podval.append(
  el(
    "p",
    "",
    `${z.instrument} ${z.versiya}, ${z.rezhim}. ` +
      `Медиана ${z.progonov} прогонов. Замер от ${z.data}.`,
  ),
);
const podval_adres = el("a", "");
podval_adres.href = ОТЧЁТ.sajt.adres;
podval_adres.textContent = ОТЧЁТ.sajt.adres;
const podval_sajt = el("p", "");
podval_sajt.append(document.createTextNode("Проверенный сайт: "), podval_adres);
podval.append(podval_sajt);
podval.append(
  el(
    "p",
    "",
    "Сырые отчёты инструмента сохранены — числа в документе можно сверить с ними.",
  ),
);
koren.append(podval);
/* ПОСТРОЕНИЕ: конец */
```

- [ ] **Step 3: Оформить**

Добавить в `<style>`:

```css
.poyasnenie{border-left:4px solid var(--sinij)}
.poyasnenie p{max-width:64ch}
.porjadok{
  margin:0;padding:0;list-style:none;
  display:flex;flex-direction:column;gap:var(--shag);
}
.porjadok li{
  position:relative;padding-left:calc(var(--shag)*3.5);
  background:var(--list);border:1px solid var(--ramka);
  border-radius:var(--shag);
  padding-top:calc(var(--shag)*1.5);padding-bottom:calc(var(--shag)*1.5);
  padding-right:calc(var(--shag)*2);
  font-size:16px;line-height:1.5;
}
.porjadok li::before{
  content:"✓";position:absolute;left:calc(var(--shag)*1.5);
  color:var(--zelenyj);font-weight:700;
}
.podval{
  margin-top:calc(var(--shag)*6);padding-top:calc(var(--shag)*3);
  border-top:1px solid var(--ramka);
  color:var(--tekst-2);font-size:14px;line-height:1.55;
}
.podval a{word-break:break-all}
.podval p+p{margin-top:4px}
```

- [ ] **Step 4: Посмотреть глазами**

Playwright, 1280×900 и 360×800, скриншот целой страницы. Прочитать текст
целиком вслух про себя: нет ли рекламы услуг, запугивания, оценок вроде
«сайт ужасен».

- [ ] **Step 5: Прогнать проверки и закоммитить**

```bash
cd ~/Progects/otchet-proverka
python3 tools/proverka.py
git add index.html
git commit -m "$(cat <<'EOF'
Пояснение про SEO, перечень проверенного, чужая зона и подвал

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 6: Печать в PDF

**Files:**
- Modify: `/Users/dmitrijvolkov/Progects/otchet-proverka/index.html` — блоки `ПЕЧАТЬ`, `ОФОРМЛЕНИЕ`, `ПОСТРОЕНИЕ`

**Interfaces:**
- Consumes: классы `.kartochka`, `.nahodka`, `.podval`, `.ocenki`, `.svodka` из задач 3–5.
- Produces: кнопку `#pechat` — на неё смотрит проверка в задаче 7 (в печати её быть не должно).

- [ ] **Step 1: Добавить кнопку печати**

Вставить в блок `ПОСТРОЕНИЕ` сразу после создания `shapka`, до
`koren.append(shapka)`:

```js
const knopka = el("button", "pechat", "Сохранить в PDF");
knopka.id = "pechat";
knopka.type = "button";
knopka.addEventListener("click", () => window.print());
shapka.append(knopka);
```

- [ ] **Step 2: Оформить кнопку с видимыми состояниями**

Добавить в `<style>`:

```css
.shapka{position:relative}
.pechat{
  position:absolute;top:0;right:0;
  font:700 15px/1 var(--shrift);color:var(--list);
  background:var(--tekst);border:1px solid var(--tekst);
  border-radius:var(--shag);padding:11px 16px;cursor:pointer;
}
.pechat:hover{background:var(--tekst-2);border-color:var(--tekst-2)}
.pechat:focus-visible{outline:3px solid var(--sinij);outline-offset:2px}
.pechat:active{transform:translateY(1px)}
@media (max-width:560px){
  .pechat{position:static;margin-top:calc(var(--shag)*1.5);width:100%}
}
```

- [ ] **Step 3: Написать правила печати**

Заменить строку `<!-- ПЕЧАТЬ: задача 6 -->` в `<head>` на `<style media="print">`
с таким содержимым (отдельным тегом, чтобы правила печати не путались с
экранными):

```css
/* ПЕЧАТЬ: начало */
@page{size:A4;margin:16mm 14mm}
body{
  background:#fff;padding:0;font-size:11.5pt;line-height:1.45;
}
#otchet{max-width:none}
.pechat{display:none}
h1{font-size:22pt}
h2{font-size:15pt}
h3{font-size:12.5pt}
/* карточки не рвутся между страницами */
.kartochka,.nahodka,.porjadok li,.cifra,.ocenka{
  break-inside:avoid;page-break-inside:avoid;
}
.razdel{break-before:auto;margin-top:14mm}
.razdel>h2{break-after:avoid;page-break-after:avoid}
/* убрать лишние фоны, оставить смысловые рамки */
.kartochka,.porjadok li{
  background:none;border:1px solid #c8ccd2;border-radius:0;
}
.cifra{background:none;border:1px solid #c8ccd2}
.ocenka{border:1px solid #c8ccd2}
.verdikt{border-left:3pt solid #000}
.nahodka{border-left:3pt solid #000}
.poyasnenie{border-left:3pt solid #000}
.nahodka__nomer{background:#000;color:#fff}
/* адреса ссылок разворачиваются в текст рядом со ссылкой */
a{color:#000;text-decoration:underline}
a[href^="http"]::after{
  content:" (" attr(href) ")";
  font-size:9.5pt;word-break:break-all;text-decoration:none;
}
/* в подвале адрес уже написан текстом — там разворачивать незачем */
.podval a[href^="http"]::after{content:""}
.podval{color:#000;border-top:1px solid #c8ccd2}
/* ПЕЧАТЬ: конец */
```

- [ ] **Step 4: Напечатать и посмотреть**

Через Playwright открыть `file:///Users/dmitrijvolkov/Progects/otchet-proverka/index.html`,
сохранить PDF и открыть его:

```bash
cd ~/Progects/otchet-proverka && open otchet-proverka.pdf
```

Смотреть: кнопки в PDF нет; ни одна карточка находки не разрезана между
страницами; заголовок раздела не остался один внизу страницы; адрес
проверенного сайта развёрнут текстом; читается как документ, а не как
обрезанный сайт.

- [ ] **Step 5: Не класть PDF в репозиторий**

```bash
cd ~/Progects/otchet-proverka
printf 'otchet-proverka.pdf\n' >> .gitignore
python3 tools/proverka.py
git add index.html .gitignore
git commit -m "$(cat <<'EOF'
Правила печати в PDF: кнопка, неразрывные карточки, адреса ссылок

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 7: Живые проверки

Здесь проверяется всё, что нельзя проверить по тексту файла. Сначала
локально, чтобы не гонять правки через выкладку.

**Files:**
- Modify: `/Users/dmitrijvolkov/Progects/otchet-proverka/index.html` — только если проверка что-то найдёт.

**Interfaces:**
- Consumes: готовую страницу из задач 1–6.
- Produces: ничего для кода — список подтверждённых свойств для README задачи 8.

- [ ] **Step 1: Ширина 360 px — нет горизонтальной прокрутки**

Открыть страницу в Playwright, размер окна 360×800, выполнить в странице:

```js
({
  prokrutka: document.documentElement.scrollWidth > document.documentElement.clientWidth,
  scrollWidth: document.documentElement.scrollWidth,
  clientWidth: document.documentElement.clientWidth,
  vylezli: [...document.querySelectorAll("*")]
    .filter(e => e.getBoundingClientRect().right > document.documentElement.clientWidth + 1)
    .map(e => e.className || e.tagName),
})
```

Ожидаем: `prokrutka: false`, `vylezli: []`. Если что-то вылезло — чинить
этот элемент, а не прятать `overflow-x: hidden` на `body`.

- [ ] **Step 2: Консоль чистая**

Снять сообщения консоли за загрузку страницы. Ожидаем пустой список — ни
ошибок, ни предупреждений.

- [ ] **Step 3: Проверить работу с клавиатуры**

Нажать Tab от начала страницы. Ожидаем: фокус доходит до кнопки «Сохранить
в PDF» и до ссылок, и на каждом видна рамка фокуса.

- [ ] **Step 4: Скриншоты для показа**

Снять три скриншота во временную папку (в репозиторий они не идут):
страница целиком на 1280, первый экран на 1280, страница целиком на 360.
Показать пользователю и дождаться его замечаний. **Правки вносятся здесь,
до выкладки.**

- [ ] **Step 5: Полный прогон проверок**

```bash
cd ~/Progects/otchet-proverka && python3 tools/proverka.py
```

Ожидаем: `Всё сошлось: числа, контраст, самодостаточность.`

- [ ] **Step 6: Коммит, если что-то правилось**

```bash
cd ~/Progects/otchet-proverka
git add index.html
git commit -m "$(cat <<'EOF'
Правки по живым проверкам: 360 px, консоль, фокус с клавиатуры

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

Если правок не потребовалось — шаг пропускается.

---

### Task 8: Выкладка на GitHub Pages и README

**Files:**
- Modify: `/Users/dmitrijvolkov/Progects/otchet-proverka/README.md`

**Interfaces:**
- Consumes: готовую проверенную страницу.
- Produces: живой адрес `https://pyhphhddb8-eng.github.io/otchet-proverka/`.

**Перед началом:** прочитать скилл `deploy-static-ru`.

- [ ] **Step 1: Спросить разрешение на публикацию**

Выкладка делает работу публичной — спросить пользователя и дождаться
ответа. Показать: аккаунт `pyhphhddb8-eng`, имя репозитория
`otchet-proverka`, видимость `public`, адрес будущей страницы.

- [ ] **Step 2: Создать репозиторий и отправить код**

```bash
cd ~/Progects/otchet-proverka
gh repo create pyhphhddb8-eng/otchet-proverka --public --source=. --remote=origin --push
```

- [ ] **Step 3: Включить Pages с ветки**

```bash
cd ~/Progects/otchet-proverka
gh api -X POST repos/pyhphhddb8-eng/otchet-proverka/pages \
  -f 'source[branch]=main' -f 'source[path]=/'
```

Если репозиторий отправился в ветку с другим именем — подставить её.

- [ ] **Step 4: Дождаться публикации и проверить живой адрес**

```bash
ADRES=https://pyhphhddb8-eng.github.io/otchet-proverka/
for i in $(seq 1 20); do
  KOD=$(curl -s -o /dev/null -w "%{http_code}" "$ADRES")
  echo "попытка $i: $KOD"
  [ "$KOD" = "200" ] && break
  sleep 15
done
curl -sS "$ADRES" | head -c 400
curl -s -o /dev/null -w "вес страницы: %{size_download} байт\n" \
  -H 'Accept-Encoding: gzip, br' "$ADRES"
```

Заголовок `Accept-Encoding` здесь обязателен: без него `curl` показывает
распакованный размер и даёт число втрое больше настоящего. На этой ошибке
в проекте уже один раз построили неверный вывод.

- [ ] **Step 5: Проверить живую страницу браузером**

Через Playwright открыть живой адрес. Проверить: страница построилась,
консоль чистая, шрифт подхватился (текст не системным), внешних запросов в
списке сетевых запросов нет — только сам документ.

- [ ] **Step 6: Обновить README**

Заменить разделы «Состояние» и «Выкладка» в `README.md`:

```markdown
## Состояние на 14.09.2026

Отчёт свёрстан, проверен и выложен:
https://pyhphhddb8-eng.github.io/otchet-proverka/

## Как повторить проверки

    python3 tools/proverka.py

Скрипт сверяет каждое число страницы с сохранёнными отчётами в `zamery/`,
считает контраст по формуле WCAG и следит, что страница осталась
самодостаточной — без единого внешнего запроса.

Шрифт подрезается разово: `python3 tools/shrift.py`. След от подрезки —
в `tools/shrift-podpis.txt`.

## Единицы измерения

Числа берутся из Lighthouse дословно, в его единицах (КиБ), а слово
пишется привычное — «КБ». Поэтому вес страницы здесь 82 КБ, а не 81, как
было в первой редакции спеки: две системы счёта в одном документе ломают
главное свойство отчёта — возможность повторить замер и сойтись в цифрах.
```

- [ ] **Step 7: Коммит и отправка**

```bash
cd ~/Progects/otchet-proverka
git add README.md
git commit -m "$(cat <<'EOF'
README: живой адрес отчёта и как повторить проверки

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
git push
```

- [ ] **Step 8: Обновить журнал второго мозга**

Дописать в `~/Obsidian/Brain/index.md`: что сделано, адрес страницы, что
дальше (починить три находки в каталоге и выпустить вторую версию отчёта с
парой «было / стало»), дата 14.09.2026.

Решение про единицы измерения — в `~/Obsidian/Brain/decisions.md`: числа в
отчётах берутся в единицах инструмента, смешивать КиБ и десятичные КБ
нельзя.

---

## Что будет считаться сделанным

- `python3 tools/proverka.py` проходит молча.
- Страница открывается по живому адресу, консоль чистая, внешних запросов ноль.
- На 360 px горизонтальной прокрутки нет.
- Печать в PDF даёт документ без разрезанных карточек, кнопки в нём нет.
- Каждое число страницы сходится с `zamery/`.
- Пользователь посмотрел скриншоты и сказал «да».
