#!/bin/bash
# Rebuild index.html by inlining the 3 JSON data files into the template.
# Usage: ./scripts/build_html.sh
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TPL="$ROOT/index.template.html"
OUT="$ROOT/index.html"
M="$ROOT/data/macro_realestate.json"
P="$ROOT/data/platform_dynamics.json"
Y="$ROOT/data/industry_policy.json"

# Build using awk to preserve JSON content verbatim (no shell escaping of {} $)
awk -v mfile="$M" -v pfile="$P" -v yfile="$Y" '
function readfile(f,   out,line){ out=""; while((getline line < f) > 0) out = out (out=="" ? "" : "\n") line; close(f); return out }
BEGIN{
  m = readfile(mfile)
  p = readfile(pfile)
  y = readfile(yfile)
}
{
  gsub(/__MACRO_JSON__/, m)
  gsub(/__PLATFORM_JSON__/, p)
  gsub(/__POLICY_JSON__/, y)
  print
}
' "$TPL" > "$OUT"

echo "Built $OUT ($(wc -c < "$OUT") bytes)"
