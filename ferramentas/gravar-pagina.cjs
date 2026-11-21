// Grava uma página animada em 1920x1080 pelo screencast do Chrome (headless, 1536x864 CSS × 1,25),
// disparando window.cena(...) no tempo da fala. Cada quadro chega com o seu tempo; o vídeo sai a 30 fps.
// Uso: node gravar-pagina.cjs <pagina.html> <roteiro.json> <saida.mp4>
// roteiro.json = {"dur": 60.5, "cenas": [[0, "todos"], [3.2, "nTg"], ...]}  (tempos desde o início da gravação)
const pw = require(process.env.PLAYWRIGHT || 'playwright');
const { execFileSync } = require('child_process');
const path = require('path'), fs = require('fs'), os = require('os');
(async () => {
  const [pagina, rot, saida] = process.argv.slice(2);
  const R = JSON.parse(fs.readFileSync(rot, 'utf8'));
  const tmp = fs.mkdtempSync(path.join(path.dirname(path.resolve(saida)), '.quadros-'));
  const b = await pw.chromium.launch();
  const p = await b.newPage({ viewport: { width: 1536, height: 864 }, deviceScaleFactor: 1.25 });
  const erros = []; p.on('pageerror', e => erros.push(e.message));
  await p.goto('file://' + path.resolve(pagina) + '?roteiro=1');
  await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(1500);
  const cdp = await p.context().newCDPSession(p);
  const quadros = []; let t0 = null;
  cdp.on('Page.screencastFrame', async f => {
    const ts = f.metadata.timestamp; if (t0 === null) t0 = ts;
    const nome = path.join(tmp, `${String(quadros.length).padStart(6, '0')}.jpg`);
    fs.writeFileSync(nome, Buffer.from(f.data, 'base64')); quadros.push([ts - t0, nome]);
    try { await cdp.send('Page.screencastFrameAck', { sessionId: f.sessionId }); } catch (e) {}
  });
  await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 92, maxWidth: 1920, maxHeight: 1080, everyNthFrame: 1 });
  const ini = Date.now();
  for (const [t, cena] of R.cenas) {
    const falta = ini + t * 1000 - Date.now();
    if (falta > 0) await p.waitForTimeout(falta);
    await p.evaluate(c => window.cena(c), cena);
  }
  const resto = ini + R.dur * 1000 - Date.now(); if (resto > 0) await p.waitForTimeout(resto);
  await cdp.send('Page.stopScreencast'); await b.close();
  // lista do concat com a duração real de cada quadro (a página só manda quadro quando muda)
  const linhas = [];
  for (let i = 0; i < quadros.length; i++) {
    const fim = i + 1 < quadros.length ? quadros[i + 1][0] : R.dur;
    linhas.push(`file '${quadros[i][1]}'`, `duration ${Math.max(fim - quadros[i][0], 0.001).toFixed(4)}`);
  }
  linhas.push(`file '${quadros[quadros.length - 1][1]}'`);
  const lista = path.join(tmp, 'lista.txt'); fs.writeFileSync(lista, linhas.join('\n') + '\n');
  execFileSync('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lista, '-vf', 'scale=1920:1080:flags=lanczos,fps=30,format=yuv420p',
    '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-t', String(R.dur), saida]);
  console.log(JSON.stringify({ quadros: quadros.length, erros, saida, pasta_quadros: tmp }));
})();
