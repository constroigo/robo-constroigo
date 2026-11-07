"""Funções simples da API do GitHub (issues de aprovação e segredos)."""

import base64
import os

import requests

API = "https://api.github.com"


def _cab(token_env: str = "GITHUB_TOKEN") -> dict:
    return {
        "Authorization": f"Bearer {os.environ[token_env]}",
        "Accept": "application/vnd.github+json",
    }


def repo() -> str:
    return os.environ["GITHUB_REPOSITORY"]


def criar_issue(titulo: str, corpo: str, rotulos: list[str]) -> int:
    r = requests.post(
        f"{API}/repos/{repo()}/issues",
        headers=_cab(),
        json={"title": titulo, "body": corpo, "labels": rotulos},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["number"]


def comentar(numero: int, texto: str) -> None:
    requests.post(
        f"{API}/repos/{repo()}/issues/{numero}/comments",
        headers=_cab(),
        json={"body": texto},
        timeout=30,
    ).raise_for_status()


def fechar(numero: int, motivo: str = "completed") -> None:
    requests.patch(
        f"{API}/repos/{repo()}/issues/{numero}",
        headers=_cab(),
        json={"state": "closed", "state_reason": motivo},
        timeout=30,
    ).raise_for_status()


def atualizar_segredo(nome: str, valor: str) -> None:
    """Grava um segredo do repositório (precisa do GH_SECRETS_TOKEN)."""
    from nacl import encoding, public

    cab = _cab("GH_SECRETS_TOKEN")
    chave = requests.get(
        f"{API}/repos/{repo()}/actions/secrets/public-key", headers=cab, timeout=30
    ).json()
    caixa = public.SealedBox(public.PublicKey(chave["key"].encode(), encoding.Base64Encoder()))
    cifrado = base64.b64encode(caixa.encrypt(valor.encode())).decode()
    requests.put(
        f"{API}/repos/{repo()}/actions/secrets/{nome}",
        headers=cab,
        json={"encrypted_value": cifrado, "key_id": chave["key_id"]},
        timeout=30,
    ).raise_for_status()
