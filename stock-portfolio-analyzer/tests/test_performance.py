"""
性能基准测试 - Stock Portfolio Analyzer
"""
import time
import sys
import os
import importlib.util

spec = importlib.util.spec_from_file_location("stock_analyzer", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "stock-analyzer.py"))
stock_analyzer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stock_analyzer)
StockAnalyzer = stock_analyzer.StockAnalyzer


def benchmark_analyzer_performance():
    """基准测试：股票分析性能"""
    print("=" * 60)
    print("股票分析器性能基准测试")
    print("=" * 60)
    
    # 测试1: 初始化性能
    start = time.time()
    analyzer = StockAnalyzer()
    init_time = time.time() - start
    print(f"\n1. 初始化性能")
    print(f"   耗时: {init_time:.4f}s")
    print(f"   状态: {'✅ 通过' if init_time < 0.5 else '⚠️ 较慢'}")
    
    # 测试2: 股票解析性能
    start = time.time()
    test_input = "\n".join([f"STOCK{i},股票{i},科技,100,{50.0+i}" for i in range(50)])
    result = analyzer.parse_stocks(test_input)
    parse_time = time.time() - start
    print(f"\n2. 股票解析性能 (50条)")
    print(f"   耗时: {parse_time:.4f}s")
    print(f"   状态: {'✅ 通过' if parse_time < 0.1 else '⚠️ 较慢'}")
    
    # 测试3: HTML生成性能
    report = stock_analyzer.AnalysisReport(
        report_id="test-001",
        timestamp="2024-01-01",
        stocks=[],
        summary={"total": 50, "buy": 20, "hold": 20, "sell": 10},
        overall_recommendation="买入"
    )
    html_gen = stock_analyzer.ReportAgent()
    start = time.time()
    html = html_gen.generate_html(report)
    html_time = time.time() - start
    print(f"\n3. HTML报告生成性能")
    print(f"   耗时: {html_time:.4f}s")
    print(f"   状态: {'✅ 通过' if html_time < 0.5 else '⚠️ 较慢'}")
    
    # 测试4: 大规模数据解析性能
    print(f"\n4. 大规模数据性能测试")
    large_input = "\n".join([f"STOCK{i},股票{i},科技,1000,{100.0}" for i in range(500)])
    start = time.time()
    result = analyzer.parse_stocks(large_input)
    large_parse_time = time.time() - start
    print(f"   解析500条股票: {large_parse_time:.4f}s")
    print(f"   状态: {'✅ 通过' if large_parse_time < 1.0 else '⚠️ 较慢'}")
    
    print("\n" + "=" * 60)
    print("性能基准测试完成")
    print("=" * 60)
    
    return {
        "init_time": init_time,
        "parse_time": parse_time,
        "html_time": html_time,
        "large_parse_time": large_parse_time
    }


if __name__ == "__main__":
    benchmark_analyzer_performance()
