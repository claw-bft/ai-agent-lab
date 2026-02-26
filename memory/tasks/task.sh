#!/bin/bash
# Task Manager CLI for Kimi Claw

TASK_DIR="/root/.openclaw/workspace/memory/tasks"
ACTIVE_FILE="$TASK_DIR/active.jsonl"
COMPLETED_FILE="$TASK_DIR/completed.jsonl"
INDEX_FILE="$TASK_DIR/index.md"

touch "$ACTIVE_FILE" "$COMPLETED_FILE"

gen_uuid() {
    cat /proc/sys/kernel/random/uuid 2>/dev/null || echo "$(date +%s)-$$"
}

cmd_add() {
    local title="$1"
    local priority="${2:-medium}"
    local id=$(gen_uuid)
    local now=$(date -Iseconds)
    local json="{\"id\":\"$id\",\"title\":\"$title\",\"status\":\"pending\",\"priority\":\"$priority\",\"created\":\"$now\",\"updated\":\"$now\",\"progress\":0}"
    echo "$json" >> "$ACTIVE_FILE"
    echo "✓ Task added: $id"
}

cmd_list() {
    echo "## Active Tasks"
    if [ ! -s "$ACTIVE_FILE" ]; then
        echo "No active tasks."
        return
    fi
    local i=1
    while IFS= read -r line; do
        local id=$(echo "$line" | grep -o '"id":"[^"]*"' | cut -d'"' -f4 | cut -c1-8)
        local title=$(echo "$line" | grep -o '"title":"[^"]*"' | cut -d'"' -f4)
        local priority=$(echo "$line" | grep -o '"priority":"[^"]*"' | cut -d'"' -f4)
        local progress=$(echo "$line" | grep -o '"progress":[0-9]*' | cut -d':' -f2)
        printf "%d. [%s] %s (%s, %d%%)\n" "$i" "$priority" "$title" "$id" "$progress"
        i=$((i+1))
    done < "$ACTIVE_FILE"
}

cmd_done() {
    local search="$1"
    local now=$(date -Iseconds)
    local temp_file=$(mktemp)
    local found=false
    while IFS= read -r line; do
        local id=$(echo "$line" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
        if [[ "$id" == *"$search"* ]]; then
            local updated=$(echo "$line" | sed "s/\"status\":\"[^\"]*\"/\"status\":\"completed\"/" | sed "s/\"progress\":[0-9]*/\"progress\":100/")
            echo "$updated" >> "$COMPLETED_FILE"
            echo "✓ Task completed: $id"
            found=true
        else
            echo "$line" >> "$temp_file"
        fi
    done < "$ACTIVE_FILE"
    mv "$temp_file" "$ACTIVE_FILE"
    [ "$found" = false ] && echo "Task not found: $search"
}

cmd_progress() {
    local search="$1"
    local progress="$2"
    local temp_file=$(mktemp)
    while IFS= read -r line; do
        local id=$(echo "$line" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
        if [[ "$id" == *"$search"* ]]; then
            local updated=$(echo "$line" | sed "s/\"progress\":[0-9]*/\"progress\":$progress/")
            [ "$progress" -gt 0 ] && updated=$(echo "$updated" | sed 's/"status":"pending"/"status":"in-progress"/')
            echo "$updated" >> "$temp_file"
            echo "✓ Progress: $id -> $progress%"
        else
            echo "$line" >> "$temp_file"
        fi
    done < "$ACTIVE_FILE"
    mv "$temp_file" "$ACTIVE_FILE"
}

case "$1" in
    add) shift; cmd_add "$@" ;;
    list) cmd_list ;;
    done) shift; cmd_done "$@" ;;
    progress) shift; cmd_progress "$@" ;;
    feishu) bash "$TASK_DIR/feishu-task.sh" list ;;
    *) echo "Usage: task [add|list|done|progress|feishu] ..." ;;
esac
