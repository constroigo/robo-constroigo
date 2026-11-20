"""Story automático: a capa do post (ou do Reel) em 1080x1920, com chamada para o perfil."""
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

HTML = """<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1920px;background:#0F2240;font-family:Sora,sans-serif;color:#fff;
     display:flex;flex-direction:column;align-items:center;justify-content:center;gap:48px;overflow:hidden}
.selo{background:#F2B705;color:#0F2240;font-weight:800;font-size:44px;letter-spacing:4px;
      padding:18px 44px;border-radius:999px}
.card{width:920px;border-radius:28px;overflow:hidden;box-shadow:0 30px 80px rgba(0,0,0,.45)}
.card img{width:100%;display:block}
.cta{font-weight:700;font-size:46px;text-align:center;line-height:1.3}
.cta b{color:#F2B705}
</style></head><body>
<div class="selo">{selo}</div>
<div class="card"><img src="{img}"></div>
<div class="cta">Confira no perfil<br><b>@constroigo</b> 👆</div>
</body></html>"""


def gerar(capa: Path, destino: Path, video: bool = False) -> Path | None:
    try:
        html = HTML.replace("{img}", capa.resolve().as_uri()).replace("{selo}", "REEL NOVO" if video else "POST NOVO")
        tmp = destino.with_suffix(".html")
        tmp.write_text(html, encoding="utf-8")
        with sync_playwright() as p:
            nav = p.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None)
            pg = nav.new_page(viewport={"width": 1080, "height": 1920})
            pg.goto(tmp.resolve().as_uri(), wait_until="networkidle")
            pg.evaluate("document.fonts.ready")
            pg.screenshot(path=str(destino), type="jpeg", quality=90)
            nav.close()
        tmp.unlink()
        return destino
    except Exception as erro:  # story é extra: nunca impede o post
        print(f"Story não gerado ({erro}).")
        return None
