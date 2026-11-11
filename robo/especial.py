"""Post especial (fora das notícias): novidades da página, sugestões do Higor etc.

Uso: python -m robo.especial especiais/arquivo.json
O JSON tem: tag, chamada, titulo, mostrar_marca, texto, itens, fonte, legenda e,
opcionalmente, patrocinador (nome), tema (marinho|claro|amarelo|azul) e layout
(classico|caixa|barra).
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .arte import _logo, proximo_estilo, renderizar
from .config import PATROCINADORES
from .preparar import escolher_patrocinador, saida

FUSO = ZoneInfo("America/Sao_Paulo")


def main() -> None:
    dados = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    agora = datetime.now(FUSO)
    pasta = Path("posts") / f"{agora:%Y-%m-%d}-especial-{agora:%H%M%S}"

    nome = dados.get("patrocinador")
    patrocinador = next((p for p in PATROCINADORES if p["nome"] == nome), None) if nome else None
    patrocinador = patrocinador or escolher_patrocinador(agora, "especial", dados.get("tag", ""))
    estilo = proximo_estilo(dados.get("layout"), dados.get("tema"))

    contexto = {k: dados.get(k) for k in ("tag", "chamada", "titulo", "mostrar_marca", "texto", "itens", "local")}
    contexto["fonte"] = dados.get("fonte") or dados.get("sub")
    contexto["patrocinador"] = _logo(patrocinador)
    if dados.get("imagem"):
        # Post com foto/imagem enviada (ex.: imagem oficial de divulgação), no layout com foto.
        contexto.update({
            "destaque": dados.get("destaque", ""), "manchete": dados.get("titulo", ""),
            "resumo": dados.get("texto", ""), "tam_destaque": 200, "tam_manchete": 76,
            "imagem": {"uri": Path(dados["imagem"]).resolve().as_uri(), "credito": dados.get("credito_imagem", ""),
                       "clara": bool(dados.get("imagem_clara"))},
        })
        renderizar("noticia_foto.html", contexto, estilo, pasta / "post.jpg")
    else:
        renderizar("especial.html", contexto, estilo, pasta / "post.jpg")

    post = {
        "categoria": dados.get("tag", "ESPECIAL"),
        "manchete": dados.get("titulo") or dados.get("chamada") or "Post especial",
        "legenda_final": dados["legenda"],
        "horario": "especial",
        "alertas": [],
        "patrocinador": patrocinador["nome"] if patrocinador else "",
        "estilo": f"{estilo['nome_tema']}/{estilo['layout']}",
        "noticia": {"titulo": "Post especial (sem notícia de origem)", "link": "", "fonte": "Constrói GO"},
        "criado_em": agora.isoformat(),
    }
    (pasta / "post.json").write_text(json.dumps(post, ensure_ascii=False, indent=2), encoding="utf-8")
    saida("pasta", pasta.as_posix())


if __name__ == "__main__":
    main()
