"""
Token Manager 性能基准测试
Performance Benchmarks for Token Manager
"""

import time
import pytest
import tempfile
import os
from pathlib import Path

from token_manager import TokenManager


class TestTokenManagerPerformance:
    """凭证管理器性能测试"""
    
    def test_add_token_performance(self):
        """测试添加凭证性能"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tokens_file = Path(tmpdir) / "tokens.json"
            manager = TokenManager(str(tokens_file))
            
            start = time.perf_counter()
            for i in range(1000):
                manager.set_token(
                    service=f"service_{i}",
                    token=f"token_value_{i}",
                    metadata={"index": i}
                )
            elapsed = time.perf_counter() - start
            
            # 1000个凭证应在3秒内完成（考虑CI环境性能差异）
            assert elapsed < 3.0, f"添加1000个凭证耗时 {elapsed:.3f}s，超过3秒"
            assert len(manager._tokens) == 1000
    
    def test_get_token_performance(self):
        """测试获取凭证性能"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tokens_file = Path(tmpdir) / "tokens.json"
            manager = TokenManager(str(tokens_file))
            
            # 先添加1000个凭证
            for i in range(1000):
                manager.set_token(f"service_{i}", f"token_{i}")
            
            start = time.perf_counter()
            for i in range(1000):
                token = manager.get_token(f"service_{i}")
            elapsed = time.perf_counter() - start
            
            # 1000次获取应在1秒内完成（考虑CI环境性能差异）
            assert elapsed < 1.0, f"1000次获取耗时 {elapsed:.3f}s，超过1秒"
    
    def test_list_services_performance(self):
        """测试列出服务性能"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tokens_file = Path(tmpdir) / "tokens.json"
            manager = TokenManager(str(tokens_file))
            
            # 添加1000个凭证
            for i in range(1000):
                manager.set_token(f"service_{i}", f"token_{i}")
            
            start = time.perf_counter()
            for _ in range(100):
                services = manager.list_services()
            elapsed = time.perf_counter() - start
            
            # 100次列出应在0.5秒内完成（考虑CI环境性能差异）
            assert elapsed < 0.5, f"100次列出耗时 {elapsed:.3f}s，超过0.5秒"
            assert len(services) == 1000
    
    def test_delete_token_performance(self):
        """测试删除凭证性能"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tokens_file = Path(tmpdir) / "tokens.json"
            manager = TokenManager(str(tokens_file))
            
            # 添加1000个凭证
            for i in range(1000):
                manager.set_token(f"service_{i}", f"token_{i}")
            
            start = time.perf_counter()
            for i in range(500):
                manager.delete_token(f"service_{i}")
            elapsed = time.perf_counter() - start
            
            # 500次删除应在1.5秒内完成（考虑CI环境性能差异）
            assert elapsed < 1.5, f"500次删除耗时 {elapsed:.3f}s，超过1.5秒"
            assert len(manager._tokens) == 500
    
    def test_search_tokens_performance(self):
        """测试搜索凭证性能"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tokens_file = Path(tmpdir) / "tokens.json"
            manager = TokenManager(str(tokens_file))
            
            # 添加1000个凭证，带不同标签
            for i in range(1000):
                manager.set_token(
                    f"service_{i}",
                    f"token_{i}",
                    tags=["prod" if i % 2 == 0 else "dev", "api"]
                )
            
            start = time.perf_counter()
            for _ in range(100):
                results = manager.search_tokens(tags=["prod"])
            elapsed = time.perf_counter() - start
            
            # 100次搜索应在1.5秒内完成（考虑CI环境性能差异）
            assert elapsed < 1.5, f"100次搜索耗时 {elapsed:.3f}s，超过1.5秒"
            assert len(results) == 500
    
    def test_bulk_operations_performance(self):
        """测试批量操作性能"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tokens_file = Path(tmpdir) / "tokens.json"
            manager = TokenManager(str(tokens_file))
            
            # 批量添加
            start = time.perf_counter()
            for i in range(500):
                manager.set_token(
                    f"service_{i}",
                    f"token_{i}",
                    metadata={"batch": True, "index": i}
                )
            add_elapsed = time.perf_counter() - start
            
            # 批量获取
            start = time.perf_counter()
            tokens = [manager.get_token(f"service_{i}") for i in range(500)]
            get_elapsed = time.perf_counter() - start
            
            # 批量更新
            start = time.perf_counter()
            for i in range(500):
                manager.update_token(
                    f"service_{i}",
                    metadata={"updated": True}
                )
            update_elapsed = time.perf_counter() - start
            
            # 性能要求（考虑CI环境性能差异，阈值放宽）
            assert add_elapsed < 1.5, f"批量添加耗时 {add_elapsed:.3f}s，超过1.5秒"
            assert get_elapsed < 1.0, f"批量获取耗时 {get_elapsed:.3f}s，超过1秒"
            assert update_elapsed < 1.5, f"批量更新耗时 {update_elapsed:.3f}s，超过1.5秒"


class TestFileOperationsPerformance:
    """文件操作性能测试"""
    
    def test_save_load_performance(self):
        """测试保存和加载性能"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tokens_file = Path(tmpdir) / "tokens.json"
            manager = TokenManager(str(tokens_file))
            
            # 添加大量凭证
            for i in range(1000):
                manager.set_token(f"service_{i}", f"token_{i}")
            
            # 测试保存
            start = time.perf_counter()
            manager._save_tokens()
            save_elapsed = time.perf_counter() - start
            
            # 测试加载
            start = time.perf_counter()
            new_manager = TokenManager(str(tokens_file))
            load_elapsed = time.perf_counter() - start
            
            # 性能要求（考虑CI环境性能差异）
            assert save_elapsed < 1.0, f"保存耗时 {save_elapsed:.3f}s，超过1秒"
            assert load_elapsed < 1.0, f"加载耗时 {load_elapsed:.3f}s，超过1秒"
            assert len(new_manager._tokens) == 1000
    
    def test_large_file_performance(self):
        """测试大文件处理性能"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tokens_file = Path(tmpdir) / "tokens.json"
            manager = TokenManager(str(tokens_file))
            
            # 添加大量大凭证
            for i in range(500):
                manager.set_token(
                    f"service_{i}",
                    f"token_{i}",
                    metadata={
                        "large_data": "x" * 1000,  # 1KB元数据
                        "nested": {"key": "value", "array": list(range(100))}
                    }
                )
            
            start = time.perf_counter()
            manager._save_tokens()
            new_manager = TokenManager(str(tokens_file))
            elapsed = time.perf_counter() - start
            
            # 大文件操作应在5秒内完成（考虑CI环境性能差异）
            assert elapsed < 5.0, f"大文件操作耗时 {elapsed:.3f}s，超过5秒"


class TestMemoryEfficiency:
    """内存效率测试"""
    
    def test_memory_footprint(self):
        """测试内存占用"""
        import sys
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tokens_file = Path(tmpdir) / "tokens.json"
            manager = TokenManager(str(tokens_file))
            
            # 添加1000个凭证
            for i in range(1000):
                manager.set_token(f"service_{i}", f"token_{i}")
            
            # 估算内存占用
            total_size = sys.getsizeof(manager._tokens)
            for key, value in manager._tokens.items():
                total_size += sys.getsizeof(key)
                total_size += sys.getsizeof(value)
            
            avg_size = total_size / len(manager._tokens)
            
            # 每个凭证应小于2KB
            assert avg_size < 2048, f"平均凭证内存占用 {avg_size:.0f} bytes，超过2KB"


class TestConcurrencyPerformance:
    """并发性能测试"""
    
    def test_rapid_operations_performance(self):
        """测试快速连续操作性能"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tokens_file = Path(tmpdir) / "tokens.json"
            manager = TokenManager(str(tokens_file))
            
            # 快速混合操作
            start = time.perf_counter()
            
            for i in range(100):
                manager.set_token(f"service_{i}", f"token_{i}")
                manager.get_token(f"service_{i}")
                if i % 2 == 0:
                    manager.update_token(f"service_{i}", metadata={"updated": True})
            
            elapsed = time.perf_counter() - start
            
            # 300次操作应在3秒内完成（考虑CI环境性能差异）
            assert elapsed < 3.0, f"快速操作耗时 {elapsed:.3f}s，超过3秒"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
