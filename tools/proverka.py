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
    "аголов" in poryadok[0]
    and "favicon" in poryadok[1].lower()
    and "JavaScript" in poryadok[2],
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
            trebuem(k >= 4.5, f"Контраст {tekst} на {fon}: {k:.2f} — норма 4,5")

# ------------------------------------------------------------- итог
if oshibki:
    print(f"Расхождений: {len(oshibki)}\n")
    for o in oshibki:
        print(f"  • {o}")
    sys.exit(1)
print("Всё сошлось: числа, контраст, самодостаточность.")
