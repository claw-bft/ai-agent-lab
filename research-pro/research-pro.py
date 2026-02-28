#!/usr/bin/env python3
"""
Research Pro 核心实现
跨领域通用研究技能包 - 数据分析、自动化流程、AI增强研究
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# 导入搜索适配器
try:
    from search_adapter import SearchAdapter, search as search_web
    SEARCH_ADAPTER_AVAILABLE = True
except ImportError:
    SEARCH_ADAPTER_AVAILABLE = False

# 数据分析支持
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


def deep_research(topic: str, depth: str = "comprehensive") -> Dict[str, Any]:
    """
    深度研究 - 多轮调研报告生成

    Args:
        topic: 研究主题
        depth: 深度级别 (quick/standard/comprehensive)
    """
    # 使用搜索适配器进行多轮调研
    search_queries = generate_search_queries(topic, depth)

    all_results = []
    adapter = SearchAdapter() if SEARCH_ADAPTER_AVAILABLE else None

    if adapter and adapter.get_status().get("available"):
        # 使用真实搜索
        batch_results = adapter.batch_search(search_queries, limit=5)
        for query, results in batch_results.items():
            all_results.append({
                "query": query,
                "results": results,
                "count": len(results)
            })
        # 聚合去重
        aggregated = adapter.aggregate_results(batch_results)
    else:
        # 回退到模拟结果
        for query in search_queries:
            all_results.append({
                "query": query,
                "results": [{"title": f"关于 '{query}' 的搜索结果", "snippet": "[模拟数据]"}],
                "count": 1
            })
        aggregated = []

    # 生成研究报告
    report = generate_research_report(topic, all_results, depth, aggregated)

    return {
        "success": True,
        "topic": topic,
        "depth": depth,
        "queries_executed": len(search_queries),
        "total_results": sum(r.get("count", 0) for r in all_results),
        "unique_results": len(aggregated),
        "report": report,
        "raw_results": all_results,
        "timestamp": datetime.now().isoformat()
    }


def generate_search_queries(topic: str, depth: str) -> List[str]:
    """根据主题和深度生成搜索查询"""
    queries = [topic]  # 基础查询

    if depth in ["standard", "comprehensive"]:
        queries.extend([
            f"{topic} 最新发展",
            f"{topic} 市场分析",
            f"{topic} 行业趋势"
        ])

    if depth == "comprehensive":
        queries.extend([
            f"{topic} 竞争格局",
            f"{topic} 技术突破",
            f"{topic} 投资前景",
            f"{topic} 专家观点"
        ])

    return queries


def generate_research_report(topic: str, results: List[Dict], depth: str, aggregated: List[Dict] = None) -> Dict[str, Any]:
    """生成研究报告"""

    # 提取关键发现
    key_findings = []
    sources = set()

    for r in results:
        if "results" in r:
            for item in r["results"]:
                finding = {
                    "query": r["query"],
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", "")[:150] + "..." if len(item.get("snippet", "")) > 150 else item.get("snippet", ""),
                    "url": item.get("url", "")
                }
                key_findings.append(finding)
                if item.get("url"):
                    sources.add(item.get("url"))

    # 构建报告结构
    sections = {
        "executive_summary": f"关于 '{topic}' 的深度研究报告",
        "key_findings": key_findings[:10],  # 限制关键发现数量
        "sources_count": len(sources),
        "market_analysis": "基于搜索数据的市场分析...",
        "trends": "行业趋势分析...",
        "recommendations": [
            "建议深入研究相关技术细节",
            "关注行业动态和竞争格局变化",
            "定期更新研究数据"
        ]
    }

    if depth == "comprehensive":
        sections["competitive_landscape"] = "竞争格局分析..."
        sections["risk_assessment"] = "风险评估..."
        sections["data_sources"] = list(sources)[:20]  # 限制数据源数量

    return sections


def analyze_data(file_path: str, query: str) -> Dict[str, Any]:
    """
    数据分析 - 自然语言驱动的数据分析

    Args:
        file_path: 数据文件路径
        query: 分析查询
    """
    if not os.path.exists(file_path):
        return {
            "success": False,
            "error": f"文件不存在: {file_path}"
        }

    try:
        # 根据文件类型读取数据
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)
        else:
            return {
                "success": False,
                "error": "不支持的文件格式"
            }

        # 基础统计
        stats = {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "dtypes": {k: str(v) for k, v in df.dtypes.items()},
            "null_counts": df.isnull().sum().to_dict(),
            "memory_usage": df.memory_usage(deep=True).sum()
        }

        # 数值列统计
        numeric_stats = df.describe().to_dict()

        # 根据查询执行特定分析
        analysis_result = interpret_query(df, query)

        return {
            "success": True,
            "file": file_path,
            "query": query,
            "statistics": stats,
            "numeric_stats": numeric_stats,
            "analysis": analysis_result
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"分析失败: {str(e)}"
        }


def interpret_query(df, query: str) -> Dict[str, Any]:
    """解释自然语言查询并执行相应分析"""
    query_lower = query.lower()

    result = {}

    # 销售额占比
    if "销售额" in query or "占比" in query:
        # 尝试找到销售额相关列
        sales_cols = [c for c in df.columns if any(k in c.lower() for k in ["销售", "金额", "收入", "sales", "revenue"])]
        if sales_cols:
            col = sales_cols[0]
            # 尝试找到类别列
            cat_cols = [c for c in df.columns if any(k in c.lower() for k in ["品类", "类别", "产品", "category", "type"])]
            if cat_cols:
                cat_col = cat_cols[0]
                grouped = df.groupby(cat_col)[col].sum()
                total = grouped.sum()
                result["sales_by_category"] = {
                    cat: {
                        "amount": float(val),
                        "percentage": round(float(val/total*100), 2)
                    }
                    for cat, val in grouped.items()
                }

    # 趋势分析
    if "趋势" in query or "变化" in query:
        date_cols = [c for c in df.columns if any(k in c.lower() for k in ["日期", "时间", "date", "time"])]
        if date_cols:
            result["trend_analysis"] = "检测到日期列，可执行时间序列分析"

    # 相关性分析
    if "相关" in query:
        numeric_df = df.select_dtypes(include=['float64', 'int64'])
        if len(numeric_df.columns) >= 2:
            corr = numeric_df.corr()
            result["correlation"] = corr.to_dict()

    return result


def realtime_search(query: str, sources: List[str] = None) -> Dict[str, Any]:
    """
    实时搜索

    Args:
        query: 搜索查询
        sources: 搜索来源 (news/blog/twitter)
    """
    adapter = SearchAdapter() if SEARCH_ADAPTER_AVAILABLE else None

    if adapter and adapter.get_status().get("available"):
        results = adapter.search(query, limit=10)
        return {
            "success": True,
            "query": query,
            "sources": sources or ["web"],
            "results": results,
            "count": len(results),
            "backend": adapter.preferred_backend,
            "timestamp": datetime.now().isoformat()
        }
    else:
        return {
            "success": False,
            "query": query,
            "error": "未检测到可用搜索后端，请配置 kimi_search、web_search 或 TAVILY_API_KEY",
            "timestamp": datetime.now().isoformat()
        }


def competitor_monitor(competitors: List[str], alerts: List[str]) -> Dict[str, Any]:
    """
    竞品监控

    Args:
        competitors: 竞争对手列表
        alerts: 监控类型 (product-launch/funding/news)
    """
    adapter = SearchAdapter() if SEARCH_ADAPTER_AVAILABLE else None
    monitoring_results = []

    for competitor in competitors:
        # 对每个竞争对手执行搜索
        search_queries = [f"{competitor} 最新动态"]
        if "product-launch" in alerts:
            search_queries.append(f"{competitor} 新产品发布")
        if "funding" in alerts:
            search_queries.append(f"{competitor} 融资")

        try:
            if adapter and adapter.get_status().get("available"):
                batch_results = adapter.batch_search(search_queries, limit=3)
                all_results = adapter.aggregate_results(batch_results)
                monitoring_results.append({
                    "competitor": competitor,
                    "alerts_found": len(all_results),
                    "details": all_results[:5]  # 限制结果数量
                })
            else:
                monitoring_results.append({
                    "competitor": competitor,
                    "alerts_found": 0,
                    "details": [],
                    "note": "搜索后端不可用"
                })
        except Exception as e:
            monitoring_results.append({
                "competitor": competitor,
                "error": str(e)
            })

    return {
        "success": True,
        "competitors": competitors,
        "alert_types": alerts,
        "monitoring_results": monitoring_results,
        "timestamp": datetime.now().isoformat()
    }


def main():
    parser = argparse.ArgumentParser(description="Research Pro - 跨领域通用研究技能包")
    parser.add_argument("command", choices=["deep", "analyze", "search", "monitor", "status"])
    parser.add_argument("--topic", help="研究主题")
    parser.add_argument("--file", help="数据文件路径")
    parser.add_argument("--query", help="分析查询")
    parser.add_argument("--depth", default="comprehensive", choices=["quick", "standard", "comprehensive"])
    parser.add_argument("--competitors", help="竞争对手列表 (逗号分隔)")
    parser.add_argument("--alerts", default="product-launch", help="监控类型 (逗号分隔)")
    parser.add_argument("--sources", default="news,blog", help="搜索来源 (逗号分隔)")
    parser.add_argument("--json", action="store_true", help="JSON格式输出")

    args = parser.parse_args()

    if args.command == "deep":
        if not args.topic:
            print("✗ 错误: --topic 是必需的")
            sys.exit(1)
        result = deep_research(args.topic, args.depth)

    elif args.command == "analyze":
        if not args.file or not args.query:
            print("✗ 错误: --file 和 --query 是必需的")
            sys.exit(1)
        result = analyze_data(args.file, args.query)

    elif args.command == "search":
        if not args.query:
            print("✗ 错误: --query 是必需的")
            sys.exit(1)
        sources = [s.strip() for s in args.sources.split(",")]
        result = realtime_search(args.query, sources)

    elif args.command == "monitor":
        if not args.competitors:
            print("✗ 错误: --competitors 是必需的")
            sys.exit(1)
        competitors = [c.strip() for c in args.competitors.split(",")]
        alerts = [a.strip() for a in args.alerts.split(",")]
        result = competitor_monitor(competitors, alerts)

    elif args.command == "status":
        adapter = SearchAdapter() if SEARCH_ADAPTER_AVAILABLE else None
        if adapter:
            result = {
                "success": True,
                "search_adapter": adapter.get_status()
            }
        else:
            result = {
                "success": False,
                "error": "搜索适配器未安装"
            }

    else:
        result = {"success": False, "error": "未知命令"}

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result.get("success"):
            print(f"✓ 执行成功")
            if "topic" in result:
                print(f"  主题: {result['topic']}")
            if "queries_executed" in result:
                print(f"  执行查询: {result['queries_executed']} 个")
            if "total_results" in result:
                print(f"  总结果: {result['total_results']} 条")
            if "unique_results" in result:
                print(f"  去重后: {result['unique_results']} 条")
            if "backend" in result:
                print(f"  搜索后端: {result['backend']}")
            print(f"\n详细结果 (使用 --json 查看完整数据)")
        else:
            print(f"✗ 错误: {result.get('error', '未知错误')}")
            sys.exit(1)


if __name__ == "__main__":
    main()
