"""Escolhe a melhor notícia e escreve o post usando a API do Gemini."""

import json
import os
import re
import time

import requests

from .config import AUTOR, HASHTAGS_FIXAS

# Modelos tentados em ordem (a variável GEMINI_MODEL, se existir, vem primeiro).
MODELOS = [m for m in [os.environ.get("GEMINI_MODEL", "").strip(), "gemini-3.8-flash", "gemini-flash-latest", "gemini-flash-lite-latest"] if m]

INSTRUCOES = """Você é o editor do perfil de Instagram "Constrói GO", assinado por {autor},
engenheiro civil em Goiânia. O público são engenheiros, construtoras, fornecedores e
investidores da construção civil em Goiás.

Tarefa: das notícias abaixo, escolha UMA — a mais relevante para esse público
(prefira Goiás/Goiânia; depois Centro-Oeste; depois Brasil). Tema deste horário: {tema}.

Regras obrigatórias:
- Use SOMENTE as informações do título e do trecho da notícia escolhida. Não invente
  números, datas, nomes ou declarações. É PROIBIDO citar órgãos, empresas, leilões,
  programas, cidades ou causas que não estejam escritos no título/trecho. Se a notícia
  tiver pouca informação, a legenda fica curta e comenta o impacto para o setor de forma
  geral, sem acrescentar fatos novos.
- Escreva com suas palavras (não copie frases da notícia).
- "destaque": um número curto que aparece no título/trecho (ex.: "R$ 948 mi", "11 mil",
  "+0,35%"). Se não houver número claro, deixe "".
- "manchete": até 90 caracteres, direta, sem ponto final. Se houver destaque, a manchete
  continua a frase depois do número (ex.: destaque "R$ 4,1 bi" + manchete "em imóveis
  vendidos em Goiânia no 1º semestre"). A manchete NUNCA repete o número do destaque.
- "resumo": 1 frase de até 150 caracteres para a arte.
- "legenda": 3 a 5 frases curtas para o Instagram, em tom profissional e próximo,
  explicando o fato e por que importa para quem constrói em Goiás. Termine com uma
  pergunta para gerar comentários. Não use emojis em excesso (no máximo 2).
- "categoria": uma destas: MERCADO IMOBILIÁRIO, INFRAESTRUTURA, ENERGIA, OBRAS,
  MÁQUINAS E EQUIPAMENTOS, TECNOLOGIA, MERCADO DE TRABALHO, ECONOMIA, SANEAMENTO.
- "local": cidade/estado da notícia em maiúsculas (ex.: "GOIÂNIA", "GOIÁS", "BRASIL").
- "hashtags": até 5 hashtags específicas do assunto, sem acento.

Responda só com JSON no formato:
{{"escolhida": <número da notícia>, "categoria": "", "local": "", "destaque": "",
"manchete": "", "resumo": "", "legenda": "", "hashtags": []}}

Notícias:
{lista}
"""


REVISAO = """Você é revisor de fatos. Fonte (única verdade):
TÍTULO: {titulo}
TRECHO: {trecho}

Post escrito a partir dela:
{post}

Corrija o post: remova ou reescreva QUALQUER afirmação, número, nome, órgão, empresa,
leilão, programa, local ou causa que NÃO esteja escrito na fonte. Comentários gerais de
impacto para o setor (sem fatos novos) podem ficar. Se "destaque" não aparecer na fonte,
deixe "". A "manchete" não pode repetir o número do "destaque". Mantenha o mesmo formato
JSON e as mesmas chaves, e responda só com o JSON corrigido."""


def _chamar(prompt: str, chave: str) -> str | None:
    for modelo in MODELOS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
        try:
            resp = requests.post(
                url,
                headers={"x-goog-api-key": chave},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"responseMimeType": "application/json", "temperature": 0.1},
                },
                timeout=(15, 75),
            )
        except requests.RequestException:
            continue
        if resp.ok:
            return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    return None


def _numeros(texto: str) -> set[str]:
    return set(re.findall(r"\d+(?:[.,]\d+)*", texto or ""))


def _revisar(post: dict, noticia: dict, chave: str) -> dict:
    campos = {k: post.get(k) for k in ("categoria", "local", "destaque", "manchete", "resumo", "legenda", "hashtags")}
    texto = _chamar(
        REVISAO.format(
            titulo=noticia["titulo"], trecho=noticia["trecho"],
            post=json.dumps(campos, ensure_ascii=False),
        ),
        chave,
    )
    if texto:
        try:
            corrigido = json.loads(texto)
            for k in campos:
                if corrigido.get(k) is not None:
                    post[k] = corrigido[k]
            print("Revisão de fatos aplicada.")
        except (ValueError, AttributeError):
            print("Revisão de fatos ignorada (resposta inválida).")

    # Checagem automática: todo número do post precisa existir na fonte.
    fonte = _numeros(noticia["titulo"] + " " + noticia["trecho"])
    if post.get("destaque") and not _numeros(post["destaque"]) <= fonte:
        post["destaque"] = ""
    suspeitos = sorted(
        n for k in ("manchete", "resumo", "legenda") for n in _numeros(post.get(k, "")) if n not in fonte
    )
    post["alertas"] = [f"Número não encontrado na notícia: {n}" for n in suspeitos]
    return post


def escrever_post(noticias: list[dict], tema: str) -> dict:
    chave = os.environ["GEMINI_API_KEY"]
    lista = "\n".join(
        f"[{i}] {n['titulo']} — {n['fonte']} ({n['data']})\n    Trecho: {n['trecho']}"
        for i, n in enumerate(noticias)
    )
    prompt = INSTRUCOES.format(autor=AUTOR, tema=tema, lista=lista)
    texto, erros = None, []
    tentativas = [(m, t) for t in range(2) for m in MODELOS]
    for modelo, rodada in tentativas:
        if rodada:
            time.sleep(20)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
        try:
            resp = requests.post(
                url,
                headers={"x-goog-api-key": chave},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"responseMimeType": "application/json", "temperature": 0.4},
                },
                timeout=(15, 75),
            )
        except requests.RequestException as erro:
            erros.append(f"{modelo}: sem resposta ({type(erro).__name__})")
            continue
        if resp.ok:
            texto = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            print("Modelo usado:", modelo)
            break
        erros.append(f"{modelo}: {resp.status_code} {resp.text[:300]}")
    if texto is None:
        raise RuntimeError("O Gemini não respondeu:\n" + "\n".join(erros))
    post = json.loads(texto)

    noticia = noticias[int(post["escolhida"])]
    post = _revisar(post, noticia, chave)
    post["noticia"] = noticia
    post["manchete"] = post["manchete"].strip().rstrip(".")[:110]
    post["resumo"] = post["resumo"].strip()[:180]

    tags = [t if t.startswith("#") else "#" + t for t in post.get("hashtags", [])]
    vistas, todas = set(), []
    for t in tags + HASHTAGS_FIXAS:
        if t.lower() not in vistas:
            vistas.add(t.lower())
            todas.append(t)
    todas = todas[:10]
    post["legenda_final"] = (
        f"{post['legenda'].strip()}\n\n"
        f"✍️ Por {AUTOR}\n"
        f"📰 Fonte: {noticia['fonte'] or 'imprensa'}\n\n"
        + " ".join(todas)
    )
    return post
