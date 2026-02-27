#!/bin/bash
# ClawHub本地API测试脚本
# 在本地启动并测试API

set -e

echo "🖥️  ClawHub本地API测试"
echo "======================="
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3"
    exit 1
fi

echo "✅ Python3已安装"

# 进入项目目录
cd "$(dirname "$0")/.."

# 检查api/index.py
if [ ! -f "api/index.py" ]; then
    echo "❌ 未找到api/index.py"
    exit 1
fi

echo "✅ API文件存在"
echo ""

# 启动测试服务器
echo "🚀 启动测试服务器 (端口8000)..."
python3 -m http.server 8000 --directory . &
SERVER_PID=$!

# 等待服务器启动
sleep 2

# 测试API
echo ""
echo "🧪 测试API端点..."
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# 测试函数
test_api() {
    local endpoint=$1
    local name=$2
    
    echo -n "测试 $name ... "
    
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/api/$endpoint" 2>/dev/null || echo "000")
    
    if [ "$HTTP_STATUS" = "200" ]; then
        echo -e "${GREEN}✅ 通过${NC}"
    else
        echo -e "${RED}❌ 失败${NC} (HTTP $HTTP_STATUS)"
    fi
}

# 测试各个端点
test_api "health" "健康检查"
test_api "skills" "技能列表"
test_api "skills/finance-pro" "技能详情"
test_api "categories" "分类列表"
test_api "stats" "统计信息"

# 停止服务器
echo ""
echo "🛑 停止测试服务器..."
kill $SERVER_PID 2>/dev/null || true

echo ""
echo "✅ 本地测试完成"
echo ""
echo "📝 提示: 本地测试仅验证文件可访问性"
echo "   完整功能测试需要部署到Vercel后执行:"
echo "   ./scripts/test-api.sh"
