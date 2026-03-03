#!/bin/bash
# Vercel deployment script for news-intelligence-hub

set -e

DEPLOY_DIR="/root/.openclaw/workspace/ai-agent-lab/skills/news-intelligence-hub/deploy"
TOKEN="vcp_8CnZxMGVDbcYde49qIp77UmmDu7Df67MPf9dhGSsZfWWAH7SKX1Ag5GK"

cd "$DEPLOY_DIR"

echo "🚀 Deploying to Vercel..."

# Set token in environment
export VERCEL_TOKEN="$TOKEN"

# Deploy using token from env
vercel --token "$VERCEL_TOKEN" --prod --yes

echo "✅ Deployment complete!"
