"""
记忆增强系统性能基准测试
Performance Benchmarks for Memory Enhanced System
"""

import time
import pytest
import numpy as np
from typing import List

from memory_system import (
    MemoryStore, MemoryEntry, MemoryType, MemoryPriority, SimpleEmbedding
)


class TestMemoryStorePerformance:
    """记忆存储性能测试"""
    
    def test_store_memory_performance(self):
        """测试添加记忆性能"""
        store = MemoryStore()
        
        start = time.perf_counter()
        for i in range(100):
            store.store(
                content=f"Test memory content {i}",
                memory_type=MemoryType.FACT,
                priority=MemoryPriority.MEDIUM,
                metadata={"index": i}
            )
        elapsed = time.perf_counter() - start
        
        # 100条记忆应在2秒内完成
        assert elapsed < 2.0, f"添加100条记忆耗时 {elapsed:.3f}s，超过2秒"
        assert len(store.memories) == 100
    
    def test_search_memory_performance(self):
        """测试检索记忆性能"""
        store = MemoryStore()
        
        # 先添加100条记忆
        for i in range(100):
            store.store(
                content=f"Test memory content {i}",
                memory_type=MemoryType.FACT,
                priority=MemoryPriority.MEDIUM
            )
        
        start = time.perf_counter()
        for i in range(10):
            results = store.search(
                query=f"Test memory content {i * 10}",
                top_k=5
            )
        elapsed = time.perf_counter() - start
        
        # 10次检索应在1秒内完成
        assert elapsed < 1.0, f"10次检索耗时 {elapsed:.3f}s，超过1秒"
    
    def test_get_by_type_performance(self):
        """测试按类型搜索性能"""
        store = MemoryStore()
        
        # 添加混合类型记忆
        for i in range(100):
            mem_type = [MemoryType.FACT, MemoryType.PREFERENCE, MemoryType.DECISION][i % 3]
            store.store(
                content=f"Test content {i}",
                memory_type=mem_type,
                priority=MemoryPriority.MEDIUM
            )
        
        start = time.perf_counter()
        for _ in range(10):
            results = store.get_by_type(memory_type=MemoryType.FACT)
        elapsed = time.perf_counter() - start
        
        # 10次类型搜索应在0.5秒内完成
        assert elapsed < 0.5, f"10次类型搜索耗时 {elapsed:.3f}s，超过0.5秒"
    
    def test_cleanup_expired_performance(self):
        """测试清理过期记忆性能"""
        store = MemoryStore()
        
        # 添加100条记忆，部分已过期
        for i in range(100):
            store.store(
                content=f"Test content {i}",
                memory_type=MemoryType.FACT,
                priority=MemoryPriority.EPHEMERAL if i % 2 == 0 else MemoryPriority.HIGH
            )
        
        # 模拟时间流逝
        for mem in store.memories.values():
            if mem.priority == MemoryPriority.EPHEMERAL:
                mem.expiration = time.time() - 1  # 已过期
        
        start = time.perf_counter()
        count = store.cleanup_expired()
        elapsed = time.perf_counter() - start
        
        # 清理应在0.5秒内完成
        assert elapsed < 0.5, f"清理耗时 {elapsed:.3f}s，超过0.5秒"
        assert count == 50  # 一半已过期


class TestMemoryEntryPerformance:
    """记忆条目性能测试"""
    
    def test_embedding_generation_performance(self):
        """测试嵌入向量生成性能"""
        embedding = SimpleEmbedding()
        contents = [f"Test content for embedding generation {i}" for i in range(100)]
        
        start = time.perf_counter()
        for content in contents:
            emb = embedding.encode(content)
        elapsed = time.perf_counter() - start
        
        # 100个嵌入应在0.5秒内完成
        assert elapsed < 0.5, f"生成100个嵌入耗时 {elapsed:.3f}s，超过0.5秒"
        assert len(emb) > 0
    
    def test_similarity_calculation_performance(self):
        """测试相似度计算性能"""
        embedding = SimpleEmbedding()
        emb1 = embedding.encode("test content one")
        emb2 = embedding.encode("test content two")
        
        start = time.perf_counter()
        for _ in range(10000):
            similarity = embedding.similarity(emb1, emb2)
        elapsed = time.perf_counter() - start
        
        # 10000次相似度计算应在0.3秒内完成
        assert elapsed < 0.3, f"10000次相似度计算耗时 {elapsed:.3f}s，超过0.3秒"


class TestMemoryPersistencePerformance:
    """记忆持久化性能测试"""
    
    def test_save_load_performance(self, tmp_path):
        """测试保存和加载性能"""
        store = MemoryStore()
        
        # 添加100条记忆
        for i in range(100):
            store.store(
                content=f"Persistent memory content {i}",
                memory_type=MemoryType.FACT,
                priority=MemoryPriority.HIGH
            )
        
        save_path = tmp_path / "memory_benchmark.json"
        
        # 测试保存性能
        start = time.perf_counter()
        store._save()
        save_elapsed = time.perf_counter() - start
        
        # 测试加载性能
        start = time.perf_counter()
        loaded_store = MemoryStore()
        load_elapsed = time.perf_counter() - start
        
        # 保存和加载应在1秒内完成
        assert save_elapsed < 1.0, f"保存耗时 {save_elapsed:.3f}s，超过1秒"
        assert load_elapsed < 1.0, f"加载耗时 {load_elapsed:.3f}s，超过1秒"
