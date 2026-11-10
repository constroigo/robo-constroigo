"""Temas e layouts dos cards.

Todos seguem a mesma marca (azul-marinho, azul, amarelo, fonte Sora, logo de blocos),
mas variam cor de fundo e composição para o feed não ficar repetitivo.
"""

TEMAS = {
    "marinho": {
        "bg": "#0F2747", "texto": "#FFFFFF", "sub": "#C9D3E3", "destaque": "#F2B705",
        "tag_bg": "#F2B705", "tag_fg": "#0F2747", "linha": "#2B4C7E",
        "bloco_a": "#FFFFFF", "bloco_b": "#9DB7E0", "bloco_c": "#F2B705",
        "go_bg": "#F2B705", "go_fg": "#0F2747", "caixa_bg": "#F2B705", "caixa_fg": "#0F2747",
    },
    "claro": {
        "bg": "#F5F6F8", "texto": "#0F2747", "sub": "#3E4C63", "destaque": "#2B4C7E",
        "tag_bg": "#0F2747", "tag_fg": "#F2B705", "linha": "#D5DBE5",
        "bloco_a": "#0F2747", "bloco_b": "#2B4C7E", "bloco_c": "#F2B705",
        "go_bg": "#F2B705", "go_fg": "#0F2747", "caixa_bg": "#0F2747", "caixa_fg": "#F2B705",
    },
    "amarelo": {
        "bg": "#F2B705", "texto": "#0F2747", "sub": "#2E3A4F", "destaque": "#0F2747",
        "tag_bg": "#0F2747", "tag_fg": "#F2B705", "linha": "#C99700",
        "bloco_a": "#0F2747", "bloco_b": "#2B4C7E", "bloco_c": "#FFFFFF",
        "go_bg": "#0F2747", "go_fg": "#F2B705", "caixa_bg": "#0F2747", "caixa_fg": "#F2B705",
    },
    "azul": {
        "bg": "#2B4C7E", "texto": "#FFFFFF", "sub": "#DCE5F2", "destaque": "#F2B705",
        "tag_bg": "#FFFFFF", "tag_fg": "#0F2747", "linha": "#4A6FA5",
        "bloco_a": "#FFFFFF", "bloco_b": "#0F2747", "bloco_c": "#F2B705",
        "go_bg": "#F2B705", "go_fg": "#0F2747", "caixa_bg": "#0F2747", "caixa_fg": "#F2B705",
    },
    # Fora da rotação: só para posts de alerta/impacto, quando pedido.
    "vermelho": {
        "bg": "#B42318", "texto": "#FFFFFF", "sub": "#FBDAD6", "destaque": "#F2B705",
        "tag_bg": "#FFFFFF", "tag_fg": "#B42318", "linha": "#D2584D",
        "bloco_a": "#FFFFFF", "bloco_b": "#FBDAD6", "bloco_c": "#F2B705",
        "go_bg": "#F2B705", "go_fg": "#0F2747", "caixa_bg": "#F2B705", "caixa_fg": "#0F2747",
    },
}

# Combinações (tema, layout) que funcionam bem. O robô passa por elas em sequência,
# então dois posts seguidos nunca saem iguais.
ESTILOS = [
    ("marinho", "classico"),
    ("claro", "caixa"),
    ("amarelo", "classico"),
    ("marinho", "barra"),
    ("claro", "classico"),
    ("azul", "caixa"),
    ("marinho", "caixa"),
    ("claro", "barra"),
    ("azul", "classico"),
]


def escolher(seed: int, layout_forcado: str | None = None, tema_forcado: str | None = None) -> dict:
    tema, layout = ESTILOS[seed % len(ESTILOS)]
    tema = tema_forcado or tema
    layout = layout_forcado or layout
    return {"layout": layout, "nome_tema": tema, **TEMAS[tema]}
