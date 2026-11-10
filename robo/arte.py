"""Gera a arte do post (JPG 1080x1350) a partir do modelo HTML."""

import os
import re
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup, escape
from playwright.sync_api import sync_playwright

from .config import AUTOR, FOTO_AUTOR
from .estilos import escolher

FOTO = Path(FOTO_AUTOR)

MESES = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]

_env = Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape(["html"]))


def _sem_quebra_no_hifen(texto: str) -> Markup:
    """Evita quebrar palavras como 'BR-153' no fim da linha."""
    seguro = str(escape(texto))
    return Markup(re.sub(r"(\S+-\S+)", r'<span style="white-space:nowrap">\1</span>', seguro))


def _tamanhos(destaque: str, manchete: str) -> tuple[int, int]:
    n = len(manchete)
    tam_manchete = 76 if n <= 50 else 66 if n <= 75 else 58
    if not destaque:
        tam_manchete += 14
    d = len(destaque)
    tam_destaque = 220 if d <= 6 else 180 if d <= 9 else 140
    return tam_destaque, tam_manchete


def proximo_estilo(layout: str | None = None, tema: str | None = None) -> dict:
    """Escolhe o estilo pela quantidade de posts já feitos: cada post sai diferente do anterior."""
    pasta = Path("posts")
    n = len([d for d in pasta.iterdir() if d.is_dir()]) if pasta.exists() else 0
    return escolher(n, layout, tema)


def _logo(patrocinador: dict | None) -> dict | None:
    if patrocinador and patrocinador.get("logo"):
        logo = Path(patrocinador["logo"]).resolve()
        return {**patrocinador, "logo_uri": logo.as_uri() if logo.exists() else ""}
    return patrocinador


def renderizar(template: str, contexto: dict, estilo: dict, destino: Path) -> Path:
    html = _env.get_template(template).render(
        e=estilo,
        autor=AUTOR,
        foto_uri=FOTO.resolve().as_uri() if FOTO.exists() else "",
        **contexto,
    )
    destino.parent.mkdir(parents=True, exist_ok=True)
    html_path = destino.with_suffix(".html")
    html_path.write_text(html, encoding="utf-8")
    with sync_playwright() as p:
        navegador = p.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None)
        pagina = navegador.new_page(viewport={"width": 1080, "height": 1350})
        pagina.goto(html_path.resolve().as_uri(), wait_until="networkidle")
        pagina.evaluate("document.fonts.ready")
        pagina.screenshot(path=str(destino), type="jpeg", quality=92, full_page=False)
        navegador.close()
    html_path.unlink()
    return destino


def gerar_arte(post: dict, patrocinador: dict | None, destino: Path, quando: datetime,
               estilo: dict | None = None) -> Path:
    estilo = estilo or proximo_estilo()
    tam_destaque, tam_manchete = _tamanhos(post.get("destaque", ""), post["manchete"])
    contexto = {
        "tag": post["categoria"],
        "local": f"{post.get('local') or 'GOIÁS'} · {quando.day:02d} {MESES[quando.month - 1]} {quando.year}",
        "destaque": post.get("destaque", ""),
        "manchete": _sem_quebra_no_hifen(post["manchete"]),
        "resumo": post["resumo"],
        "fonte": "Fonte: " + (post["noticia"]["fonte"] or "imprensa"),
        "patrocinador": _logo(patrocinador),
        "tam_destaque": tam_destaque,
        "tam_manchete": tam_manchete,
    }
    return renderizar("noticia.html", contexto, estilo, destino)
