#!/bin/bash
# Rebuild index.html by inlining the JSON data files into the template.
# Usage: ./scripts/build_html.sh
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TPL="$ROOT/index.template.html"
OUT="$ROOT/index.html"
M="$ROOT/data/macro_realestate.json"
P="$ROOT/data/platform_dynamics.json"
Y="$ROOT/data/industry_policy.json"
H="$ROOT/data/v2/monthly_highlights.json"
D="$ROOT/data/sources/layerC_doudian_compass.json"
C="$ROOT/data/sources/r6_chanmama_furniture_30d.json"
J="$ROOT/data/sources/r6_juliangsuanshu_keywords.json"
S="$ROOT/data/v2/data_sources_index.json"
A="$ROOT/data/archive_manifest.json"

# Build using awk to preserve JSON content verbatim (no shell escaping of {} $)
awk -v mfile="$M" -v pfile="$P" -v yfile="$Y" -v hfile="$H" -v dfile="$D" -v cfile="$C" -v jfile="$J" -v sfile="$S" -v afile="$A" '
function readfile(f,   out,line){ out=""; while((getline line < f) > 0) out = out (out=="" ? "" : "\n") line; close(f); return out }
BEGIN{
  m = readfile(mfile)
  p = readfile(pfile)
  y = readfile(yfile)
  h = readfile(hfile)
  d = readfile(dfile)
  c = readfile(cfile)
  j = readfile(jfile)
  s = readfile(sfile)
  a = readfile(afile)
  # Escape & so gsub does not expand it to the matched text
  gsub(/&/,"\\\\&",m); gsub(/&/,"\\\\&",p); gsub(/&/,"\\\\&",y)
  gsub(/&/,"\\\\&",h); gsub(/&/,"\\\\&",d); gsub(/&/,"\\\\&",s)
  gsub(/&/,"\\\\&",c); gsub(/&/,"\\\\&",j)
  gsub(/&/,"\\\\&",a)
}
{
  gsub(/__MACRO_JSON__/, m)
  gsub(/__PLATFORM_JSON__/, p)
  gsub(/__POLICY_JSON__/, y)
  gsub(/__HIGHLIGHTS_JSON__/, h)
  gsub(/__DOUDIAN_JSON__/, d)
  gsub(/__CHANMAMA_JSON__/, c)
  gsub(/__JULIANG_JSON__/, j)
  gsub(/__SOURCES_JSON__/, s)
  gsub(/__ARCHIVE_JSON__/, a)
  print
}
' "$TPL" > "$OUT"

echo "Built $OUT ($(wc -c < "$OUT") bytes)"
