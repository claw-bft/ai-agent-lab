#!/bin/bash
# ClawHub API测试脚本
# 测试远程注册表API的可用性

set -e

# 默认注册表URL
REGISTRY_URL="${CLAWHUB_REGISTRY:-https://clawhub-registry.vercel.app}"

echo "🧪 ClawHub API测试"
echo "=================="
echo "注册表URL: $REGISTRY_URL"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数
PASSED=0
FAILED=0

# 测试函数
test_endpoint() {
    local name=$1
    local url=$2
    local expected_status=$3
    
    echo -n "测试 $name ... "
    
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$HTTP_STATUS" = "$expected_status" ]; then
        echo -e "${GREEN}✅ 通过${NC} (HTTP $HTTP_STATUS)"
        ((PASSED++))
    else
        echo -e "${RED}❌ 失败${NC} (期望 HTTP $expected_status, 实际 HTTP $HTTP_STATUS)"
        ((FAILED++))
    fi
}

# 1. 健康检查
test_endpoint "健康检查" "$REGISTRY_URL/health" "200"

# 2. 技能列表
test_endpoint "技能列表" "$REGISTRY_URL/skills" "200"

# 3. 技能详情
test_endpoint "技能详情" "$REGISTRY_URL/skills/finance-pro" "200"

# 4. 分类列表
test_endpoint "分类列表" "$REGISTRY_URL/categories" "200"

# 5. 统计信息
test_endpoint "统计信息" "$REGISTRY_URL/stats" "200"

# 6. 不存在的技能（应返回404）
test_endpoint "404处理" "$REGISTRY_URL/skills/nonexistent" "404"

echo ""
echo "=================="
echo "测试结果: $PASSED 通过, $FAILED 失败"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ 所有测试通过!${NC}"
    exit 0
else
    echo -e "${RED}❌ 有测试失败${NC}"
    exit 1
fi
