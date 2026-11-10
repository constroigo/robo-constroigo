"""Imagem do post: primeiro uma foto real do Pexels (uso comercial liberado);
se não houver, uma ilustração gerada pelo Gemini, marcada como "Imagem ilustrativa".
"""

import base64
import json
import os
import random
from pathlib import Path

import requests

USADAS = Path("data/fotos_usadas.json")


def _usadas() -> list:
    return json.loads(USADAS.read_text(encoding="utf-8")) if USADAS.exists() else []


def _marcar(chave: str) -> None:
    lista = (_usadas() + [chave])[-500:]
    USADAS.parent.mkdir(parents=True, exist_ok=True)
    USADAS.write_text(json.dumps(lista), encoding="utf-8")


def pexels(busca: str, destino: Path) -> dict | None:
    chave = os.environ.get("PEXELS_API_KEY", "").strip()
    if not chave or not busca:
        return None
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": chave},
            params={"query": busca, "orientation": "landscape", "per_page": 15, "size": "large"},
            timeout=30,
        )
        r.raise_for_status()
        usadas = set(_usadas())
        fotos = [f for f in r.json().get("photos", []) if f"pexels:{f['id']}" not in usadas]
        if not fotos:
            return None
        foto = random.choice(fotos[:8])
        img = requests.get(foto["src"]["large2x"], timeout=60)
        img.raise_for_status()
        destino.write_bytes(img.content)
        _marcar(f"pexels:{foto['id']}")
        return {"arquivo": destino, "credito": f"Foto: {foto['photographer']} / Pexels", "origem": "pexels"}
    except requests.RequestException as erro:
        print("Pexels indisponível:", erro)
        return None


def pixabay(busca: str, destino: Path) -> dict | None:
    chave = os.environ.get("PIXABAY_API_KEY", "").strip()
    if not chave or not busca:
        return None
    try:
        r = requests.get(
            "https://pixabay.com/api/",
            params={"key": chave, "q": busca, "image_type": "photo", "orientation": "horizontal",
                    "safesearch": "true", "per_page": 20, "min_width": 1600},
            timeout=30,
        )
        r.raise_for_status()
        usadas = set(_usadas())
        fotos = [f for f in r.json().get("hits", []) if f"pixabay:{f['id']}" not in usadas]
        if not fotos:
            return None
        foto = random.choice(fotos[:8])
        img = requests.get(foto["largeImageURL"], timeout=60)
        img.raise_for_status()
        destino.write_bytes(img.content)
        _marcar(f"pixabay:{foto['id']}")
        return {"arquivo": destino, "credito": f"Foto: {foto['user']} / Pixabay", "origem": "pixabay"}
    except requests.RequestException as erro:
        print("Pixabay indisponível:", erro)
        return None


def _modelos_imagem(chave: str) -> list[str]:
    preferidos = [m for m in [os.environ.get("GEMINI_IMAGE_MODEL", "").strip()] if m]
    try:
        r = requests.get(
            "https://generativelanguage.googleapis.com/v1beta/models",
            headers={"x-goog-api-key": chave}, params={"pageSize": 200}, timeout=30,
        )
        for m in r.json().get("models", []):
            nome = m["name"].split("/")[-1]
            if "image" in nome and "generateContent" in m.get("supportedGenerationMethods", []):
                preferidos.append(nome)
    except (requests.RequestException, ValueError, KeyError):
        pass
    # Modelos "flash" primeiro (mais baratos), depois o resto.
    return sorted(dict.fromkeys(preferidos), key=lambda n: (0 if "flash" in n else 1, "preview" in n))


def gemini(descricao: str, destino: Path) -> dict | None:
    chave = os.environ.get("GEMINI_API_KEY", "").strip()
    if not chave or not descricao:
        return None
    prompt = (
        "Fotografia realista, horizontal, luz natural, alta qualidade, para ilustrar uma notícia do setor "
        f"de construção civil no Brasil: {descricao}. "
        "Sem nenhum texto, letras, números, placas legíveis, logotipos ou marcas. "
        "Pessoas, se aparecerem, de costas ou distantes, com EPI completo (capacete e colete)."
    )
    for modelo in _modelos_imagem(chave):
        try:
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent",
                headers={"x-goog-api-key": chave},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "16:9"}},
                },
                timeout=(15, 120),
            )
        except requests.RequestException as erro:
            print(f"Gemini imagem ({modelo}) sem resposta:", type(erro).__name__)
            continue
        if not r.ok:
            print(f"Gemini imagem ({modelo}):", r.status_code, r.text[:200])
            continue
        for parte in r.json().get("candidates", [{}])[0].get("content", {}).get("parts", []):
            dados = parte.get("inlineData") or parte.get("inline_data")
            if dados and dados.get("data"):
                destino.write_bytes(base64.b64decode(dados["data"]))
                print("Imagem gerada com", modelo)
                return {"arquivo": destino, "credito": "Imagem ilustrativa", "origem": "gemini"}
    return None


def obter(post: dict, pasta: Path) -> dict | None:
    pasta.mkdir(parents=True, exist_ok=True)
    busca = post.get("busca_foto", "")
    foto = pexels(busca, pasta / "foto.jpg") or pixabay(busca, pasta / "foto.jpg")
    # Ilustração do Gemini só se a variável USAR_GEMINI_IMAGEM = sim (exige faturamento da API).
    if not foto and os.environ.get("USAR_GEMINI_IMAGEM", "").lower() == "sim":
        foto = gemini(post.get("descricao_imagem", ""), pasta / "foto.png")
    return foto
