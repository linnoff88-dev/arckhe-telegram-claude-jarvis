#!/usr/bin/env python3
"""Monta os 6 vídeos narrados quando o avatar existe: transcriçêo → visual no tempo da fala → avatar + voz + trilha.

uso: montar.py <id> [<id>...]   ids: 1a 2a 3a 1b 2b 3b   (ou "todos")
Saída: entrega/<id>.mp4 + entrega/<id>.json (âncoras, t_meia, duraçêo)
"""
import json, os, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(R, "tools")
sys.path.insert(0, T)
from tempos import ancoras

FALA = {"1a": "1a-motionlab", "2a": "2a-filme", "3a": "3a-real", "1b": "1b-motionlab", "2b": "2b-filme", "3b": "3b-real"}
VIS = {
    "1a": ("pagina", "demo1-motion-lab/index.html", "montagem/spec-1a.json", "capa-1a.png", "cta-a.png", "A_quatro", "dir"),
    "1b": ("pagina", "demo1b-motion-lab/index.html", "montagem/spec-1b.json", "capa-1b.png", "cta-b.png", "A_oito", "dir"),
    "2a": ("filme", "demo2a-filme", "demo2a-filme/spec.json", None, None, "A_msg", "dir"),
    "2b": ("filme", "demo2b-filme", "demo2b-filme/spec.json", None, None, "A_antes", "dir"),
    "3a": ("stop", "capt-3a3", "montagem/spec-3a.json", "capa-3a.png", "cta-a.png", "A_eu", "esq"),
    "3b": ("stop", "capt-3b4", "montagem/spec-3b.json", "capa-3b.png", "cta-b.png", "A_peco", "esq"),
}
run = lambda *c, **k: subprocess.run(list(c), check=True, cwd=k.get("cwd", R))


def palavras(i):
    av = f"{R}/falas/avatar/{FALA[i]}.mp4"
    out = f"{R}/montagem/{i}/palavras.json"
    if os.path.exists(out):
        return out
    td = f"{R}/montagem/{i}/transcricao"
    os.makedirs(td, exist_ok=True)
    run(os.path.expanduser("~/projetos/wifi/scripts/fila-vaga"), "gpu", f"tcj-whisper-{i}", "--",
        os.path.expanduser("~/projetos/inemavox/venv/bin/python"), "transcrever_v1.py", "--in", av, "--outdir", td,
        "--whisper-model", "large-v3", "--src", "pt", "--words", cwd=os.path.expanduser("~/projetos/inemavox"))
    ws = json.load(open(f"{td}/words.json"))
    json.dump([{"w": w["word"], "ini": w["start"], "fim": w["end"]} for w in ws], open(out, "w"), ensure_ascii=False, indent=0)
    return out


def montar(i):
    os.makedirs(f"{R}/montagem/{i}", exist_ok=True); os.makedirs(f"{R}/entrega", exist_ok=True)
    av = f"{R}/falas/avatar/{FALA[i]}.mp4"
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", av]).decode())
    pal = palavras(i)
    tipo, fonte, spec, capa, cta, a_meia, canto = VIS[i]
    A = ancoras(json.load(open(pal)), json.load(open(f"{R}/{spec}"))["ancoras"])
    vis = f"{R}/montagem/{i}/visual.mp4"
    C = f"{R}/montagem/capas"
    if tipo == "pagina":
        run("python3", f"{T}/pagina.py", fonte, spec, pal, f"{dur:.3f}", f"{C}/{capa}", f"{C}/{cta}", vis)
    elif tipo == "stop":
        run("python3", f"{T}/stopmotion.py", fonte, spec, pal, f"{dur:.3f}", f"{C}/{capa}", f"{C}/{cta}", vis)
    else:
        run("python3", f"{T}/filme.py", fonte, spec, pal, f"{dur:.3f}")
        run("npx", "--yes", "hyperframes@0.8.77", "check", cwd=f"{R}/{fonte}")
        run(os.path.expanduser("~/projetos/wifi/scripts/fila-vaga"), "render", f"tcj-render-{i}", "--",
            "npx", "--yes", "hyperframes@0.8.77", "render", "-o", vis, "-q", "looks", "--quiet", cwd=f"{R}/{fonte}")
    final = f"{R}/entrega/{i}.mp4"
    run("python3", f"{T}/compor.py", vis, av, f"{A[a_meia]:.3f}", canto, final)
    json.dump({"id": i, "dur": round(dur, 2), "t_meia": A[a_meia], "ancoras": A}, open(f"{R}/entrega/{i}.json", "w"), indent=1)
    print(f"Terminei: {i} → {final} ({dur:.1f} s)", flush=True)


ids = list(FALA) if sys.argv[1:] == ["todos"] else sys.argv[1:]
for i in ids:
    if not os.path.exists(f"{R}/falas/avatar/{FALA[i]}.mp4"):
        print(f"sem avatar ainda: {i}"); continue
    montar(i)
