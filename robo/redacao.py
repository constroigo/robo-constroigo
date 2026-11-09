"""Escolhe a melhor notícia e escreve o post usando a API do Gemini."""

import json
import os

import requests

from .config import AUTOR, HASHTAGS_FIXAS

MODELO = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

INSTRUCOES = """Você é o editor do perfil de Instagram "Constrói GO", assinado por {autor},
engenheiro civil em Goiânia. O público são engenheiros, construtoras, fornecedores e
investidores da construção civil em Goiás.

Tarefa: das notícias abaixo, escolha UMA — a mais relevante para esse público
(prefira Goiás/Goiânia; depois Centro-Oeste; depois Brasil). Tema deste horário: {tema}.

Regras obrigatórias:
- Use SOMENTE as informações do título e do trecho da notícia escolhida. Não invente
  números, datas, nomes ou declarações. Se não tiver certeza, deixe de fora.
- Escreva com suas palavras (não copie frases da notícia).
- "destaque": um número curto que aparece no título/trecho (ex.: "R$ 948 mi", "11 mil",
  "+0,35%"). Se não houver número claro, deixe "".
- "manchete": até 90 caracteres, direta, sem ponto final. Se houver destaque, a manchete
  continua a frase depois do número (ex.: destaque "R$ 4,1 bi" + manchete "em imóveis
  vendidos em Goiânia no 1º semestre").
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


def escrever_post(noticias: list[dict], tema: str) -> dict:
    chave = os.environ["GEMINI_API_KEY"]
    lista = "\n".join(
        f"[{i}] {n['titulo']} — {n['fonte']} ({n['data']})\n    Trecho: {n['trecho']}"
        for i, n in enumerate(noticias)
    )
    prompt = INSTRUCOES.format(autor=AUTOR, tema=tema, lista=lista)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent"
    resp = requests.post(
        url,
        headers={"x-goog-api-key": chave},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.4},
        },
        timeout=90,
    )
    resp.raise_for_status()
    texto = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    post = json.loads(texto)

    noticia = noticias[int(post["escolhida"])]
    post["noticia"] = noticia
    post["manchete"] = post["manchete"].strip().rstrip(".")[:110]
    post["resumo"] = post["resumo"].strip()[:180]

    tags = [t if t.startswith("#") else "#" + t for t in post.get("hashtags", [])]
    todas = list(dict.fromkeys(tags + HASHTAGS_FIXAS))[:10]
    post["legenda_final"] = (
        f"{post['legenda'].strip()}\n\n"
        f"✍️ Por {AUTOR}\n"
        f"📰 Fonte: {noticia['fonte'] or 'imprensa'}\n\n"
        + " ".join(todas)
    )
    return post
