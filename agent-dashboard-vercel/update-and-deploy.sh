#!/bin/bash
# 更新数据并重新部署到Vercel

# 复制最新数据
cp /root/.openclaw/workspace/agent-dashboard-public/data/dashboard.json ./data/

# 部署到Vercel
export VERCEL_TOKEN="vcp_8CnZxMGVDbcYde49qIp77UmmDu7Df67MPf9dhGSsZfWWAH7SKX1Ag5GK"
vercel deploy --prod --yes --token="$VERCEL_TOKEN"
