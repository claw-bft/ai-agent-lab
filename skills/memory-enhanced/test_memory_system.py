"""
Tests for Memory Enhanced System
"""

import pytest
import time
import os
import tempfile
from datetime import datetime

from memory_system import (
    MemoryType, MemoryPriority, MemoryEntry, SimpleEmbedding,
    MemoryStore, ContextWindow, MemoryEnhancedAgent,
    create_memory_agent
)


class TestSimpleEmbedding:
    """测试简单嵌入生成器"""
    
    def test_encode_returns_vector(self):
        emb = SimpleEmbedding(dim=64)
        vector = emb.encode("这是一个测试")
        assert len(vector) == 64
        assert all(isinstance(v, float) for v in vector)
    
    def test_encode_empty_text(self):
        emb = SimpleEmbedding(dim=64)
        vector = emb.encode("")
        assert len(vector) == 64
        assert all(v == 0.0 for v in vector)
    
    def test_similarity_identical(self):
        emb = SimpleEmbedding(dim=64)
        v1 = emb.encode("相同文本")
        v2 = emb.encode("相同文本")
        sim = emb.similarity(v1, v2)
        assert sim > 0.99  # 几乎相同
    
    def test_similarity_different(self):
        emb = SimpleEmbedding(dim=64)
        v1 = emb.encode("Python编程")
        v2 = emb.encode("股票投资")
        sim = emb.similarity(v1, v2)
        assert 0 <= sim < 1  # 不同文本相似度较低
    
    def test_similarity_orthogonal(self):
        emb = SimpleEmbedding(dim=64)
        v1 = [1.0] + [0.0] * 63
        v2 = [0.0] * 63 + [1.0]
        sim = emb.similarity(v1, v2)
        assert sim == 0.0


class TestMemoryEntry:
    """测试记忆条目"""
    
    def test_creation(self):
        entry = MemoryEntry(
            memory_id="test-123",
            content="测试内容",
            memory_type=MemoryType.FACT,
            priority=MemoryPriority.MEDIUM,
            timestamp=time.time(),
            last_accessed=time.time(),
            access_count=0,
            metadata={"key": "value"}
        )
        assert entry.memory_id == "test-123"
        assert entry.content == "测试内容"
    
    def test_to_dict_and_back(self):
        entry = MemoryEntry(
            memory_id="test-123",
            content="测试内容",
            memory_type=MemoryType.PREFERENCE,
            priority=MemoryPriority.HIGH,
            timestamp=1234567890.0,
            last_accessed=1234567890.0,
            access_count=5,
            metadata={"pref": "value"},
            embedding=[0.1, 0.2, 0.3]
        )
        data = entry.to_dict()
        restored = MemoryEntry.from_dict(data)
        
        assert restored.memory_id == entry.memory_id
        assert restored.content == entry.content
        assert restored.memory_type == entry.memory_type
        assert restored.priority == entry.priority
        assert restored.access_count == entry.access_count
    
    def test_is_expired_no_expiration(self):
        entry = MemoryEntry(
            memory_id="test",
            content="内容",
            memory_type=MemoryType.FACT,
            priority=MemoryPriority.CRITICAL,
            timestamp=time.time(),
            last_accessed=time.time(),
            access_count=0,
            metadata={},
            expiration=None
        )
        assert not entry.is_expired()
    
    def test_is_expired_with_expiration(self):
        entry = MemoryEntry(
            memory_id="test",
            content="内容",
            memory_type=MemoryType.FACT,
            priority=MemoryPriority.LOW,
            timestamp=time.time(),
            last_accessed=time.time(),
            access_count=0,
            metadata={},
            expiration=time.time() - 1  # 已过期
        )
        assert entry.is_expired()
    
    def test_touch_updates_access(self):
        entry = MemoryEntry(
            memory_id="test",
            content="内容",
            memory_type=MemoryType.FACT,
            priority=MemoryPriority.MEDIUM,
            timestamp=time.time(),
            last_accessed=time.time() - 100,
            access_count=0,
            metadata={}
        )
        old_accessed = entry.last_accessed
        entry.touch()
        assert entry.last_accessed > old_accessed
        assert entry.access_count == 1


class TestMemoryStore:
    """测试记忆存储"""
    
    @pytest.fixture
    def temp_store(self):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            path = f.name
        store = MemoryStore(path)
        yield store
        os.unlink(path)
    
    def test_store_and_retrieve(self, temp_store):
        mid = temp_store.store("测试内容", MemoryType.FACT, MemoryPriority.MEDIUM)
        assert mid is not None
        
        entry = temp_store.retrieve(mid)
        assert entry is not None
        assert entry.content == "测试内容"
    
    def test_store_generates_embedding(self, temp_store):
        mid = temp_store.store("测试内容")
        entry = temp_store.retrieve(mid)
        assert entry.embedding is not None
        assert len(entry.embedding) == 128  # 默认维度
    
    def test_search_finds_similar(self, temp_store):
        temp_store.store("Python编程语言", MemoryType.FACT)
        temp_store.store("JavaScript前端开发", MemoryType.FACT)
        temp_store.store("股票投资分析", MemoryType.FACT)
        
        results = temp_store.search("编程", top_k=2)
        assert len(results) > 0
        # 第一个结果应该与编程相关
        assert "编程" in results[0][0].content or "开发" in results[0][0].content
    
    def test_get_by_type(self, temp_store):
        temp_store.store("偏好1", MemoryType.PREFERENCE)
        temp_store.store("偏好2", MemoryType.PREFERENCE)
        temp_store.store("事实1", MemoryType.FACT)
        
        prefs = temp_store.get_by_type(MemoryType.PREFERENCE)
        assert len(prefs) == 2
        assert all(p.memory_type == MemoryType.PREFERENCE for p in prefs)
    
    def test_delete(self, temp_store):
        mid = temp_store.store("待删除")
        assert temp_store.retrieve(mid) is not None
        
        deleted = temp_store.delete(mid)
        assert deleted is True
        assert temp_store.retrieve(mid) is None
    
    def test_cleanup_expired(self, temp_store):
        # 存储一个即将过期的记忆
        temp_store.store("临时内容", MemoryType.FACT, MemoryPriority.EPHEMERAL)
        # 手动设置过期
        for entry in temp_store.memories.values():
            entry.expiration = time.time() - 1
        
        count = temp_store.cleanup_expired()
        assert count >= 1
        assert len(temp_store.memories) == 0
    
    def test_get_stats(self, temp_store):
        temp_store.store("内容1", MemoryType.FACT, MemoryPriority.HIGH)
        temp_store.store("内容2", MemoryType.PREFERENCE, MemoryPriority.MEDIUM)
        
        stats = temp_store.get_stats()
        assert stats["total_memories"] == 2
        assert "fact" in stats["by_type"]
        assert "preference" in stats["by_type"]
    
    def test_persistence(self):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            path = f.name
        
        try:
            # 创建并存储
            store1 = MemoryStore(path)
            mid = store1.store("持久化测试")
            
            # 重新加载
            store2 = MemoryStore(path)
            entry = store2.retrieve(mid)
            assert entry is not None
            assert entry.content == "持久化测试"
        finally:
            os.unlink(path)


class TestContextWindow:
    """测试上下文窗口"""
    
    def test_add_and_get_context(self):
        ctx = ContextWindow(max_tokens=1000)
        entry = MemoryEntry(
            memory_id="test",
            content="测试上下文",
            memory_type=MemoryType.CONTEXT,
            priority=MemoryPriority.MEDIUM,
            timestamp=time.time(),
            last_accessed=time.time(),
            access_count=0,
            metadata={}
        )
        ctx.add(entry)
        
        context_str = ctx.get_context_string()
        assert "测试上下文" in context_str
    
    def test_trim_when_exceeds_limit(self):
        ctx = ContextWindow(max_tokens=50)  # 很小的限制
        
        # 添加多个长记忆
        for i in range(5):
            entry = MemoryEntry(
                memory_id=f"test-{i}",
                content=f"这是一个非常长的记忆内容编号{i}" * 10,
                memory_type=MemoryType.CONTEXT,
                priority=MemoryPriority.LOW,
                timestamp=time.time(),
                last_accessed=time.time(),
                access_count=0,
                metadata={}
            )
            ctx.add(entry)
        
        # 应该被修剪
        assert len(ctx.entries) < 5
    
    def test_clear(self):
        ctx = ContextWindow()
        entry = MemoryEntry(
            memory_id="test",
            content="内容",
            memory_type=MemoryType.FACT,
            priority=MemoryPriority.MEDIUM,
            timestamp=time.time(),
            last_accessed=time.time(),
            access_count=0,
            metadata={}
        )
        ctx.add(entry)
        assert len(ctx.entries) == 1
        
        ctx.clear()
        assert len(ctx.entries) == 0


class TestMemoryEnhancedAgent:
    """测试记忆增强Agent"""
    
    @pytest.fixture
    def temp_agent(self):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            path = f.name
        agent = MemoryEnhancedAgent("test-agent", path)
        yield agent
        os.unlink(path)
    
    def test_remember_and_recall(self, temp_agent):
        temp_agent.remember("Python是最好的语言", "preference", "high")
        temp_agent.remember("使用FastAPI构建API", "skill", "medium")
        
        results = temp_agent.recall("编程语言", top_k=2)
        assert len(results) > 0
        assert any("Python" in r["content"] for r in results)
    
    def test_get_preferences(self, temp_agent):
        temp_agent.remember(
            "用户偏好", "preference", "high",
            preferences={"theme": "dark", "language": "zh"}
        )
        
        prefs = temp_agent.get_preferences()
        assert "theme" in prefs
        assert prefs["theme"] == "dark"
    
    def test_get_recent_context(self, temp_agent):
        temp_agent.remember("刚刚发生的事情", "context", "medium")
        
        context = temp_agent.get_recent_context(hours=1)
        assert len(context) >= 1
    
    def test_forget(self, temp_agent):
        mid = temp_agent.remember("临时信息", "fact", "low")
        assert len(temp_agent.recall("临时")) > 0
        
        deleted = temp_agent.forget(mid)
        assert deleted is True
    
    def test_stats(self, temp_agent):
        temp_agent.remember("内容", "fact")
        stats = temp_agent.stats()
        assert stats["total_memories"] >= 1


class TestIntegration:
    """集成测试"""
    
    def test_end_to_end_workflow(self):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            path = f.name
        
        try:
            agent = create_memory_agent("integration-test", path)
            
            # 1. 存储不同类型的记忆
            agent.remember("用户是产品经理", "fact", "high")
            agent.remember("偏好深色主题", "preference", "high", 
                          preferences={"theme": "dark"})
            agent.remember("决定使用React", "decision", "critical",
                          project="frontend", decision_id="D001")
            
            # 2. 语义搜索
            results = agent.recall("用户", top_k=3)
            assert len(results) >= 1
            
            # 3. 获取偏好
            prefs = agent.get_preferences()
            assert prefs.get("theme") == "dark"
            
            # 4. 检查统计
            stats = agent.stats()
            assert stats["total_memories"] == 3
            
            print(f"\n集成测试通过! 统计: {stats}")
            
        finally:
            os.unlink(path)
    
    def test_memory_types_isolation(self):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            path = f.name
        
        try:
            agent = create_memory_agent("type-test", path)
            
            # 存储不同类型的记忆
            agent.remember("事实1", "fact")
            agent.remember("事实2", "fact")
            agent.remember("偏好1", "preference")
            
            # 按类型检索
            store = agent.memory
            facts = store.get_by_type(MemoryType.FACT)
            prefs = store.get_by_type(MemoryType.PREFERENCE)
            
            assert len(facts) == 2
            assert len(prefs) == 1
            
        finally:
            os.unlink(path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
