#!/usr/bin/env python3
"""Ponte de demonstraçêo (Opçêo 2): chat estilo Telegram -> INTELECTO v2 de verdade (as 8 peças).

O cérebro é o `mock` do próprio intelecto (sem rede, sem modelo): as outras 7 peças sêo as reais
(canal com lista de donos, loop com freio, identidade, memória SQLite, ferramentas, trava/aprovaçêo
com auditoria e a caixa Docker sem rede). Cada peça avisa quando age, e a tela acende a peça.
Uso: python3 server.py [porta]   (só 127.0.0.1)
"""
import asyncio, json, os, sys, tempfile, threading, time, pathlib
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

AQUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, os.path.expanduser(os.environ.get("INTELECTO_V2", "~/projetos/intelecto-v2")))
os.environ["INTELECTO_HOME"] = tempfile.mkdtemp(prefix="jarvis-demo-")
from intelecto import config as cfg            # noqa: E402
from intelecto.montagem import montar          # noqa: E402
from intelecto.provedores.mock import Mock     # noqa: E402

PORTA = int(sys.argv[1]) if len(sys.argv) > 1 else 8795
DONOS = {"nei"}   # no Telegram real: config.telegram_donos (ids numéricos)

EVENTOS, TRAVA = [], threading.Lock()
PENDENTE = {"comando": None, "motivo": None, "resposta": None, "ev": threading.Event()}


def evento(peca, texto):
    with TRAVA:
        EVENTOS.append({"n": len(EVENTOS), "peca": peca, "texto": texto, "t": round(time.time(), 2)})


async def perguntar(comando, motivo):
    PENDENTE.update(comando=comando, motivo=motivo, resposta=None)
    PENDENTE["ev"].clear()
    evento("trava", f"pede OK ao dono: {comando}")
    await asyncio.get_running_loop().run_in_executor(None, PENDENTE["ev"].wait, 300)
    sim = bool(PENDENTE["resposta"])
    PENDENTE.update(comando=None, motivo=None)
    evento("trava", "dono aprovou" if sim else "dono recusou")
    return sim


def preparar():
    global c, P, area
    c = cfg.Config()
    c.provedor, c.executor, c.aprovacao = "mock", "caixa", "perigosos"
    P = montar(c, perguntar=perguntar, provedor=Mock())
    area = pathlib.Path(c.area)
    (area / "logs").mkdir(parents=True, exist_ok=True)
    for i in range(1, 7):
        (area / "logs" / f"app-0{i}.log").write_text("linha de log de teste\n" * 50)

    # --- cada peça avisa quando age (envolve as instâncias reais, sem mudar o intelecto) ---
    _montar = P.agente.contexto.montar
    def montar_ctx(hist, pergunta):
        msgs = _montar(hist, pergunta)
        evento("identidade", "SOUL + AGENTS + USER entram no contexto")
        achadas = [m for m in msgs if m.papel == "system" and m.texto.startswith("Memórias que podem ajudar")]
        evento("memoria", f"{achadas[0].texto.count(chr(10))} memória(s) achada(s) para a pergunta" if achadas else "nenhuma memória casou")
        return msgs
    P.agente.contexto.montar = montar_ctx

    _conv = P.provedor.conversar
    async def conversar(msgs, ferramentas=None):
        evento("cerebro", "cérebro (mock) pensa")
        r = await _conv(msgs, ferramentas)
        for ch in r.chamadas:
            evento("loop", f"rodada: pede a ferramenta {ch['nome']}")
        return r
    P.provedor.conversar = conversar

    _salvar = P.memorias.salvar
    def salvar(*a, **k):
        i = _salvar(*a, **k); evento("memoria", f"guardado na memória (#{i})"); return i
    P.memorias.salvar = salvar

    _decidir = P.portao.decidir
    async def decidir(comando):
        from intelecto.seguranca.trava import classificar
        v = classificar(comando)
        evento("trava", {"livre": f"'{comando}' só lê → passa", "aprovar": f"'{comando}' muda algo → precisa de OK",
                         "bloqueado": f"'{comando}' destrutivo → bloqueado"}[v.classe])
        ok, txt = await _decidir(comando)
        evento("auditoria", f"registrado: {comando} · {txt}")
        return ok, txt
    P.portao.decidir = decidir

    _rodar = P.executor.rodar
    async def rodar(comando):
        evento("caixa", f"roda na caixa (Docker sem rede): {comando}")
        return await _rodar(comando)
    P.executor.rodar = rodar

    for nome in ("salvar_memoria", "buscar_memoria", "rodar_comando", "ler_arquivo", "escrever_arquivo", "listar_arquivos"):
        f = P.registro.pegar(nome)
        if f is None:
            continue
        def embrulha(f=f, nome=nome):
            orig = f.executar
            async def executar(**kw):
                evento("ferramentas", f"ferramenta {nome}")
                return await orig(**kw)
            f.executar = executar
        embrulha()




LOOP = asyncio.new_event_loop()
threading.Thread(target=LOOP.run_forever, daemon=True).start()
asyncio.run_coroutine_threadsafe(asyncio.to_thread(lambda: None), LOOP).result()


async def _prep():
    preparar()
asyncio.run_coroutine_threadsafe(_prep(), LOOP).result()


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, code, obj):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            b = (AQUI / "chat.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b)
        elif self.path.startswith("/api/estado"):
            desde = int(self.path.split("=")[-1]) if "=" in self.path else 0
            with TRAVA:
                ev = EVENTOS[desde:]
            self._json(200, {"eventos": ev, "pendente": PENDENTE["comando"]})
        else:
            self.send_error(404)

    def do_POST(self):
        dados = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        if self.path == "/api/aprova":
            PENDENTE["resposta"] = bool(dados.get("sim"))
            PENDENTE["ev"].set()
            return self._json(200, {"ok": True})
        if self.path != "/api/msg":
            return self.send_error(404)
        if dados.get("usuario") not in DONOS:
            evento("canal", "remetente fora da lista → ignorado")
            return self._json(403, {"resposta": "Acesso negado."})
        evento("canal", "mensagem do dono (id na lista) ✓")
        t0 = time.time()
        r = asyncio.run_coroutine_threadsafe(P.agente.responder("nei", dados.get("texto", "")[:2000]), LOOP).result(600)
        evento("canal", f"resposta enviada ({time.time() - t0:.1f} s)")
        self._json(200, {"resposta": r})


if __name__ == "__main__":
    print(f"jarvis em http://127.0.0.1:{PORTA}  (home {c.home})", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORTA), H).serve_forever()
