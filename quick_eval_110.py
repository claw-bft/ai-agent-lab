#!/usr/bin/env python3
"""快速评测脚本 - 评测关键技能包"""

import subprocess
import json
import time

skills_to_eval = [
    "memory-enhanced",
    "token-manager",
    "agent-collaboration",
    "notification-service"
]

results = {}

for skill in skills_to_eval:
    print(f"\n评测: {skill}")
    try:
        result = subprocess.run(
            ["python3", "skill-evaluator/skill_evaluator.py", "--skill", skill, "--verbose"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd="/root/.openclaw/workspace/ai-agent-lab"
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
    except Exception as e:
        print(f"评测失败: {e}")

print("\n关键技能包评测完成")
