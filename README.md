# Seu Jarvis no Telegram

<div align="center">
  <img src="capa/logo.svg" alt="Arckhé AI" height="48" />
  <p><strong>Arckhé AI</strong></p>
</div>


[![Seu Jarvis no Telegram](guia/assets/banner.jpg)](https://inematds.github.io/telegram-claude-jarvis/guia/)

**ðŸ‡§ðŸ‡· [PortuguÃªs](README.md) Â· ðŸ‡ºðŸ‡¸ [English](README.en.md) Â· ðŸ‡ªðŸ‡¸ [EspaÃ±ol](README.es.md)**

## O que Ã©

Aqui vocÃª vÃª dois jeitos de conversar pelo Telegram com uma IA que trabalha no seu servidor. O primeiro Ã© o **controle remoto do Claude Code**: um bot confere se Ã© vocÃª e repassa o pedido ao Claude Code, que responde ou executa. O segundo Ã© o **Jarvis do Intelecto**: um assistente com identidade, memÃ³ria, regras e trava, que usa a IA como cÃ©rebro e pode trocar de cÃ©rebro. Serve para quem quer mandar tarefas pelo celular sem abrir o computador. O projeto traz as demonstraÃ§Ãµes reais, as peÃ§as animadas e os vÃ­deos.

## ðŸ“– Guia de uso

Guia completo (landing + passo a passo): **https://inematds.github.io/telegram-claude-jarvis/guia/**

## Como comeÃ§ar (sem instalar nada Ã  mÃ£o)

Abra o Claude Code ou o Codex no computador onde a IA vai trabalhar e cole:

```text
Leia o projeto "Seu Jarvis no Telegram" em https://github.com/inematds/telegram-claude-jarvis (o README explica tudo, inclusive a instalaÃ§Ã£o).
Quero conversar pelo Telegram com uma IA que trabalha neste computador.
Me responda em portuguÃªs simples:
1. Qual das duas opÃ§Ãµes faz sentido para mim agora: o controle remoto do Claude Code ou o Jarvis do Intelecto? Por quÃª?
2. O que eu preciso ter (bot do Telegram, meu nÃºmero de usuÃ¡rio, onde fica a IA) e onde guardar o token com seguranÃ§a.
3. Quais pedidos vÃ£o rodar direto e quais vÃ£o me pedir confirmaÃ§Ã£o antes.
NÃ£o instale nem mude nada ainda. Mostre o plano e espere eu dizer sim.
```

## As duas opÃ§Ãµes

| | OpÃ§Ã£o 1 Â· controle remoto | OpÃ§Ã£o 2 Â· Jarvis do Intelecto |
|---|---|---|
| Fluxo | Telegram â†’ bot â†’ Claude Code â†’ resposta | Telegram â†’ Intelecto (8 peÃ§as) â†’ cÃ©rebro e ferramentas â†’ resposta |
| Quem pensa | Claude Code | o cÃ©rebro escolhido (local, nuvem ou de teste) |
| MemÃ³ria e identidade | as do agente | camada prÃ³pria: SOUL, AGENTS, USER, MEMORY + memÃ³ria SQLite |
| SeguranÃ§a | lista de usuÃ¡rios + "Confirma?" antes de apagar, pagar ou enviar | trava (lÃª passa, muda pede OK, destrutivo recusado), cofre, auditoria e caixa Docker sem rede |
| Melhor para | comeÃ§ar rÃ¡pido | evoluir para um assistente pessoal |

---

## InstalaÃ§Ã£o tÃ©cnica

### PrÃ©-requisitos

- Python 3.10+ e Node 18+ (Playwright, sÃ³ para gravar as demonstraÃ§Ãµes).
- **OpÃ§Ã£o 1:** Claude Code instalado e logado pela assinatura (`claude -p` funcionando).
- **OpÃ§Ã£o 2:** o [Intelecto v2](https://github.com/inematds/intelecto-v2) baixado (`git clone https://github.com/inematds/intelecto-v2 ~/projetos/intelecto-v2`; outro lugar â†’ variÃ¡vel `INTELECTO_V2`) e Docker com a imagem `python:3.12-slim` (`docker pull python:3.12-slim`), que Ã© a "caixa".

### Arquivos

| Caminho | O que Ã© |
|---|---|
| `ponte-opcao1/server.py` + `chat.html` | Ponte da OpÃ§Ã£o 1: tela estilo Telegram â†’ confere o usuÃ¡rio â†’ `claude -p` (stream-json) com ferramentas limitadas e a regra do "Confirma?". SÃ³ em 127.0.0.1. |
| `ponte-opcao1/preparar-sandbox.sh` | Cria a pasta de teste (12 logs antigos + 9 recentes) onde o Claude trabalha. |
| `ponte-opcao2/server.py` + `chat.html` | Ponte da OpÃ§Ã£o 2: tela estilo Telegram â†’ Intelecto v2 de verdade com cÃ©rebro `mock`; cada peÃ§a avisa quando age e a tela acende a peÃ§a. AprovaÃ§Ã£o pelo botÃ£o no chat. |
| `pecas/opcao1-telegram.html` | PeÃ§a animada da OpÃ§Ã£o 1 (3 casos, sem biblioteca). `?roteiro=1` desliga o ciclo e expÃµe `window.cena()`. |
| `pecas/opcao2-jarvis.html` | PeÃ§a animada da OpÃ§Ã£o 2 (8 peÃ§as com "por quÃª" e "como"). |
| `filmes/opcao1`, `filmes/opcao2` | Filmes HyperFrames 0.8.77 + GSAP; `tpl/` tem os moldes com tempos `{{var}}` e `spec.json` as Ã¢ncoras da fala. |
| `ferramentas/` | Captura quadro a quadro, gravaÃ§Ã£o das pÃ¡ginas, montagem no tempo da fala e composiÃ§Ã£o com o avatar. |

### Rodar as demonstraÃ§Ãµes

```bash
git clone https://github.com/inematds/telegram-claude-jarvis && cd telegram-claude-jarvis

# OpÃ§Ã£o 1 â€” Claude Code de verdade (assinatura)
(cd ponte-opcao1 && ./preparar-sandbox.sh && python3 server.py 8794)
# abra http://127.0.0.1:8794 e pergunte: "Quanto espaÃ§o livre tem no disco do servidor?"

# OpÃ§Ã£o 2 â€” Intelecto v2 com cÃ©rebro de teste
(cd ponte-opcao2 && INTELECTO_V2=~/projetos/intelecto-v2 python3 server.py 8798)   # em outro terminal; nÃ£o precisa instalar o intelecto com pip
# abra http://127.0.0.1:8798 e mande: "lembre que o meu servidor de backup se chama Atlas", "rode: df -h /", "rode: rm -r logs"
```

Ligar no Telegram de verdade:
- **OpÃ§Ã£o 2:** o Intelecto jÃ¡ tem o canal (`python3 -m intelecto telegram`, com o token no cofre e o seu id em `telegram_donos`).
- **OpÃ§Ã£o 1:** falta o adaptador do bot (receber a mensagem pelo Telegram, conferir o id e chamar a mesma funÃ§Ã£o `chama_claude` da ponte). Ã‰ o prÃ³ximo passo.

### O processo, do inÃ­cio ao fim

| # | Passo | Comando | Quem faz |
|---|---|---|---|
| 1 | Falas dos 6 vÃ­deos (chamada D20, uma linha, sem "IAs") | `falas/*.txt` | ðŸ§  sessÃ£o com o Nei |
| 2 | Avatar no estÃºdio HeyGen (pela assinatura) | `node explicavideos/engine/heygen-studio.mjs --titulo tcj-<id> --fala-arquivo <txt> --template TEMPLATE-AVATAR16` | âš™ï¸ script |
| 3 | Baixar o avatar (API de leitura) | `node explicavideos/engine/heygen-estudio-baixar.mjs --id <id> --saida <mp4>` | âš™ï¸ script |
| 4 | Tempo de cada palavra da fala | Whisper local (inemavox) â†’ `palavras.json` | âš™ï¸ script |
| 5 | Demos reais quadro a quadro | `node ferramentas/capturar-real.cjs <porta> a\|b <pasta>` | âš™ï¸ script (a resposta vem do ðŸ¤– `claude -p` na OpÃ§Ã£o 1) |
| 6 | Demos reais no tempo da fala | `python3 ferramentas/stopmotion.py <quadros> <spec> <palavras> <dur> <capa> <cta> <saida>` | âš™ï¸ script |
| 7 | PeÃ§as animadas no tempo da fala | `node ferramentas/gravar-pagina.cjs <pagina> <roteiro.json> <saida>` | âš™ï¸ script |
| 8 | Filmes no tempo da fala | `python3 ferramentas/filme.py filmes/opcaoN spec.json <palavras> <dur>` + `npx hyperframes@0.8.77 check` + `render` | âš™ï¸ script |
| 9 | Juntar avatar (meia tela â†’ canto), voz e trilha | `python3 ferramentas/compor.py <visual> <avatar> <t_meia> dir\|esq <saida>` | âš™ï¸ script |
| 10 | RevisÃ£o independente do guia e dos vÃ­deos | revisor novo pelo runbook | ðŸ¤– revisor |
| 11 | Guia no Pages, portal, tÃ³pico no INEMA.VIBE e vÃ­deos no lives3 (1 h entre eles) | `git push`, `atualiza-portal`, `postar-telegram`, fila do yt-pub-x3 | ðŸ§  sessÃ£o com o Nei |

### Limites conhecidos

- A demonstraÃ§Ã£o da OpÃ§Ã£o 1 usa uma tela local no estilo do Telegram, nÃ£o o Telegram.
- O cÃ©rebro da demonstraÃ§Ã£o da OpÃ§Ã£o 2 Ã© o `mock` (nÃ£o raciocina; segue um roteiro fixo). As outras 7 peÃ§as sÃ£o as reais.
- Numa das 3 gravaÃ§Ãµes da OpÃ§Ã£o 1, o Claude contou 4,8 MB (base decimal) em vez de 4,6 MB; o vÃ­deo usa a gravaÃ§Ã£o que bate com a narraÃ§Ã£o.

## LicenÃ§a

MIT. GrÃ¡tis no [inema.club](https://inema.club), direto na internet.

---

<div align="center">
  <img src="capa/logo.svg" alt="Arckhé AI" height="32" />
  <p><strong>Arckhé AI</strong></p>
</div>