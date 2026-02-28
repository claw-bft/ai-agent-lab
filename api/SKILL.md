---
name: api
description: OpenClaw REST API 网关 - 提供统一的API接口和工具调用服务
---

# OpenClaw API Gateway

OpenClaw的统一API网关，提供RESTful接口和工具调用服务，支持多种AI模型和工具集成。

## 核心功能

### 1. 模型调用API
- 支持多种AI模型 (Kimi, Claude, GPT等)
- 统一的请求/响应格式
- 自动重试和错误处理
- 流式响应支持

### 2. 工具调用服务
- 内置工具注册和发现
- 动态工具加载
- 工具执行沙箱
- 结果格式化输出

### 3. 会话管理
- 多会话支持
- 上下文保持
- 会话状态持久化
- 跨会话消息传递

### 4. 安全认证
- API密钥管理
- 请求签名验证
- 速率限制
- 访问日志记录

## 快速开始

### 环境配置

```bash
# 设置API密钥
export OPENCLAW_API_KEY="your-api-key"
export KIMI_API_KEY="your-kimi-key"
export CLAUDE_API_KEY="your-claude-key"
```

### 启动服务

```bash
# 开发模式
python api/index.py --dev

# 生产模式
python api/index.py --host 0.0.0.0 --port 8080
```

### 基础调用示例

```python
import requests

# 调用AI模型
response = requests.post(
    "http://localhost:8080/v1/chat/completions",
    headers={"Authorization": "Bearer your-api-key"},
    json={
        "model": "kimi-k2.5",
        "messages": [
            {"role": "user", "content": "你好"}
        ]
    }
)
print(response.json())
```

## API端点

### 聊天补全

```http
POST /v1/chat/completions
Content-Type: application/json
Authorization: Bearer {api_key}

{
    "model": "kimi-k2.5",
    "messages": [
        {"role": "system", "content": "你是一个助手"},
        {"role": "user", "content": "你好"}
    ],
    "temperature": 0.7,
    "max_tokens": 2000,
    "stream": false
}
```

### 工具调用

```http
POST /v1/tools/execute
Content-Type: application/json
Authorization: Bearer {api_key}

{
    "tool": "web_search",
    "parameters": {
        "query": "OpenClaw最新动态",
        "limit": 5
    }
}
```

### 获取可用工具列表

```http
GET /v1/tools/list
Authorization: Bearer {api_key}
```

### 会话管理

```http
# 创建会话
POST /v1/sessions/create
{
    "name": "我的会话",
    "context": {}
}

# 发送消息到会话
POST /v1/sessions/{session_id}/message
{
    "content": "你好",
    "model": "kimi-k2.5"
}

# 获取会话历史
GET /v1/sessions/{session_id}/history
```

## 支持的模型

| 模型 | 提供商 | 特点 |
|------|--------|------|
| kimi-k2.5 | Moonshot | 长上下文，代码能力强 |
| claude-3-5-sonnet | Anthropic | 推理能力强，安全 |
| gpt-4o | OpenAI | 通用能力强 |
| gpt-4o-mini | OpenAI | 快速，成本低 |

## 工具列表

### 内置工具

| 工具名 | 描述 | 参数 |
|--------|------|------|
| `web_search` | 网络搜索 | query, limit |
| `web_fetch` | 网页抓取 | url, extract_mode |
| `file_read` | 文件读取 | path, offset, limit |
| `file_write` | 文件写入 | path, content |
| `exec_command` | 执行命令 | command, timeout |
| `memory_search` | 记忆搜索 | query, max_results |

### 自定义工具

```python
# 注册自定义工具
from api.index import register_tool

@register_tool(
    name="my_tool",
    description="我的自定义工具",
    parameters={
        "input": {"type": "string", "required": True}
    }
)
def my_tool(input: str) -> dict:
    return {"result": f"处理结果: {input}"}
```

## 错误处理

### 错误码

| 状态码 | 描述 | 处理建议 |
|--------|------|----------|
| 200 | 成功 | - |
| 400 | 请求参数错误 | 检查请求体格式 |
| 401 | 认证失败 | 检查API密钥 |
| 429 | 请求过于频繁 | 降低请求频率 |
| 500 | 服务器错误 | 稍后重试 |
| 503 | 服务不可用 | 检查服务状态 |

### 错误响应格式

```json
{
    "error": {
        "code": "invalid_request",
        "message": "请求参数错误",
        "details": {
            "field": "model",
            "issue": "required"
        }
    }
}
```

## 速率限制

- 免费用户: 60请求/分钟
- 付费用户: 600请求/分钟
- 企业用户: 6000请求/分钟

## SDK示例

### Python

```python
from openclaw import OpenClawClient

client = OpenClawClient(api_key="your-key")

# 聊天
response = client.chat.completions.create(
    model="kimi-k2.5",
    messages=[{"role": "user", "content": "你好"}]
)

# 工具调用
result = client.tools.execute(
    tool="web_search",
    parameters={"query": "AI新闻"}
)
```

### JavaScript

```javascript
import { OpenClawClient } from '@openclaw/sdk';

const client = new OpenClawClient({ apiKey: 'your-key' });

// 聊天
const response = await client.chat.completions.create({
    model: 'kimi-k2.5',
    messages: [{ role: 'user', content: '你好' }]
});

// 工具调用
const result = await client.tools.execute({
    tool: 'web_search',
    parameters: { query: 'AI新闻' }
});
```

## 部署指南

### Docker部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

EXPOSE 8080
CMD ["python", "api/index.py", "--host", "0.0.0.0"]
```

```bash
docker build -t openclaw-api .
docker run -p 8080:8080 -e OPENCLAW_API_KEY=xxx openclaw-api
```

### 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `OPENCLAW_API_KEY` | API密钥 | 必填 |
| `KIMI_API_KEY` | Kimi API密钥 | - |
| `CLAUDE_API_KEY` | Claude API密钥 | - |
| `PORT` | 服务端口 | 8080 |
| `LOG_LEVEL` | 日志级别 | INFO |
| `MAX_WORKERS` | 最大工作线程 | 4 |

## 监控与日志

### 健康检查

```http
GET /health
```

响应:
```json
{
    "status": "healthy",
    "version": "1.0.0",
    "uptime": 3600
}
```

### 指标端点

```http
GET /metrics
```

返回Prometheus格式的监控指标。

## 更新日志

### v1.0.0
- ✅ RESTful API接口
- ✅ 多模型支持
- ✅ 工具调用框架
- ✅ 会话管理
- ✅ 认证与限流
- ✅ Docker部署支持

## 相关链接

- [API文档](https://docs.openclaw.ai/api)
- [SDK下载](https://github.com/claw-bft/openclaw-sdk)
- [示例代码](./examples/)
