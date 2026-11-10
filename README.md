# Robô Constrói GO

Robô que publica no Instagram **@constroigo** notícias da construção civil em Goiás, 3 vezes por dia.

## Como funciona

1. **07:37, 11:52 e 17:47** (horário de Brasília) o robô busca no Google Notícias as notícias das últimas 48 horas sobre o tema do horário:
   - **Manhã:** construção civil e mercado imobiliário
   - **Meio-dia:** infraestrutura, energia e saneamento
   - **Fim da tarde:** obras, máquinas e tecnologia
2. O **Gemini** escolhe a notícia mais relevante para Goiás e escreve manchete, resumo e legenda, usando só o que está na notícia.
3. O robô gera a arte (1080 × 1350) com a marca, o "Por Higor Siqueira", a fonte e a faixa **Oferecimento** (H2R Engenharia, Siqueira Locação, Histórias Helvécia, H2R Incorp e H2R Energia, escolhida pelo assunto do post).
4. Abre um pedido de aprovação na aba **Issues**, com a arte e a legenda. O app do GitHub avisa no celular.
5. Você responde **ok** para publicar ou **não** para descartar.

Para dispensar a aprovação, crie a variável `AUTO_PUBLICAR` com o valor `sim` (Settings › Secrets and variables › Actions › Variables).

## Cofre de chaves (Settings › Secrets and variables › Actions › Secrets)

| Nome | O que é |
| --- | --- |
| `GEMINI_API_KEY` | Chave do Google AI Studio (aistudio.google.com › Get API key) |
| `IG_ACCESS_TOKEN` | Chave do Instagram gerada no app da Meta (login unificado; começa com EAA e não vence) |
| `IG_USER_ID` | ID da conta do Instagram (obrigatório no login unificado) |
| `GH_SECRETS_TOKEN` | Opcional: chave do GitHub com permissão **Secrets: read and write**, para renovar o token do Instagram sozinho a cada 15 dias |

## Gerar um post agora (teste)

Aba **Actions** › **Preparar post** › **Run workflow** › escolha o horário › **Run workflow**.

## Ajustes

Temas, buscas, anunciantes e hashtags ficam em `robo/config.py`. Logos dos anunciantes vão em `assets/patrocinadores/` (PNG com fundo transparente), com o caminho preenchido em `config.py`.
