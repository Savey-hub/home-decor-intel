#!/bin/bash
# 每周四 11:00 由 qoder_cron 触发的刷新入口。
# 逻辑：
#   1) 由 agent 侧完成对 3 份 JSON 的抓取/更新（cron payload.message 会驱动）；
#   2) 本脚本负责重新 build 出 index.html，并把最新版拷到 outputs/；
#   3) 若已配 GitHub 远端，则自动 push（首版先保留 offline，下周接远端）。
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAMP="$(date '+%Y-%m-%d %H:%M')"

echo "[$STAMP] weekly_refresh start"

# Rebuild HTML
bash "$ROOT/scripts/build_html.sh"

# Copy to outputs (user-visible)
OUTDIR="$(cd "$ROOT/.." && pwd)/outputs/home-decor-intel"
mkdir -p "$OUTDIR"
cp "$ROOT/index.html" "$OUTDIR/index.html"
echo "[$STAMP] copied to $OUTDIR/index.html"

# Optional git commit + push (only if remote origin is configured)
cd "$ROOT"
if git remote get-url origin >/dev/null 2>&1; then
  git add -A
  if ! git diff --cached --quiet; then
    git -c user.email=intel@local -c user.name=IntelBot commit -m "chore: weekly refresh $STAMP" >/dev/null
    git push origin main
    echo "[$STAMP] pushed to origin"
  else
    echo "[$STAMP] no diff to commit"
  fi
else
  # Local-only commit (no remote yet — GitHub Pages 迁移下周做)
  git add -A
  if ! git diff --cached --quiet; then
    git -c user.email=intel@local -c user.name=IntelBot commit -m "chore: weekly refresh $STAMP" >/dev/null
    echo "[$STAMP] local commit only (no remote configured yet)"
  fi
fi

echo "[$STAMP] weekly_refresh done"
