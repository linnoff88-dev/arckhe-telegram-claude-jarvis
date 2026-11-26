ï»¿# Seu Jarvis no Telegram

<div align="center">
  <img src="capa/logo.svg" alt="Arckhé AI" height="48" />
  <p><strong>Arckhé AI</strong></p>
</div>


[![Seu Jarvis no Telegram](guia/assets/banner.jpg)](https://linnoff88-dev.github.io/arckhe-/guia/)

**ê°Å¸â¡Â§ê°Å¸â¡Â· [PortuguêÂªs](README.md) êÂ· ê°Å¸â¡Âºê°Å¸â¡Â¸ [English](README.en.md) êÂ· ê°Å¸â¡Âªê°Å¸â¡Â¸ [EspaêÂ±ol](README.es.md)**

## O que êÂ©

Aqui vocêÂª vêÂª dois jeitos de conversar pelo Telegram com uma IA que trabalha no seu servidor. O primeiro êÂ© o **controle remoto do Claude Code**: um bot confere se êÂ© vocêÂª e repassa o pedido ao Claude Code, que responde ou executa. O segundo êÂ© o **Jarvis do Intelecto**: um assistente com identidade, memêÂ³ria, regras e trava, que usa a IA como cêÂ©rebro e pode trocar de cêÂ©rebro. Serve para quem quer mandar tarefas pelo celular sem abrir o computador. O projeto traz as demonstraêÂ§êÂµes reais, as peêÂ§as animadas e os vêÂ­deos.

## ê°Å¸ââ Guia de uso

Guia completo (landing + passo a passo): **https://linnoff88-dev.github.io/arckhe-/guia/**

## Como comeêÂ§ar (sem instalar nada êÂ  mêÂ£o)

Abra o Claude Code ou o Codex no computador onde a IA vai trabalhar e cole:

```text
Leia o projeto "Seu Jarvis no Telegram" em https://github.com/linnoff88-dev/telegram-claude-jarvis (o README explica tudo, inclusive a instalaêÂ§êÂ£o).
Quero conversar pelo Telegram com uma IA que trabalha neste computador.
Me responda em portuguêÂªs simples:
1. Qual das duas opêÂ§êÂµes faz sentido para mim agora: o controle remoto do Claude Code ou o Jarvis do Intelecto? Por quêÂª?
2. O que eu preciso ter (bot do Telegram, meu nêÂºmero de usuêÂ¡rio, onde fica a IA) e onde guardar o token com seguranêÂ§a.
3. Quais pedidos vêÂ£o rodar direto e quais vêÂ£o me pedir confirmaêÂ§êÂ£o antes.
NêÂ£o instale nem mude nada ainda. Mostre o plano e espere eu dizer sim.
```

## As duas opêÂ§êÂµes

| | OpêÂ§êÂ£o 1 êÂ· controle remoto | OpêÂ§êÂ£o 2 êÂ· Jarvis do Intelecto |
|---|---|---|
| Fluxo | Telegram ê¢â â bot ê¢â â Claude Code ê¢â â resposta | Telegram ê¢â â Intelecto (8 peêÂ§as) ê¢â â cêÂ©rebro e ferramentas ê¢â â resposta |
| Quem pensa | Claude Code | o cêÂ©rebro escolhido (local, nuvem ou de teste) |
| MemêÂ³ria e identidade | as do agente | camada prêÂ³pria: SOUL, AGENTS, USER, MEMORY + memêÂ³ria SQLite |
| SeguranêÂ§a | lista de usuêÂ¡rios + "Confirma?" antes de apagar, pagar ou enviar | trava (lêÂª passa, muda pede OK, destrutivo recusado), cofre, auditoria e caixa Docker sem rede |
| Melhor para | comeêÂ§ar rêÂ¡pido | evoluir para um assistente pessoal |

---

## InstalaêÂ§êÂ£o têÂ©cnica

### PrêÂ©-requisitos

- Python 3.10+ e Node 18+ (Playwright, sêÂ³ para gravar as demonstraêÂ§êÂµes).
- **OpêÂ§êÂ£o 1:** Claude Code instalado e logado pela assinatura (`claude -p` funcionando).
- **OpêÂ§êÂ£o 2:** o [Intelecto v2](https://github.com/linnoff88-dev/intelecto-v2) baixado (`git clone https://github.com/linnoff88-dev/intelecto-v2 ~/projetos/intelecto-v2`; outro lugar ê¢â â variêÂ¡vel `INTELECTO_V2`) e Docker com a imagem `python:3.12-slim` (`docker pull python:3.12-slim`), que êÂ© a "caixa".

### Arquivos

| Caminho | O que êÂ© |
|---|---|
| `ponte-opcao1/server.py` + `chat.html` | Ponte da OpêÂ§êÂ£o 1: tela estilo Telegram ê¢â â confere o usuêÂ¡rio ê¢â â `claude -p` (stream-json) com ferramentas limitadas e a regra do "Confirma?". SêÂ³ em 127.0.0.1. |
| `ponte-opcao1/preparar-sandbox.sh` | Cria a pasta de teste (12 logs antigos + 9 recentes) onde o Claude trabalha. |
| `ponte-opcao2/server.py` + `chat.html` | Ponte da OpêÂ§êÂ£o 2: tela estilo Telegram ê¢â â Intelecto v2 de verdade com cêÂ©rebro `mock`; cada peêÂ§a avisa quando age e a tela acende a peêÂ§a. AprovaêÂ§êÂ£o pelo botêÂ£o no chat. |
| `pecas/opcao1-telegram.html` | PeêÂ§a animada da OpêÂ§êÂ£o 1 (3 casos, sem biblioteca). `?roteiro=1` desliga o ciclo e expêÂµe `window.cena()`. |
| `pecas/opcao2-jarvis.html` | PeêÂ§a animada da OpêÂ§êÂ£o 2 (8 peêÂ§as com "por quêÂª" e "como"). |
| `filmes/opcao1`, `filmes/opcao2` | Filmes HyperFrames 0.8.77 + GSAP; `tpl/` tem os moldes com tempos `{{var}}` e `spec.json` as êÂ¢ncoras da fala. |
| `ferramentas/` | Captura quadro a quadro, gravaêÂ§êÂ£o das pêÂ¡ginas, montagem no tempo da fala e composiêÂ§êÂ£o com o avatar. |

### Rodar as demonstraêÂ§êÂµes

```bash
git clone https://github.com/linnoff88-dev/telegram-claude-jarvis && cd telegram-claude-jarvis

# OpêÂ§êÂ£o 1 ê¢â¬â Claude Code de verdade (assinatura)
(cd ponte-opcao1 && ./preparar-sandbox.sh && python3 server.py 8794)
# abra http://127.0.0.1:8794 e pergunte: "Quanto espaêÂ§o livre tem no disco do servidor?"

# OpêÂ§êÂ£o 2 ê¢â¬â Intelecto v2 com cêÂ©rebro de teste
(cd ponte-opcao2 && INTELECTO_V2=~/projetos/intelecto-v2 python3 server.py 8798)   # em outro terminal; nêÂ£o precisa instalar o intelecto com pip
# abra http://127.0.0.1:8798 e mande: "lembre que o meu servidor de backup se chama Atlas", "rode: df -h /", "rode: rm -r logs"
```

Ligar no Telegram de verdade:
- **OpêÂ§êÂ£o 2:** o Intelecto jêÂ¡ tem o canal (`python3 -m intelecto telegram`, com o token no cofre e o seu id em `telegram_donos`).
- **OpêÂ§êÂ£o 1:** falta o adaptador do bot (receber a mensagem pelo Telegram, conferir o id e chamar a mesma funêÂ§êÂ£o `chama_claude` da ponte). êâ° o prêÂ³ximo passo.

### O processo, do inêÂ­cio ao fim

| # | Passo | Comando | Quem faz |
|---|---|---|---|
| 1 | Falas dos 6 vêÂ­deos (chamada D20, uma linha, sem "IAs") | `falas/*.txt` | ê°Å¸Â§Â  sessêÂ£o com o Nei |
| 2 | Avatar no estêÂºdio HeyGen (pela assinatura) | `node explicavideos/engine/heygen-studio.mjs --titulo tcj-<id> --fala-arquivo <txt> --template TEMPLATE-AVATAR16` | ê¢Å¡â¢ê¯Â¸Â script |
| 3 | Baixar o avatar (API de leitura) | `node explicavideos/engine/heygen-estudio-baixar.mjs --id <id> --saida <mp4>` | ê¢Å¡â¢ê¯Â¸Â script |
| 4 | Tempo de cada palavra da fala | Whisper local (ARCKHÉvox) ê¢â â `palavras.json` | ê¢Å¡â¢ê¯Â¸Â script |
| 5 | Demos reais quadro a quadro | `node ferramentas/capturar-real.cjs <porta> a\|b <pasta>` | ê¢Å¡â¢ê¯Â¸Â script (a resposta vem do ê°Å¸Â¤â `claude -p` na OpêÂ§êÂ£o 1) |
| 6 | Demos reais no tempo da fala | `python3 ferramentas/stopmotion.py <quadros> <spec> <palavras> <dur> <capa> <cta> <saida>` | ê¢Å¡â¢ê¯Â¸Â script |
| 7 | PeêÂ§as animadas no tempo da fala | `node ferramentas/gravar-pagina.cjs <pagina> <roteiro.json> <saida>` | ê¢Å¡â¢ê¯Â¸Â script |
| 8 | Filmes no tempo da fala | `python3 ferramentas/filme.py filmes/opcaoN spec.json <palavras> <dur>` + `npx hyperframes@0.8.77 check` + `render` | ê¢Å¡â¢ê¯Â¸Â script |
| 9 | Juntar avatar (meia tela ê¢â â canto), voz e trilha | `python3 ferramentas/compor.py <visual> <avatar> <t_meia> dir\|esq <saida>` | ê¢Å¡â¢ê¯Â¸Â script |
| 10 | RevisêÂ£o independente do guia e dos vêÂ­deos | revisor novo pelo runbook | ê°Å¸Â¤â revisor |
| 11 | Guia no Pages, portal, têÂ³pico no ARCKHÉ.VIBE e vêÂ­deos no lives3 (1 h entre eles) | `git push`, `atualiza-portal`, `postar-telegram`, fila do yt-pub-x3 | ê°Å¸Â§Â  sessêÂ£o com o Nei |

### Limites conhecidos

- A demonstraêÂ§êÂ£o da OpêÂ§êÂ£o 1 usa uma tela local no estilo do Telegram, nêÂ£o o Telegram.
- O cêÂ©rebro da demonstraêÂ§êÂ£o da OpêÂ§êÂ£o 2 êÂ© o `mock` (nêÂ£o raciocina; segue um roteiro fixo). As outras 7 peêÂ§as sêÂ£o as reais.
- Numa das 3 gravaêÂ§êÂµes da OpêÂ§êÂ£o 1, o Claude contou 4,8 MB (base decimal) em vez de 4,6 MB; o vêÂ­deo usa a gravaêÂ§êÂ£o que bate com a narraêÂ§êÂ£o.

## LicenêÂ§a

MIT. GrêÂ¡tis no [ARCKHÉ AI](https://ARCKHÉ AI), direto na internet.

---

<div align="center">
  <img src="capa/logo.svg" alt="Arckhé AI" height="32" />
  <p><strong>Arckhé AI</strong></p>
</div>