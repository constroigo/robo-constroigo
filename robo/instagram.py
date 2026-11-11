"""Publicação pela API do Instagram.

Funciona com os dois tipos de chave:
- "Login unificado" (apps novos da Meta): chave começa com EAA, não vence e usa
  graph.facebook.com. Exige IG_USER_ID.
- "Login do Instagram" (apps antigos): usa graph.instagram.com e vence em 60 dias.
"""

import os
import time

import requests

def _api(token: str) -> str:
    return "https://graph.facebook.com" if token.startswith("EAA") else "https://graph.instagram.com"


def publicar_imagem(url_imagem: str, legenda: str) -> str:
    token = os.environ["IG_ACCESS_TOKEN"].strip()
    API = _api(token)
    usuario = (os.environ.get("IG_USER_ID") or "").strip() or "me"

    r = requests.post(
        f"{API}/{usuario}/media",
        data={"image_url": url_imagem, "caption": legenda, "access_token": token},
        timeout=60,
    )
    if not r.ok:
        raise RuntimeError(f"Erro ao criar a mídia: {r.status_code} {r.text}")
    container = r.json()["id"]

    # Espera o Instagram terminar de baixar e processar a imagem.
    for _ in range(20):
        s = requests.get(
            f"{API}/{container}",
            params={"fields": "status_code", "access_token": token},
            timeout=30,
        ).json()
        if s.get("status_code") == "FINISHED":
            break
        if s.get("status_code") == "ERROR":
            raise RuntimeError(f"O Instagram recusou a imagem: {s}")
        time.sleep(5)

    r = requests.post(
        f"{API}/{usuario}/media_publish",
        data={"creation_id": container, "access_token": token},
        timeout=60,
    )
    if not r.ok:
        raise RuntimeError(f"Erro ao publicar: {r.status_code} {r.text}")
    media_id = r.json()["id"]

    link = requests.get(
        f"{API}/{media_id}",
        params={"fields": "permalink", "access_token": token},
        timeout=30,
    ).json()
    return link.get("permalink", media_id)


def renovar_token() -> str | None:
    """Renova o token de longa duração do login do Instagram (60 dias).

    Chaves do login unificado (EAA...) não vencem; nesse caso não faz nada.
    """
    token = os.environ["IG_ACCESS_TOKEN"].strip()
    if token.startswith("EAA"):
        return None
    r = requests.get(
        "https://graph.instagram.com/refresh_access_token",
        params={"grant_type": "ig_refresh_token", "access_token": os.environ["IG_ACCESS_TOKEN"]},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def publicar_video(url_video: str, legenda: str, capa_url: str | None = None) -> str:
    """Publica um Reel (vídeo vertical, até 90 s recomendado)."""
    token = os.environ["IG_ACCESS_TOKEN"].strip()
    API = _api(token)
    usuario = (os.environ.get("IG_USER_ID") or "").strip() or "me"
    dados = {"media_type": "REELS", "video_url": url_video, "caption": legenda,
             "share_to_feed": "true", "access_token": token}
    if capa_url:
        dados["cover_url"] = capa_url
    r = requests.post(f"{API}/{usuario}/media", data=dados, timeout=60)
    if not r.ok:
        raise RuntimeError(f"Erro ao criar o Reel: {r.status_code} {r.text}")
    container = r.json()["id"]
    for _ in range(60):  # vídeo demora mais para processar (até ~10 min)
        s = requests.get(f"{API}/{container}", params={"fields": "status_code,status", "access_token": token},
                         timeout=30).json()
        if s.get("status_code") == "FINISHED":
            break
        if s.get("status_code") == "ERROR":
            raise RuntimeError(f"O Instagram recusou o vídeo: {s}")
        time.sleep(10)
    r = requests.post(f"{API}/{usuario}/media_publish", data={"creation_id": container, "access_token": token},
                      timeout=60)
    if not r.ok:
        raise RuntimeError(f"Erro ao publicar o Reel: {r.status_code} {r.text}")
    media_id = r.json()["id"]
    link = requests.get(f"{API}/{media_id}", params={"fields": "permalink", "access_token": token}, timeout=30).json()
    return link.get("permalink", media_id)


def publicar_carrossel(urls: list[str], legenda: str) -> str:
    token = os.environ["IG_ACCESS_TOKEN"].strip()
    API = _api(token)
    usuario = (os.environ.get("IG_USER_ID") or "").strip() or "me"
    filhos = []
    for url in urls:
        r = requests.post(f"{API}/{usuario}/media",
                          data={"image_url": url, "is_carousel_item": "true", "access_token": token}, timeout=60)
        if not r.ok:
            raise RuntimeError(f"Erro ao criar item do carrossel: {r.status_code} {r.text}")
        filhos.append(r.json()["id"])
    for filho in filhos:
        for _ in range(20):
            s = requests.get(f"{API}/{filho}", params={"fields": "status_code", "access_token": token}, timeout=30).json()
            if s.get("status_code") in ("FINISHED", None):
                break
            if s.get("status_code") == "ERROR":
                raise RuntimeError(f"O Instagram recusou uma imagem do carrossel: {s}")
            time.sleep(5)
    r = requests.post(f"{API}/{usuario}/media", data={"media_type": "CAROUSEL", "children": ",".join(filhos),
                      "caption": legenda, "access_token": token}, timeout=60)
    if not r.ok:
        raise RuntimeError(f"Erro ao criar o carrossel: {r.status_code} {r.text}")
    container = r.json()["id"]
    for _ in range(20):
        s = requests.get(f"{API}/{container}", params={"fields": "status_code", "access_token": token}, timeout=30).json()
        if s.get("status_code") == "FINISHED":
            break
        time.sleep(5)
    r = requests.post(f"{API}/{usuario}/media_publish", data={"creation_id": container, "access_token": token}, timeout=60)
    if not r.ok:
        raise RuntimeError(f"Erro ao publicar o carrossel: {r.status_code} {r.text}")
    media_id = r.json()["id"]
    link = requests.get(f"{API}/{media_id}", params={"fields": "permalink", "access_token": token}, timeout=30).json()
    return link.get("permalink", media_id)
