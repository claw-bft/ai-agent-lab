#!/usr/bin/env python3
"""
搜索适配器 - 统一搜索接口
支持 Tavily、Brave Search、kimi_search 和 web_search 工具调用

改进特性:
- 自动后端检测与优先级排序
- API错误处理和降级机制
- 结果标准化与去重
- 批量搜索支持
"""

import json
import os
import subprocess
import time
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
from functools import wraps
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """标准化搜索结果"""
    title: str
    snippet: str
    url: str
    source: str = "web"
    score: float = 0.0
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SearchError(Exception):
    """搜索错误基类"""
    pass


class BackendNotAvailableError(SearchError):
    """后端不可用错误"""
    pass


def retry_on_error(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """重试装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            last_error = None

            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    retries += 1
                    if retries < max_retries:
                        logger.warning(f"{func.__name__} 失败 (尝试 {retries}/{max_retries}): {e}")
                        time.sleep(current_delay)
                        current_delay *= backoff

            logger.error(f"{func.__name__} 最终失败: {last_error}")
            raise last_error
        return wrapper
    return decorator


class SearchAdapter:
    """搜索适配器 - 统一多种搜索后端"""

    # 后端优先级配置
    BACKEND_PRIORITY = ["tavily", "brave", "kimi_search", "web_search"]

    def __init__(self, preferred_backend: Optional[str] = None):
        """
        初始化搜索适配器

        Args:
            preferred_backend: 优先使用的后端，None则自动检测
        """
        self.backends = self._detect_backends()
        self.preferred_backend = preferred_backend or self._select_backend()
        self._backend_stats = {backend: {"success": 0, "fail": 0} for backend in self.backends}
        logger.info(f"搜索适配器初始化完成，首选后端: {self.preferred_backend}")

    def _detect_backends(self) -> Dict[str, bool]:
        """检测可用的搜索后端"""
        backends = {
            "tavily": False,
            "brave": False,
            "kimi_search": False,
            "web_search": False
        }

        # 检测 Tavily
        if os.environ.get("TAVILY_API_KEY"):
            try:
                from tavily import TavilyClient
                backends["tavily"] = True
                logger.info("✓ Tavily API 已配置")
            except ImportError:
                logger.warning("Tavily 包未安装，运行: pip install tavily-python")

        # 检测 Brave Search
        if os.environ.get("BRAVE_API_KEY"):
            backends["brave"] = True
            logger.info("✓ Brave Search API 已配置")

        # 检测 kimi_search (OpenClaw 内置)
        try:
            result = subprocess.run(
                ["python3", "-c", "from kimi_search import kimi_search; print('OK')"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                backends["kimi_search"] = True
                logger.info("✓ kimi_search 工具可用")
        except Exception as e:
            logger.debug(f"kimi_search 检测失败: {e}")

        # 检测 web_search (OpenClaw 内置)
        try:
            result = subprocess.run(
                ["python3", "-c", "from web_search import web_search; print('OK')"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                backends["web_search"] = True
                logger.info("✓ web_search 工具可用")
        except Exception as e:
            logger.debug(f"web_search 检测失败: {e}")

        return backends

    def _select_backend(self) -> str:
        """选择最佳可用后端"""
        for backend in self.BACKEND_PRIORITY:
            if self.backends.get(backend):
                return backend
        return "none"

    def _get_fallback_backend(self, current: str) -> Optional[str]:
        """获取降级后端"""
        current_idx = self.BACKEND_PRIORITY.index(current) if current in self.BACKEND_PRIORITY else -1
        for backend in self.BACKEND_PRIORITY[current_idx + 1:]:
            if self.backends.get(backend):
                return backend
        return None

    @retry_on_error(max_retries=2, delay=1.0)
    def search(self, query: str, limit: int = 5, **kwargs) -> List[SearchResult]:
        """
        执行搜索，带降级机制

        Args:
            query: 搜索查询
            limit: 返回结果数量
            **kwargs: 额外参数

        Returns:
            标准化搜索结果列表
        """
        backend = self.preferred_backend
        errors = []

        while backend and backend != "none":
            try:
                results = self._search_with_backend(backend, query, limit, **kwargs)
                self._backend_stats[backend]["success"] += 1
                logger.info(f"✓ 使用 {backend} 成功获取 {len(results)} 条结果")
                return results
            except Exception as e:
                self._backend_stats[backend]["fail"] += 1
                errors.append(f"{backend}: {str(e)}")
                logger.warning(f"✗ {backend} 搜索失败: {e}")

                # 尝试降级
                fallback = self._get_fallback_backend(backend)
                if fallback:
                    logger.info(f"→ 降级到 {fallback}")
                    backend = fallback
                else:
                    break

        # 所有后端都失败
        error_msg = "; ".join(errors)
        logger.error(f"所有搜索后端都失败: {error_msg}")
        return [SearchResult(
            title=f"搜索失败: {query}",
            snippet=f"所有后端都不可用。错误: {error_msg}",
            url="",
            source="error"
        )]

    def _search_with_backend(self, backend: str, query: str, limit: int, **kwargs) -> List[SearchResult]:
        """使用指定后端执行搜索"""
        if backend == "tavily":
            return self._search_tavily(query, limit, **kwargs)
        elif backend == "brave":
            return self._search_brave(query, limit, **kwargs)
        elif backend == "kimi_search":
            return self._search_kimi(query, limit, **kwargs)
        elif backend == "web_search":
            return self._search_web(query, limit, **kwargs)
        else:
            raise BackendNotAvailableError(f"未知后端: {backend}")

    def _search_tavily(self, query: str, limit: int, **kwargs) -> List[SearchResult]:
        """使用 Tavily API 执行搜索"""
        from tavily import TavilyClient

        api_key = os.environ.get("TAVILY_API_KEY")
        if not api_key:
            raise BackendNotAvailableError("TAVILY_API_KEY 未设置")

        client = TavilyClient(api_key=api_key)
        response = client.search(
            query=query,
            max_results=limit,
            search_depth=kwargs.get("depth", "basic"),
            include_answer=kwargs.get("include_answer", False)
        )

        results = []
        for r in response.get("results", []):
            results.append(SearchResult(
                title=r.get("title", "无标题"),
                snippet=r.get("content", r.get("snippet", "")),
                url=r.get("url", ""),
                source="tavily",
                score=r.get("score", 0)
            ))

        return results

    def _search_brave(self, query: str, limit: int, **kwargs) -> List[SearchResult]:
        """使用 Brave Search API 执行搜索"""
        import requests

        api_key = os.environ.get("BRAVE_API_KEY")
        if not api_key:
            raise BackendNotAvailableError("BRAVE_API_KEY 未设置")

        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "X-Subscription-Token": api_key,
            "Accept": "application/json"
        }
        params = {
            "q": query,
            "count": limit,
            "offset": 0,
            "mkt": kwargs.get("locale", "zh-CN")
        }

        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        results = []
        for r in data.get("web", {}).get("results", []):
            results.append(SearchResult(
                title=r.get("title", "无标题"),
                snippet=r.get("description", ""),
                url=r.get("url", ""),
                source="brave"
            ))

        return results

    def _search_kimi(self, query: str, limit: int, **kwargs) -> List[SearchResult]:
        """使用 kimi_search 执行搜索"""
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

        if result.returncode != 0:
            raise SearchError(f"kimi_search 失败: {result.stderr}")

        data = json.loads(result.stdout)
        if isinstance(data, dict) and "results" in data:
            data = data["results"]

        results = []
        for r in data:
            results.append(SearchResult(
                title=r.get("title", "无标题"),
                snippet=r.get("snippet", r.get("content", "")[:200]),
                url=r.get("url", r.get("link", "")),
                source="kimi"
            ))

        return results

    def _search_web(self, query: str, limit: int, **kwargs) -> List[SearchResult]:
        """使用 web_search 执行搜索"""
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

        if result.returncode != 0:
            raise SearchError(f"web_search 失败: {result.stderr}")

        data = json.loads(result.stdout)

        results = []
        for r in data:
            results.append(SearchResult(
                title=r.get("title", "无标题"),
                snippet=r.get("snippet", r.get("description", "")),
                url=r.get("url", r.get("link", "")),
                source="web"
            ))

        return results

    def batch_search(self, queries: List[str], limit: int = 5, **kwargs) -> Dict[str, List[SearchResult]]:
        """
        批量搜索

        Args:
            queries: 查询列表
            limit: 每个查询的结果数量
            **kwargs: 额外参数

        Returns:
            查询到结果的映射
        """
        results = {}
        for query in queries:
            results[query] = self.search(query, limit, **kwargs)
        return results

    def deduplicate_results(self, results: List[SearchResult], key: str = "url") -> List[SearchResult]:
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
            val = getattr(r, key, "")
            if val and val not in seen:
                seen.add(val)
                unique.append(r)
            elif not val:
                unique.append(r)
        return unique

    def aggregate_results(self, batch_results: Dict[str, List[SearchResult]]) -> List[SearchResult]:
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
                r._source_query = query
                all_results.append(r)

        return self.deduplicate_results(all_results)

    def get_status(self) -> Dict[str, Any]:
        """获取适配器状态"""
        return {
            "backends": self.backends,
            "preferred": self.preferred_backend,
            "available": self.preferred_backend != "none",
            "stats": self._backend_stats
        }


# 便捷函数
def search(query: str, limit: int = 5, **kwargs) -> List[SearchResult]:
    """便捷搜索函数"""
    adapter = SearchAdapter()
    return adapter.search(query, limit, **kwargs)


def batch_search(queries: List[str], limit: int = 5, **kwargs) -> Dict[str, List[SearchResult]]:
    """便捷批量搜索函数"""
    adapter = SearchAdapter()
    return adapter.batch_search(queries, limit, **kwargs)


if __name__ == "__main__":
    import sys

    # 测试适配器
    adapter = SearchAdapter()
    status = adapter.get_status()
    print("=" * 50)
    print("搜索适配器状态")
    print("=" * 50)
    print(f"可用后端: {', '.join([k for k, v in status['backends'].items() if v]) or '无'}")
    print(f"首选后端: {status['preferred']}")
    print(f"可用状态: {'✓ 可用' if status['available'] else '✗ 不可用'}")

    if len(sys.argv) > 1:
        query = sys.argv[1]
        print(f"\n搜索: {query}")
        print("-" * 50)
        results = adapter.search(query, limit=3)
        for i, r in enumerate(results, 1):
            print(f"{i}. {r.title}")
            print(f"   {r.snippet[:100]}...")
            print(f"   → {r.url}")
            print()
