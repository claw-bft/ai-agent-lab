#!/bin/bash
# ClawHub Vercel部署脚本
# 用于部署ClawHub注册表API到Vercel

set -e

echo "🚀 ClawHub Vercel部署脚本"
echo "=========================="

# 检查vercel CLI
if ! command -v vercel &> /dev/null; then
    echo "❌ 未安装Vercel CLI"
    echo "   请运行: npm i -g vercel"
    exit 1
fi

# 检查VERCEL_TOKEN
if [ -z "$VERCEL_TOKEN" ]; then
    echo "⚠️  未设置VERCEL_TOKEN环境变量"
    echo "   请设置: export VERCEL_TOKEN=your_token"
    echo ""
    echo "   获取Token步骤:"
    echo "   1. 访问 https://vercel.com/account/tokens"
    echo "   2. 点击 'Create Token'"
    echo "   3. 复制token并设置环境变量"
    exit 1
fi

# 检查当前目录
if [ ! -f "vercel.json" ]; then
    echo "❌ 当前目录不是ClawHub项目根目录"
    echo "   请在ai-agent-lab目录下运行此脚本"
    exit 1
fi

echo "✅ 环境检查通过"
echo ""

# 登录Vercel
echo "🔑 登录Vercel..."
vercel login --token "$VERCEL_TOKEN"

# 部署
echo ""
echo "📦 开始部署..."
vercel --prod --token "$VERCEL_TOKEN" --yes

echo ""
echo "✅ 部署完成!"
echo ""
echo "📝 下一步:"
echo "   1. 访问Vercel控制台查看部署状态"
echo "   2. 运行 ./scripts/test-api.sh 测试API"
echo "   3. 更新CLAWHUB_REGISTRY环境变量为部署后的URL"
