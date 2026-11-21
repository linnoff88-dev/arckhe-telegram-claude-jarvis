#!/usr/bin/env python3
"""Junta o visual (sem voz) com o avatar do Nei: meia tela à direita na capa (até t_meia), depois PiP no canto.

uso: compor.py <visual.mp4> <avatar.mp4> <t_meia> <canto: dir|esq> <saida.mp4> [--crop X,Y,L] [--vol-visual 0.7]
- áudio: voz do avatar + trilha do kit em volume baixo (com fade no fim) + o som do visual, se houver (SFX dos filmes)
- avatar nunca em tela cheia (D8): meia tela no máximo, depois PiP de 360 px com borda amarela
"""
import argparse, json, os, subprocess, tempfile
from PIL import Image, ImageDraw

ap = argparse.ArgumentParser()
ap.add_argument("visual"); ap.add_argument("avatar"); ap.add_argument("t_meia", type=float)
ap.add_argument("canto", choices=["dir", "esq"]); ap.add_argument("saida")
ap.add_argument("--crop", default="600,40,720", help="recorte quadrado do rosto no avatar 1920x1080: x,y,lado")
ap.add_argument("--meia-x", type=int, default=480, help="x do recorte 960x1080 da meia tela")
ap.add_argument("--vol-visual", type=float, default=0.7)
ap.add_argument("--vol-trilha", type=float, default=0.10)
a = ap.parse_args()
AQUI = os.path.dirname(os.path.abspath(__file__))
TRILHA = os.path.join(AQUI, "..", "filmes", "opcao1", "assets", "audio", "trilha.wav")

dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.avatar]).decode())
tem_audio_visual = bool(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", a.visual]).strip())

P, R, B = 360, 40, 6                       # PiP: lado, raio, borda
X = 1530 if a.canto == "dir" else 30
Y = 690
tmp = tempfile.mkdtemp(prefix="compor-")
m = Image.new("L", (P, P), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, P - 1, P - 1], R, fill=255); m.save(f"{tmp}/mask.png")
bd = Image.new("RGBA", (P + 2 * B, P + 2 * B), (0, 0, 0, 0))
ImageDraw.Draw(bd).rounded_rectangle([0, 0, P + 2 * B - 1, P + 2 * B - 1], R + B, outline=(250, 204, 21, 255), width=B)
bd.save(f"{tmp}/borda.png")
cx, cy, cl = map(int, a.crop.split(","))
T = a.t_meia

fc = (
    f"[1:v]split=2[av1][av2];"
    f"[av1]crop=960:1080:{a.meia_x}:0[meia];"
    f"[av2]crop={cl}:{cl}:{cx}:{cy},scale={P}:{P},format=rgba[pq];[pq][4:v]alphamerge[pip];"
    f"[0:v]scale=1920:1080,fps=30,format=yuv420p,tpad=stop_mode=clone:stop_duration=30[base];"
    f"[base][meia]overlay=960:0:enable='lt(t,{T})'[v1];"
    f"[v1][5:v]overlay={X - B}:{Y - B}:enable='gte(t,{T})'[v2];"
    f"[v2][pip]overlay={X}:{Y}:enable='gte(t,{T})',format=yuv420p[vout];"
    f"[1:a]volume=1.0[voz];"
    f"[2:a]atrim=0:{dur:.3f},volume={a.vol_trilha},afade=t=out:st={max(dur - 2.5, 0):.3f}:d=2.5[tri];"
)
mix = "[voz][tri]"
n = 2
if tem_audio_visual:
    fc += f"[0:a]volume={a.vol_visual},apad[sfx];"
    mix += "[sfx]"; n = 3
fc += f"{mix}amix=inputs={n}:normalize=0:duration=first,loudnorm=I=-16:TP=-1.5:LRA=11[aout]"
cmd = ["ffmpeg", "-loglevel", "error", "-y", "-i", a.visual, "-i", a.avatar, "-stream_loop", "-1", "-i", TRILHA,
       "-f", "lavfi", "-i", "anullsrc", "-loop", "1", "-i", f"{tmp}/mask.png", "-loop", "1", "-i", f"{tmp}/borda.png",
       "-filter_complex", fc, "-map", "[vout]", "-map", "[aout]", "-t", f"{dur:.3f}",
       "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", a.saida]
subprocess.run(cmd, check=True)
print(json.dumps({"saida": a.saida, "dur": round(dur, 2), "t_meia": T, "canto": a.canto, "sfx_do_visual": tem_audio_visual}))
