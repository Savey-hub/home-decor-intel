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

# ---- Commit + Publish ----
# 根因修复(2026-08-12)：本环境 github.com:443 被阻断，`git push origin main` 必然失败；
# 叠加脚本顶部 set -e，push 一失败就整体中断 → 每周刷新的数据烂在本地、线上看板长期陈旧
# (08-06 那期就是这样积压了13个未提交文件)。现改为：先本地 commit，再走 api.github.com
# 的 Data API 推送(scripts/api_push.py)，并强制校验 PUSH_OK 标记。
cd "$ROOT"
PY="C:/Users/Savey/.qoderwork/bin/python312/python.exe"

git add -A
if git diff --cached --quiet; then
  echo "[$STAMP] no diff to commit"
else
  git -c user.email=intel@local -c user.name=IntelBot commit -m "chore: weekly refresh $STAMP" >/dev/null
  echo "[$STAMP] local commit created"
fi

# 发布(不因失败而中断，改为显式告警，便于 cron agent 捕获并通知用户)
PUSHLOG="$ROOT/_push_last.log"
set +e
"$PY" "$ROOT/scripts/api_push.py" >"$PUSHLOG" 2>&1
PUSH_RC=$?
set -e
if grep -q "PUSH_OK" "$PUSHLOG"; then
  echo "[$STAMP] PUBLISH_OK $(grep -o 'PUSH_OK.*' "$PUSHLOG" | tail -1)"
elif grep -q "NOTHING_TO_PUSH" "$PUSHLOG"; then
  echo "[$STAMP] PUBLISH_SKIPPED 无待发布差异"
else
  echo "[$STAMP] PUBLISH_FAILED rc=$PUSH_RC —— 线上看板未更新，请检查 token/网络。日志尾部："
  tail -15 "$PUSHLOG"
  echo "[$STAMP] 注意：本地 commit 已保留，修好后重跑 scripts/api_push.py 即可补发。"
fi

echo "[$STAMP] weekly_refresh done"
