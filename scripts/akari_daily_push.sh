#!/bin/bash
# 阿清每日自动推送 — 每天凌晨 2:00 执行
# 将 ai-handdrawn-toolkit 仓库的变更自动 push 到 GitHub

set -e
REPO_DIR="/home/ubuntu/ai-handdrawn-toolkit"
LOG_FILE="/home/ubuntu/.hermes/cron/output/akari_daily_push.log"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

export HOME=/home/ubuntu
export PATH="/home/ubuntu/.local/bin:/usr/bin:/bin"

cd "$REPO_DIR"

# 检测是否有变更
if [[ -z $(git status --porcelain) ]]; then
    echo "[$TIMESTAMP] 无变更，跳过推送" >> "$LOG_FILE"
    exit 0
fi

# 拉取最新远程变更
git fetch origin main 2>/dev/null || true

# 添加所有变更，commit 并推送
git add -A
git commit -m "akari auto sync $(date +%Y-%m-%d)" --author="阿清 <poncianopadolcg658@gmail.com>" 2>/dev/null || true

# 用 gh token（阿清专用密钥）推送
git push origin main 2>> "$LOG_FILE" && \
  echo "[$TIMESTAMP] ✅ 推送成功 ($(git rev-parse --short HEAD))" >> "$LOG_FILE" || \
  echo "[$TIMESTAMP] ❌ 推送失败" >> "$LOG_FILE"