#!/usr/bin/env python3
"""Peça animada no tempo da fala: capa → gravação da página (cenas nas âncoras) → CTA.

uso: pagina.py <pagina.html> <spec.json> <palavras.json> <total> <capa.png> <cta.png> <saida.mp4>
spec.json: {"ancoras": {...}, "inicio": "A_x", "cenas": [["A_x", "todos"], ["A_tg - 0.3", "nTg"], ...], "cta": "A_cta"}
"""
import json, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__))
from tempos import ancoras

pagina, spec_p, pal_p, total, capa, cta, saida = sys.argv[1:8]
total = float(total)
spec = json.load(open(spec_p))
A = ancoras(json.load(open(pal_p)), spec["ancoras"]); A["END"] = total
ev = lambda e: float(eval(str(e), {}, A))
ini, t_cta = ev(spec["inicio"]), ev(spec["cta"])
rot = {"dur": round(t_cta - ini, 3), "cenas": [[round(max(ev(t) - ini, 0), 3), c] for t, c in spec["cenas"]]}
tmp = tempfile.mkdtemp(prefix="pagina-", dir=os.path.dirname(os.path.abspath(saida)))
json.dump(rot, open(f"{tmp}/roteiro.json", "w"))
grav = f"{tmp}/gravacao.mp4"
subprocess.run(["node", os.path.join(os.path.dirname(__file__), "gravar-pagina.cjs"), pagina, f"{tmp}/roteiro.json", grav], check=True)
# capa (0 → início) + gravação + CTA (até o fim)
fc = (f"[0:v]scale=1920:1080,fps=30,format=yuv420p,trim=duration={ini:.3f}[a];"
      f"[1:v]fps=30,format=yuv420p,setpts=PTS-STARTPTS[b];"
      f"[2:v]scale=1920:1080,fps=30,format=yuv420p,trim=duration={total - t_cta:.3f}[c];[a][b][c]concat=n=3:v=1:a=0[v]")
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-loop", "1", "-t", f"{ini:.3f}", "-i", capa, "-i", grav,
                "-loop", "1", "-t", f"{total - t_cta:.3f}", "-i", cta, "-filter_complex", fc, "-map", "[v]",
                "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-t", f"{total:.3f}", saida], check=True)
print("gravado", saida, "início", round(ini, 2), "cta", round(t_cta, 2), "cenas", rot["cenas"])
