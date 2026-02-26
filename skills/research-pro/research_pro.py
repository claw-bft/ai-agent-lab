#!/usr/bin/env python3
"""
Research Pro - 专业研究技能包
实现真实搜索、深度研究、数据分析功能
"""

import os
import sys
import json
import time
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))


@dataclass
class SearchResult:
    """搜索结果"""
    title: str
    url: str
    snippet: str
    source: str
    timestamp: Optional[str] = None


@dataclass
class ResearchReport:
    """研究报告"""
    topic: str
    summary: str
    key_findings: List[str] = field(default_factory=list)
    sources: List[SearchResult] = field(default_factory=list)
    analysis: str = ""
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())


class WebSearchClient:
    """网页搜索客户端 - 支持多种搜索源"""
    
    def __init__(self):
        self.brave_api_key = os.environ.get("BRAVE_API_KEY")
        self.tavily_api_key = os.environ.get("TAVILY_API_KEY")
        self.last_search_results: List[SearchResult] = []
    
    def search(self, query: str, count: int = 10, sources: List[str] = None) -> List[SearchResult]:
        """
        执行搜索
        
        Args:
            query: 搜索查询
            count: 结果数量
            sources: 来源类型 [news, blog, academic, web]
        """
        results = []
        
        # 优先使用 Brave Search API
        if self.brave_api_key:
            results = self._search_brave(query, count)
        # 备选 Tavily
        elif self.tavily_api_key:
            results = self._search_tavily(query, count)
        else:
            # 模拟搜索结果（用于演示）
            results = self._mock_search(query, count)
        
        self.last_search_results = results
        return results
    
    def _search_brave(self, query: str, count: int) -> List[SearchResult]:
        """使用 Brave Search API"""
        import urllib.request
        import urllib.parse
        
        encoded_query = urllib.parse.quote(query)
        url = f"https://api.search.brave.com/res/v1/web/search?q={encoded_query}&count={count}"
        
        headers = {
            "X-Subscription-Token": self.brave_api_key,
            "Accept": "application/json"
        }
        
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                results = []
                for item in data.get("web", {}).get("results", []):
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=item.get("description", ""),
                        source="brave"
                    ))
                return results
        except Exception as e:
            print(f"Brave search error: {e}")
            return self._mock_search(query, count)
    
    def _search_tavily(self, query: str, count: int) -> List[SearchResult]:
        """使用 Tavily API"""
        import urllib.request
        
        url = "https://api.tavily.com/search"
        data = json.dumps({
            "api_key": self.tavily_api_key,
            "query": query,
            "search_depth": "basic",
            "include_answer": False,
            "max_results": count
        }).encode('utf-8')
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                results = []
                for item in data.get("results", []):
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=item.get("content", ""),
                        source="tavily"
                    ))
                return results
        except Exception as e:
            print(f"Tavily search error: {e}")
            return self._mock_search(query, count)
    
    def _mock_search(self, query: str, count: int) -> List[SearchResult]:
        """模拟搜索结果（当没有API key时使用）"""
        return [
            SearchResult(
                title=f"关于 '{query}' 的搜索结果示例",
                url="https://example.com/search-result-1",
                snippet=f"这是关于{query}的模拟搜索结果。实际使用时请配置 BRAVE_API_KEY 或 TAVILY_API_KEY 环境变量以获取真实数据。",
                source="mock"
            ),
            SearchResult(
                title="Research Pro 使用指南",
                url="https://github.com/claw-bft/ai-agent-lab",
                snippet="Research Pro 是 ai-agent-lab 项目的一部分，提供深度研究、数据分析和竞品监控功能。",
                source="mock"
            )
        ]


class DeepResearchEngine:
    """深度研究引擎"""
    
    def __init__(self):
        self.search_client = WebSearchClient()
    
    def research(self, topic: str, depth: str = "comprehensive") -> ResearchReport:
        """
        执行深度研究
        
        Args:
            topic: 研究主题
            depth: 深度级别 [quick, standard, comprehensive]
        """
        # 1. 生成搜索查询
        queries = self._generate_queries(topic, depth)
        
        # 2. 执行多维度搜索
        all_results = []
        for query in queries:
            results = self.search_client.search(query, count=5)
            all_results.extend(results)
            time.sleep(0.5)  # 避免请求过快
        
        # 3. 去重和排序
        unique_results = self._deduplicate_results(all_results)
        
        # 4. 生成报告
        report = self._generate_report(topic, unique_results, depth)
        
        return report
    
    def _generate_queries(self, topic: str, depth: str) -> List[str]:
        """生成多角度搜索查询"""
        queries = [topic]  # 基础查询
        
        if depth in ["standard", "comprehensive"]:
            queries.extend([
                f"{topic} 最新趋势",
                f"{topic} 行业分析",
                f"{topic} 市场报告"
            ])
        
        if depth == "comprehensive":
            queries.extend([
                f"{topic} 技术发展",
                f"{topic} 竞争格局",
                f"{topic} 投资融资",
                f"{topic} 专家观点"
            ])
        
        return queries
    
    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """去重并排序结果"""
        seen_urls = set()
        unique = []
        
        for r in results:
            if r.url not in seen_urls:
                seen_urls.add(r.url)
                unique.append(r)
        
        return unique[:20]  # 最多保留20条
    
    def _generate_report(self, topic: str, results: List[SearchResult], depth: str) -> ResearchReport:
        """生成研究报告"""
        # 提取关键发现
        key_findings = self._extract_findings(results)
        
        # 生成摘要
        summary = f"关于「{topic}」的深度研究报告\n\n"
        summary += f"搜索深度: {depth}\n"
        summary += f"数据来源: {len(results)} 个信源\n"
        summary += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        # 分析内容
        analysis = self._analyze_content(results, topic)
        
        return ResearchReport(
            topic=topic,
            summary=summary,
            key_findings=key_findings,
            sources=results,
            analysis=analysis
        )
    
    def _extract_findings(self, results: List[SearchResult]) -> List[str]:
        """从搜索结果中提取关键发现"""
        findings = []
        
        for i, r in enumerate(results[:10], 1):
            if r.snippet:
                # 提取核心句子
                sentences = re.split(r'[。！？]', r.snippet)
                for s in sentences[:2]:
                    if len(s) > 20:
                        findings.append(f"[{i}] {s.strip()}")
                        break
        
        return findings[:8]  # 最多8条发现
    
    def _analyze_content(self, results: List[SearchResult], topic: str) -> str:
        """分析内容并生成洞察"""
        domains = {}
        for r in results:
            try:
                domain = r.url.split('/')[2]
                domains[domain] = domains.get(domain, 0) + 1
            except:
                pass
        
        analysis = "【信源分布】\n"
        for domain, count in sorted(domains.items(), key=lambda x: -x[1])[:5]:
            analysis += f"  - {domain}: {count} 条\n"
        
        analysis += f"\n【研究建议】\n"
        analysis += f"1. 关于「{topic}」的信息主要来自 {len(domains)} 个不同域名\n"
        analysis += f"2. 建议进一步验证高权重信源的内容\n"
        analysis += f"3. 可结合实时数据更新研究结论\n"
        
        return analysis


class DataAnalyzer:
    """数据分析器"""
    
    def analyze_file(self, file_path: str, query: str) -> Dict[str, Any]:
        """
        分析数据文件
        
        Args:
            file_path: 文件路径
            query: 分析查询
        """
        path = Path(file_path)
        
        if not path.exists():
            return {"error": f"文件不存在: {file_path}"}
        
        # 根据文件类型选择解析方式
        if path.suffix == '.csv':
            return self._analyze_csv(path, query)
        elif path.suffix in ['.json', '.jsonl']:
            return self._analyze_json(path, query)
        else:
            return {"error": f"不支持的文件格式: {path.suffix}"}
    
    def _analyze_csv(self, path: Path, query: str) -> Dict[str, Any]:
        """分析CSV文件"""
        try:
            import csv
            
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                headers = reader.fieldnames or []
            
            return {
                "file": str(path),
                "format": "CSV",
                "rows": len(rows),
                "columns": headers,
                "sample": rows[:3] if rows else [],
                "query": query,
                "note": "完整分析需要 pandas 库支持"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_json(self, path: Path, query: str) -> Dict[str, Any]:
        """分析JSON文件"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                return {
                    "file": str(path),
                    "format": "JSON",
                    "type": "array",
                    "count": len(data),
                    "sample": data[:3] if data else [],
                    "query": query
                }
            else:
                return {
                    "file": str(path),
                    "format": "JSON",
                    "type": "object",
                    "keys": list(data.keys()),
                    "query": query
                }
        except Exception as e:
            return {"error": str(e)}


class CompetitorMonitor:
    """竞品监控器"""
    
    def __init__(self):
        self.search_client = WebSearchClient()
    
    def monitor(self, competitors: List[str], alert_types: List[str] = None) -> Dict[str, Any]:
        """
        监控竞品动态
        
        Args:
            competitors: 竞品名称列表
            alert_types: 关注类型 [product-launch, funding, partnership, acquisition]
        """
        if alert_types is None:
            alert_types = ["product-launch", "funding", "news"]
        
        all_alerts = []
        
        for competitor in competitors:
            for alert_type in alert_types:
                query = self._build_monitor_query(competitor, alert_type)
                results = self.search_client.search(query, count=3)
                
                for r in results:
                    all_alerts.append({
                        "competitor": competitor,
                        "type": alert_type,
                        "title": r.title,
                        "url": r.url,
                        "snippet": r.snippet
                    })
        
        return {
            "monitored_competitors": competitors,
            "alert_types": alert_types,
            "alerts_found": len(all_alerts),
            "alerts": all_alerts[:20],  # 最多返回20条
            "generated_at": datetime.now().isoformat()
        }
    
    def _build_monitor_query(self, competitor: str, alert_type: str) -> str:
        """构建监控查询"""
        type_keywords = {
            "product-launch": "发布 新品 产品",
            "funding": "融资 投资 估值",
            "partnership": "合作 伙伴 战略",
            "acquisition": "收购 并购",
            "news": "新闻 动态 公告"
        }
        
        keywords = type_keywords.get(alert_type, "")
        return f"{competitor} {keywords}"


# ============ 公共API ============

def deep_research(topic: str, depth: str = "comprehensive") -> Dict[str, Any]:
    """
    执行深度研究
    
    Args:
        topic: 研究主题
        depth: 深度级别 [quick, standard, comprehensive]
    
    Returns:
        研究报告字典
    """
    engine = DeepResearchEngine()
    report = engine.research(topic, depth)
    
    return {
        "topic": report.topic,
        "summary": report.summary,
        "key_findings": report.key_findings,
        "sources_count": len(report.sources),
        "sources": [
            {"title": s.title, "url": s.url, "snippet": s.snippet}
            for s in report.sources[:10]
        ],
        "analysis": report.analysis,
        "generated_at": report.generated_at
    }


def search(query: str, count: int = 10) -> List[Dict[str, str]]:
    """
    执行搜索
    
    Args:
        query: 搜索查询
        count: 结果数量
    
    Returns:
        搜索结果列表
    """
    client = WebSearchClient()
    results = client.search(query, count)
    
    return [
        {"title": r.title, "url": r.url, "snippet": r.snippet}
        for r in results
    ]


def analyze_data(file_path: str, query: str) -> Dict[str, Any]:
    """
    分析数据文件
    
    Args:
        file_path: 文件路径
        query: 分析查询
    
    Returns:
        分析结果
    """
    analyzer = DataAnalyzer()
    return analyzer.analyze_file(file_path, query)


def monitor_competitors(competitors: List[str], alert_types: List[str] = None) -> Dict[str, Any]:
    """
    监控竞品动态
    
    Args:
        competitors: 竞品名称列表
        alert_types: 关注类型
    
    Returns:
        监控报告
    """
    monitor = CompetitorMonitor()
    return monitor.monitor(competitors, alert_types)


# ============ CLI 入口 ============

def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Research Pro - 专业研究工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # deep 命令
    deep_parser = subparsers.add_parser("deep", help="深度研究")
    deep_parser.add_argument("--topic", "-t", required=True, help="研究主题")
    deep_parser.add_argument("--depth", "-d", default="comprehensive", 
                            choices=["quick", "standard", "comprehensive"],
                            help="研究深度")
    
    # search 命令
    search_parser = subparsers.add_parser("search", help="实时搜索")
    search_parser.add_argument("--query", "-q", required=True, help="搜索查询")
    search_parser.add_argument("--count", "-c", type=int, default=10, help="结果数量")
    
    # analyze 命令
    analyze_parser = subparsers.add_parser("analyze", help="数据分析")
    analyze_parser.add_argument("--file", "-f", required=True, help="数据文件路径")
    analyze_parser.add_argument("--query", "-q", default="统计分析", help="分析查询")
    
    # monitor 命令
    monitor_parser = subparsers.add_parser("monitor", help="竞品监控")
    monitor_parser.add_argument("--competitors", "-c", required=True, 
                               help="竞品名称，逗号分隔")
    
    args = parser.parse_args()
    
    if args.command == "deep":
        result = deep_research(args.topic, args.depth)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.command == "search":
        result = search(args.query, args.count)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.command == "analyze":
        result = analyze_data(args.file, args.query)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.command == "monitor":
        competitors = [c.strip() for c in args.competitors.split(",")]
        result = monitor_competitors(competitors)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
