#!/bin/bash
#
# Vercel Deploy Skill Tests
# 测试vercel-deploy技能包的脚本功能

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数器
TESTS_PASSED=0
TESTS_FAILED=0

# 测试函数
run_test() {
    local test_name="$1"
    local test_cmd="$2"
    
    printf "Testing: %s... " "$test_name"
    if eval "$test_cmd" > /dev/null 2>&1; then
        printf "%bPASSED%b\n" "$GREEN" "$NC"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        printf "%bFAILED%b\n" "$RED" "$NC"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "Vercel Deploy Skill Test Suite"
echo "========================================"
echo ""

# 测试1: 检查脚本文件存在
echo "--- File Existence Tests ---"
run_test "vercel_deploy.sh exists" "test -f $SKILL_DIR/scripts/vercel_deploy.sh"
run_test "vercel_env.sh exists" "test -f $SKILL_DIR/scripts/vercel_env.sh"
run_test "vercel_status.sh exists" "test -f $SKILL_DIR/scripts/vercel_status.sh"

# 测试2: 检查文档存在
echo ""
echo "--- Documentation Tests ---"
run_test "README.md exists" "test -f $SKILL_DIR/README.md"
run_test "SKILL.md exists" "test -f $SKILL_DIR/SKILL.md"
run_test "SETUP.md exists" "test -f $SKILL_DIR/SETUP.md"

# 测试3: 检查脚本可执行
echo ""
echo "--- Script Permission Tests ---"
run_test "vercel_deploy.sh is executable" "test -x $SKILL_DIR/scripts/vercel_deploy.sh"
run_test "vercel_env.sh is executable" "test -x $SKILL_DIR/scripts/vercel_env.sh"
run_test "vercel_status.sh is executable" "test -x $SKILL_DIR/scripts/vercel_status.sh"

# 测试4: 检查脚本语法
echo ""
echo "--- Script Syntax Tests ---"
run_test "vercel_deploy.sh syntax valid" "bash -n $SKILL_DIR/scripts/vercel_deploy.sh"
run_test "vercel_env.sh syntax valid" "bash -n $SKILL_DIR/scripts/vercel_env.sh"
run_test "vercel_status.sh syntax valid" "bash -n $SKILL_DIR/scripts/vercel_status.sh"

# 测试5: 检查脚本内容
echo ""
echo "--- Script Content Tests ---"
run_test "vercel_deploy.sh contains VERCEL_TOKEN check" "grep -q 'VERCEL_TOKEN' $SKILL_DIR/scripts/vercel_deploy.sh"
run_test "vercel_env.sh contains list option" "grep -q '\-\-list' $SKILL_DIR/scripts/vercel_env.sh"
run_test "vercel_status.sh contains project option" "grep -q '\-\-project' $SKILL_DIR/scripts/vercel_status.sh"

# 测试6: 检查README内容
echo ""
echo "--- README Content Tests ---"
run_test "README contains Vercel token info" "grep -q 'VERCEL_TOKEN' $SKILL_DIR/README.md"
run_test "README contains deployment info" "grep -qi 'deploy' $SKILL_DIR/README.md"
run_test "README contains environment variables" "grep -qi 'environment' $SKILL_DIR/README.md"

# 测试7: 检查SKILL.md内容
echo ""
echo "--- SKILL.md Content Tests ---"
run_test "SKILL.md has name field" "grep -q '^name:' $SKILL_DIR/SKILL.md"
run_test "SKILL.md has description" "grep -q '^description:' $SKILL_DIR/SKILL.md"
run_test "SKILL.md contains workflows" "grep -q 'Workflows\|workflow' $SKILL_DIR/SKILL.md"

# 测试8: 检查references目录
echo ""
echo "--- References Tests ---"
run_test "references directory exists" "test -d $SKILL_DIR/references"
run_test "references not empty" "test "$(ls -A $SKILL_DIR/references)""

# 测试9: 检查_meta.json
echo ""
echo "--- Metadata Tests ---"
run_test "_meta.json exists" "test -f $SKILL_DIR/_meta.json"
run_test "_meta.json is valid JSON" "python3 -c 'import json; json.load(open(\"'$SKILL_DIR'/_meta.json\"))'"

echo ""
echo "========================================"
echo "Test Summary"
echo "========================================"
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
