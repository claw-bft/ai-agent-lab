# OpenClaw Dashboard

基于 Vercel KV 的 Dashboard 后端公网访问方案。

## 项目结构

```
openclaw-dashboard-full/
├── server/          # Backend (Node.js + Express + Vercel KV)
│   ├── index.ts     # 主服务器代码
│   ├── kv-store.ts  # Vercel KV 操作封装
│   └── package.json
├── client/          # Frontend (React + Vite)
│   ├── src/
│   │   ├── hooks/
│   │   │   └── useKVData.ts    # KV 数据轮询 Hook
│   │   ├── pages/
│   │   │   └── Dashboard.tsx   # Dashboard 页面
│   │   └── App.tsx
│   └── package.json
└── VERCEL_KV_SETUP.md  # 配置指南
```

## 快速开始

### 1. 配置 Vercel KV

1. 访问 https://vercel.com/dashboard/stores
2. 创建 KV 数据库
3. 获取 `KV_REST_API_URL` 和 `KV_REST_API_TOKEN`

### 2. 启动 Backend

```bash
cd server
npm install

# 设置环境变量
export KV_REST_API_URL="https://your-url.vercel-storage.com"
export KV_REST_API_TOKEN="your-token"

# 开发模式
npm run dev

# 生产模式
npm run build
npm start
```

### 3. 部署 Frontend

```bash
cd client
npm install

# 创建环境变量文件
echo "VITE_KV_REST_API_URL=https://your-url.vercel-storage.com" > .env.local
echo "VITE_KV_REST_API_TOKEN=your-token" >> .env.local

# 构建并部署
npm run build
vercel --prod
```

## 访问链接

- Frontend: https://your-app.vercel.app
- Backend API: http://your-server:3001/api

## 特性

- ✅ 每秒同步 sessions 到 Vercel KV
- ✅ Frontend 每 3 秒轮询 KV 数据
- ✅ 显示最后更新时间
- ✅ 支持 WebSocket 回退模式
- ✅ 自动检测 KV 配置

## 环境变量

### Backend

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `KV_REST_API_URL` | Vercel KV REST API URL | - |
| `KV_REST_API_TOKEN` | Vercel KV Token | - |
| `SYNC_INTERVAL` | 同步间隔（毫秒） | 1000 |
| `PORT` | 服务器端口 | 3001 |

### Frontend

| 变量 | 说明 |
|------|------|
| `VITE_KV_REST_API_URL` | Vercel KV REST API URL |
| `VITE_KV_REST_API_TOKEN` | Vercel KV Token（只读） |

## 数据流

```
┌─────────────┐     WebSocket      ┌─────────────┐
│   Client    │ ◄────────────────► │   Backend   │
│  (Vercel)   │   (fallback mode)  │  (Server)   │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  Poll (3s)                       │  Sync (1s)
       ▼                                  ▼
┌─────────────┐                    ┌─────────────┐
│  Vercel KV  │ ◄───────────────── │  Sessions   │
│  (Storage)  │                    │   & Stats   │
└─────────────┘                    └─────────────┘
```
