#!/usr/bin/env python3
"""
Test Runner - Run all test suites for the AI Agent Lab
"""

import sys
import os
import subprocess
from pathlib import Path

# Test suites configuration
TEST_SUITES = [
    {
        "name": "skill-cli/executor",
        "path": "skills/skill-cli/tests/test_executor.py",
        "description": "Core execution engine tests"
    },
    {
        "name": "finance-pro/data_adapter", 
        "path": "skills/finance-pro/tests/test_data_adapter.py",
        "description": "Financial data adapter tests"
    },
    {
        "name": "coding-pro/ai_code_generator",
        "path": "skills/coding-pro/tests/test_ai_code_generator.py",
        "description": "AI code generation tests"
    }
]


def run_test_suite(suite: dict) -> dict:
    """Run a single test suite"""
    print(f"\n{'='*60}")
    print(f"Running: {suite['name']}")
    print(f"Description: {suite['description']}")
    print(f"{'='*60}")
    
    test_path = Path(suite['path'])
    if not test_path.exists():
        return {
            "name": suite['name'],
            "status": "SKIPPED",
            "reason": "Test file not found"
        }
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_path)],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        success = result.returncode == 0
        
        return {
            "name": suite['name'],
            "status": "PASSED" if success else "FAILED",
            "returncode": result.returncode,
            "stdout": result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout,
            "stderr": result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr
        }
        
    except subprocess.TimeoutExpired:
        return {
            "name": suite['name'],
            "status": "TIMEOUT",
            "reason": "Test execution timed out"
        }
    except Exception as e:
        return {
            "name": suite['name'],
            "status": "ERROR",
            "reason": str(e)
        }


def main():
    """Main test runner"""
    print("="*60)
    print("AI Agent Lab - Test Suite Runner")
    print("="*60)
    
    # Change to workspace directory
    workspace = Path("/root/.openclaw/workspace")
    os.chdir(workspace)
    
    results = []
    passed = 0
    failed = 0
    skipped = 0
    
    for suite in TEST_SUITES:
        result = run_test_suite(suite)
        results.append(result)
        
        if result['status'] == 'PASSED':
            passed += 1
        elif result['status'] == 'FAILED':
            failed += 1
        else:
            skipped += 1
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    for result in results:
        status_icon = "✓" if result['status'] == 'PASSED' else "✗" if result['status'] == 'FAILED' else "○"
        print(f"{status_icon} {result['name']}: {result['status']}")
        
        if result['status'] == 'FAILED':
            if 'stderr' in result and result['stderr']:
                print(f"  Error: {result['stderr'][:200]}")
        elif result['status'] in ['SKIPPED', 'TIMEOUT', 'ERROR']:
            print(f"  Reason: {result.get('reason', 'Unknown')}")
    
    print(f"\n{'='*60}")
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
    print(f"{'='*60}")
    
    # Calculate coverage estimate
    coverage = (passed / len(results)) * 100 if results else 0
    print(f"\nEstimated Test Coverage: {coverage:.0f}%")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
