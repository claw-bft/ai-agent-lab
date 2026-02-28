"""
Notification Service 性能基准测试

测试通知服务的性能指标，包括：
- 消息创建性能
- 消息格式转换性能
- 批量通知性能
"""

import time
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notify import NotificationService, NotificationMessage, NotificationChannel


class PerformanceBenchmark:
    """性能基准测试"""
    
    def __init__(self):
        self.results = []
        self.service = NotificationService(feishu_key="test_key")
    
    def benchmark_message_creation(self, iterations=10000):
        """测试消息创建性能"""
        start = time.time()
        
        for i in range(iterations):
            msg = NotificationMessage(
                title=f"测试通知 {i}",
                content=f"这是第 {i} 条测试消息的内容",
                level="info"
            )
        
        elapsed = time.time() - start
        ops_per_sec = iterations / elapsed
        
        self.results.append({
            "test": "消息创建",
            "iterations": iterations,
            "elapsed_ms": elapsed * 1000,
            "ops_per_sec": int(ops_per_sec)
        })
        
        return elapsed, ops_per_sec
    
    def benchmark_feishu_card_conversion(self, iterations=10000):
        """测试飞书卡片格式转换性能"""
        msg = NotificationMessage(
            title="性能测试",
            content="测试内容",
            level="info",
            url="https://example.com"
        )
        
        start = time.time()
        
        for _ in range(iterations):
            card = msg.to_feishu_card()
        
        elapsed = time.time() - start
        ops_per_sec = iterations / elapsed
        
        self.results.append({
            "test": "飞书卡片转换",
            "iterations": iterations,
            "elapsed_ms": elapsed * 1000,
            "ops_per_sec": int(ops_per_sec)
        })
        
        return elapsed, ops_per_sec
    
    def benchmark_text_conversion(self, iterations=10000):
        """测试纯文本格式转换性能"""
        msg = NotificationMessage(
            title="性能测试",
            content="测试内容",
            level="warning"
        )
        
        start = time.time()
        
        for _ in range(iterations):
            text = msg.to_text()
        
        elapsed = time.time() - start
        ops_per_sec = iterations / elapsed
        
        self.results.append({
            "test": "文本转换",
            "iterations": iterations,
            "elapsed_ms": elapsed * 1000,
            "ops_per_sec": int(ops_per_sec)
        })
        
        return elapsed, ops_per_sec
    
    def benchmark_different_levels(self, iterations=5000):
        """测试不同级别消息创建性能"""
        levels = ["info", "warning", "error", "success"]
        
        start = time.time()
        
        for i in range(iterations):
            level = levels[i % len(levels)]
            msg = NotificationMessage(
                title=f"{level.upper()} 通知",
                content=f"级别: {level}",
                level=level
            )
        
        elapsed = time.time() - start
        ops_per_sec = iterations / elapsed
        
        self.results.append({
            "test": "多级别消息创建",
            "iterations": iterations,
            "elapsed_ms": elapsed * 1000,
            "ops_per_sec": int(ops_per_sec)
        })
        
        return elapsed, ops_per_sec
    
    def benchmark_service_initialization(self, iterations=1000):
        """测试服务初始化性能"""
        start = time.time()
        
        for _ in range(iterations):
            service = NotificationService(feishu_key="test_key")
        
        elapsed = time.time() - start
        ops_per_sec = iterations / elapsed
        
        self.results.append({
            "test": "服务初始化",
            "iterations": iterations,
            "elapsed_ms": elapsed * 1000,
            "ops_per_sec": int(ops_per_sec)
        })
        
        return elapsed, ops_per_sec
    
    def run_all_benchmarks(self):
        """运行所有性能测试"""
        print("=" * 60)
        print("Notification Service 性能基准测试")
        print("=" * 60)
        
        self.benchmark_message_creation()
        self.benchmark_feishu_card_conversion()
        self.benchmark_text_conversion()
        self.benchmark_different_levels()
        self.benchmark_service_initialization()
        
        print("\n测试结果汇总:")
        print("-" * 60)
        print(f"{'测试项目':<20} {'迭代次数':>10} {'耗时(ms)':>12} {'操作/秒':>12}")
        print("-" * 60)
        
        for result in self.results:
            print(f"{result['test']:<20} {result['iterations']:>10} "
                  f"{result['elapsed_ms']:>12.2f} {result['ops_per_sec']:>12}")
        
        print("-" * 60)
        
        # 计算平均性能
        avg_ops = sum(r['ops_per_sec'] for r in self.results) / len(self.results)
        print(f"\n平均性能: {avg_ops:,.0f} 操作/秒")
        
        # 性能评级
        if avg_ops > 50000:
            rating = "优秀"
        elif avg_ops > 20000:
            rating = "良好"
        elif avg_ops > 10000:
            rating = "合格"
        else:
            rating = "待优化"
        
        print(f"性能评级: {rating}")
        print("=" * 60)
        
        return self.results


def main():
    """主函数"""
    benchmark = PerformanceBenchmark()
    results = benchmark.run_all_benchmarks()
    return results


if __name__ == "__main__":
    main()
