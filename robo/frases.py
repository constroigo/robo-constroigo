"""Stories de frases motivacionais: 2 por dia, com autor e a marca Constrói GO."""
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

from playwright.sync_api import sync_playwright

LISTA = Path("data/frases.json")
FUNDOS = [("#0F2240", "#F2B705"), ("#1E4FA0", "#F2B705"), ("#F2B705", "#0F2240")]
BLOCOS = ('<svg viewBox="0 0 200 200" width="{t}" height="{t}"><rect x="30" y="134" width="44" height="44" rx="8" fill="{a}"/>'
          '<rect x="82" y="134" width="44" height="44" rx="8" fill="{a}"/><rect x="134" y="134" width="44" height="44" rx="8" fill="{a}"/>'
          '<rect x="82" y="82" width="44" height="44" rx="8" fill="{a}"/><rect x="134" y="82" width="44" height="44" rx="8" fill="{a}"/>'
          '<rect x="134" y="30" width="44" height="44" rx="8" fill="{b}"/></svg>')

HTML = """<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;background:{bg};color:{fg};font-family:Sora,sans-serif;
     display:flex;flex-direction:column;justify-content:space-between;padding:200px 100px 220px}}
.aspas{{font-size:260px;line-height:.6;font-weight:800;color:{dest}}}
.frase{{font-size:{tam}px;font-weight:700;line-height:1.25;letter-spacing:-.02em;margin-top:40px}}
.autor{{margin-top:56px;font-size:44px;font-weight:600;color:{dest}}}
.cta{{font-size:38px;font-weight:600;opacity:.9;margin-bottom:48px}}
.marca{{display:flex;align-items:center;gap:20px}}
.marca .nome{{font-size:60px;font-weight:800;letter-spacing:-.04em}}
.marca .go{{font-size:46px;font-weight:800;background:{gobg};color:{gofg};padding:4px 16px;border-radius:12px}}
</style></head><body>
<div><div class="aspas">“</div><div class="frase">{frase}</div><div class="autor">— {autor}</div></div>
<div><div class="cta">Gostou? Compartilhe com quem precisa ler isso hoje. 🔁</div>
<div class="marca">{blocos}<span class="nome">constrói</span><span class="go">GO</span></div></div>
</body></html>"""


def gerar(item: dict, destino: Path, seed: int = 0) -> Path:
    bg, dest = FUNDOS[seed % len(FUNDOS)]
    fg = "#0F2240" if bg == "#F2B705" else "#FFFFFF"
    n = len(item["frase"])
    tam = 92 if n < 40 else 80 if n < 70 else 68
    blocos = BLOCOS.format(t=90, a=fg, b="#0F2240" if bg == "#F2B705" else "#F2B705")
    html = HTML.format(bg=bg, fg=fg, dest=dest if bg != "#F2B705" else "#1E4FA0", tam=tam,
                       frase=item["frase"], autor=item["autor"], blocos=blocos,
                       gobg="#0F2240" if bg == "#F2B705" else "#F2B705", gofg="#F2B705" if bg == "#F2B705" else "#0F2240")
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_suffix(".html"); tmp.write_text(html, encoding="utf-8")
    with sync_playwright() as p:
        nav = p.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None)
        pg = nav.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto(tmp.resolve().as_uri(), wait_until="networkidle"); pg.evaluate("document.fonts.ready")
        pg.screenshot(path=str(destino), type="jpeg", quality=92); nav.close()
    tmp.unlink()
    return destino


def do_dia(turno: int) -> tuple[dict, int]:
    """turno 0 = manhã, 1 = tarde. Percorre a lista em ordem, 2 por dia, sem repetir até acabar."""
    frases = json.loads(LISTA.read_text(encoding="utf-8"))
    hoje = datetime.now(timezone(timedelta(hours=-3))).date()
    i = (hoje.toordinal() * 2 + turno) % len(frases)
    return frases[i], i


if __name__ == "__main__":  # python -m robo.frases <turno>  → gera e publica o story
    turno = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    item, i = do_dia(turno)
    hoje = datetime.now(timezone(timedelta(hours=-3))).strftime("%Y-%m-%d")
    destino = Path(f"posts/stories/{hoje}-{turno}.jpg")
    gerar(item, destino, seed=i)
    print(f"arquivo={destino}")
    with open(os.environ.get("GITHUB_OUTPUT", os.devnull), "a") as f:
        f.write(f"arquivo={destino}\n")
