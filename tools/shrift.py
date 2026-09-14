#!/usr/bin/env python3
"""Разовая подготовка шрифта: скачать Inter, подрезать, выдать base64.

Запуск: python3 tools/shrift.py > tools/.shrift-vremenno/pravila.css

Печатает готовое правило @font-face — его вставляют в index.html.
Набор символов берётся из самого index.html, поэтому скрипт можно
перезапустить, когда текст отчёта изменится.

Берётся переменный файл Inter: одна ось начертания вместо двух отдельных
файлов на 400 и 700. Ось оптического размера прижимается к 16 — отчёт
набран одним кеглем, вторая ось ему не нужна.
"""
import base64
import pathlib
import subprocess
import sys
import urllib.request

KOREN = pathlib.Path(__file__).resolve().parent.parent
HTML = (KOREN / "index.html").read_text(encoding="utf-8")
VREMENNO = KOREN / "tools" / ".shrift-vremenno"
VREMENNO.mkdir(exist_ok=True)

ADRES = (
    "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/"
    "Inter%5Bopsz%2Cwght%5D.ttf"
)
NACHERTANIYA = "400 700"  # совпадает с осью после сужения
OSI = ["opsz=16", "wght=400:700"]


def simvoly_stranicy():
    """Все символы, которые страница может показать, плюс запас."""
    import re

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


def main():
    syroj = VREMENNO / "inter-var.ttf"
    if not syroj.exists():
        print("Качаю Inter…", file=sys.stderr)
        with urllib.request.urlopen(ADRES) as otvet:
            syroj.write_bytes(otvet.read())
    print(f"Исходный файл: {syroj.stat().st_size / 1024:.0f} КБ", file=sys.stderr)

    # 1. Прижать ось оптического размера, сузить ось начертания.
    suzhennyj = VREMENNO / "inter-suzhennyj.ttf"
    subprocess.run(
        [sys.executable, "-m", "fontTools.varLib.instancer", str(syroj)]
        + OSI
        + ["-o", str(suzhennyj)],
        check=True,
        stdout=subprocess.DEVNULL,
    )

    # 2. Оставить только те символы, которые есть на странице.
    nabor = simvoly_stranicy()
    print(f"Символов в наборе: {len(nabor)}", file=sys.stderr)
    podrezannyj = VREMENNO / "inter.woff2"
    subprocess.run(
        [
            sys.executable, "-m", "fontTools.subset", str(suzhennyj),
            f"--text={nabor}",
            "--layout-features=kern,liga,calt",
            "--flavor=woff2",
            "--no-hinting",
            f"--output-file={podrezannyj}",
        ],
        check=True,
    )

    bajty = podrezannyj.read_bytes()
    print(f"После подрезки: {len(bajty) / 1024:.1f} КБ", file=sys.stderr)
    kod = base64.b64encode(bajty).decode("ascii")
    print(
        '@font-face{font-family:"Inter";font-style:normal;'
        f"font-weight:{NACHERTANIYA};font-display:swap;"
        f'src:url(data:font/woff2;base64,{kod}) format("woff2")}}'
    )


if __name__ == "__main__":
    main()
