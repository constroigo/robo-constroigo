"""Configurações do robô Constrói GO.

Para mudar temas, horários ou anunciantes, edite só este arquivo.
"""

AUTOR = "Higor Siqueira"
FOTO_AUTOR = "assets/higor.jpg"  # foto redonda no rodapé; deixe "" para não usar
PERFIL = "@constroigo"

# Cada horário tem um tema e as buscas usadas no Google Notícias.
HORARIOS = {
    "manha": {
        "rotulo": "Notícia do dia",
        "buscas": [
            "construção civil Goiás",
            "mercado imobiliário Goiânia",
            "construção civil Brasil",
            "Sinduscon-GO",
        ],
    },
    "meiodia": {
        "rotulo": "Infraestrutura e energia",
        "buscas": [
            "infraestrutura Goiás obra",
            "rodovia Goiás Goinfra",
            "energia Goiás",
            "saneamento Goiás obra",
        ],
    },
    "tarde": {
        "rotulo": "Obras, máquinas e tecnologia",
        "buscas": [
            "obra Goiânia",
            "máquinas pesadas construção",
            "tecnologia construção civil",
            "lançamento imobiliário Goiânia",
        ],
    },
}

# Faixa "Oferecimento": um anunciante por post, em rodízio.
# Para usar a logo, coloque o arquivo em assets/patrocinadores/ e preencha "logo".
PATROCINADORES = [
    {"nome": "H2R Engenharia", "logo": "assets/patrocinadores/h2r.png"},
    {"nome": "Siqueira Locação", "logo": "assets/patrocinadores/siqueira-locacao.png"},
    {"nome": "Histórias Helvécia", "logo": "assets/patrocinadores/historias-helvecia.png"},
    {"nome": "H2R Incorp", "logo": "assets/patrocinadores/h2r-incorp.png"},
]

HASHTAGS_FIXAS = ["#constroigo", "#construcaocivil", "#goias", "#goiania", "#engenharia"]

# Só considera notícias publicadas nas últimas X horas.
JANELA_HORAS = 48
