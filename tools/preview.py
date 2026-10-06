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


shrift = "\n".join(re.findall(r"@font-face\{.*?\}", HTML, re.S))
if not shrift:
    raise SystemExit("Не нашёл в index.html: правила @font-face")
tokeny = kusok(r":root\{.*?\}", "блок :root")

# данные для превью — из того же объекта, что и сам отчёт
dannye = re.search(r"const ОТЧЁТ = (\{.*?\n\s*\});", HTML, re.S).group(1)
import json

otchet = json.loads(dannye)
ocenki = "".join(
    f'<tr><td>{o["imya"]}</td><td class="{"z" if o["ball"] >= 90 else "zh"}">{o["ball"]}</td></tr>'
    for o in otchet["ocenki"]
)
data = otchet["zamery"]["posle"]["data"].replace(" года", "")

# Превью — верх того же листа: лист отчёта на столе со штампом проверки.
STRANICA = f"""<!doctype html><html lang="ru"><head><meta charset="utf-8"><style>
{shrift}
{tokeny}
*{{box-sizing:border-box;margin:0}}
body{{width:1200px;height:630px;overflow:hidden;background:var(--fon);
  font-family:var(--sans);color:var(--tekst);position:relative}}
.list{{position:absolute;left:150px;top:56px;width:900px;height:640px;background:var(--list);
  padding:52px 64px;box-shadow:0 2px 4px rgba(27,31,38,.15),0 30px 60px -30px rgba(27,31,38,.55)}}
.shapka{{font-size:21px;padding-bottom:20px;border-bottom:3px solid var(--tekst);line-height:1.45}}
.shapka span{{color:var(--tekst-2)}}
h1{{font-family:var(--serif);font-weight:600;font-size:62px;line-height:1.08;margin-top:34px;max-width:12ch;text-wrap:balance}}
.shtamp{{position:absolute;right:70px;top:150px;width:280px;padding:16px 10px 13px;
  border:5px double var(--shtamp);border-radius:9px;color:var(--shtamp);text-align:center;
  transform:rotate(-7deg)}}
.shtamp b{{display:block;font-size:36px;font-weight:600;letter-spacing:.06em;line-height:1.1}}
.shtamp span{{display:block;font-size:20px;margin-top:4px}}
table{{margin-top:30px;border-collapse:collapse;font-size:23px;width:470px}}
td{{padding:8px 0;border-top:1px solid var(--ramka)}}
td+td{{text-align:right;font-weight:600}}
.z{{color:var(--zelenyj)}} .zh{{color:var(--zheltyj)}}
</style></head><body>
<div class="list">
  <p class="shapka">Отчёт о проверке сайта перед запуском<br><span>{otchet["sajt"]["nazvanie"]}</span></p>
  <h1>{otchet["verdikt"]["zagolovok"]}</h1>
  <table>{ocenki}</table>
  <p class="shtamp"><b>ПРОВЕРЕНО</b><span>{data}</span></p>
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
