# 快速任务模板 - 集成指南

## 集成到主Agent

在每次对话开始时，检测用户输入是否匹配快速模板：

```python
# 伪代码
def handle_user_input(text):
    # 1. 检查是否匹配快速模板
    template = match_template(text)
    
    if template:
        # 2. 执行对应模板
        return execute_template(template)
    
    # 3. 不匹配，正常处理
    return normal_handle(text)
```

## 模板执行逻辑

### 早报 (morning_report)
```javascript
sessions_spawn({
  task: `生成股市早报...
  
任务完成后发送通知：
message action=send target="user:ou_a3b690a5560dafe48a8c244c42c76bf0" text="【任务完成】早报生成：结果摘要"`
});
```

### 搜索 (search)
```javascript
kimi_search({ query: params.query });
```

### 部署 (deploy)
```javascript
sessions_spawn({
  task: `部署项目 ${params.path} 到Vercel...
  
任务完成后发送通知...`
});
```

### 状态 (status)
```javascript
sessions_list();
cron list();
// 汇总状态返回给用户
```

### 帮助 (help)
```javascript
return get_help_text();
```

## 用户交互示例

```
用户: 早报
我: 🚀 开始生成早报...
    [后台执行中]
    
用户: 搜索 最新AI新闻  
我: 🔍 搜索"最新AI新闻"...
    [返回搜索结果]
    
用户: 状态
我: 📊 当前状态：
    - 运行中任务: 2个
    - 定时任务: 1个
    - 最近完成: 早报生成
    
用户: 帮助
我: 📋 快速任务模板
    • 早报 - 生成股市早报
    • 搜索 [关键词] - 网络搜索
    • 部署 [路径] - 部署到Vercel
    • 状态 - 查看任务状态
```
