#!/usr/bin/env python3
"""
AI Agent Self-Monitoring System
监控AI Agent的"生理状态" - CPU、内存、任务数等
"""

import os
import sys
import json
import time
import psutil
import subprocess
from datetime import datetime
from pathlib import Path

class SelfMonitor:
    """AI Agent自我监控系统"""
    
    def __init__(self, data_dir="./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.hostname = os.uname().nodename
        
    def collect_system_stats(self):
        """收集系统状态"""
        stats = {
            "timestamp": datetime.now().isoformat(),
            "hostname": self.hostname,
            "cpu": {
                "percent": psutil.cpu_percent(interval=1),
                "count_physical": psutil.cpu_count(logical=False),
                "count_logical": psutil.cpu_count(logical=True),
                "freq_mhz": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            "memory": {
                "total_mb": round(psutil.virtual_memory().total / 1024 / 1024, 2),
                "available_mb": round(psutil.virtual_memory().available / 1024 / 1024, 2),
                "percent": psutil.virtual_memory().percent,
                "used_mb": round(psutil.virtual_memory().used / 1024 / 1024, 2)
            },
            "disk": {
                "total_gb": round(psutil.disk_usage('/').total / 1024 / 1024 / 1024, 2),
                "used_gb": round(psutil.disk_usage('/').used / 1024 / 1024 / 1024, 2),
                "free_gb": round(psutil.disk_usage('/').free / 1024 / 1024 / 1024, 2),
                "percent": psutil.disk_usage('/').percent
            },
            "network": {
                "bytes_sent_mb": round(psutil.net_io_counters().bytes_sent / 1024 / 1024, 2),
                "bytes_recv_mb": round(psutil.net_io_counters().bytes_recv / 1024 / 1024, 2)
            },
            "processes": self._get_process_info(),
            "agent_context": self._get_agent_context()
        }
        return stats
    
    def _get_process_info(self):
        """获取进程信息"""
        processes = []
        try:
            # 获取当前Python进程及其子进程
            current_pid = os.getpid()
            parent = psutil.Process(current_pid)
            
            # 获取所有相关进程
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    pinfo = proc.info
                    # 只收集Python/OpenClaw相关进程
                    if any(keyword in pinfo['name'].lower() for keyword in ['python', 'node', 'openclaw', 'claw']):
                        processes.append({
                            "pid": pinfo['pid'],
                            "name": pinfo['name'],
                            "cpu_percent": pinfo['cpu_percent'],
                            "memory_percent": round(pinfo['memory_percent'], 2) if pinfo['memory_percent'] else 0,
                            "status": pinfo['status']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            processes.append({"error": str(e)})
        
        return {
            "total_count": len(processes),
            "agent_processes": processes[:10]  # 限制数量
        }
    
    def _get_agent_context(self):
        """获取Agent上下文信息"""
        context = {
            "workspace": os.getcwd(),
            "python_version": sys.version,
            "monitor_pid": os.getpid(),
            "uptime_seconds": time.time() - psutil.boot_time()
        }
        
        # 尝试获取OpenClaw相关信息
        try:
            result = subprocess.run(['openclaw', 'version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                context['openclaw_version'] = result.stdout.strip()
        except:
            context['openclaw_version'] = "unknown"
        
        return context
    
    def save_to_json(self, stats):
        """保存数据到JSON文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"monitor_{timestamp}.json"
        filepath = self.data_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        # 同时更新最新的汇总文件
        summary_file = self.data_dir / "latest.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def generate_report(self, stats):
        """生成简单的状态报告"""
        report_lines = [
            "=" * 60,
            "         🤖 AI Agent 自我监控报告",
            "=" * 60,
            f"📅 时间: {stats['timestamp']}",
            f"🖥️  主机: {stats['hostname']}",
            "",
            "【系统资源】",
            f"  CPU 使用率: {stats['cpu']['percent']}%",
            f"  CPU 核心数: {stats['cpu']['count_physical']} 物理 / {stats['cpu']['count_logical']} 逻辑",
            "",
            f"  内存总量: {stats['memory']['total_mb']} MB",
            f"  内存使用: {stats['memory']['used_mb']} MB ({stats['memory']['percent']}%)",
            f"  内存可用: {stats['memory']['available_mb']} MB",
            "",
            f"  磁盘总量: {stats['disk']['total_gb']} GB",
            f"  磁盘使用: {stats['disk']['used_gb']} GB ({stats['disk']['percent']}%)",
            f"  磁盘可用: {stats['disk']['free_gb']} GB",
            "",
            "【进程状态】",
            f"  Agent相关进程数: {stats['processes']['total_count']}",
        ]
        
        # 添加进程详情
        for proc in stats['processes']['agent_processes']:
            if 'error' not in proc:
                report_lines.append(f"    - PID {proc['pid']}: {proc['name']} (CPU:{proc['cpu_percent']}%, MEM:{proc['memory_percent']}%)")
        
        report_lines.extend([
            "",
            "【Agent上下文】",
            f"  工作目录: {stats['agent_context']['workspace']}",
            f"  监控PID: {stats['agent_context']['monitor_pid']}",
            f"  系统运行时间: {int(stats['agent_context']['uptime_seconds'] / 3600)} 小时",
            "",
            "=" * 60,
            "状态评估:",
        ])
        
        # 状态评估
        health_score = 100
        warnings = []
        
        if stats['cpu']['percent'] > 80:
            health_score -= 20
            warnings.append("⚠️ CPU使用率过高")
        if stats['memory']['percent'] > 80:
            health_score -= 20
            warnings.append("⚠️ 内存使用率过高")
        if stats['disk']['percent'] > 90:
            health_score -= 20
            warnings.append("⚠️ 磁盘空间不足")
        
        if health_score >= 90:
            report_lines.append("✅ 系统状态良好")
        elif health_score >= 70:
            report_lines.append("⚠️ 系统状态一般")
        else:
            report_lines.append("❌ 系统状态需要关注")
        
        report_lines.append(f"健康评分: {health_score}/100")
        
        if warnings:
            report_lines.extend(["", "警告:"])
            report_lines.extend(warnings)
        
        report_lines.append("=" * 60)
        
        report = "\n".join(report_lines)
        
        # 保存报告
        report_file = self.data_dir / "report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report
    
    def run(self):
        """运行监控"""
        print("🤖 AI Agent自我监控系统启动...")
        print(f"📁 数据保存目录: {self.data_dir.absolute()}")
        print()
        
        # 收集数据
        stats = self.collect_system_stats()
        
        # 保存到JSON
        json_file = self.save_to_json(stats)
        print(f"✅ 数据已保存: {json_file}")
        
        # 生成报告
        report = self.generate_report(stats)
        print(f"✅ 报告已生成: {self.data_dir / 'report.txt'}")
        print()
        
        # 打印报告
        print(report)
        
        return stats


def main():
    """主函数"""
    monitor = SelfMonitor()
    monitor.run()


if __name__ == "__main__":
    main()
