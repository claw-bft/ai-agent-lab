#!/usr/bin/env python3
"""
统一测试入口 - 运行所有技能测试
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

# 测试配置
SKILL_DIRS = [
    "skills/skill-cli",
    "skills/finance-pro", 
    "skills/coding-pro",
    "skills/product-pro",
    "skills/research-pro",
]

def run_skill_tests(skill_dir: str) -> dict:
    """运行单个技能的测试"""
    skill_path = Path(__file__).parent.parent / skill_dir
    tests_path = skill_path / "tests"
    
    result = {
        "skill": skill_dir,
        "tests_found": False,
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "duration_ms": 0,
        "output": ""
    }
    
    if not tests_path.exists():
        result["output"] = "No tests directory found"
        return result
    
    test_files = list(tests_path.glob("test_*.py"))
    if not test_files:
        result["output"] = "No test files found"
        return result
    
    result["tests_found"] = True
    
    # 尝试使用pytest
    try:
        start = datetime.now()
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", str(tests_path), "-v", "--tb=short"],
            capture_output=True,
            text=True,
            cwd=str(skill_path),
            timeout=60
        )
        duration = (datetime.now() - start).total_seconds() * 1000
        result["duration_ms"] = int(duration)
        
        output = proc.stdout + proc.stderr
        result["output"] = output[:2000]  # 限制输出长度
        
        # 解析结果
        if "passed" in output:
            import re
            passed_match = re.search(r'(\d+) passed', output)
            failed_match = re.search(r'(\d+) failed', output)
            error_match = re.search(r'(\d+) error', output)
            
            if passed_match:
                result["passed"] = int(passed_match.group(1))
            if failed_match:
                result["failed"] = int(failed_match.group(1))
            if error_match:
                result["errors"] = int(error_match.group(1))
        
        result["success"] = proc.returncode == 0
        
    except subprocess.TimeoutExpired:
        result["output"] = "Test timeout"
        result["errors"] = 1
    except Exception as e:
        # pytest不可用，尝试直接运行测试文件
        result["output"] = f"pytest not available: {e}"
        result["errors"] = 1
    
    return result

def run_all_tests():
    """运行所有测试"""
    print("=" * 70)
    print("AI Agent Lab - 统一测试套件")
    print(f"时间: {datetime.now().isoformat()}")
    print("=" * 70)
    
    all_results = []
    total_passed = 0
    total_failed = 0
    total_errors = 0
    
    for skill in SKILL_DIRS:
        print(f"\n📦 测试技能: {skill}")
        print("-" * 50)
        
        result = run_skill_tests(skill)
        all_results.append(result)
        
        total_passed += result["passed"]
        total_failed += result["failed"]
        total_errors += result["errors"]
        
        if result["tests_found"]:
            status = "✓" if result.get("success") else "✗"
            print(f"{status} 通过: {result['passed']}, 失败: {result['failed']}, 错误: {result['errors']}")
        else:
            print("⚠ 未找到测试")
        
        if result["output"] and len(result["output"]) < 500:
            print(result["output"])
    
    # 汇总
    print("\n" + "=" * 70)
    print("测试结果汇总")
    print("=" * 70)
    
    for r in all_results:
        status = "✓" if r.get("success") else "✗" if r["tests_found"] else "○"
        print(f"{status} {r['skill']}: 通过={r['passed']}, 失败={r['failed']}, 错误={r['errors']}")
    
    print("-" * 70)
    print(f"总计: 通过={total_passed}, 失败={total_failed}, 错误={total_errors}")
    
    # 保存报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_passed": total_passed,
            "total_failed": total_failed,
            "total_errors": total_errors,
            "total_tests": total_passed + total_failed + total_errors
        },
        "results": all_results
    }
    
    report_path = Path(__file__).parent / "test_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 测试报告已保存: {report_path}")
    
    return total_failed == 0 and total_errors == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
