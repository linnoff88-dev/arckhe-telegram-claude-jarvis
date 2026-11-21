// Captura quadro a quadro (stop-motion) de uma conversa REAL na tela estilo Telegram:
// digitação letra a letra, "digitando…", resposta, pedido de OK. Cada quadro vira PNG 1920x1080
// e frames.json guarda as marcas (para casar com a fala do avatar depois).
// Uso: node capturar-real.cjs <porta> <a|b> <pasta-saida>
const pw = require(process.env.PLAYWRIGHT || 'playwright');
const path = require('path'), fs = require('fs');
const [PORTA, QUAL, SAIDA] = [process.argv[2], process.argv[3], path.resolve(process.argv[4])];
fs.mkdirSync(SAIDA, { recursive: true });
const ROTEIRO = {
  a: [
    { leg: '1 · Você pergunta pelo chat', txt: 'Quanto espaço livre tem no disco do servidor?' },
    { leg: '2 · Um pedido que apaga arquivos', txt: 'Apaga os logs com mais de 30 dias da pasta logs.' },
    { leg: '3 · Você confirma', txt: 'Sim, pode apagar.' },
  ],
  b: [
    { leg: '1 · Memória: guardar', txt: 'lembre que o meu servidor de backup se chama Atlas' },
    { leg: '2 · Memória: buscar', txt: 'qual é o meu servidor de backup?' },
    { leg: '3 · Só lê: a trava deixa passar', txt: 'rode: df -h /' },
    { leg: '4 · Muda arquivos: a trava pede OK', txt: 'rode: rm -r logs', aprova: true },
    { leg: '5 · Destrutivo: bloqueado', txt: 'rode: sudo reboot' },
  ],
}[QUAL];
(async () => {
  const b = await pw.chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1.5 });
  const erros = []; p.on('pageerror', e => erros.push(e.message));
  if (QUAL === 'a') await p.goto(`http://127.0.0.1:${PORTA}/reset`);
  await p.goto(`http://127.0.0.1:${PORTA}/`); await p.waitForTimeout(600);
  const quadros = []; let n = 0;
  const shot = async (marca) => { const f = `${String(n++).padStart(4, '0')}.png`; await p.screenshot({ path: path.join(SAIDA, f) }); quadros.push({ f, marca: marca || '' }); };
  const leg = t => p.evaluate(t => window.legenda ? window.legenda(t) : null, t);
  await shot('inicio');
  let i = 0;
  for (const passo of ROTEIRO) {
    i++;
    await leg(passo.leg); await p.waitForTimeout(250); await shot(`m${i}-legenda`);
    await p.click('#txt');
    for (let k = 0; k < passo.txt.length; k++) {
      await p.type('#txt', passo.txt[k]);
      if (k % 2 === 1 || k === passo.txt.length - 1) await shot(k < 2 ? `m${i}-digita` : 'dig');
    }
    await p.click('#send'); await p.waitForTimeout(120); await shot(`m${i}-enviado`);
    // enquanto espera: um quadro a cada 400 ms (as peças acendem, a ponte registra)
    let espera = 0;
    while (true) {
      if (passo.aprova && await p.locator('#bSim').count()) {
        await p.waitForTimeout(500); await shot(`m${i}-pede-ok`);
        await p.locator('#bSim').hover(); await shot('hover');
        await p.click('#bSim'); await p.waitForTimeout(200); await shot(`m${i}-aprovou`);
        passo.aprova = false;
      }
      const busy = await p.evaluate(() => document.body.dataset.busy);
      if (busy === '0') break;
      await p.waitForTimeout(400); if (espera++ < 40 || espera % 5 === 0) await shot('espera');
      if (espera > 600) throw new Error('resposta demorou demais');
    }
    await p.waitForTimeout(700); await shot(`m${i}-resposta`);
  }
  await leg(''); await p.waitForTimeout(300); await shot('fim');
  const conversa = await p.locator('.m').allInnerTexts();
  fs.writeFileSync(path.join(SAIDA, 'frames.json'), JSON.stringify({ quadros, conversa }, null, 2));
  console.log(JSON.stringify({ quadros: quadros.length, erros, conversa }, null, 2));
  await b.close();
})();
