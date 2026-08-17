#!/usr/bin/env bash
# Todas las pruebas. Se corre antes de cada push.
#
#     bash 07_APP/pruebas/correr.sh
set -u
cd "$(dirname "$0")/../.."
fallos=0

echo "── Tubería de contenido ──"
python3 07_APP/pruebas/test_tuberia.py 2>&1 | tail -3 || fallos=1
python3 07_APP/pruebas/test_tuberia.py >/dev/null 2>&1 || fallos=1

echo
echo "── Estado de la app ──"
node 07_APP/pruebas/test_almacen.mjs || fallos=1

echo
echo "── Sintaxis del navegador ──"
tmp=$(mktemp -d)
for f in docs/js/*.js docs/sw.js; do
  cp "$f" "$tmp/m.mjs"
  if node --check "$tmp/m.mjs" 2>/dev/null; then
    echo "  ok    $f"
  else
    echo "  FALLA $f"; fallos=1
  fi
done
rm -rf "$tmp"

echo
echo "── Datos publicados ──"
python3 - <<'PY' || fallos=1
import json, sys
from pathlib import Path
d = Path("docs/contenido")
try:
    man = json.loads((d / "manifiesto.json").read_text())
    json.loads((d / "cronograma.json").read_text())
    faltan = [t["archivo"] for t in man["tandas"] if not (d / t["archivo"]).exists()]
    if faltan:
        print(f"  FALLA faltan tandas: {faltan}"); sys.exit(1)
    print(f"  ok    manifiesto, cronograma y {len(man['tandas'])} tandas")
    if man.get("cifrado"):
        print("  ok    contenido cifrado")
    else:
        print("  AVISO contenido sin cifrar: no publicar"); sys.exit(1)
except Exception as e:
    print(f"  FALLA {e}"); sys.exit(1)
PY

echo
if [ "$fallos" -ne 0 ]; then echo "HAY FALLOS — no publicar"; exit 1; fi
echo "Todo en verde"
