#!/usr/bin/env python3
"""Иконка отчёта: галочка в скруглённом квадрате.

Запуск: python3 tools/ikonka.py
Кладёт рядом favicon.ico (32×32) и печатает data-URI векторной версии —
её вставляют в <link rel="icon"> внутри index.html.

Без зависимостей: PNG и ICO собираются байтами, сглаживание — усреднением
по сетке 4×4 на пиксель.
"""
import pathlib
import struct
import zlib

KOREN = pathlib.Path(__file__).resolve().parent.parent
STORONA = 32
PODSETKA = 4

FON = (0x15, 0x70, 0x4A)  # --zelenyj из index.html
GALKA = (0xFF, 0xFF, 0xFF)
RADIUS = 0.22  # доля стороны
TOLSHCHINA = 0.115
TOCHKI = [(0.27, 0.52), (0.435, 0.685), (0.75, 0.32)]


def vnutri_skruglyonnogo_kvadrata(x, y):
    r = RADIUS
    dx = abs(x - 0.5) - (0.5 - r)
    dy = abs(y - 0.5) - (0.5 - r)
    if dx <= 0 or dy <= 0:
        return max(dx, dy) <= 0
    return dx * dx + dy * dy <= r * r


def rasstoyanie_do_otrezka(x, y, ax, ay, bx, by):
    vx, vy = bx - ax, by - ay
    dlina2 = vx * vx + vy * vy
    t = 0.0 if dlina2 == 0 else max(0.0, min(1.0, ((x - ax) * vx + (y - ay) * vy) / dlina2))
    px, py = ax + t * vx, ay + t * vy
    return ((x - px) ** 2 + (y - py) ** 2) ** 0.5


def na_galke(x, y):
    pol = TOLSHCHINA / 2
    for (ax, ay), (bx, by) in zip(TOCHKI, TOCHKI[1:]):
        if rasstoyanie_do_otrezka(x, y, ax, ay, bx, by) <= pol:
            return True
    return False


def piksel(px, py):
    """Цвет и прозрачность одного пикселя со сглаживанием."""
    fon_dolya = galka_dolya = 0
    vsego = PODSETKA * PODSETKA
    for i in range(PODSETKA):
        for j in range(PODSETKA):
            x = (px + (i + 0.5) / PODSETKA) / STORONA
            y = (py + (j + 0.5) / PODSETKA) / STORONA
            if vnutri_skruglyonnogo_kvadrata(x, y):
                fon_dolya += 1
                if na_galke(x, y):
                    galka_dolya += 1
    if fon_dolya == 0:
        return (0, 0, 0, 0)
    dolya_galki = galka_dolya / fon_dolya
    cvet = tuple(
        round(FON[k] * (1 - dolya_galki) + GALKA[k] * dolya_galki) for k in range(3)
    )
    return cvet + (round(255 * fon_dolya / vsego),)


def sobrat_png():
    stroki = bytearray()
    for y in range(STORONA):
        stroki.append(0)  # фильтр «без фильтра»
        for x in range(STORONA):
            stroki.extend(piksel(x, y))

    def kusok(imya, dannye):
        telo = imya + dannye
        return struct.pack(">I", len(dannye)) + telo + struct.pack(
            ">I", zlib.crc32(telo) & 0xFFFFFFFF
        )

    return (
        b"\x89PNG\r\n\x1a\n"
        + kusok(b"IHDR", struct.pack(">IIBBBBB", STORONA, STORONA, 8, 6, 0, 0, 0))
        + kusok(b"IDAT", zlib.compress(bytes(stroki), 9))
        + kusok(b"IEND", b"")
    )


def sobrat_ico(png):
    """ICO с вложенным PNG — формат понимают все браузеры от Vista и Safari."""
    zagolovok = struct.pack("<HHH", 0, 1, 1)
    zapis = struct.pack(
        "<BBBBHHII", STORONA, STORONA, 0, 0, 1, 32, len(png), 6 + 16
    )
    return zagolovok + zapis + png


def svg():
    tochki = " ".join(f"{x * 32:.1f} {y * 32:.1f}" for x, y in TOCHKI)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
        f'<rect width="32" height="32" rx="{RADIUS * 32:.0f}" fill="#15704a"/>'
        f'<polyline points="{tochki}" fill="none" stroke="#fff" '
        f'stroke-width="{TOLSHCHINA * 32:.1f}" stroke-linecap="round" '
        'stroke-linejoin="round"/></svg>'
    )


if __name__ == "__main__":
    png = sobrat_png()
    (KOREN / "favicon.ico").write_bytes(sobrat_ico(png))
    import urllib.parse

    data_uri = "data:image/svg+xml," + urllib.parse.quote(svg(), safe="")
    print(f'<link rel="icon" href="{data_uri}">')
