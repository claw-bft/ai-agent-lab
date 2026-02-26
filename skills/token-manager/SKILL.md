# Token Manager - 全局凭证管理

## 设计原则
- 安全存储敏感信息
- 按服务分类管理
- 支持快速读取
- 权限控制

## 存储位置
`~/.openclaw/secrets/tokens.json`

## 结构
```json
{
  "github": {
    "username": "claw-bft",
    "token": "ghp_xxx",
    "scopes": ["repo", "user"],
    "created_at": "2026-02-26",
    "note": "GitHub CLI token"
  },
  "vercel": {
    "token": "vcp_xxx",
    "note": "Vercel deployment"
  }
}
```

## 使用方式
- 读取: `getToken('github')`
- 写入: `setToken('service', token, metadata)`
