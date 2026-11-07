"""Prepara o post de um horário: busca a notícia, escreve o texto e gera a arte.

Uso: python -m robo.preparar manha|meiodia|tarde
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from . import noticias, redacao
from .arte import gerar_arte
from .config import HORARIOS, PATROCINADORES

FUSO = ZoneInfo("America/Sao_Paulo")


def escolher_patrocinador(quando: datetime, horario: str) -> dict | None:
    if not PATROCINADORES:
        return None
    ordem = list(HORARIOS).index(horario)
    indice = (quando.timetuple().tm_yday * len(HORARIOS) + ordem) % len(PATROCINADORES)
    return PATROCINADORES[indice]


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

    lista = noticias.buscar(conf["buscas"])
    print(f"{len(lista)} notícias novas encontradas.")
    if not lista:
        saida("pasta", "")
        return

    post = redacao.escrever_post(lista, conf["rotulo"])
    patrocinador = escolher_patrocinador(agora, horario)

    pasta = Path("posts") / f"{agora:%Y-%m-%d}-{horario}"
    gerar_arte(post, patrocinador, pasta / "post.jpg", agora)
    post["patrocinador"] = patrocinador["nome"] if patrocinador else ""
    post["horario"] = horario
    post["criado_em"] = agora.isoformat()
    (pasta / "post.json").write_text(json.dumps(post, ensure_ascii=False, indent=2), encoding="utf-8")

    noticias.salvar_no_historico(post["noticia"]["titulo"], post["noticia"]["link"])
    print("Notícia escolhida:", post["noticia"]["titulo"])
    saida("pasta", pasta.as_posix())


if __name__ == "__main__":
    main()
