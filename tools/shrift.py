#!/usr/bin/env python3
"""Разовая подготовка шрифтов: скачать IBM Plex, подрезать, выдать base64.

Запуск: python3 tools/shrift.py > tools/.shrift-vremenno/pravila.css

Печатает два правила @font-face — их вставляют в index.html.
Набор символов берётся из самого index.html, поэтому скрипт можно
перезапустить, когда текст отчёта изменится.

IBM Plex — шрифт технической документации: Sans для текста отчёта,
Serif для заголовков, как в бумажном акте. У Sans переменный файл:
ось ширины прижимается к обычной, ось толщины сужается до 400–600.
"""
import base64
import pathlib
import re
import subprocess
import sys
import urllib.request

KOREN = pathlib.Path(__file__).resolve().parent.parent
HTML = (KOREN / "index.html").read_text(encoding="utf-8")
VREMENNO = KOREN / "tools" / ".shrift-vremenno"
VREMENNO.mkdir(exist_ok=True)

ISTOCHNIK = "https://raw.githubusercontent.com/google/fonts/main/ofl/"
SHRIFTY = [
    # (семейство, файл в google/fonts, оси для сужения или None, толщина в CSS)
    ("IBM Plex Sans", "ibmplexsans/IBMPlexSans%5Bwdth%2Cwght%5D.ttf",
     ["wdth=100", "wght=400:600"], "400 600"),
    ("IBM Plex Serif", "ibmplexserif/IBMPlexSerif-SemiBold.ttf", None, "600"),
]


def simvoly_stranicy():
    """Все символы, которые страница может показать, плюс запас."""
    bez_tegov = re.sub(r"<[^>]+>", " ", HTML)
    zapas = (
        "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
        "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789"
        " .,:;!?—–-«»\"'()[]{}/\\%№×→•…+=@#&*_|<>"
        "✓"
    )
    return "".join(sorted(set(bez_tegov + zapas) - set("\n\r\t")))


def podgotovit(semejstvo, put, osi, tolshchina, nabor):
    imya = put.split("/")[-1].split("%")[0].replace(".ttf", "")
    syroj = VREMENNO / f"{imya}.ttf"
    if not syroj.exists():
        print(f"Качаю {semejstvo}…", file=sys.stderr)
        with urllib.request.urlopen(ISTOCHNIK + put) as otvet:
            syroj.write_bytes(otvet.read())

    ishodnyj = syroj
    if osi:
        ishodnyj = VREMENNO / f"{imya}-suzhennyj.ttf"
        subprocess.run(
            [sys.executable, "-m", "fontTools.varLib.instancer", str(syroj)]
            + osi + ["-o", str(ishodnyj)],
            check=True, stdout=subprocess.DEVNULL,
        )

    podrezannyj = VREMENNO / f"{imya}.woff2"
    subprocess.run(
        [
            sys.executable, "-m", "fontTools.subset", str(ishodnyj),
            f"--text={nabor}",
            "--layout-features=kern,liga,calt",
            "--flavor=woff2",
            "--no-hinting",
            f"--output-file={podrezannyj}",
        ],
        check=True,
    )
    bajty = podrezannyj.read_bytes()
    print(f"{semejstvo}: {len(bajty) / 1024:.1f} КБ", file=sys.stderr)
    kod = base64.b64encode(bajty).decode("ascii")
    return (
        f'@font-face{{font-family:"{semejstvo}";font-style:normal;'
        f"font-weight:{tolshchina};font-display:swap;"
        f'src:url(data:font/woff2;base64,{kod}) format("woff2")}}'
    )


def main():
    nabor = simvoly_stranicy()
    print(f"Символов в наборе: {len(nabor)}", file=sys.stderr)
    for semejstvo, put, osi, tolshchina in SHRIFTY:
        print(podgotovit(semejstvo, put, osi, tolshchina, nabor))


if __name__ == "__main__":
    main()
