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

# Fontes indicadas pelo Higor. O robô busca notícias delas todo dia e dá preferência a elas.
# "busca": como procurar no Google Notícias (nome do órgão/veículo ou site:dominio).
FONTES_PREFERIDAS = [
    {"nome": "DNIT", "busca": "DNIT Goiás OR DNIT rodovia", "tipo": "Órgão federal"},
    {"nome": "ANTT", "busca": "ANTT concessão rodovia OR ANTT ferrovia", "tipo": "Órgão federal"},
    {"nome": "Goinfra", "busca": "Goinfra", "tipo": "Órgão estadual"},
    {"nome": "Seinfra Goiânia", "busca": "Seinfra Goiânia OR \"Prefeitura de Goiânia\" obras pavimentação", "tipo": "Órgão municipal"},
    {"nome": "Seinfra Aparecida", "busca": "\"Aparecida de Goiânia\" obras OR asfalto", "tipo": "Órgão municipal"},
    {"nome": "CBIC", "busca": "CBIC construção", "tipo": "Entidade"},
    {"nome": "Sinduscon-GO", "busca": "Sinduscon-GO OR \"Sinduscon Goiás\" OR \"CUB Goiás\"", "tipo": "Entidade"},
    {"nome": "CREA-GO", "busca": "CREA-GO OR \"Crea Goiás\"", "tipo": "Conselho"},
    {"nome": "Confea", "busca": "Confea engenharia", "tipo": "Conselho"},
    {"nome": "CAU/GO", "busca": "\"CAU/GO\" OR \"CAU Goiás\" arquitetura", "tipo": "Conselho"},
    {"nome": "Sobratema", "busca": "Sobratema OR site:sobratema.org.br", "tipo": "Máquinas"},
    {"nome": "Revista M&T", "busca": "\"Revista M&T\" OR site:revistamt.com.br", "tipo": "Máquinas"},
    {"nome": "Construmarket", "busca": "Construmarket", "tipo": "Construção"},
    {"nome": "Grandes Construções", "busca": "\"Grandes Construções\" OR site:grandesconstrucoes.com.br", "tipo": "Construção"},
    {"nome": "Jornal da Construção Civil", "busca": "\"Jornal da Construção Civil\"", "tipo": "Construção"},
    {"nome": "Construction Briefing", "busca": "\"Construction Briefing\" Brasil", "tipo": "Máquinas"},
]

# Faixa "Oferecimento": um anunciante por post, em rodízio.
# Para usar a logo, coloque o arquivo em assets/patrocinadores/ e preencha "logo".
PATROCINADORES = [
    {"nome": "H2R Engenharia", "logo": "assets/patrocinadores/h2r.png"},
    {"nome": "Siqueira Locação", "logo": "assets/patrocinadores/siqueira-locacao.png"},
    {"nome": "Histórias Helvécia", "logo": "assets/patrocinadores/historias-helvecia.png"},
    {"nome": "H2R Incorp", "logo": "assets/patrocinadores/h2r-incorp.png"},
    {"nome": "H2R Energia", "logo": "assets/patrocinadores/h2r-energia.png"},
    # Parceiros externos: só entram quando escolhidos (post especial ou categoria), fora do rodízio.
    {"nome": "Recurso Sustentável", "logo": "assets/patrocinadores/recurso-sustentavel.png", "rodizio": False},
]

# Anunciante preferido por assunto do post (o resto entra em rodízio).
PATROCINADOR_POR_CATEGORIA = {
    "INFRAESTRUTURA": "Siqueira Locação",
    "MÁQUINAS E EQUIPAMENTOS": "Siqueira Locação",
    "SANEAMENTO": "Siqueira Locação",
    "MERCADO IMOBILIÁRIO": "Histórias Helvécia",
    "OBRAS": "H2R Engenharia",
    "MERCADO DE TRABALHO": "H2R Engenharia",
    "ENERGIA": "H2R Energia",
    "TECNOLOGIA": "H2R Energia",
    "ECONOMIA": "H2R Incorp",
    "NOVIDADE": "H2R Engenharia",
    "MEIO AMBIENTE": "Recurso Sustentável",
}

HASHTAGS_FIXAS = ["#constroigo", "#construcaocivil", "#goias", "#goiania", "#engenharia"]

# Só considera notícias publicadas nas últimas X horas.
JANELA_HORAS = 48
