# OpenClaw Dashboard - Vercel KV 配置指南

## 架构

```
Backend (服务器) → 写入 Vercel KV ← Frontend (Vercel) 读取
```

## 1. 配置 Vercel KV

### 1.1 创建 KV 数据库

1. 登录 [Vercel Dashboard](https://vercel.com/dashboard/stores)
2. 点击 "Create Store" → 选择 "KV"
3. 输入名称：`openclaw-dashboard`
4. 选择区域（建议选择离服务器最近的区域）
5. 点击 "Create"

### 1.2 获取环境变量

创建完成后，进入 KV 数据库详情页，点击 "Connect" → "Environment Variables"，获取以下值：

- `KV_REST_API_URL`
- `KV_REST_API_TOKEN`

## 2. 配置 Backend

### 2.1 安装依赖

```bash
cd /root/.openclaw/workspace/openclaw-dashboard-full/server
npm install
```

### 2.2 设置环境变量

```bash
export KV_REST_API_URL="https://your-kv-url.vercel-storage.com"
export KV_REST_API_TOKEN="your-token-here"
export SYNC_INTERVAL="1000"  # 同步间隔（毫秒），默认 1000ms
```

### 2.3 启动 Backend

```bash
npm run build
npm start
```

或使用开发模式：

```bash
npm run dev
```

## 3. 配置 Frontend

### 3.1 设置环境变量

创建 `client/.env.local`：

```env
VITE_KV_REST_API_URL=https://your-kv-url.vercel-storage.com
VITE_KV_REST_API_TOKEN=your-token-here
```

### 3.2 构建并部署

```bash
cd /root/.openclaw/workspace/openclaw-dashboard-full/client
npm install
npm run build
vercel --prod
```

## 4. 数据结构

KV 中存储的数据结构：

| Key | Type | Description |
|-----|------|-------------|
| `sessions:list` | JSON | 会话列表数组 |
| `sessions:{id}` | JSON | 单个会话详情 |
| `stats` | JSON | 系统统计信息 |
| `tasks` | JSON | 任务列表 |
| `messages` | JSON | 消息列表 |
| `lastUpdate` | string | 最后更新时间戳 |

## 5. 验证部署

### 5.1 检查 Backend 连接

```bash
curl http://your-server:3001/api/health
```

应返回：
```json
{
  "status": "ok",
  "timestamp": "2024-...",
  "kv": "connected"
}
```

### 5.2 检查 Frontend

访问部署后的 Vercel URL，检查：
- Dashboard 显示 "KV Mode"
- 数据每 3 秒自动刷新
- 显示最后更新时间

## 6. 故障排查

### Backend 无法连接 KV

1. 检查环境变量是否正确设置
2. 验证 KV URL 和 Token
3. 查看日志：`KV_REST_API_URL` 和 `KV_REST_API_TOKEN` 是否显示

### Frontend 无法读取数据

1. 检查 `.env.local` 中的变量名是否正确（必须以 `VITE_` 开头）
2. 检查浏览器控制台是否有 CORS 错误
3. 验证 KV Token 是否有读取权限

### 数据不同步

1. 检查 Backend 是否在运行
2. 检查 SYNC_INTERVAL 设置
3. 查看 Backend 日志是否有同步错误

## 7. 安全注意事项

⚠️ **重要**：
- `KV_REST_API_TOKEN` 具有写入权限，请勿泄露
- Frontend 只需要读取权限，建议使用只读 Token
- 生产环境应使用 Vercel 的环境变量功能，而非 `.env.local`

## 8. 切换回 WebSocket 模式

如需切换回本地 WebSocket 模式：

1. Backend：不设置 KV 环境变量
2. Frontend：删除或注释掉 `.env.local` 中的 KV 配置

系统会自动回退到 WebSocket 模式。
