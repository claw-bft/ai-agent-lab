#!/usr/bin/env python3
"""
搜索适配器 - 统一搜索接口
支持 kimi_search 和 web_search 工具调用
"""

import json
import subprocess
from typing import List, Dict, Any, Optional
from datetime import datetime

class SearchAdapter:
    """搜索适配器 - 统一多种搜索后端"""
    
    def __init__(self):
        self.backends = self._detect_backends()
        self.preferred_backend = self._select_backend()
    
    def _detect_backends(self) -> Dict[str, bool]:
        """检测可用的搜索后端"""
        backends = {
            "kimi_search": False,
            "web_search": False,
            "tavily": False
        }
        
        # 检测 kimi_search
        try:
            result = subprocess.run(
                ["python3", "-c", "from kimi_search import kimi_search; print('OK')"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                backends["kimi_search"] = True
        except:
            pass
        
        # 检测 web_search
        try:
            result = subprocess.run(
                ["python3", "-c", "from web_search import web_search; print('OK')"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                backends["web_search"] = True
        except:
            pass
        
        # 检测 Tavily
        try:
            import os
            if os.environ.get("TAVILY_API_KEY"):
                backends["tavily"] = True
        except:
            pass
        
        return backends
    
    def _select_backend(self) -> str:
        """选择最佳可用后端"""
        priority = ["kimi_search", "web_search", "tavily"]
        for backend in priority:
            if self.backends.get(backend):
                return backend
        return "none"
    
    def search(self, query: str, limit: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """
        执行搜索
        
        Args:
            query: 搜索查询
            limit: 返回结果数量
            **kwargs: 额外参数
        
        Returns:
            搜索结果列表
        """
        if self.preferred_backend == "kimi_search":
            return self._search_kimi(query, limit, **kwargs)
        elif self.preferred_backend == "web_search":
            return self._search_web(query, limit, **kwargs)
        elif self.preferred_backend == "tavily":
            return self._search_tavily(query, limit, **kwargs)
        else:
            # 无可用后端，返回模拟结果
            return self._mock_search(query)
    
    def _search_kimi(self, query: str, limit: int, **kwargs) -> List[Dict[str, Any]]:
        """使用 kimi_search 执行搜索"""
        try:
            # 构建搜索脚本
            search_script = f'''
import json
from kimi_search import kimi_search

results = kimi_search("{query}", limit={limit})
print(json.dumps(results, ensure_ascii=False))
'''
            result = subprocess.run(
                ["python3", "-c", search_script],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if isinstance(data, list):
                    return self._normalize_kimi_results(data)
                elif isinstance(data, dict) and "results" in data:
                    return self._normalize_kimi_results(data["results"])
            
            return [{"error": f"搜索失败: {result.stderr}"}]
        except Exception as e:
            return [{"error": f"搜索异常: {str(e)}"}]
    
    def _search_web(self, query: str, limit: int, **kwargs) -> List[Dict[str, Any]]:
        """使用 web_search 执行搜索"""
        try:
            search_script = f'''
import json
from web_search import web_search

results = web_search("{query}", count={limit})
print(json.dumps(results, ensure_ascii=False))
'''
            result = subprocess.run(
                ["python3", "-c", search_script],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return self._normalize_web_results(data)
            
            return [{"error": f"搜索失败: {result.stderr}"}]
        except Exception as e:
            return [{"error": f"搜索异常: {str(e)}"}]
    
    def _search_tavily(self, query: str, limit: int, **kwargs) -> List[Dict[str, Any]]:
        """使用 Tavily API 执行搜索"""
        try:
            from tavily import TavilyClient
            import os
            
            client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))
            response = client.search(query=query, max_results=limit)
            
            return self._normalize_tavily_results(response.get("results", []))
        except Exception as e:
            return [{"error": f"Tavily搜索失败: {str(e)}"}]
    
    def _normalize_kimi_results(self, results: List[Dict]) -> List[Dict[str, Any]]:
        """标准化 kimi_search 结果"""
        normalized = []
        for r in results:
            normalized.append({
                "title": r.get("title", "无标题"),
                "snippet": r.get("snippet", r.get("content", "")[:200]),
                "url": r.get("url", r.get("link", "")),
                "source": r.get("source", "web"),
                "timestamp": datetime.now().isoformat()
            })
        return normalized
    
    def _normalize_web_results(self, results: List[Dict]) -> List[Dict[str, Any]]:
        """标准化 web_search 结果"""
        normalized = []
        for r in results:
            normalized.append({
                "title": r.get("title", "无标题"),
                "snippet": r.get("snippet", r.get("description", "")),
                "url": r.get("url", r.get("link", "")),
                "source": r.get("source", "web"),
                "timestamp": datetime.now().isoformat()
            })
        return normalized
    
    def _normalize_tavily_results(self, results: List[Dict]) -> List[Dict[str, Any]]:
        """标准化 Tavily 结果"""
        normalized = []
        for r in results:
            normalized.append({
                "title": r.get("title", "无标题"),
                "snippet": r.get("content", r.get("snippet", "")),
                "url": r.get("url", ""),
                "source": r.get("source", "web"),
                "score": r.get("score", 0),
                "timestamp": datetime.now().isoformat()
            })
        return normalized
    
    def _mock_search(self, query: str) -> List[Dict[str, Any]]:
        """模拟搜索结果（无可用后端时）"""
        return [{
            "title": f"关于 '{query}' 的搜索结果",
            "snippet": "[模拟数据] 未检测到可用搜索后端，请配置 kimi_search、web_search 或 TAVILY_API_KEY",
            "url": "",
            "source": "mock",
            "timestamp": datetime.now().isoformat()
        }]
    
    def batch_search(self, queries: List[str], limit: int = 5) -> Dict[str, List[Dict]]:
        """
        批量搜索
        
        Args:
            queries: 查询列表
            limit: 每个查询的结果数量
        
        Returns:
            查询到结果的映射
        """
        results = {}
        for query in queries:
            results[query] = self.search(query, limit)
        return results
    
    def deduplicate_results(self, results: List[Dict], key: str = "url") -> List[Dict]:
        """
        去重搜索结果
        
        Args:
            results: 搜索结果列表
            key: 去重键
        
        Returns:
            去重后的结果
        """
        seen = set()
        unique = []
        for r in results:
            val = r.get(key, "")
            if val and val not in seen:
                seen.add(val)
                unique.append(r)
            elif not val:
                unique.append(r)
        return unique
    
    def aggregate_results(self, batch_results: Dict[str, List[Dict]]) -> List[Dict]:
        """
        聚合多个搜索结果并去重
        
        Args:
            batch_results: 批量搜索结果
        
        Returns:
            聚合去重后的结果
        """
        all_results = []
        for query, results in batch_results.items():
            for r in results:
                r["_source_query"] = query
                all_results.append(r)
        
        return self.deduplicate_results(all_results)
    
    def get_status(self) -> Dict[str, Any]:
        """获取适配器状态"""
        return {
            "backends": self.backends,
            "preferred": self.preferred_backend,
            "available": self.preferred_backend != "none"
        }


# 便捷函数
def search(query: str, limit: int = 5, **kwargs) -> List[Dict[str, Any]]:
    """便捷搜索函数"""
    adapter = SearchAdapter()
    return adapter.search(query, limit, **kwargs)


def batch_search(queries: List[str], limit: int = 5) -> Dict[str, List[Dict]]:
    """便捷批量搜索函数"""
    adapter = SearchAdapter()
    return adapter.batch_search(queries, limit)


if __name__ == "__main__":
    import sys
    
    # 测试适配器
    adapter = SearchAdapter()
    print("搜索适配器状态:")
    print(json.dumps(adapter.get_status(), indent=2, ensure_ascii=False))
    
    if len(sys.argv) > 1:
        query = sys.argv[1]
        print(f"\n搜索: {query}")
        results = adapter.search(query, limit=3)
        print(json.dumps(results, indent=2, ensure_ascii=False))
