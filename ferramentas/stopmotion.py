#!/usr/bin/env python3
"""Quadros capturados (frames.json) viram vídeo no tempo da fala.

uso: stopmotion.py <pasta-quadros> <spec.json> <palavras.json> <total> <capa.png> <cta.png> <saida.mp4>
spec.json: {"ancoras": {...frases...}, "marcas": {"m1-legenda": "A_eu", ...}, "cta": "A_cta"}
- capa de 0 até a 1ª marca; cada marca cai no tempo da sua âncora; os quadros entre duas marcas
  se espalham por igual (a digitaçêo acompanha a fala); o último quadro segura até o CTA.
"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from tempos import ancoras

pasta, spec_p, pal_p, total, capa, cta, saida = sys.argv[1:8]
total = float(total)
spec = json.load(open(spec_p))
A = ancoras(json.load(open(pal_p)), spec["ancoras"]); A["END"] = total
ev = lambda e: float(eval(str(e), {}, A))
q = json.load(open(os.path.join(pasta, "frames.json")))["quadros"]
idx = {f["marca"]: i for i, f in enumerate(q) if f["marca"]}
fixos = sorted((idx[m], ev(e)) for m, e in spec["marcas"].items())
t_cta = ev(spec["cta"])
tempos = {}
for (i, ti), (j, tj) in zip(fixos, fixos[1:]):
    if tj <= ti:
        raise SystemExit(f"marcas fora de ordem: {q[i]['marca']}@{ti} → {q[j]['marca']}@{tj}")
    for k in range(i, j):
        tempos[k] = ti + (tj - ti) * (k - i) / (j - i)
ultimo_i, ultimo_t = fixos[-1]
# depois da última marca: os quadros que sobram andam a 0,4 s cada e o último segura
for n, k in enumerate(range(ultimo_i, len(q))):
    tempos[k] = min(ultimo_t + 0.4 * n, t_cta - 0.05)
lista = os.path.join(os.path.dirname(os.path.abspath(saida)), os.path.basename(saida) + ".txt")
linhas = [f"file '{os.path.abspath(capa)}'", f"duration {fixos[0][1]:.3f}"]
ks = sorted(tempos)
for a, b in zip(ks, ks[1:] + [None]):
    fim = tempos[b] if b is not None else t_cta
    d = max(fim - tempos[a], 0.0)
    if d < 0.001:
        continue
    linhas += [f"file '{os.path.abspath(os.path.join(pasta, q[a]['f']))}'", f"duration {d:.3f}"]
linhas += [f"file '{os.path.abspath(cta)}'", f"duration {total - t_cta:.3f}", f"file '{os.path.abspath(cta)}'"]
open(lista, "w").write("\n".join(linhas) + "\n")
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista,
                "-vf", "scale=1920:1080:flags=lanczos,fps=30,format=yuv420p", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                "-t", f"{total:.3f}", saida], check=True)
print("gravado", saida, {m: round(ev(e), 2) for m, e in spec["marcas"].items()}, "cta", round(t_cta, 2))
