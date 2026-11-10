"""Post especial (fora das notícias): novidades da página, sugestões do Higor etc.

Uso: python -m robo.especial especiais/arquivo.json
O JSON tem: tag, chamada, titulo, mostrar_marca, texto, itens, sub, legenda.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from jinja2 import Environment, FileSystemLoader, select_autoescape
from playwright.sync_api import sync_playwright

from .arte import FOTO
from .config import AUTOR
from .preparar import saida

FUSO = ZoneInfo("America/Sao_Paulo")
_env = Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape(["html"]))


def main() -> None:
    origem = Path(sys.argv[1])
    dados = json.loads(origem.read_text(encoding="utf-8"))
    agora = datetime.now(FUSO)
    pasta = Path("posts") / f"{agora:%Y-%m-%d}-especial-{agora:%H%M%S}"
    pasta.mkdir(parents=True, exist_ok=True)

    html = _env.get_template("especial.html").render(
        autor=AUTOR,
        foto_uri=FOTO.resolve().as_uri() if FOTO.exists() else "",
        **{k: dados.get(k) for k in ("tag", "chamada", "titulo", "mostrar_marca", "texto", "itens", "sub")},
    )
    html_path = pasta / "post.html"
    html_path.write_text(html, encoding="utf-8")
    import os

    with sync_playwright() as p:
        nav = p.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None)
        pag = nav.new_page(viewport={"width": 1080, "height": 1350})
        pag.goto(html_path.resolve().as_uri(), wait_until="networkidle")
        pag.evaluate("document.fonts.ready")
        pag.screenshot(path=str(pasta / "post.jpg"), type="jpeg", quality=92)
        nav.close()
    html_path.unlink()

    post = {
        "categoria": dados.get("tag", "ESPECIAL"),
        "manchete": dados.get("titulo") or dados.get("chamada") or "Post especial",
        "legenda_final": dados["legenda"],
        "horario": "especial",
        "alertas": [],
        "noticia": {"titulo": "Post especial (sem notícia de origem)", "link": "", "fonte": "Constrói GO"},
        "criado_em": agora.isoformat(),
    }
    (pasta / "post.json").write_text(json.dumps(post, ensure_ascii=False, indent=2), encoding="utf-8")
    saida("pasta", pasta.as_posix())


if __name__ == "__main__":
    main()
