"""Busca notícias no Google Notícias (RSS) e remove as já publicadas."""

import calendar
import json
import re
import time
import unicodedata
from pathlib import Path
from urllib.parse import quote_plus

import feedparser

from .config import JANELA_HORAS

HISTORICO = Path("data/historico.json")


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]", "", texto).strip()


def carregar_historico() -> dict:
    if HISTORICO.exists():
        return json.loads(HISTORICO.read_text(encoding="utf-8"))
    return {"titulos": [], "links": []}


def salvar_no_historico(titulo: str, link: str) -> None:
    hist = carregar_historico()
    hist["titulos"] = (hist["titulos"] + [_normalizar(titulo)])[-600:]
    hist["links"] = (hist["links"] + [link])[-600:]
    HISTORICO.parent.mkdir(parents=True, exist_ok=True)
    HISTORICO.write_text(json.dumps(hist, ensure_ascii=False, indent=1), encoding="utf-8")


def _limpar_titulo(titulo: str, fonte: str) -> str:
    # O Google Notícias coloca " - Nome do Jornal" no fim do título.
    if fonte and titulo.endswith(" - " + fonte):
        return titulo[: -len(" - " + fonte)].strip()
    return re.sub(r"\s+-\s+[^-]+$", "", titulo).strip()


def _limpar_html(texto: str) -> str:
    return re.sub(r"<[^>]+>", " ", texto or "").replace("&nbsp;", " ").strip()


def buscar(buscas: list[str], limite: int = 25) -> list[dict]:
    hist = carregar_historico()
    vistos_titulos = set(hist["titulos"])
    vistos_links = set(hist["links"])
    agora = time.time()
    resultado, ja_na_lista = [], set()

    for busca in buscas:
        url = (
            "https://news.google.com/rss/search?q="
            + quote_plus(f"{busca} when:2d")
            + "&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        )
        feed = feedparser.parse(url)
        for e in feed.entries:
            fonte = getattr(getattr(e, "source", None), "title", "") or ""
            titulo = _limpar_titulo(e.get("title", ""), fonte)
            chave = _normalizar(titulo)
            if not titulo or chave in vistos_titulos or chave in ja_na_lista:
                continue
            if e.get("link") in vistos_links:
                continue
            publicado = e.get("published_parsed")
            if publicado:
                idade_h = (agora - calendar.timegm(publicado)) / 3600
                if idade_h > JANELA_HORAS:
                    continue
            ja_na_lista.add(chave)
            resultado.append(
                {
                    "titulo": titulo,
                    "fonte": fonte,
                    "link": e.get("link", ""),
                    "data": e.get("published", ""),
                    "trecho": _limpar_html(e.get("summary", ""))[:400],
                    "busca": busca,
                }
            )
    return resultado[:limite]
