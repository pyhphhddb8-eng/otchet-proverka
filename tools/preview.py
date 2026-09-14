#!/usr/bin/env python3
"""Картинка превью ссылки (Open Graph, 1200×630).

Запуск: python3 tools/preview.py
Собирает og.png в корне репозитория.

Шрифт и цвета берутся из самого index.html, чтобы превью не разъезжалось
с документом. Рисует headless Chrome: снимок страницы 1200×630.
"""
import pathlib
import re
import subprocess
import tempfile

KOREN = pathlib.Path(__file__).resolve().parent.parent
HTML = (KOREN / "index.html").read_text(encoding="utf-8")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def kusok(obrazec, chto):
    m = re.search(obrazec, HTML, re.S)
    if not m:
        raise SystemExit(f"Не нашёл в index.html: {chto}")
    return m.group(0)


shrift = kusok(r"@font-face\{.*?\}", "правило @font-face")
tokeny = kusok(r":root\{.*?\}", "блок :root")

# данные для превью — из того же объекта, что и сам отчёт
dannye = re.search(r"const ОТЧЁТ = (\{.*?\n\s*\});", HTML, re.S).group(1)
import json

otchet = json.loads(dannye)
ocenki = "".join(
    f'<div class="o"><b class="{"z" if o["ball"] >= 90 else "zh"}">{o["ball"]}</b>'
    f"<span>{o['imya']}</span></div>"
    for o in otchet["ocenki"]
)

STRANICA = f"""<!doctype html><html lang="ru"><head><meta charset="utf-8"><style>
{shrift}
{tokeny}
*{{box-sizing:border-box;margin:0}}
body{{width:1200px;height:630px;background:var(--fon);
  font-family:var(--shrift);color:var(--tekst);
  padding:64px 80px;display:flex;flex-direction:column;justify-content:space-between}}
.nadpis{{font-size:22px;font-weight:700;letter-spacing:.09em;text-transform:uppercase;
  color:var(--tekst-2)}}
h1{{font-size:76px;font-weight:700;letter-spacing:-.025em;line-height:1.04;margin:14px 0 0}}
.galka{{color:var(--zelenyj);font-size:52px;font-weight:700;line-height:1}}
.pod{{font-size:26px;color:var(--tekst-2);margin-top:18px;max-width:30ch;line-height:1.4}}
.ocenki{{display:flex;gap:16px}}
.o{{flex:1;background:var(--list);border:1px solid var(--ramka);border-radius:14px;
  padding:20px;text-align:center}}
.o b{{display:block;font-size:52px;line-height:1.05;letter-spacing:-.02em}}
.o .z{{color:var(--zelenyj)}} .o .zh{{color:var(--zheltyj)}}
.o span{{font-size:19px;color:var(--tekst-2)}}
.niz{{display:flex;flex-direction:column;gap:18px}}
.adres{{font-size:20px;color:var(--tekst-2);line-height:1.45}}
</style></head><body>
<div>
  <p class="nadpis">Отчёт о проверке сайта перед запуском</p>
  <p class="galka">✓</p>
  <h1>{otchet["verdikt"]["zagolovok"]}</h1>
  <p class="pod">Три пункта поправить после запуска. Ни один не мешает открыть сайт.</p>
</div>
<div class="niz">
  <div class="ocenki">{ocenki}</div>
  <p class="adres">Проверен каталог аренды строительного инструмента<br>{otchet["sajt"]["adres"]}</p>
</div>
</body></html>"""

if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as vremenno:
        istochnik = pathlib.Path(vremenno) / "og.html"
        istochnik.write_text(STRANICA, encoding="utf-8")
        subprocess.run(
            [
                CHROME, "--headless", "--disable-gpu",
                "--window-size=1200,630",
                "--default-background-color=FFFFFFFF",
                "--hide-scrollbars",
                f"--screenshot={KOREN / 'og.png'}",
                "--virtual-time-budget=3000",
                istochnik.as_uri(),
            ],
            check=True,
            capture_output=True,
        )
    razmer = (KOREN / "og.png").stat().st_size
    print(f"og.png готов: {razmer / 1024:.0f} КБ")
