#!/bin/bash
# archive_snapshot.sh — Freeze the current edition into archive/<id>/ and append it
# to data/archive_manifest.json so it appears in the 历史存档 directory of the dashboard.
#
# Run this AFTER build_html.sh + gen_word.py have produced the current
# index.html and the two Word docs at ROOT, and BEFORE the final build_html.sh
# (so the manifest with the new edition gets baked into the fresh index.html).
#
# Usage:
#   ./scripts/archive_snapshot.sh <id> "<label>" "<type>" "<dataRange>" "<asOf>" "<summary>"
# Example:
#   ./scripts/archive_snapshot.sh 2026-07-23 "2026年7月 · 第2期" "周报" \
#     "近30天(06-24~07-23)" "2026-07-23" "本周..."
#
# id 建议格式：YYYY-MM-DD（数据截止日），保证目录名可排序、可回溯。
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="C:/Users/Savey/.qoderwork/bin/python312/python.exe"

ID="${1:?need edition id, e.g. 2026-07-23}"
LABEL="${2:-$ID}"
TYPE="${3:-月报}"
RANGE="${4:-}"
ASOF="${5:-$ID}"
SUMMARY="${6:-}"

SRC_HTML="$ROOT/index.html"
SRC_BRIEF="$ROOT/家装建材家具行业竞争情报月报_汇报稿.docx"
SRC_DETAIL="$ROOT/家装建材家具行业竞争情报月报_详报.docx"
DEST="$ROOT/archive/$ID"

mkdir -p "$DEST"
[ -f "$SRC_HTML" ]   && cp "$SRC_HTML"   "$DEST/index.html"
[ -f "$SRC_BRIEF" ]  && cp "$SRC_BRIEF"  "$DEST/汇报稿.docx"
[ -f "$SRC_DETAIL" ] && cp "$SRC_DETAIL" "$DEST/详报.docx"
echo "Snapshotted edition $ID -> $DEST"

# Append / update the edition in the manifest (idempotent by id) via python.
"$PY" - "$ROOT/data/archive_manifest.json" "$ID" "$LABEL" "$TYPE" "$RANGE" "$ASOF" "$SUMMARY" <<'PYEOF'
import json, sys, os
mf, eid, label, etype, rng, asof, summary = sys.argv[1:8]
with open(mf, encoding='utf-8') as f:
    data = json.load(f)
eds = data.setdefault('editions', [])
entry = {
    "id": eid, "label": label, "type": etype,
    "dataRange": rng, "asOf": asof, "publishDate": asof,
    "html": f"archive/{eid}/index.html",
    "brief": f"archive/{eid}/汇报稿.docx",
    "detail": f"archive/{eid}/详报.docx",
    "summary": summary, "highlights": [], "sourceStats": {}
}
# preserve existing highlights/sourceStats if re-running for same id
for i, e in enumerate(eds):
    if e.get('id') == eid:
        entry['highlights'] = e.get('highlights', [])
        entry['sourceStats'] = e.get('sourceStats', {})
        eds[i] = entry
        break
else:
    eds.append(entry)
eds.sort(key=lambda e: str(e.get('id','')), reverse=True)
data['latest'] = eds[0]['id'] if eds else eid
with open(mf, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"Manifest updated: {len(eds)} editions, latest={data['latest']}")
PYEOF

echo "Done. Re-run scripts/build_html.sh to bake the updated archive directory into index.html."
