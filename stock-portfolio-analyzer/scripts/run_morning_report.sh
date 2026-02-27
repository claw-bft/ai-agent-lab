#!/bin/bash
# 早报任务执行脚本 - 带重试机制

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
TASK_FILE="${1:-$HOME/.openclaw/shared/incoming/morning_task.json}"
MAX_RETRIES=5
RETRY_DELAY=15

echo "🚀 启动早报任务执行..."
echo "📄 任务文件: $TASK_FILE"
echo ""

# 检查任务文件
if [ ! -f "$TASK_FILE" ]; then
    echo "❌ 错误: 任务文件不存在: $TASK_FILE"
    exit 1
fi

# 检查 VERCEL_TOKEN
if [ -z "${VERCEL_TOKEN:-}" ]; then
    echo "⚠️ 警告: VERCEL_TOKEN 未设置，尝试从 ~/.bashrc 加载"
    if [ -f "$HOME/.bashrc" ]; then
        export VERCEL_TOKEN=$(grep "VERCEL_TOKEN" "$HOME/.bashrc" | grep "export" | cut -d'"' -f2 | head -1)
    fi
fi

if [ -z "${VERCEL_TOKEN:-}" ]; then
    echo "❌ 错误: VERCEL_TOKEN 无法获取"
    exit 1
fi

echo "✅ 环境检查通过"
echo ""

# 执行早报任务（带重试）
attempt=1
success=false

while [ $attempt -le $MAX_RETRIES ] && [ "$success" = false ]; do
    echo "🔄 执行尝试 $attempt/$MAX_RETRIES..."
    
    if python3 "$SKILL_DIR/stock-analyzer.py" morning-report --task-file "$TASK_FILE" --json 2>&1; then
        success=true
        echo ""
        echo "✅ 早报任务执行成功！"
    else
        echo "⚠️ 尝试 $attempt 失败"
        if [ $attempt -lt $MAX_RETRIES ]; then
            echo "⏱️ 等待 ${RETRY_DELAY}秒后重试..."
            sleep $RETRY_DELAY
        fi
    fi
    
    attempt=$((attempt + 1))
done

if [ "$success" = false ]; then
    echo ""
    echo "❌ 早报任务执行失败，已重试 $MAX_RETRIES 次"
    exit 1
fi

# 输出任务状态
echo ""
echo "📊 任务状态摘要:"
python3 -c "
import json
import sys

try:
    with open('$TASK_FILE', 'r', encoding='utf-8') as f:
        config = json.load(f)
    print(f\"  任务ID: {config.get('task_id', 'N/A')}\")
    print(f\"  任务名称: {config.get('task_name', 'N/A')}\")
    print(f\"  上次运行: {config.get('last_run', 'N/A')}\")
    print(f\"  上次状态: {config.get('last_status', 'N/A')}\")
    if config.get('last_report_url'):
        print(f\"  报告链接: {config['last_report_url']}\")
except Exception as e:
    print(f\"  读取任务状态失败: {e}\")
    sys.exit(1)
"

echo ""
echo "🎉 早报任务执行完成！"
