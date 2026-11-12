"""Prepara o post de um horário: busca a notícia, escreve o texto e gera a arte.

Uso: python -m robo.preparar manha|meiodia|tarde
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from . import imagens, noticias, redacao
from .arte import gerar_arte
from .config import FONTES_PREFERIDAS, HORARIOS, PATROCINADOR_POR_CATEGORIA, PATROCINADORES

FUSO = ZoneInfo("America/Sao_Paulo")


def escolher_patrocinador(quando: datetime, horario: str, categoria: str = "") -> dict | None:
    if not PATROCINADORES:
        return None
    preferido = PATROCINADOR_POR_CATEGORIA.get(categoria.upper())
    for p in PATROCINADORES:
        if p["nome"] == preferido:
            return p
    rodizio = [p for p in PATROCINADORES if p.get("rodizio", True)]
    ordem = list(HORARIOS).index(horario) if horario in HORARIOS else 0
    indice = (quando.timetuple().tm_yday * len(HORARIOS) + ordem) % len(rodizio)
    return rodizio[indice]


def saida(nome: str, valor: str) -> None:
    arq = os.environ.get("GITHUB_OUTPUT")
    if arq:
        with open(arq, "a", encoding="utf-8") as f:
            f.write(f"{nome}={valor}\n")
    print(f"{nome}={valor}")


def main() -> None:
    horario = sys.argv[1] if len(sys.argv) > 1 else "manha"
    if horario not in HORARIOS:
        sys.exit(f"Horário desconhecido: {horario}. Use: {', '.join(HORARIOS)}")
    conf = HORARIOS[horario]
    agora = datetime.now(FUSO)

    # O agendamento roda duas vezes por horário (o GitHub às vezes atrasa ou pula).
    # Na segunda vez, se o post do horário já foi feito hoje, não faz de novo.
    if os.environ.get("AGENDADO") == "sim" and list(Path("posts").glob(f"{agora:%Y-%m-%d}-{horario}-*")):
        print("Post deste horário já foi preparado hoje.")
        saida("pasta", "")
        return

    extras = [f["busca"] for f in FONTES_PREFERIDAS]
    lista = noticias.buscar(conf["buscas"] + extras, limite=40)
    print(f"{len(lista)} notícias novas encontradas.")
    if not lista:
        saida("pasta", "")
        return

    post = redacao.escrever_post(lista, conf["rotulo"])
    patrocinador = escolher_patrocinador(agora, horario, post.get("categoria", ""))

    # Pasta única por execução, para dois posts do mesmo horário não se sobrescreverem.
    pasta = Path("posts") / f"{agora:%Y-%m-%d}-{horario}-{agora:%H%M%S}"
    imagem = imagens.obter(post, pasta) if os.environ.get("USAR_IMAGENS", "sim").lower() != "nao" else None
    gerar_arte(post, patrocinador, pasta / "post.jpg", agora, imagem=imagem)
    if imagem:
        post["imagem"] = {"origem": imagem["origem"], "credito": imagem["credito"]}
        Path(imagem["arquivo"]).unlink(missing_ok=True)  # só a arte final fica no repositório
        print("Imagem:", imagem["credito"])
    post["patrocinador"] = patrocinador["nome"] if patrocinador else ""
    post["horario"] = horario
    post["criado_em"] = agora.isoformat()
    (pasta / "post.json").write_text(json.dumps(post, ensure_ascii=False, indent=2), encoding="utf-8")

    noticias.salvar_no_historico(post["noticia"]["titulo"], post["noticia"]["link"])
    print("Notícia escolhida:", post["noticia"]["titulo"])
    saida("pasta", pasta.as_posix())


if __name__ == "__main__":
    main()
