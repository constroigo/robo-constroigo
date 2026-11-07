"""Renova o token do Instagram e grava o novo no cofre do GitHub."""

from . import github, instagram


def main() -> None:
    novo = instagram.renovar_token()
    github.atualizar_segredo("IG_ACCESS_TOKEN", novo)
    print("Token do Instagram renovado por mais 60 dias.")


if __name__ == "__main__":
    main()
