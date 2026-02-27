#!/usr/bin/env python3
"""
Task Executor - 增强版任务执行器
支持重试机制、状态监控、告警通知
"""

import os
import sys
import json
import time
import subprocess
import traceback
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Callable
from enum import Enum

# 路径配置
SKILLS_DIR = Path("/root/.openclaw/workspace/skills")
SHARED_DIR = Path("/root/.openclaw/shared")
INCOMING_DIR = SHARED_DIR / "incoming"
REPORTS_DIR = SHARED_DIR / "reports"
LOGS_DIR = SHARED_DIR / "logs"

# 确保目录存在
LOGS_DIR.mkdir(parents=True, exist_ok=True)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class TaskExecution:
    """任务执行记录"""
    task_id: str
    task_name: str
    start_time: str
    end_time: Optional[str] = None
    status: str = TaskStatus.PENDING.value
    attempts: int = 0
    max_retries: int = 5
    error: Optional[str] = None
    output: Optional[str] = None
    report_url: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TaskExecution':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

class TaskExecutor:
    """任务执行器 - 带重试和监控"""
    
    def __init__(self, max_retries: int = 5, retry_delay: int = 15):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.execution_history: List[TaskExecution] = []
        self.current_execution: Optional[TaskExecution] = None
        
    def _log(self, message: str, level: str = "INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}"
        print(log_line)
        
        # 写入日志文件
        log_file = LOGS_DIR / f"task-{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")
    
    def _save_execution_history(self):
        """保存执行历史"""
        history_file = LOGS_DIR / "execution-history.json"
        history_data = [e.to_dict() for e in self.execution_history]
        history_file.write_text(json.dumps(history_data, indent=2, ensure_ascii=False), encoding="utf-8")
    
    def _send_notification(self, execution: TaskExecution):
        """发送通知(飞书)"""
        try:
            # 构建通知消息
            if execution.status == TaskStatus.SUCCESS.value:
                title = f"✅ 任务执行成功: {execution.task_name}"
                content = f"任务ID: {execution.task_id}\n完成时间: {execution.end_time}\n报告链接: {execution.report_url or 'N/A'}"
            else:
                title = f"❌ 任务执行失败: {execution.task_name}"
                content = f"任务ID: {execution.task_id}\n失败时间: {execution.end_time}\n尝试次数: {execution.attempts}/{execution.max_retries}\n错误: {execution.error or '未知错误'}"
            
            # 这里可以集成飞书消息发送
            # 由于是在cron任务中，我们记录到日志
            self._log(f"通知: {title}")
            self._log(f"通知内容: {content}")
            
        except Exception as e:
            self._log(f"发送通知失败: {e}", "ERROR")
    
    def execute_with_retry(self, task_id: str, task_name: str, command: List[str], 
                          cwd: Optional[Path] = None, env: Optional[Dict] = None) -> TaskExecution:
        """带重试的任务执行"""
        
        execution = TaskExecution(
            task_id=task_id,
            task_name=task_name,
            start_time=datetime.now().isoformat(),
            max_retries=self.max_retries
        )
        self.current_execution = execution
        
        self._log(f"开始执行任务: {task_name} (ID: {task_id})")
        
        for attempt in range(1, self.max_retries + 1):
            execution.attempts = attempt
            execution.status = TaskStatus.RETRYING.value if attempt > 1 else TaskStatus.RUNNING.value
            
            self._log(f"第 {attempt}/{self.max_retries} 次尝试...")
            
            try:
                # 设置环境变量
                run_env = {**os.environ}
                if env:
                    run_env.update(env)
                
                # 执行任务
                result = subprocess.run(
                    command,
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5分钟超时
                    env=run_env
                )
                
                execution.output = result.stdout
                
                if result.returncode == 0:
                    execution.status = TaskStatus.SUCCESS.value
                    execution.end_time = datetime.now().isoformat()
                    
                    # 尝试提取报告URL
                    for line in result.stdout.split('\n'):
                        if 'http' in line and 'vercel' in line:
                            execution.report_url = line.strip().split()[-1]
                    
                    self._log(f"✅ 任务执行成功 (尝试 {attempt} 次)")
                    break
                else:
                    execution.error = result.stderr or "未知错误"
                    self._log(f"⚠️ 任务返回非零状态: {result.returncode}", "WARN")
                    self._log(f"错误输出: {result.stderr}", "WARN")
                    
                    if attempt < self.max_retries:
                        self._log(f"等待 {self.retry_delay} 秒后重试...")
                        time.sleep(self.retry_delay)
                    
            except subprocess.TimeoutExpired:
                execution.error = "任务执行超时 (>300秒)"
                self._log("❌ 任务执行超时", "ERROR")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                    
            except Exception as e:
                execution.error = str(e)
                execution.output = traceback.format_exc()
                self._log(f"❌ 任务执行异常: {e}", "ERROR")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
        
        if execution.status != TaskStatus.SUCCESS.value:
            execution.status = TaskStatus.FAILED.value
            execution.end_time = datetime.now().isoformat()
            self._log(f"❌ 任务最终失败，已尝试 {execution.attempts} 次", "ERROR")
        
        # 保存执行记录
        self.execution_history.append(execution)
        self._save_execution_history()
        
        # 发送通知
        self._send_notification(execution)
        
        return execution
    
    def run_morning_report(self) -> TaskExecution:
        """执行早报任务"""
        task_file = INCOMING_DIR / "morning_task.json"
        
        if not task_file.exists():
            return TaskExecution(
                task_id="morning-report",
                task_name="股市早报",
                start_time=datetime.now().isoformat(),
                end_time=datetime.now().isoformat(),
                status=TaskStatus.FAILED.value,
                error=f"任务文件不存在: {task_file}"
            )
        
        # 使用stock-analyzer执行早报任务
        stock_analyzer = SKILLS_DIR / "stock-portfolio-analyzer" / "stock-analyzer.py"
        
        return self.execute_with_retry(
            task_id=f"morning-{datetime.now().strftime('%Y%m%d')}",
            task_name="股市早报",
            command=["python3", str(stock_analyzer), "morning-report", "--json"],
            cwd=SKILLS_DIR / "stock-portfolio-analyzer"
        )
    
    def get_task_status(self, task_id: str) -> Optional[TaskExecution]:
        """获取任务状态"""
        for execution in reversed(self.execution_history):
            if execution.task_id == task_id:
                return execution
        return None
    
    def get_recent_executions(self, limit: int = 10) -> List[TaskExecution]:
        """获取最近执行记录"""
        return sorted(
            self.execution_history,
            key=lambda x: x.start_time,
            reverse=True
        )[:limit]

def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="增强版任务执行器")
    parser.add_argument("command", choices=["morning-report", "status", "history", "test"], help="命令")
    parser.add_argument("--task-id", help="任务ID")
    parser.add_argument("--max-retries", type=int, default=5, help="最大重试次数")
    parser.add_argument("--retry-delay", type=int, default=15, help="重试间隔(秒)")
    
    args = parser.parse_args()
    
    executor = TaskExecutor(max_retries=args.max_retries, retry_delay=args.retry_delay)
    
    if args.command == "morning-report":
        result = executor.run_morning_report()
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
        sys.exit(0 if result.status == TaskStatus.SUCCESS.value else 1)
    
    elif args.command == "status":
        if not args.task_id:
            print("错误: 请提供 --task-id")
            sys.exit(1)
        status = executor.get_task_status(args.task_id)
        if status:
            print(json.dumps(status.to_dict(), indent=2, ensure_ascii=False))
        else:
            print(f"未找到任务: {args.task_id}")
    
    elif args.command == "history":
        history = executor.get_recent_executions()
        print(json.dumps([h.to_dict() for h in history], indent=2, ensure_ascii=False))
    
    elif args.command == "test":
        # 测试重试机制
        print("测试任务执行器...")
        result = executor.execute_with_retry(
            task_id="test-task",
            task_name="测试任务",
            command=["echo", "测试成功"]
        )
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
