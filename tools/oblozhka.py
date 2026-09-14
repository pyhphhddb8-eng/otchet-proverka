#!/usr/bin/env python3
"""Обложки работы для бирж.

Запуск: python3 tools/oblozhka.py [fl|kwork]
  fl    — квадрат 1000×1000 (FL.ru требует 1:1)  -> pokazat/fl/oblozhka.png
  kwork — 1200×800 (Kwork требует от 660×440)   -> pokazat/kwork/oblozhka.png

Стиль повторяет две работы, уже стоящие в портфолио: тёмный фон,
рубрика капсом, крупный заголовок, две цифры и снимок самой работы.
Шрифт берётся из index.html — тот же, что в документе.
"""
import base64
import pathlib
import re
import subprocess
import tempfile

KOREN = pathlib.Path(__file__).resolve().parent.parent
HTML = (KOREN / "index.html").read_text(encoding="utf-8")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SNIMOK = KOREN / "pokazat" / "otchet-na-kompyutere.png"

import sys

FORMAT = sys.argv[1] if len(sys.argv) > 1 else "fl"
RAZMERY = {"fl": (1000, 1000, "fl"), "kwork": (1200, 800, "kwork")}
if FORMAT not in RAZMERY:
    sys.exit("Формат: fl или kwork")
SHIRINA, VYSOTA, PAPKA = RAZMERY[FORMAT]

shrift = re.search(r"@font-face\{.*?\}", HTML, re.S).group(0)
snimok_b64 = base64.b64encode(SNIMOK.read_bytes()).decode("ascii")

STRANICA = f"""<!doctype html><html lang="ru"><head><meta charset="utf-8"><style>
{shrift}
*{{box-sizing:border-box;margin:0}}
:root{{
  --fon:#121518; --list:#1b1f24; --ramka:#2b3138;
  --tekst:#f3f5f7; --tekst-2:#9aa4b0;
  --zelenyj:#4ec98a; --zheltyj:#e0a54a;
}}
body{{width:{SHIRINA}px;height:{VYSOTA}px;background:var(--fon);color:var(--tekst);
  font-family:"Inter",system-ui,sans-serif;
  padding:{"56px 60px 0" if FORMAT == "kwork" else "64px 60px 0"};display:flex;flex-direction:column;overflow:hidden}}
.rubrika{{font-size:19px;font-weight:700;letter-spacing:.11em;text-transform:uppercase;
  color:var(--tekst-2)}}
h1{{font-size:{62 if FORMAT == "fl" else 58}px;font-weight:700;letter-spacing:-.025em;line-height:1.06;margin-top:20px}}
.cifry{{display:flex;gap:18px;margin-top:{36 if FORMAT == "fl" else 28}px}}
.c{{flex:1;background:var(--list);border:1px solid var(--ramka);border-radius:16px;padding:24px 26px}}
.c b{{display:block;font-size:46px;font-weight:700;letter-spacing:-.02em;line-height:1.05}}
.c .z{{color:var(--zelenyj)}}
.c i{{display:block;font-style:normal;font-size:20px;font-weight:600;margin-top:8px}}
.c span{{display:block;font-size:17px;color:var(--tekst-2);margin-top:3px;line-height:1.35}}
.snimok{{margin-top:{40 if FORMAT == "fl" else 30}px;border-radius:16px 16px 0 0;overflow:hidden;
  border:1px solid var(--ramka);border-bottom:0;flex:1}}
.snimok img{{display:block;width:100%}}
</style></head><body>
  <p class="rubrika">Проверка перед запуском · каталог аренды</p>
  <h1>Отчёт о проверке<br>сайта перед запуском</h1>
  <div class="cifry">
    <div class="c"><b class="z">3</b><i>находки</i><span>ни одна не мешает запуску</span></div>
    <div class="c"><b class="zh" style="color:var(--zheltyj)">7</b><i>областей проверено</i><span>без замечаний</span></div>
  </div>
  <div class="snimok"><img src="data:image/png;base64,{snimok_b64}"></div>
</body></html>"""

if __name__ == "__main__":
    vyhod = KOREN / "pokazat" / PAPKA / "oblozhka.png"
    vyhod.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as vremenno:
        istochnik = pathlib.Path(vremenno) / "o.html"
        istochnik.write_text(STRANICA, encoding="utf-8")
        subprocess.run(
            [CHROME, "--headless", "--disable-gpu", f"--window-size={SHIRINA},{VYSOTA}",
             "--hide-scrollbars", f"--screenshot={vyhod}",
             "--virtual-time-budget=3000", istochnik.as_uri()],
            check=True, capture_output=True,
        )
    print(f"обложка готова: {vyhod.stat().st_size / 1024:.0f} КБ")
