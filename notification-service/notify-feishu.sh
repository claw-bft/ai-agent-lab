#!/bin/bash
# 发送飞书通知
# 用法: ./notify-feishu.sh "消息内容"

MESSAGE="${1:-任务完成通知}"
TARGET="${2:-user:ou_a3b690a5560dafe48a8c244c42c76bf0}"

# 使用 openclaw message 命令发送
# 注意：需要在OpenClaw环境中运行

echo "[$(date '+%H:%M:%S')] 发送通知: $MESSAGE"

# 记录到通知日志
echo "$(date -Iseconds) | $TARGET | $MESSAGE" >> /root/.openclaw/shared/notifications/history.log

# 实际发送需要通过OpenClaw的message工具
# 这里作为占位符，后续集成到子任务中
