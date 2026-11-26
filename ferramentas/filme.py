#!/usr/bin/env python3
"""Monta um filme HyperFrames no tempo da fala do avatar.

uso: filme.py <projeto> <spec.json> <palavras.json> <duracao_total>
- lê tpl/<cena>.html, troca {{var}} pelo tempo RELATIVO ao início da cena e grava compositions/<cena>.html
- grava index.html com as cenas (data-start/data-duration) e os SFX (sem trilha: a trilha entra na mixagem final)
Expressões do spec usam as âncoras (A_*), END (duraçêo total) e ini/fim da cena.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from tempos import ancoras

proj, spec_p, pal_p, total = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
spec = json.load(open(spec_p))
A = ancoras(json.load(open(pal_p)), spec["ancoras"])
A["END"] = total
ev = lambda e, extra=None: round(float(eval(str(e), {}, {**A, **(extra or {})})), 3)

cenas_html, sfx_html = [], []
for c in spec["cenas"]:
    ini, fim = ev(c["ini"]), ev(c["fim"])
    vars_ = {k: round(ev(v, {"ini": ini, "fim": fim}) - ini, 3) for k, v in c.get("vars", {}).items()}
    for k, v in vars_.items():
        if v < 0 or v > fim - ini + 0.01:
            print(f"AVISO {c['id']}.{k} = {v} fora da cena (dur {fim-ini:.2f})")
    tpl = open(os.path.join(proj, "tpl", c["id"] + ".html")).read()
    out = re.sub(r"\{\{(\w+)\}\}", lambda m: str(vars_[m.group(1)]), tpl)
    open(os.path.join(proj, "compositions", c["id"] + ".html"), "w").write(out)
    cenas_html.append(f'      <div id="{c["id"]}" data-composition-id="{c["id"]}" data-composition-src="compositions/{c["id"]}.html" '
                      f'data-start="{ini}" data-duration="{round(fim-ini,3)}" data-track-index="1" data-track-kind="graphics" data-width="1920" data-height="1080"></div>')
    print(f"{c['id']:10s} {ini:7.2f} → {fim:7.2f}  {vars_}")
for i, s in enumerate(spec.get("sfx", [])):
    t = ev(s["t"])
    sfx_html.append(f'      <audio id="sx{i}" class="clip" src="assets/audio/{s["src"]}" data-start="{t}" data-duration="{s["dur"]}" data-track-index="{3 + i % 3}" data-volume="{s.get("vol", 0.7)}"></audio>')

html = f'''<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>{spec.get("titulo", "filme")}</title>
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: #0c0c10; }}
      #root {{ position: relative; width: 1920px; height: 1080px; overflow: hidden; }}
    </style>
  </head>
  <body>
    <!-- Gerado por tools/filme.py no tempo da fala do avatar. Canto de baixo à direita livre para o avatar (PiP). Sem whoosh (regra INEMA). -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1920" data-height="1080">
{chr(10).join(cenas_html)}
{chr(10).join(sfx_html)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
'''
open(os.path.join(proj, "index.html"), "w").write(html)
json.dump(A, open(os.path.join(proj, "ancoras.json"), "w"), indent=1)
print("index.html gravado · total", total)
