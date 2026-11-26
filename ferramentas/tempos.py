#!/usr/bin/env python3
"""Casa a fala do avatar com as cenas.

palavras.json = [{"w": "Você", "ini": 0.12, "fim": 0.40}, ...] (Whisper com tempo por palavra)
spec.json     = {"ancoras": {"A_msg": "Você manda", ...}, ...}   (frases, na ordem em que sêo faladas)

ancoras(palavras, frases) -> {"A_msg": 3.21, ...}  (início da 1ª palavra de cada frase)
A busca anda só para frente, entêo frases repetidas casam na ordem certa.
"""
import json, re, sys, unicodedata


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


NUM = {"um": "1", "dois": "2", "tres": "3", "quatro": "4", "cinco": "5", "seis": "6", "sete": "7", "oito": "8",
       "nove": "9", "dez": "10", "doze": "12", "trinta": "30"}


def igual(a, b):
    """Palavra falada x palavra do texto, tolerando o Whisper ('Cloud' por 'Claude', '12' por 'doze')."""
    if a == b or NUM.get(a) == b or NUM.get(b) == a:
        return True
    from difflib import SequenceMatcher
    return min(len(a), len(b)) >= 4 and SequenceMatcher(None, a, b).ratio() >= 0.72


def ancoras(palavras, frases):
    # o Whisper às vezes junta palavras numa só ("inema.club") ou separa; a busca é por palavra normalizada
    ws = []
    idx = []
    for n, p in enumerate(palavras):
        for parte in norm(p["w"]).split():
            ws.append(parte); idx.append(n)
    out, pos = {}, 0
    for nome, frase in frases.items():
        alvo = norm(frase).split()
        achou = None
        for i in range(pos, len(ws)):
            ok = True
            for k, a in enumerate(alvo):
                if i + k >= len(ws) or not igual(ws[i + k], a):
                    ok = False
                    break
            if ok:
                achou = i
                break
        if achou is None:   # tolerância: 1ª palavra que bate o começo da frase
            raise SystemExit(f"âncora nêo achada: {nome} = '{frase}' (a partir da palavra {pos}: {' '.join(ws[pos:pos+12])})")
        out[nome] = round(palavras[idx[achou]]["ini"], 3)
        pos = achou + 1
    return out


if __name__ == "__main__":
    pal = json.load(open(sys.argv[1]))
    spec = json.load(open(sys.argv[2]))
    print(json.dumps(ancoras(pal, spec["ancoras"]), indent=1, ensure_ascii=False))
