"""
记忆增强系统性能基准测试
Performance Benchmarks for Memory Enhanced System
"""

import time
import pytest
import numpy as np
from typing import List

from memory_system import (
    MemorySystem, MemoryEntry, MemoryType, MemoryPriority,
    ConversationMemory, ProjectMemory
)


class TestMemorySystemPerformance:
    """记忆系统性能测试"""
    
    def test_add_memory_performance(self):
        """测试添加记忆性能"""
        system = MemorySystem()
        
        start = time.perf_counter()
        for i in range(1000):
            system.add_memory(
                content=f"Test memory content {i}",
                memory_type=MemoryType.FACT,
                priority=MemoryPriority.MEDIUM,
                metadata={"index": i}
            )
        elapsed = time.perf_counter() - start
        
        # 1000条记忆应在1秒内完成
        assert elapsed < 1.0, f"添加1000条记忆耗时 {elapsed:.3f}s，超过1秒"
        assert len(system.memories) == 1000
    
    def test_retrieve_memory_performance(self):
        """测试检索记忆性能"""
        system = MemorySystem()
        
        # 先添加1000条记忆
        for i in range(1000):
            system.add_memory(
                content=f"Test memory content {i}",
                memory_type=MemoryType.FACT,
                priority=MemoryPriority.MEDIUM
            )
        
        start = time.perf_counter()
        for i in range(100):
            results = system.retrieve_relevant_memories(
                query=f"Test memory content {i * 10}",
                top_k=5
            )
        elapsed = time.perf_counter() - start
        
        # 100次检索应在0.5秒内完成
        assert elapsed < 0.5, f"100次检索耗时 {elapsed:.3f}s，超过0.5秒"
    
    def test_search_by_type_performance(self):
        """测试按类型搜索性能"""
        system = MemorySystem()
        
        # 添加混合类型记忆
        for i in range(1000):
            mem_type = [MemoryType.FACT, MemoryType.PREFERENCE, MemoryType.DECISION][i % 3]
            system.add_memory(
                content=f"Test content {i}",
                memory_type=mem_type,
                priority=MemoryPriority.MEDIUM
            )
        
        start = time.perf_counter()
        for _ in range(100):
            results = system.search_memories(memory_type=MemoryType.FACT)
        elapsed = time.perf_counter() - start
        
        # 100次类型搜索应在0.3秒内完成
        assert elapsed < 0.3, f"100次类型搜索耗时 {elapsed:.3f}s，超过0.3秒"
    
    def test_cleanup_expired_performance(self):
        """测试清理过期记忆性能"""
        system = MemorySystem()
        
        # 添加1000条记忆，部分已过期
        for i in range(1000):
            system.add_memory(
                content=f"Test content {i}",
                memory_type=MemoryType.FACT,
                priority=MemoryPriority.EPHEMERAL if i % 2 == 0 else MemoryPriority.HIGH
            )
        
        # 模拟时间流逝
        for mem in system.memories.values():
            if mem.priority == MemoryPriority.EPHEMERAL:
                mem.expiration = time.time() - 1  # 已过期
        
        start = time.perf_counter()
        count = system.cleanup_expired_memories()
        elapsed = time.perf_counter() - start
        
        # 清理应在0.5秒内完成
        assert elapsed < 0.5, f"清理耗时 {elapsed:.3f}s，超过0.5秒"
        assert count == 500  # 一半已过期


class TestConversationMemoryPerformance:
    """对话记忆性能测试"""
    
    def test_add_message_performance(self):
        """测试添加消息性能"""
        conv = ConversationMemory()
        
        start = time.perf_counter()
        for i in range(1000):
            conv.add_message(
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message content {i}",
                metadata={"index": i}
            )
        elapsed = time.perf_counter() - start
        
        # 1000条消息应在0.5秒内完成
        assert elapsed < 0.5, f"添加1000条消息耗时 {elapsed:.3f}s，超过0.5秒"
        assert len(conv.messages) == 1000
    
    def test_get_context_performance(self):
        """测试获取上下文性能"""
        conv = ConversationMemory()
        
        # 添加1000条消息
        for i in range(1000):
            conv.add_message(
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message content {i}"
            )
        
        start = time.perf_counter()
        for _ in range(100):
            context = conv.get_context_window(max_messages=50)
        elapsed = time.perf_counter() - start
        
        # 100次获取应在0.3秒内完成
        assert elapsed < 0.3, f"100次获取耗时 {elapsed:.3f}s，超过0.3秒"
        assert len(context) == 50
    
    def test_summarize_performance(self):
        """测试摘要生成性能"""
        conv = ConversationMemory()
        
        # 添加长对话
        for i in range(500):
            conv.add_message(
                role="user" if i % 2 == 0 else "assistant",
                content=f"This is a longer message with more content for testing summarization performance {i}"
            )
        
        start = time.perf_counter()
        summary = conv.summarize_conversation()
        elapsed = time.perf_counter() - start
        
        # 摘要生成应在0.5秒内完成
        assert elapsed < 0.5, f"摘要生成耗时 {elapsed:.3f}s，超过0.5秒"
        assert summary is not None


class TestProjectMemoryPerformance:
    """项目记忆性能测试"""
    
    def test_add_decision_performance(self):
        """测试添加决策性能"""
        proj = ProjectMemory(project_id="test_proj")
        
        start = time.perf_counter()
        for i in range(500):
            proj.add_decision(
                decision=f"Decision {i}",
                rationale=f"Rationale for decision {i}",
                alternatives=[f"Alt {j}" for j in range(3)]
            )
        elapsed = time.perf_counter() - start
        
        # 500个决策应在0.5秒内完成
        assert elapsed < 0.5, f"添加500个决策耗时 {elapsed:.3f}s，超过0.5秒"
    
    def test_get_decision_history_performance(self):
        """测试获取决策历史性能"""
        proj = ProjectMemory(project_id="test_proj")
        
        # 添加500个决策
        for i in range(500):
            proj.add_decision(
                decision=f"Decision {i}",
                rationale=f"Rationale {i}"
            )
        
        start = time.perf_counter()
        for _ in range(100):
            history = proj.get_decision_history(limit=50)
        elapsed = time.perf_counter() - start
        
        # 100次获取应在0.3秒内完成
        assert elapsed < 0.3, f"100次获取耗时 {elapsed:.3f}s，超过0.3秒"


class TestEmbeddingPerformance:
    """向量嵌入性能测试"""
    
    def test_embedding_generation_performance(self):
        """测试嵌入生成性能"""
        system = MemorySystem()
        
        texts = [f"Test text content for embedding generation {i}" for i in range(100)]
        
        start = time.perf_counter()
        for text in texts:
            embedding = system._generate_embedding(text)
        elapsed = time.perf_counter() - start
        
        # 100个嵌入应在1秒内完成
        assert elapsed < 1.0, f"100个嵌入生成耗时 {elapsed:.3f}s，超过1秒"
        assert len(embedding) > 0
    
    def test_similarity_calculation_performance(self):
        """测试相似度计算性能"""
        system = MemorySystem()
        
        # 生成测试嵌入
        embedding1 = np.random.randn(128).tolist()
        embeddings = [np.random.randn(128).tolist() for _ in range(1000)]
        
        start = time.perf_counter()
        for emb in embeddings:
            similarity = system._calculate_similarity(embedding1, emb)
        elapsed = time.perf_counter() - start
        
        # 1000次相似度计算应在0.5秒内完成
        assert elapsed < 0.5, f"1000次相似度计算耗时 {elapsed:.3f}s，超过0.5秒"


class TestMemoryEfficiency:
    """内存效率测试"""
    
    def test_memory_footprint(self):
        """测试内存占用"""
        import sys
        
        system = MemorySystem()
        
        # 添加1000条记忆
        for i in range(1000):
            system.add_memory(
                content=f"Test content {i}",
                memory_type=MemoryType.FACT,
                priority=MemoryPriority.MEDIUM
            )
        
        # 估算内存占用
        total_size = sum(
            sys.getsizeof(mem.__dict__) 
            for mem in system.memories.values()
        )
        avg_size = total_size / len(system.memories)
        
        # 每条记忆应小于5KB
        assert avg_size < 5120, f"平均记忆内存占用 {avg_size:.0f} bytes，超过5KB"


class TestScalability:
    """可扩展性测试"""
    
    def test_large_scale_memory_operations(self):
        """测试大规模记忆操作"""
        system = MemorySystem()
        
        # 添加10000条记忆
        start = time.perf_counter()
        for i in range(10000):
            system.add_memory(
                content=f"Large scale test memory {i}",
                memory_type=MemoryType.FACT,
                priority=MemoryPriority.LOW
            )
        add_elapsed = time.perf_counter() - start
        
        # 检索100次
        start = time.perf_counter()
        for i in range(100):
            results = system.retrieve_relevant_memories(
                query=f"Large scale test memory {i * 100}",
                top_k=10
            )
        retrieve_elapsed = time.perf_counter() - start
        
        # 性能要求
        assert add_elapsed < 5.0, f"添加10000条记忆耗时 {add_elapsed:.3f}s，超过5秒"
        assert retrieve_elapsed < 2.0, f"100次检索耗时 {retrieve_elapsed:.3f}s，超过2秒"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
