// Capas do quadro 0 (título na metade esquerda; a metade direita fica para o avatar em meia tela).
// Uso: node capas.cjs <pasta-saida>
const pw = require(process.env.PLAYWRIGHT || 'playwright');
const path = require('path'), fs = require('fs');
const SORA = path.resolve(__dirname, '../filmes/opcao1/assets/fonts/Sora.ttf');
const CAPAS = {
  '1a': { l: ['Mande o seu', '<span>servidor trabalhar</span>', 'pelo celular.'], sub: 'Telegram como controle remoto do Claude Code: as 4 peças e os 3 casos.' },
  '3a': { l: ['Não é animação.', '<span>É o Claude Code</span>', 'de verdade.'], sub: 'Uma conversa real pelo chat: ele responde, executa e pede o seu OK.' },
  '1b': { l: ['Um assistente', '<span>que lembra de você</span>', 'e não faz besteira.'], sub: 'O Jarvis do Intelecto: 8 peças, cada uma com um motivo.' },
  '3b': { l: ['O Jarvis', '<span>rodando</span>', 'de verdade.'], sub: 'As peças do Intelecto v2 reais, com o cérebro de teste.' },
};
const html = c => `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:Sora;src:url("file://${SORA}");font-weight:100 800}
*{margin:0;padding:0;box-sizing:border-box}
body{width:1920px;height:1080px;background:#facc15;font-family:Sora,sans-serif;color:#0c0c10;position:relative;overflow:hidden}
.l{position:absolute;left:110px;font-size:80px;font-weight:800;letter-spacing:-.04em;line-height:1;white-space:nowrap}
.l span{background:#0c0c10;color:#facc15;padding:4px 20px;border-radius:14px}
#a{top:250px}#b{top:375px}#c{top:500px}
#s{position:absolute;left:114px;top:670px;width:780px;font-family:Inter,sans-serif;font-size:38px;font-weight:600;color:#3a2f06;line-height:1.3}
#m{position:absolute;left:114px;top:930px;font-weight:800;font-size:30px;letter-spacing:.08em;color:#3a2f06}
</style></head><body><p class="l" id="a">${c.l[0]}</p><p class="l" id="b">${c.l[1]}</p><p class="l" id="c">${c.l[2]}</p><p id="s">${c.sub}</p><p id="m">INEMA.CLUB</p></body></html>`;
(async () => {
  const out = path.resolve(process.argv[2]); fs.mkdirSync(out, { recursive: true });
  const b = await pw.chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  for (const [k, c] of Object.entries(CAPAS)) {
    const arq = path.join(out, `.capa-${k}.html`); fs.writeFileSync(arq, html(c)); await p.goto('file://' + arq); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
    const fonte = await p.evaluate(() => document.fonts.check('800 80px Sora'));
    const w = await p.evaluate(() => Math.max(...[...document.querySelectorAll('.l')].map(e => e.getBoundingClientRect().right)));
    await p.screenshot({ path: path.join(out, `capa-${k}.png`) }); console.log(k, 'Sora:', fonte, 'borda direita do título:', Math.round(w));
  }
  await b.close();
})();
