# ClawHub Registry API

Vercel Serverless Function 实现的技能包注册表API，为 ClawHub CLI 提供后端服务支持。

## 功能特性

- **技能包注册**: 发布新技能包到注册表
- **技能包查询**: 搜索和浏览可用技能包
- **技能包详情**: 获取单个技能包的详细信息
- **统计分析**: 下载量、评分等统计数据

## 快速开始

```bash
# 本地开发
pip install -r requirements.txt
vercel dev

# 部署到Vercel
vercel --prod
```

## API端点

### 健康检查
```bash
GET /api/health
```

### 获取所有技能包
```bash
GET /api/skills
GET /api/skills?tag=finance
GET /api/skills?q=stock
GET /api/skills?sort=downloads|rating|updated
```

### 获取单个技能包
```bash
GET /api/skills/{name}
```

### 获取分类
```bash
GET /api/categories
```

### 获取统计信息
```bash
GET /api/stats
```

### 发布技能包
```bash
POST /api/skills
Content-Type: application/json

{
  "name": "skill-name",
  "version": "1.0.0",
  "description": "技能描述",
  "author": "author-name",
  "tags": ["tag1", "tag2"],
  "repository": "https://github.com/...",
  "install_url": "https://github.com/.../releases/..."
}
```

## 响应示例

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

## 部署

### Vercel部署

```bash
# 安装 Vercel CLI
npm i -g vercel

# 登录
vercel login

# 部署
vercel --prod
```

### GitHub Pages部署

静态文件部署到 GitHub Pages：

```bash
# 构建静态JSON文件
python3 build_static.py

# 推送到gh-pages分支
git subtree push --prefix registry origin gh-pages
```

## 与ClawHub CLI集成

```python
# CLI使用此API获取技能包信息
REGISTRY_URL = "https://claw-bft.github.io/ai-agent-lab/registry/api"

# 搜索技能包
requests.get(f"{REGISTRY_URL}/search?q={query}")

# 获取安装URL
requests.get(f"{REGISTRY_URL}/skills/{skill_name}")
```

## 测试

```bash
# 运行测试
python3 -m pytest tests/ -v
```

## 许可证

MIT
