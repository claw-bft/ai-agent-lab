#!/usr/bin/env python3
"""
执行引擎 - Executor
执行技能命令并处理结果
"""

import subprocess
import json
import sys
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from pathlib import Path
from enum import Enum

from intent_parser import IntentParser, Intent
from skill_router import SkillRouter, SkillRoute

class ExecutionStatus(Enum):
    """执行状态"""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    NOT_FOUND = "not_found"
    PARTIAL = "partial"

@dataclass
class ExecutionResult:
    """执行结果"""
    status: ExecutionStatus
    skill_name: str
    command: str
    output: str
    error: Optional[str]
    duration_ms: float
    metadata: Dict[str, Any]

class SkillExecutor:
    """技能执行引擎"""
    
    def __init__(self, skills_dir: str = "/root/.openclaw/workspace/skills"):
        self.skills_dir = Path(skills_dir)
        self.intent_parser = IntentParser()
        self.skill_router = SkillRouter(skills_dir)
        self.pre_hooks: List[Callable] = []
        self.post_hooks: List[Callable] = []
    
    def execute_natural_language(self, text: str, context: Optional[Dict] = None) -> ExecutionResult:
        """
        执行自然语言命令
        
        Args:
            text: 自然语言命令
            context: 可选的上下文信息
            
        Returns:
            ExecutionResult对象
        """
        import time
        start_time = time.time()
        
        # 1. 解析意图
        intent = self.intent_parser.parse(text)
        
        # 2. 路由到技能
        route = self.skill_router.route(intent)
        
        # 3. 执行命令
        result = self._execute_skill_command(
            route.skill_name, 
            route.command, 
            route.args
        )
        
        duration = (time.time() - start_time) * 1000
        
        return ExecutionResult(
            status=result.get("status", ExecutionStatus.ERROR),
            skill_name=route.skill_name,
            command=route.command,
            output=result.get("output", ""),
            error=result.get("error"),
            duration_ms=duration,
            metadata={
                "intent": intent.type.value,
                "intent_confidence": intent.confidence,
                "route_confidence": route.confidence,
                "route_reason": route.reason,
                "entities": intent.entities,
                "context": context or {}
            }
        )
    
    def execute_structured(self, skill_name: str, command: str, args: List[str] = None) -> ExecutionResult:
        """
        执行结构化命令
        
        Args:
            skill_name: 技能名称
            command: 子命令
            args: 参数列表
            
        Returns:
            ExecutionResult对象
        """
        import time
        start_time = time.time()
        
        args = args or []
        result = self._execute_skill_command(skill_name, command, args)
        
        duration = (time.time() - start_time) * 1000
        
        return ExecutionResult(
            status=result.get("status", ExecutionStatus.ERROR),
            skill_name=skill_name,
            command=command,
            output=result.get("output", ""),
            error=result.get("error"),
            duration_ms=duration,
            metadata=result.get("metadata", {})
        )
    
    def _execute_skill_command(self, skill_name: str, command: str, args: List[str]) -> Dict[str, Any]:
        """执行具体的技能命令"""
        
        # 检查技能是否存在
        skill_path = self.skills_dir / skill_name
        if not skill_path.exists():
            return {
                "status": ExecutionStatus.NOT_FOUND,
                "output": "",
                "error": f"技能包 '{skill_name}' 不存在",
                "metadata": {}
            }
        
        # 构建命令行
        # 优先尝试直接调用Python实现
        py_file = skill_path / f"{skill_name}.py"
        if py_file.exists():
            return self._execute_python_skill(py_file, command, args)
        
        # 尝试调用skill-cli.py
        cli_file = self.skills_dir / "skill-cli" / "skill-cli.py"
        if cli_file.exists():
            return self._execute_cli_skill(skill_name, command, args)
        
        # 技能存在但没有可执行实现
        return {
            "status": ExecutionStatus.PARTIAL,
            "output": f"技能 '{skill_name}' 已找到，但缺少可执行实现",
            "error": None,
            "metadata": {
                "skill_path": str(skill_path),
                "note": "该技能包只有文档，需要补充实现"
            }
        }
    
    def _execute_python_skill(self, py_file: Path, command: str, args: List[str]) -> Dict[str, Any]:
        """执行Python技能文件"""
        try:
            # 构建命令
            cmd = [sys.executable, str(py_file), command] + args
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(py_file.parent)
            )
            
            if result.returncode == 0:
                return {
                    "status": ExecutionStatus.SUCCESS,
                    "output": result.stdout,
                    "error": None,
                    "metadata": {"command": " ".join(cmd)}
                }
            else:
                return {
                    "status": ExecutionStatus.ERROR,
                    "output": result.stdout,
                    "error": result.stderr,
                    "metadata": {"command": " ".join(cmd)}
                }
                
        except subprocess.TimeoutExpired:
            return {
                "status": ExecutionStatus.TIMEOUT,
                "output": "",
                "error": "执行超时（30秒）",
                "metadata": {}
            }
        except Exception as e:
            return {
                "status": ExecutionStatus.ERROR,
                "output": "",
                "error": str(e),
                "metadata": {}
            }
    
    def _execute_cli_skill(self, skill_name: str, command: str, args: List[str]) -> Dict[str, Any]:
        """通过skill-cli执行"""
        cli_file = self.skills_dir / "skill-cli" / "skill-cli.py"
        
        try:
            cmd = [sys.executable, str(cli_file), skill_name, command] + args + ["--json"]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # 尝试解析JSON输出
            try:
                output_data = json.loads(result.stdout)
                return {
                    "status": ExecutionStatus.SUCCESS if output_data.get("success") else ExecutionStatus.ERROR,
                    "output": json.dumps(output_data, indent=2, ensure_ascii=False),
                    "error": output_data.get("error"),
                    "metadata": {"raw_output": output_data}
                }
            except json.JSONDecodeError:
                return {
                    "status": ExecutionStatus.SUCCESS if result.returncode == 0 else ExecutionStatus.ERROR,
                    "output": result.stdout,
                    "error": result.stderr if result.stderr else None,
                    "metadata": {}
                }
                
        except subprocess.TimeoutExpired:
            return {
                "status": ExecutionStatus.TIMEOUT,
                "output": "",
                "error": "执行超时（30秒）",
                "metadata": {}
            }
        except Exception as e:
            return {
                "status": ExecutionStatus.ERROR,
                "output": "",
                "error": str(e),
                "metadata": {}
            }
    
    def batch_execute(self, texts: List[str]) -> List[ExecutionResult]:
        """批量执行自然语言命令"""
        return [self.execute_natural_language(text) for text in texts]
    
    def get_execution_summary(self, results: List[ExecutionResult]) -> Dict[str, Any]:
        """获取执行摘要"""
        total = len(results)
        success = sum(1 for r in results if r.status == ExecutionStatus.SUCCESS)
        error = sum(1 for r in results if r.status == ExecutionStatus.ERROR)
        timeout = sum(1 for r in results if r.status == ExecutionStatus.TIMEOUT)
        
        avg_duration = sum(r.duration_ms for r in results) / total if total > 0 else 0
        
        return {
            "total": total,
            "success": success,
            "error": error,
            "timeout": timeout,
            "success_rate": success / total if total > 0 else 0,
            "avg_duration_ms": avg_duration
        }


# 测试代码
if __name__ == "__main__":
    executor = SkillExecutor()
    
    test_cases = [
        "查询一下茅台股票",
        "帮我写个Python函数",
        "研究AI发展趋势",
    ]
    
    print("=" * 60)
    print("自然语言执行引擎测试")
    print("=" * 60)
    
    for text in test_cases:
        print(f"\n📝 输入: {text}")
        result = executor.execute_natural_language(text)
        print(f"✓ 技能: {result.skill_name}")
        print(f"✓ 命令: {result.command}")
        print(f"✓ 状态: {result.status.value}")
        print(f"✓ 耗时: {result.duration_ms:.1f}ms")
        if result.output:
            print(f"✓ 输出:\n{result.output[:200]}...")
        if result.error:
            print(f"✗ 错误: {result.error}")
