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

    cards = dados.get("cards") or [dados]
    for i, card in enumerate(cards, start=1):
        base = {**dados, **card}
        contexto = {k: base.get(k) for k in ("tag", "chamada", "titulo", "mostrar_marca", "texto", "itens", "local")}
        contexto["fonte"] = base.get("fonte") or base.get("sub")
        contexto["patrocinador"] = _logo(patrocinador)
        destino = pasta / ("post.jpg" if len(cards) == 1 else f"post-{i}.jpg")
        if base.get("busca_foto") and not base.get("imagem"):
            from .imagens import pixabay
            pasta.mkdir(parents=True, exist_ok=True)
            foto = pixabay(base["busca_foto"], pasta / f"foto-{i}.jpg", base.get("titulo", ""), base.get("categoria_foto", ""))
            if foto:
                base["imagem"], base["credito_imagem"] = str(foto["arquivo"]), foto["credito"]
                print(f"card {i}: {foto['credito']}")
        if base.get("imagem"):
            contexto.update({
                "destaque": base.get("destaque", ""), "manchete": base.get("titulo", ""),
                "resumo": base.get("texto", ""), "tam_destaque": 200, "tam_manchete": base.get("tam_titulo", 76),
                "imagem": {"uri": Path(base["imagem"]).resolve().as_uri(), "credito": base.get("credito_imagem", ""),
                           "clara": bool(base.get("imagem_clara")), "posicao": base.get("posicao_imagem", "")},
            })
            renderizar("noticia_foto.html", contexto, estilo, destino)
        else:
            renderizar("especial.html", contexto, estilo, destino)
    if len(cards) > 1:
        import shutil
        shutil.copy(pasta / "post-1.jpg", pasta / "post.jpg")  # capa, para a prévia

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
