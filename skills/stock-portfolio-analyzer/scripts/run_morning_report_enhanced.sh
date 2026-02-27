#!/bin/bash
# Enhanced Morning Report Runner - 增强版早报任务执行脚本
# 带重试机制、状态监控和告警

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
SHARED_DIR="/root/.openclaw/shared"
LOGS_DIR="$SHARED_DIR/logs"

# 确保日志目录存在
mkdir -p "$LOGS_DIR"

# 日志函数
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message"
    echo "[$timestamp] [$level] $message" >> "$LOGS_DIR/morning-report-$(date +%Y%m%d).log"
}

# 发送飞书通知 (如果配置了webhook)
send_feishu_notification() {
    local title="$1"
    local content="$2"
    
    # 记录到日志
    log "INFO" "通知: $title"
    log "INFO" "内容: $content"
    
    # 如果有飞书webhook配置，可以取消注释以下代码
    # local webhook_url="${FEISHU_WEBHOOK_URL:-}"
    # if [ -n "$webhook_url" ]; then
    #     curl -s -X POST "$webhook_url" \
    #         -H 'Content-Type: application/json' \
    #         -d "{\"msg_type\":\"text\",\"content\":{\"text\":\"$title\n$content\"}}" > /dev/null 2>&1
    # fi
}

# 执行任务
run_task() {
    local attempt=$1
    log "INFO" "===== 早报任务执行 (尝试 $attempt/$MAX_RETRIES) ====="
    
    cd "$SKILL_DIR"
    
    # 检查环境
    if ! command -v python3 &> /dev/null; then
        log "ERROR" "Python3 未安装"
        return 1
    fi
    
    # 检查VERCEL_TOKEN
    if [ -z "$VERCEL_TOKEN" ]; then
        # 尝试从.bashrc加载
        if [ -f "$HOME/.bashrc" ]; then
            export VERCEL_TOKEN=$(grep "VERCEL_TOKEN" "$HOME/.bashrc" | grep export | cut -d'"' -f2)
        fi
    fi
    
    if [ -z "$VERCEL_TOKEN" ]; then
        log "WARN" "VERCEL_TOKEN 未设置，部署可能失败"
    else
        log "INFO" "VERCEL_TOKEN 已配置"
    fi
    
    # 检查任务文件
    local task_file="${TASK_FILE:-$SHARED_DIR/incoming/morning_task.json}"
    if [ ! -f "$task_file" ]; then
        log "ERROR" "任务文件不存在: $task_file"
        return 1
    fi
    
    log "INFO" "任务文件: $task_file"
    
    # 执行任务
    local output_file="$LOGS_DIR/morning-output-$(date +%Y%m%d-%H%M%S).json"
    
    if python3 "$SKILL_DIR/task_executor.py" morning-report --max-retries 1 > "$output_file" 2>&1; then
        log "INFO" "✅ 任务执行成功"
        
        # 提取报告URL
        local report_url=$(grep -o 'https://[^"]*vercel[^"]*' "$output_file" | head -1)
        if [ -n "$report_url" ]; then
            log "INFO" "报告链接: $report_url"
            send_feishu_notification "✅ 股市早报生成成功" "报告链接: $report_url"
        fi
        
        return 0
    else
        log "ERROR" "❌ 任务执行失败"
        log "ERROR" "输出: $(cat $output_file)"
        return 1
    fi
}

# 主函数
main() {
    MAX_RETRIES="${MAX_RETRIES:-5}"
    RETRY_DELAY="${RETRY_DELAY:-15}"
    TASK_FILE="${1:-}"
    
    log "INFO" "=========================================="
    log "INFO" "启动早报任务执行器"
    log "INFO" "最大重试次数: $MAX_RETRIES"
    log "INFO" "重试间隔: ${RETRY_DELAY}秒"
    log "INFO" "=========================================="
    
    local success=0
    
    for attempt in $(seq 1 $MAX_RETRIES); do
        if run_task $attempt; then
            success=1
            break
        fi
        
        if [ $attempt -lt $MAX_RETRIES ]; then
            log "INFO" "等待 ${RETRY_DELAY} 秒后重试..."
            sleep $RETRY_DELAY
        fi
    done
    
    if [ $success -eq 1 ]; then
        log "INFO" "✅ 早报任务最终成功"
        exit 0
    else
        log "ERROR" "❌ 早报任务最终失败，已尝试 $MAX_RETRIES 次"
        send_feishu_notification "❌ 股市早报生成失败" "已尝试 $MAX_RETRIES 次，请检查日志: $LOGS_DIR"
        exit 1
    fi
}

# 运行主函数
main "$@"
