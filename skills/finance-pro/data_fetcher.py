"""
Data Fetcher Module - Robust data fetching with caching and retry logic
用于解决akshare网络不稳定问题
"""

import json
import time
import hashlib
import os
from pathlib import Path
from typing import Optional, Callable, Any, Dict
from functools import wraps
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 缓存目录
CACHE_DIR = Path.home() / ".cache" / "finance-pro"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# 默认配置
DEFAULT_CACHE_TTL = 900  # 15分钟
DEFAULT_MAX_RETRIES = 5
DEFAULT_TIMEOUT = 10  # 秒
DEFAULT_BACKOFF_BASE = 2  # 指数退避基数


class DataFetcher:
    """
    健壮的数据获取器，支持重试、缓存和优雅降级
    """
    
    def __init__(
        self,
        cache_ttl: int = DEFAULT_CACHE_TTL,
        max_retries: int = DEFAULT_MAX_RETRIES,
        timeout: int = DEFAULT_TIMEOUT,
        backoff_base: int = DEFAULT_BACKOFF_BASE
    ):
        self.cache_ttl = cache_ttl
        self.max_retries = max_retries
        self.timeout = timeout
        self.backoff_base = backoff_base
    
    def _get_cache_key(self, func_name: str, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = f"{func_name}:{str(args)}:{str(kwargs)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """获取缓存文件路径"""
        return CACHE_DIR / f"{cache_key}.json"
    
    def _is_cache_valid(self, cache_path: Path) -> bool:
        """检查缓存是否有效"""
        if not cache_path.exists():
            return False
        
        cache_age = time.time() - cache_path.stat().st_mtime
        return cache_age < self.cache_ttl
    
    def _read_cache(self, cache_path: Path) -> Optional[Any]:
        """读取缓存数据"""
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"[Cache Hit] 使用缓存数据: {cache_path.name}")
                return data
        except Exception as e:
            logger.warning(f"[Cache Error] 读取缓存失败: {e}")
            return None
    
    def _write_cache(self, cache_path: Path, data: Any):
        """写入缓存数据"""
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, default=str)
            logger.info(f"[Cache Write] 写入缓存: {cache_path.name}")
        except Exception as e:
            logger.warning(f"[Cache Error] 写入缓存失败: {e}")
    
    def fetch_with_retry(
        self,
        fetch_func: Callable,
        *args,
        use_cache: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        带重试和缓存的数据获取
        
        Args:
            fetch_func: 数据获取函数
            *args: 传递给fetch_func的位置参数
            use_cache: 是否使用缓存
            **kwargs: 传递给fetch_func的关键字参数
            
        Returns:
            {
                "success": bool,
                "data": Any,  # 成功时返回数据
                "error": str, # 失败时返回错误信息
                "from_cache": bool,
                "retry_count": int
            }
        """
        func_name = fetch_func.__name__
        cache_key = self._get_cache_key(func_name, *args, **kwargs)
        cache_path = self._get_cache_path(cache_key)
        
        # 1. 尝试读取缓存
        if use_cache and self._is_cache_valid(cache_path):
            cached_data = self._read_cache(cache_path)
            if cached_data is not None:
                return {
                    "success": True,
                    "data": cached_data,
                    "error": None,
                    "from_cache": True,
                    "retry_count": 0
                }
        
        # 2. 尝试获取数据（带重试）
        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"[Fetch] {func_name} - 尝试 {attempt}/{self.max_retries}")
                
                # 设置超时（如果函数支持）
                if 'timeout' in fetch_func.__code__.co_varnames:
                    kwargs['timeout'] = self.timeout
                
                data = fetch_func(*args, **kwargs)
                
                # 写入缓存
                if use_cache:
                    self._write_cache(cache_path, data)
                
                logger.info(f"[Fetch Success] {func_name} - 第{attempt}次尝试成功")
                
                return {
                    "success": True,
                    "data": data,
                    "error": None,
                    "from_cache": False,
                    "retry_count": attempt
                }
                
            except Exception as e:
                last_error = str(e)
                logger.warning(f"[Fetch Failed] {func_name} - 第{attempt}次尝试失败: {e}")
                
                if attempt < self.max_retries:
                    # 指数退避
                    sleep_time = self.backoff_base ** attempt
                    logger.info(f"[Retry] 等待 {sleep_time} 秒后重试...")
                    time.sleep(sleep_time)
        
        # 3. 所有重试失败，尝试使用过期缓存（优雅降级）
        if use_cache and cache_path.exists():
            expired_data = self._read_cache(cache_path)
            if expired_data is not None:
                logger.warning(f"[Graceful Degradation] 使用过期缓存数据")
                return {
                    "success": True,
                    "data": expired_data,
                    "error": f"Fetch failed after {self.max_retries} retries, using expired cache. Last error: {last_error}",
                    "from_cache": True,
                    "expired": True,
                    "retry_count": self.max_retries
                }
        
        # 4. 彻底失败
        logger.error(f"[Fetch Failed] {func_name} - 所有尝试失败，无可用缓存")
        return {
            "success": False,
            "data": None,
            "error": f"Failed after {self.max_retries} retries. Last error: {last_error}",
            "from_cache": False,
            "retry_count": self.max_retries
        }


# 全局数据获取器实例
default_fetcher = DataFetcher()


def fetch_with_retry(
    fetch_func: Callable,
    *args,
    use_cache: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    便捷函数：使用默认配置的数据获取器
    
    示例:
        result = fetch_with_retry(ak.stock_zh_a_spot_em)
        if result["success"]:
            df = result["data"]
    """
    return default_fetcher.fetch_with_retry(fetch_func, *args, use_cache=use_cache, **kwargs)


def clear_cache():
    """清理所有缓存"""
    try:
        for cache_file in CACHE_DIR.glob("*.json"):
            cache_file.unlink()
        logger.info("[Cache] 缓存已清理")
    except Exception as e:
        logger.error(f"[Cache Error] 清理缓存失败: {e}")


def get_cache_stats() -> Dict[str, Any]:
    """获取缓存统计信息"""
    try:
        cache_files = list(CACHE_DIR.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            "cache_dir": str(CACHE_DIR),
            "file_count": len(cache_files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2)
        }
    except Exception as e:
        return {
            "error": str(e)
        }


# 专为akshare设计的便捷函数
class AkshareFetcher:
    """
    专为akshare设计的数据获取器
    自动处理akshare特有的DataFrame格式
    """
    
    def __init__(self):
        self.fetcher = DataFetcher()
    
    def fetch_stock_spot(self) -> Dict[str, Any]:
        """获取A股实时行情"""
        try:
            import akshare as ak
            return self.fetcher.fetch_with_retry(ak.stock_zh_a_spot_em)
        except ImportError:
            return {
                "success": False,
                "error": "akshare not installed",
                "data": None
            }
    
    def fetch_stock_daily(self, symbol: str) -> Dict[str, Any]:
        """获取个股日线数据"""
        try:
            import akshare as ak
            return self.fetcher.fetch_with_retry(ak.stock_zh_a_hist, symbol=symbol)
        except ImportError:
            return {
                "success": False,
                "error": "akshare not installed",
                "data": None
            }
    
    def fetch_index_spot(self) -> Dict[str, Any]:
        """获取指数实时行情"""
        try:
            import akshare as ak
            return self.fetcher.fetch_with_retry(ak.index_zh_a_spot_em)
        except ImportError:
            return {
                "success": False,
                "error": "akshare not installed",
                "data": None
            }


# 便捷实例
akshare_fetcher = AkshareFetcher()
