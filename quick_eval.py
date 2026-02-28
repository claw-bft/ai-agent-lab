#!/usr/bin/env python3
"""
快速评测脚本 - 验证测试修复
"""

import subprocess
import sys
from pathlib import Path

def run_tests(skill_path):
    """运行测试并返回结果"""
    skill_path = Path(skill_path)
    
    # 运行测试
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=no", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(skill_path)
    )
    
    output = result.stdout + result.stderr
    print(f"=== {skill_path.name} ===")
    print(output)
    
    # 解析结果
    import re
    passed = re.search(r"(\d+) passed", output)
    failed = re.search(r"(\d+) failed", output)
    error = re.search(r"(\d+) error", output)
    
    tests_passed = int(passed.group(1)) if passed else 0
    tests_failed = int(failed.group(1)) if failed else 0
    tests_failed += int(error.group(1)) if error else 0
    
    return tests_passed, tests_failed

if __name__ == "__main__":
    print("验证测试修复...\n")
    
    # 测试 memory-enhanced
    me_passed, me_failed = run_tests("/root/.openclaw/workspace/ai-agent-lab/memory-enhanced")
    
    # 测试 token-manager
    tm_passed, tm_failed = run_tests("/root/.openclaw/workspace/ai-agent-lab/token-manager")
    
    print("\n=== 总结 ===")
    print(f"memory-enhanced: {me_passed} passed, {me_failed} failed")
    print(f"token-manager: {tm_passed} passed, {tm_failed} failed")
    
    if me_failed == 0 and tm_failed == 0:
        print("\n✅ 所有测试通过！")
        sys.exit(0)
    else:
        print("\n❌ 有测试失败")
        sys.exit(1)
