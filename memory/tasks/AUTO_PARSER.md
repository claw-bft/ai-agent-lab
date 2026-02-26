# Auto Task Parser for Feishu Messages

## Trigger Patterns

When receiving Feishu messages, check for these task indicators:

### Task Creation Patterns (Chinese)
- "帮我..." / "给我..." / "给我做..."
- "需要..." / "要..."
- "做一个..." / "生成..." / "创建..."
- "部署..." / "配置..." / "设置..."
- "分析一下..." / "研究一下..."

### Task Completion Indicators
- "完成了" / "搞定了" / "好了"
- "部署成功" / "已上线"
- "发送了" / "已回复"

### Progress Update Patterns
- "进度..." / "完成了...%"
- "正在做..." / "处理中"

## Auto-Action Rules

1. **New Task Detected** → Log to `feishu-tasks.jsonl` with status "pending"
2. **Task In Progress** → Update status to "in-progress"
3. **Task Completed** → Update status to "completed", record timestamp
4. **User Asks Status** → Reply with current task list

## Response Templates

**Task Logged:**
> ✅ 任务已记录: [任务简述] (ID: xxx)
> 当前队列: N个待处理任务

**Task Completed:**
> ✅ 任务已完成: [任务简述]
> 耗时: X分钟 | 查看: `task feishu`

**Status Query:**
> 📋 当前任务状态:
> - 进行中: X个
> - 待处理: Y个
> - 已完成: Z个
