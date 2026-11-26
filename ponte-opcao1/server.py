#!/usr/bin/env python3
"""Ponte de demonstraçêo (Opçêo 1): chat estilo Telegram -> bot -> Claude Code real (claude -p).

Roda só em 127.0.0.1. O "bot" confere o usuário (lista fixa), repassa o texto ao
`claude -p` pela assinatura, com ferramentas limitadas, e devolve a resposta + os
comandos que o Claude executou. A pasta de trabalho é uma caixa de areia (sandbox/).
Uso: python3 server.py [porta]
"""
import json, subprocess, sys, time, pathlib
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

AQUI = pathlib.Path(__file__).resolve().parent
SANDBOX = AQUI / "sandbox"
PORTA = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
AUTORIZADOS = {"nei"}  # no bot real: o ID numérico do Telegram
SESSAO = {"id": None}

REGRAS = (
    "Você é o Claude Code atendendo pelo Telegram (demonstraçêo). Responda em português do Brasil, "
    "curto (até 3 frases), sem markdown pesado. Você está na pasta sandbox/ de um servidor. "
    "Pode usar o terminal para olhar o sistema (df, ls, du, find, uptime). "
    "REGRA: antes de qualquer açêo que apaga, altera, paga ou envia algo para fora, NêO execute: "
    "diga exatamente o que faria (quantos arquivos, quanto espaço) e pergunte 'Confirma?'. "
    "Só execute depois que o usuário responder sim."
)
FERRAMENTAS = ["Bash(df:*)", "Bash(ls:*)", "Bash(du:*)", "Bash(uptime)", "Bash(find:*)", "Read"]


def chama_claude(texto):
    cmd = ["claude", "-p", texto, "--model", "haiku", "--output-format", "stream-json", "--verbose",
           "--append-system-prompt", REGRAS, "--allowedTools", *FERRAMENTAS]
    if SESSAO["id"]:
        cmd += ["--resume", SESSAO["id"]]
    t0 = time.time()
    p = subprocess.run(cmd, cwd=SANDBOX, capture_output=True, text=True, timeout=180, stdin=subprocess.DEVNULL)
    comandos, resposta = [], ""
    for linha in p.stdout.splitlines():
        try:
            ev = json.loads(linha)
        except ValueError:
            continue
        if ev.get("type") == "assistant":
            for b in ev.get("message", {}).get("content", []):
                if b.get("type") == "tool_use" and b.get("name") == "Bash":
                    comandos.append(b.get("input", {}).get("command", ""))
        if ev.get("type") == "result":
            resposta = ev.get("result", "")
            SESSAO["id"] = ev.get("session_id") or SESSAO["id"]
    if not resposta:
        resposta = "Falhou: " + (p.stderr.strip()[-300:] or "sem resposta")
    return {"resposta": resposta, "comandos": comandos, "segundos": round(time.time() - t0, 1)}


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
        elif self.path == "/reset":
            SESSAO["id"] = None
            self._json(200, {"ok": True})
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path != "/api/msg":
            return self.send_error(404)
        dados = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        if dados.get("usuario") not in AUTORIZADOS:
            return self._json(403, {"resposta": "Acesso negado.", "comandos": [], "autorizado": False})
        r = chama_claude(dados.get("texto", "")[:2000])
        r["autorizado"] = True
        self._json(200, r)


if __name__ == "__main__":
    SANDBOX.mkdir(exist_ok=True)
    print(f"ponte em http://127.0.0.1:{PORTA}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORTA), H).serve_forever()
