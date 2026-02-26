#!/bin/bash

# OpenClaw Dashboard Backend 启动脚本

# 设置工作目录
cd "$(dirname "$0")"

# 检查环境变量
if [ -z "$KV_REST_API_URL" ] || [ -z "$KV_REST_API_TOKEN" ]; then
    echo "⚠️  Warning: Vercel KV environment variables not set"
    echo ""
    echo "Please set the following environment variables:"
    echo "  export KV_REST_API_URL='https://your-url.vercel-storage.com'"
    echo "  export KV_REST_API_TOKEN='your-token'"
    echo ""
    echo "Starting in WebSocket-only mode..."
    echo ""
fi

# 检查 node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# 检查 dist
if [ ! -d "dist" ]; then
    echo "🔨 Building..."
    npm run build
fi

# 启动服务器
echo "🚀 Starting OpenClaw Dashboard Server..."
echo ""

npm start
