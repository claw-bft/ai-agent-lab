---
name: api
description: ClawHub Registry API - 技能包注册表API，支持技能包的发布、查询、安装
---

# ClawHub Registry API

Vercel Serverless Function 实现的技能包注册表API，为 ClawHub CLI 提供后端服务支持。

## 核心功能

- **技能包注册**: 发布新技能包到注册表
- **技能包查询**: 搜索和浏览可用技能包
- **技能包详情**: 获取单个技能包的详细信息
- **统计分析**: 下载量、评分等统计数据

## API 端点

### GET /api
获取API信息和可用端点列表

```bash
curl https://claw-bft.github.io/ai-agent-lab/registry/api
```

### GET /api/skills
获取所有技能包列表

```bash
curl https://claw-bft.github.io/ai-agent-lab/registry/api/skills
```

**响应示例**:
```json
{
  "skills": [
    {
      "name": "finance-pro",
      "version": "1.2.0",
      "description": "多数据源金融数据获取",
      "author": "claw-bft",
      "tags": ["finance", "stock"],
      "downloads": 1250,
      "rating": 4.8
    }
  ],
  "total": 7
}
```

### GET /api/skills/:name
获取单个技能包详情

```bash
curl https://claw-bft.github.io/ai-agent-lab/registry/api/skills/finance-pro
```

### GET /api/search?q=keyword
搜索技能包

```bash
curl "https://claw-bft.github.io/ai-agent-lab/registry/api/search?q=finance"
```

### GET /api/stats
获取注册表统计信息

```bash
curl https://claw-bft.github.io/ai-agent-lab/registry/api/stats
```

## 技能包数据结构

```json
{
  "name": "skill-name",
  "version": "1.0.0",
  "description": "技能包描述",
  "author": "author-name",
  "tags": ["tag1", "tag2"],
  "downloads": 100,
  "rating": 4.5,
  "updated_at": "2026-02-28T00:00:00Z",
  "repository": "https://github.com/...",
  "install_url": "https://github.com/.../releases/..."
}
```

## 部署

### Vercel 部署

```bash
# 安装 Vercel CLI
npm i -g vercel

# 登录
vercel login

# 部署
vercel --prod
```

### 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
vercel dev
```

## 与 ClawHub CLI 集成

```python
# CLI 使用此API获取技能包信息
REGISTRY_URL = "https://claw-bft.github.io/ai-agent-lab/registry/api"

# 搜索技能包
requests.get(f"{REGISTRY_URL}/search?q={query}")

# 获取安装URL
requests.get(f"{REGISTRY_URL}/skills/{skill_name}")
```

## 更新日志

### 2026-02-28
- ✅ 实现基础API端点
- ✅ 支持技能包CRUD操作
- ✅ 添加搜索和统计功能
- ✅ 部署到 GitHub Pages
