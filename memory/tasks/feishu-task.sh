#!/bin/bash
# Feishu Task Tracker - Auto-log tasks from Feishu conversations

TASK_DIR="/root/.openclaw/workspace/memory/tasks"
FEISHU_TASKS="$TASK_DIR/feishu-tasks.jsonl"

touch "$FEISHU_TASKS"

# Log a task from Feishu conversation
log_task() {
    local source="$1"      # feishu group ID or user
    local sender="$2"      # sender name/ID
    local content="$3"     # task description
    local context="$4"     # conversation context
    local id=$(cat /proc/sys/kernel/random/uuid 2>/dev/null || echo "$(date +%s)-$$")
    local now=$(date -Iseconds)
    
    local json="{\"id\":\"$id\",\"source\":\"$source\",\"sender\":\"$sender\",\"content\":\"$content\",\"context\":\"$context\",\"status\":\"logged\",\"created\":\"$now\",\"updated\":\"$now\",\"progress\":0,\"notes\":[]}"
    echo "$json" >> "$FEISHU_TASKS"
    echo "✓ Feishu task logged: $id"
}

# Update task status from Feishu
update_task() {
    local task_id="$1"
    local status="$2"      # in-progress|blocked|completed|cancelled
    local note="$3"
    local now=$(date -Iseconds)
    
    local temp_file=$(mktemp)
    while IFS= read -r line; do
        local id=$(echo "$line" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
        if [[ "$id" == *"$task_id"* ]]; then
            local updated=$(echo "$line" | sed "s/\"status\":\"[^\"]*\"/\"status\":\"$status\"/" | sed "s/\"updated\":\"[^\"]*\"/\"updated\":\"$now\"/")
            echo "$updated" >> "$temp_file"
            echo "✓ Task $id updated: $status"
        else
            echo "$line" >> "$temp_file"
        fi
    done < "$FEISHU_TASKS"
    mv "$temp_file" "$FEISHU_TASKS"
}

# List all Feishu tasks
list_tasks() {
    echo "## Feishu Tasks"
    if [ ! -s "$FEISHU_TASKS" ]; then
        echo "No Feishu tasks recorded."
        return
    fi
    
    local i=1
    while IFS= read -r line; do
        local id=$(echo "$line" | grep -o '"id":"[^"]*"' | cut -d'"' -f4 | cut -c1-8)
        local content=$(echo "$line" | grep -o '"content":"[^"]*"' | cut -d'"' -f4)
        local status=$(echo "$line" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
        local sender=$(echo "$line" | grep -o '"sender":"[^"]*"' | cut -d'"' -f4)
        local progress=$(echo "$line" | grep -o '"progress":[0-9]*' | cut -d':' -f2)
        
        local icon="📝"
        case "$status" in
            "in-progress") icon="🔄" ;;
            "blocked") icon="🚫" ;;
            "completed") icon="✅" ;;
            "cancelled") icon="❌" ;;
        esac
        
        printf "%s %d. %s (%s) [%s, %d%%]\n" "$icon" "$i" "$content" "$sender" "$id" "$progress"
        i=$((i+1))
    done < "$FEISHU_TASKS"
}

case "$1" in
    log) shift; log_task "$@" ;;
    update) shift; update_task "$@" ;;
    list) list_tasks ;;
    *) echo "Usage: feishu-task [log|update|list] ..." ;;
esac
