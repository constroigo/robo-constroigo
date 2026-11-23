"""Abre o pedido de aprovação (issue) ou publica direto, conforme AUTO_PUBLICAR.

Uso: python -m robo.aprovacao posts/2026-11-08-manha
"""

import json
import os
import re
import sys
from pathlib import Path

from . import github, instagram


def modo_manual() -> bool:
    """Com o arquivo data/modo-manual o robô só prepara o conteúdo; quem publica é o Higor."""
    return Path("data/modo-manual").exists() or os.environ.get("MODO_MANUAL", "").lower() == "sim"


def url_publica(pasta: str, arquivo: str = "post.jpg") -> str:
    return f"https://raw.githubusercontent.com/{github.repo()}/main/{pasta}/{arquivo}"


def _cards(pasta: str) -> list[str]:
    return sorted((p.name for p in Path(pasta).glob("post-*.jpg")), key=lambda n: int(n[5:-4]))


def _publicar(pasta: str, post: dict) -> str:
    link = _publicar_feed(pasta, post)
    if os.environ.get("STORIES_AUTO", "sim").lower() != "nao" and (Path(pasta) / "story.jpg").exists():
        try:
            instagram.publicar_story(url_publica(pasta, "story.jpg"))
            print("Story publicado.")
        except Exception as erro:  # o post já saiu; o story é extra
            print(f"Story não publicado: {erro}")
    return link


def _publicar_feed(pasta: str, post: dict) -> str:
    cards = _cards(pasta)
    if (Path(pasta) / "video.mp4").exists():  # Reel tem prioridade (inclusive carrossel convertido em vídeo)
        capa = url_publica(pasta) if (Path(pasta) / "post.jpg").exists() else None
        return instagram.publicar_video(url_publica(pasta, "video.mp4"), post["legenda_final"], capa,
                                        post.get("colaboradores"))
    if len(cards) > 1:
        return instagram.publicar_carrossel([url_publica(pasta, c) for c in cards], post["legenda_final"], post.get("colaboradores"))
    return instagram.publicar_imagem(url_publica(pasta), post["legenda_final"])


def abrir(pasta: str) -> None:
    post = json.loads((Path(pasta) / "post.json").read_text(encoding="utf-8"))
    url = url_publica(pasta)

    if modo_manual():
        _abrir_manual(pasta, post)
        return

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


def _abrir_manual(pasta: str, post: dict) -> None:
    horario = {"manha": "Manhã", "meiodia": "Meio-dia", "tarde": "Fim da tarde", "especial": "Especial"}.get(post["horario"], "")
    pasta_p = Path(pasta)
    cards = _cards(pasta)
    tem_video = (pasta_p / "video.mp4").exists()
    alertas = "".join(f"> ⚠️ {a}\n" for a in post.get("alertas", []))
    if alertas:
        alertas = "**Confira antes de postar:**\n" + alertas + "\n"

    passos, n = [], 1
    if tem_video:
        tipo = "Reel"
        passos.append(f"{n}. 🎬 **Baixe o vídeo:** [video.mp4]({url_publica(pasta, 'video.mp4')}) (abra e toque em compartilhar → salvar vídeo)")
    elif len(cards) > 1:
        tipo = f"Carrossel ({len(cards)} imagens)"
        links = " · ".join(f"[{i}]({url_publica(pasta, c)})" for i, c in enumerate(cards, 1))
        passos.append(f"{n}. 🖼️ **Baixe as imagens na ordem:** {links}")
    else:
        tipo = "Imagem"
        passos.append(f"{n}. 🖼️ **Baixe a imagem:** [post.jpg]({url_publica(pasta)})")
    n += 1
    passos.append(f"{n}. 📋 **Copie a legenda** (bloco abaixo) e poste no app do Instagram como **{tipo}**.")
    n += 1
    if post.get("colaboradores"):
        passos.append(f"{n}. 🤝 Em *Marcar pessoas → Convidar colaborador*, adicione: "
                      + ", ".join("@" + c.lstrip("@") for c in post["colaboradores"]))
        n += 1
    if (pasta_p / "story.jpg").exists():
        passos.append(f"{n}. 📲 **Story de divulgação:** [story.jpg]({url_publica(pasta, 'story.jpg')}) "
                      "(poste depois do feed e coloque o adesivo de link/menção do post)")
        n += 1

    previa = ("".join(f"![card]({url_publica(pasta, c)})\n" for c in cards) + "\n" if cards
              else (f"![arte]({url_publica(pasta)})\n\n" if (pasta_p / "post.jpg").exists() else ""))
    noticia = post.get("noticia") or {}
    fonte = (f"**Notícia original:** [{noticia.get('titulo', '')}]({noticia.get('link', '')}) — {noticia.get('fonte', '')}\n\n"
             if noticia.get("link") else "")
    corpo = (
        "📱 **Modo manual** — o robô preparou tudo, é só postar pelo app.\n\n"
        + alertas
        + "\n".join(passos) + "\n\n"
        + previa
        + f"**Legenda:**\n\n```\n{post['legenda_final']}\n```\n\n"
        + fonte
        + "---\n"
        "👉 Depois de postar, responda **postado** (ou **ok**) para fechar.\n"
        "👉 Para **descartar**, responda **não**.\n\n"
        f"<!-- pasta: {pasta} -->"
    )
    numero = github.criar_issue(
        f"📱 [{horario}] {post['categoria'].title()}: {post['manchete'][:65]}",
        corpo,
        ["aprovacao"],
    )
    print("Pacote para postagem manual aberto: #", numero)


def abrir_story_frase(arquivo: str) -> None:
    pasta, nome = os.path.split(arquivo)
    url = url_publica(pasta, nome)
    corpo = (
        "📱 **Story de frase do dia** — baixe a imagem e poste nos Stories.\n\n"
        f"1. 🖼️ **Baixe:** [{nome}]({url})\n"
        "2. Poste nos Stories e, se quiser, adicione o adesivo de **@constroigo** ou uma enquete.\n\n"
        f"![story]({url})\n\n"
        "---\n👉 Depois de postar, responda **postado** para fechar.\n\n"
        f"<!-- story: {arquivo} -->"
    )
    numero = github.criar_issue(f"📲 Story de frase — {nome[:-4]}", corpo, ["story"])
    print("Story de frase aberto: #", numero)


POSTADO = re.compile(r"^\s*(postado|postei|feito|publicado)\b", re.I)
APROVAR = re.compile(r"^\s*(ok|aprovar|aprovado|publicar|sim)\b", re.I)
REJEITAR = re.compile(r"^\s*(n[aã]o|rejeitar|descartar|cancelar)\b", re.I)


def responder() -> None:
    """Chamado quando alguém comenta numa issue de aprovação."""
    comentario = os.environ.get("COMENTARIO", "")
    numero = int(os.environ["ISSUE_NUMBER"])
    corpo = os.environ.get("ISSUE_BODY", "")
    if "<!-- story:" in corpo:
        if POSTADO.match(comentario) or APROVAR.match(comentario):
            github.comentar(numero, "Story postado. ✅")
            github.fechar(numero)
        elif REJEITAR.match(comentario):
            github.fechar(numero, "not_planned")
        return
    achou = re.search(r"<!-- pasta: (\S+) -->", corpo)
    if not achou:
        print("Issue sem pasta de post; nada a fazer.")
        return
    pasta = achou.group(1)

    if REJEITAR.match(comentario):
        github.comentar(numero, "Post descartado. 👍")
        github.fechar(numero, "not_planned")
        return
    if modo_manual():
        if POSTADO.match(comentario) or APROVAR.match(comentario):
            github.comentar(numero, "Marcado como postado. ✅")
            github.fechar(numero)
        else:
            print("Comentário não é 'postado' nem descarte; ignorando.")
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
    elif len(sys.argv) > 2 and sys.argv[1] == "--story":
        abrir_story_frase(sys.argv[2])
    elif len(sys.argv) > 1 and sys.argv[1]:
        abrir(sys.argv[1])
    else:
        print("Nenhum post novo para aprovar.")
