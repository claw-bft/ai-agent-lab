"""
财经日报生成器性能基准测试
Performance Benchmarks for Financial Daily Generator
"""

import time
import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime

# 导入被测模块
import sys
sys.path.insert(0, '/root/.openclaw/workspace/ai-agent-lab/financial-daily')

from generator import FinancialNewsDaily


class TestGeneratorPerformance:
    """日报生成器性能测试"""
    
    def test_report_generation_performance(self):
        """测试报告生成性能"""
        generator = FinancialNewsDaily()
        
        # 模拟新闻数据
        mock_news = [
            {
                "title": f"Test News {i}",
                "summary": f"Summary for test news {i}",
                "source": "Test Source",
                "url": f"https://example.com/news/{i}",
                "timestamp": datetime.now().isoformat()
            }
            for i in range(100)
        ]
        
        start = time.perf_counter()
        report = generator.generate_daily_report(mock_news)
        elapsed = time.perf_counter() - start
        
        # 100条新闻的报告应在0.5秒内生成
        assert elapsed < 0.5, f"报告生成耗时 {elapsed:.3f}s，超过0.5秒"
        assert report is not None
        assert "Financial Daily Report" in report or "财经日报" in report
    
    def test_market_data_processing_performance(self):
        """测试市场数据处理性能"""
        generator = FinancialNewsDaily()
        
        # 模拟大量市场数据
        mock_data = {
            "stocks": [
                {"symbol": f"STOCK{i}", "price": i * 10, "change": i * 0.1}
                for i in range(500)
            ],
            "indices": [
                {"name": f"INDEX{i}", "value": i * 100}
                for i in range(20)
            ]
        }
        
        start = time.perf_counter()
        processed = generator.process_market_data(mock_data)
        elapsed = time.perf_counter() - start
        
        # 数据处理应在0.3秒内完成
        assert elapsed < 0.3, f"数据处理耗时 {elapsed:.3f}s，超过0.3秒"
    
    def test_news_formatting_performance(self):
        """测试新闻格式化性能"""
        generator = FinancialNewsDaily()
        
        # 大量新闻条目
        news_items = [
            {
                "title": f"News Title {i}",
                "summary": f"This is a detailed summary for news item {i}",
                "source": "Financial Times",
                "category": ["stock", "market", "economy"][i % 3]
            }
            for i in range(200)
        ]
        
        start = time.perf_counter()
        formatted = generator.format_news_section(news_items)
        elapsed = time.perf_counter() - start
        
        # 格式化应在0.3秒内完成
        assert elapsed < 0.3, f"格式化耗时 {elapsed:.3f}s，超过0.3秒"
    
    def test_file_operations_performance(self):
        """测试文件操作性能"""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = FinancialNewsDaily()
            generator.output_dir = tmpdir
            
            # 测试保存多个报告
            start = time.perf_counter()
            for i in range(50):
                report_content = f"# Report {i}\n\nContent for report {i}"
                generator.save_report(f"report_{i}.md", report_content)
            elapsed = time.perf_counter() - start
            
            # 50个文件保存应在1秒内完成
            assert elapsed < 1.0, f"文件保存耗时 {elapsed:.3f}s，超过1秒"
            
            # 测试读取
            start = time.perf_counter()
            for i in range(50):
                content = generator.load_report(f"report_{i}.md")
            elapsed = time.perf_counter() - start
            
            # 50个文件读取应在0.5秒内完成
            assert elapsed < 0.5, f"文件读取耗时 {elapsed:.3f}s，超过0.5秒"


class TestDataProcessingPerformance:
    """数据处理性能测试"""
    
    def test_large_dataset_processing(self):
        """测试大数据集处理"""
        generator = FinancialNewsDaily()
        
        # 创建大型数据集
        large_dataset = [
            {
                "title": f"Large Dataset News {i}",
                "content": f"Content {i}" * 100,  # 较长内容
                "metadata": {
                    "tags": ["finance", "market", "stock"],
                    "sentiment": ["positive", "negative", "neutral"][i % 3],
                    "score": i * 0.1
                }
            }
            for i in range(1000)
        ]
        
        start = time.perf_counter()
        processed = generator.analyze_sentiment_batch(large_dataset)
        elapsed = time.perf_counter() - start
        
        # 1000条数据处理应在2秒内完成
        assert elapsed < 2.0, f"大数据集处理耗时 {elapsed:.3f}s，超过2秒"
    
    def test_filtering_performance(self):
        """测试数据过滤性能"""
        generator = FinancialNewsDaily()
        
        # 创建测试数据
        items = [
            {
                "category": ["stock", "bond", "forex", "commodity"][i % 4],
                "priority": i % 5,
                "timestamp": datetime.now().timestamp() - i * 3600
            }
            for i in range(1000)
        ]
        
        start = time.perf_counter()
        
        # 多次过滤操作
        for _ in range(100):
            filtered = generator.filter_by_category(items, "stock")
            filtered = generator.filter_by_priority(filtered, min_priority=3)
        
        elapsed = time.perf_counter() - start
        
        # 100次过滤应在1秒内完成
        assert elapsed < 1.0, f"过滤操作耗时 {elapsed:.3f}s，超过1秒"


class TestMemoryEfficiency:
    """内存效率测试"""
    
    def test_report_memory_footprint(self):
        """测试报告内存占用"""
        import sys
        
        generator = FinancialNewsDaily()
        
        # 生成大型报告
        large_report = generator.generate_daily_report([
            {"title": f"News {i}", "content": f"Content {i}" * 50}
            for i in range(100)
        ])
        
        report_size = sys.getsizeof(large_report)
        
        # 报告应小于1MB
        assert report_size < 1024 * 1024, f"报告内存占用 {report_size} bytes，超过1MB"
    
    def test_cache_efficiency(self):
        """测试缓存效率"""
        generator = FinancialNewsDaily()
        
        # 填充缓存
        for i in range(100):
            generator.cache_set(f"key_{i}", f"value_{i}")
        
        # 测试缓存命中率
        hits = 0
        for i in range(100):
            if generator.cache_get(f"key_{i}") is not None:
                hits += 1
        
        # 缓存命中率应为100%
        assert hits == 100, f"缓存命中率 {hits}%，低于100%"


class TestScalability:
    """可扩展性测试"""
    
    def test_concurrent_report_generation(self):
        """测试并发报告生成"""
        generator = FinancialNewsDaily()
        
        # 模拟多类别同时生成
        categories = ["stock", "bond", "forex", "commodity", "crypto"]
        
        start = time.perf_counter()
        
        reports = []
        for category in categories:
            news = [{"title": f"{category} news {i}", "category": category} for i in range(50)]
            report = generator.generate_category_report(category, news)
            reports.append(report)
        
        elapsed = time.perf_counter() - start
        
        # 5个类别报告应在2秒内完成
        assert elapsed < 2.0, f"并发生成耗时 {elapsed:.3f}s，超过2秒"
        assert len(reports) == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
