#!/bin/bash
# Cria a caixa de areia da demonstração: 12 logs antigos (mais de 30 dias, ~4,6 MB) e 9 recentes.
# O Claude só trabalha dentro de sandbox/. Rode de novo para repetir a demo do "apaga os logs".
cd "$(dirname "$0")" && mkdir -p sandbox/logs && cd sandbox/logs
for i in $(seq 1 12); do f=$(date -d "-$((70 - i)) days" +app-%Y-%m-%d.log); head -c 400000 /dev/zero | tr '\0' 'x' > "$f"; touch -d "-$((70 - i)) days" "$f"; done
for i in $(seq 1 9); do f=$(date -d "-$i days" +app-%Y-%m-%d.log); echo ok > "$f"; touch -d "-$i days" "$f"; done
echo "logs: $(ls | wc -l) ($(find . -type f -mtime +30 | wc -l) com mais de 30 dias)"
