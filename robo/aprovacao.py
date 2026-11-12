"""Abre o pedido de aprovação (issue) ou publica direto, conforme AUTO_PUBLICAR.

Uso: python -m robo.aprovacao posts/2026-11-08-manha
"""

import json
import os
import re
import sys
from pathlib import Path

from . import github, instagram


def url_publica(pasta: str, arquivo: str = "post.jpg") -> str:
    return f"https://raw.githubusercontent.com/{github.repo()}/main/{pasta}/{arquivo}"


def _cards(pasta: str) -> list[str]:
    return sorted((p.name for p in Path(pasta).glob("post-*.jpg")), key=lambda n: int(n[5:-4]))


def _publicar(pasta: str, post: dict) -> str:
    cards = _cards(pasta)
    if len(cards) > 1:
        return instagram.publicar_carrossel([url_publica(pasta, c) for c in cards], post["legenda_final"], post.get("colaboradores"))
    if (Path(pasta) / "video.mp4").exists():
        capa = url_publica(pasta) if (Path(pasta) / "post.jpg").exists() else None
        return instagram.publicar_video(url_publica(pasta, "video.mp4"), post["legenda_final"], capa)
    return instagram.publicar_imagem(url_publica(pasta), post["legenda_final"])


def abrir(pasta: str) -> None:
    post = json.loads((Path(pasta) / "post.json").read_text(encoding="utf-8"))
    url = url_publica(pasta)

    if os.environ.get("AUTO_PUBLICAR", "").lower() == "sim":
        link = _publicar(pasta, post)
        print("Publicado automaticamente:", link)
        return

    horario = {"manha": "Manhã", "meiodia": "Meio-dia", "tarde": "Fim da tarde", "especial": "Especial"}.get(post["horario"], "")
    alertas = "".join(f"> ⚠️ {a}\n" for a in post.get("alertas", []))
    if alertas:
        alertas = "**Confira antes de aprovar:**\n" + alertas + "\n"
    if post.get("categoria", "").upper() in ("MÁQUINAS E EQUIPAMENTOS", "TECNOLOGIA"):
        alertas += "🎥 **Boa pauta para vídeo comentado:** se quiser gravar, me manda o vídeo que eu publico como Reel.\n\n"
    tem_video = (Path(pasta) / "video.mp4").exists()
    previa = (f"🎬 **Reel:** [assistir o vídeo]({url_publica(pasta, 'video.mp4')})\n\n" if tem_video else "")
    corpo = (
        alertas
        + previa
        + ("".join(f"![card]({url_publica(pasta, c)})\n" for c in _cards(pasta)) + "\n" if _cards(pasta)
           else (f"![arte]({url})\n\n" if (Path(pasta) / "post.jpg").exists() else ""))
        + f"**Legenda:**\n\n```\n{post['legenda_final']}\n```\n\n"
        f"**Notícia original:** [{post['noticia']['titulo']}]({post['noticia']['link']}) — "
        f"{post['noticia']['fonte']}\n\n"
        "---\n"
        "👉 Para **publicar**, responda **ok**.\n"
        "👉 Para **descartar**, responda **não**.\n\n"
        f"<!-- pasta: {pasta} -->"
    )
    numero = github.criar_issue(
        f"[{horario}] {post['categoria'].title()}: {post['manchete'][:70]}",
        corpo,
        ["aprovacao"],
    )
    print("Pedido de aprovação aberto: #", numero)


APROVAR = re.compile(r"^\s*(ok|aprovar|aprovado|publicar|sim)\b", re.I)
REJEITAR = re.compile(r"^\s*(n[aã]o|rejeitar|descartar|cancelar)\b", re.I)


def responder() -> None:
    """Chamado quando alguém comenta numa issue de aprovação."""
    comentario = os.environ.get("COMENTARIO", "")
    numero = int(os.environ["ISSUE_NUMBER"])
    corpo = os.environ.get("ISSUE_BODY", "")
    achou = re.search(r"<!-- pasta: (\S+) -->", corpo)
    if not achou:
        print("Issue sem pasta de post; nada a fazer.")
        return
    pasta = achou.group(1)

    if REJEITAR.match(comentario):
        github.comentar(numero, "Post descartado. 👍")
        github.fechar(numero, "not_planned")
        return
    if not APROVAR.match(comentario):
        print("Comentário não é aprovação nem rejeição; ignorando.")
        return

    post = json.loads((Path(pasta) / "post.json").read_text(encoding="utf-8"))
    try:
        link = _publicar(pasta, post)
    except Exception as erro:  # noqa: BLE001
        github.comentar(numero, f"⚠️ Não consegui publicar:\n\n```\n{erro}\n```")
        raise
    github.comentar(numero, f"✅ Publicado no Instagram: {link}")
    github.fechar(numero)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--responder":
        responder()
    elif len(sys.argv) > 1 and sys.argv[1]:
        abrir(sys.argv[1])
    else:
        print("Nenhum post novo para aprovar.")
