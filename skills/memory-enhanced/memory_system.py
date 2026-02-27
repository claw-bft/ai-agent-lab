"""
Memory Enhanced System - 记忆增强系统
基于向量数据库的长期记忆，支持跨会话上下文保持
"""

import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np


class MemoryType(Enum):
    """记忆类型"""
    FACT = "fact"              # 事实性记忆
    PREFERENCE = "preference"  # 用户偏好
    DECISION = "decision"      # 历史决策
    CONTEXT = "context"        # 项目上下文
    SKILL = "skill"            # 技能使用记录
    CONVERSATION = "conversation"  # 对话片段


class MemoryPriority(Enum):
    """记忆优先级"""
    CRITICAL = 5    # 关键记忆，永不过期
    HIGH = 4        # 重要记忆，长期保留
    MEDIUM = 3      # 普通记忆，定期清理
    LOW = 2         # 次要记忆，快速过期
    EPHEMERAL = 1   # 临时记忆，会话结束即清除


@dataclass
class MemoryEntry:
    """记忆条目"""
    memory_id: str
    content: str
    memory_type: MemoryType
    priority: MemoryPriority
    timestamp: float
    last_accessed: float
    access_count: int
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    expiration: Optional[float] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "memory_id": self.memory_id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "priority": self.priority.value,
            "timestamp": self.timestamp,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count,
            "metadata": self.metadata,
            "embedding": self.embedding,
            "expiration": self.expiration
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "MemoryEntry":
        """从字典创建"""
        return cls(
            memory_id=data["memory_id"],
            content=data["content"],
            memory_type=MemoryType(data["memory_type"]),
            priority=MemoryPriority(data["priority"]),
            timestamp=data["timestamp"],
            last_accessed=data["last_accessed"],
            access_count=data["access_count"],
            metadata=data["metadata"],
            embedding=data.get("embedding"),
            expiration=data.get("expiration")
        )
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.expiration is None:
            return False
        return time.time() > self.expiration
    
    def touch(self):
        """更新访问时间"""
        self.last_accessed = time.time()
        self.access_count += 1


class SimpleEmbedding:
    """简单嵌入生成器(无需外部API)"""
    
    def __init__(self, dim: int = 128):
        self.dim = dim
        self.vocab = {}
        self.vocab_size = 0
    
    def _tokenize(self, text: str) -> List[str]:
        """简单分词"""
        # 转换为小写，按空格和标点分割
        import re
        text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        return tokens
    
    def _get_or_create_id(self, token: str) -> int:
        """获取或创建token ID"""
        if token not in self.vocab:
            self.vocab[token] = self.vocab_size
            self.vocab_size += 1
        return self.vocab[token]
    
    def encode(self, text: str) -> List[float]:
        """生成文本嵌入"""
        tokens = self._tokenize(text)
        if not tokens:
            return [0.0] * self.dim
        
        # 使用token哈希生成固定维度的向量
        embedding = np.zeros(self.dim)
        for token in tokens:
            token_id = self._get_or_create_id(token)
            # 使用多个哈希位置
            for i in range(3):
                idx = (token_id + i * 997) % self.dim
                embedding[idx] += 1.0
        
        # L2归一化
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding.tolist()
    
    def similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """计算余弦相似度"""
        v1 = np.array(emb1)
        v2 = np.array(emb2)
        dot = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(dot / (norm1 * norm2))


class MemoryStore:
    """记忆存储"""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or ".memory_store.json"
        self.memories: Dict[str, MemoryEntry] = {}
        self.embedding = SimpleEmbedding()
        self._load()
    
    def _generate_id(self, content: str) -> str:
        """生成记忆ID"""
        return hashlib.md5(f"{content}:{time.time()}".encode()).hexdigest()[:16]
    
    def _calculate_expiration(self, priority: MemoryPriority) -> Optional[float]:
        """计算过期时间"""
        now = time.time()
        if priority == MemoryPriority.CRITICAL:
            return None  # 永不过期
        elif priority == MemoryPriority.HIGH:
            return now + 90 * 24 * 3600  # 90天
        elif priority == MemoryPriority.MEDIUM:
            return now + 30 * 24 * 3600  # 30天
        elif priority == MemoryPriority.LOW:
            return now + 7 * 24 * 3600   # 7天
        else:  # EPHEMERAL
            return now + 3600  # 1小时
    
    def store(self, content: str, memory_type: MemoryType = MemoryType.FACT,
              priority: MemoryPriority = MemoryPriority.MEDIUM,
              metadata: Optional[Dict] = None) -> str:
        """
        存储记忆
        
        Args:
            content: 记忆内容
            memory_type: 记忆类型
            priority: 优先级
            metadata: 额外元数据
            
        Returns:
            memory_id: 记忆ID
        """
        memory_id = self._generate_id(content)
        now = time.time()
        
        # 生成嵌入
        embedding = self.embedding.encode(content)
        
        entry = MemoryEntry(
            memory_id=memory_id,
            content=content,
            memory_type=memory_type,
            priority=priority,
            timestamp=now,
            last_accessed=now,
            access_count=0,
            metadata=metadata or {},
            embedding=embedding,
            expiration=self._calculate_expiration(priority)
        )
        
        self.memories[memory_id] = entry
        self._save()
        
        return memory_id
    
    def retrieve(self, memory_id: str) -> Optional[MemoryEntry]:
        """根据ID检索记忆"""
        entry = self.memories.get(memory_id)
        if entry and not entry.is_expired():
            entry.touch()
            self._save()
            return entry
        return None
    
    def search(self, query: str, top_k: int = 5, 
               memory_type: Optional[MemoryType] = None) -> List[Tuple[MemoryEntry, float]]:
        """
        语义搜索记忆
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            memory_type: 可选的类型过滤
            
        Returns:
            List of (entry, similarity) tuples
        """
        query_embedding = self.embedding.encode(query)
        
        results = []
        for entry in self.memories.values():
            # 跳过过期记忆
            if entry.is_expired():
                continue
            
            # 类型过滤
            if memory_type and entry.memory_type != memory_type:
                continue
            
            # 计算相似度
            if entry.embedding:
                sim = self.embedding.similarity(query_embedding, entry.embedding)
                results.append((entry, sim))
        
        # 按相似度排序
        results.sort(key=lambda x: x[1], reverse=True)
        
        # 更新访问记录
        for entry, _ in results[:top_k]:
            entry.touch()
        
        self._save()
        
        return results[:top_k]
    
    def get_by_type(self, memory_type: MemoryType, 
                    limit: int = 10) -> List[MemoryEntry]:
        """按类型获取记忆"""
        entries = [
            e for e in self.memories.values() 
            if e.memory_type == memory_type and not e.is_expired()
        ]
        # 按优先级和时间排序
        entries.sort(key=lambda e: (e.priority.value, e.timestamp), reverse=True)
        return entries[:limit]
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """获取用户偏好汇总"""
        prefs = self.get_by_type(MemoryType.PREFERENCE, limit=50)
        result = {}
        for p in prefs:
            result.update(p.metadata.get("preferences", {}))
        return result
    
    def get_recent_context(self, hours: int = 24) -> List[MemoryEntry]:
        """获取近期上下文"""
        cutoff = time.time() - hours * 3600
        entries = [
            e for e in self.memories.values()
            if e.timestamp > cutoff and not e.is_expired()
        ]
        entries.sort(key=lambda e: e.timestamp, reverse=True)
        return entries
    
    def delete(self, memory_id: str) -> bool:
        """删除记忆"""
        if memory_id in self.memories:
            del self.memories[memory_id]
            self._save()
            return True
        return False
    
    def cleanup_expired(self) -> int:
        """清理过期记忆，返回删除数量"""
        expired = [
            mid for mid, entry in self.memories.items() 
            if entry.is_expired()
        ]
        for mid in expired:
            del self.memories[mid]
        if expired:
            self._save()
        return len(expired)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        total = len(self.memories)
        by_type = {}
        by_priority = {}
        expired = 0
        
        for entry in self.memories.values():
            by_type[entry.memory_type.value] = by_type.get(entry.memory_type.value, 0) + 1
            by_priority[entry.priority.name] = by_priority.get(entry.priority.name, 0) + 1
            if entry.is_expired():
                expired += 1
        
        return {
            "total_memories": total,
            "active_memories": total - expired,
            "expired_memories": expired,
            "by_type": by_type,
            "by_priority": by_priority,
            "vocab_size": self.embedding.vocab_size
        }
    
    def _save(self):
        """保存到文件"""
        data = {
            "memories": {mid: entry.to_dict() for mid, entry in self.memories.items()},
            "vocab": self.embedding.vocab,
            "vocab_size": self.embedding.vocab_size
        }
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _load(self):
        """从文件加载"""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return  # 空文件，保持默认状态
                data = json.loads(content)
            
            self.memories = {
                mid: MemoryEntry.from_dict(mdata) 
                for mid, mdata in data.get("memories", {}).items()
            }
            self.embedding.vocab = data.get("vocab", {})
            self.embedding.vocab_size = data.get("vocab_size", 0)
        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            pass  # 损坏的JSON文件，保持默认状态


class ContextWindow:
    """上下文窗口管理"""
    
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
        self.entries: List[MemoryEntry] = []
    
    def add(self, entry: MemoryEntry):
        """添加记忆到上下文"""
        self.entries.append(entry)
        self._trim()
    
    def _trim(self):
        """修剪超出限制的记忆"""
        # 简单估算：每个字符约0.5个token
        total_chars = sum(len(e.content) for e in self.entries)
        estimated_tokens = total_chars * 0.5
        
        while estimated_tokens > self.max_tokens and len(self.entries) > 1:
            # 移除最旧的低优先级记忆
            self.entries.sort(key=lambda e: (e.priority.value, e.timestamp))
            removed = self.entries.pop(0)
            total_chars -= len(removed.content)
            estimated_tokens = total_chars * 0.5
    
    def get_context_string(self) -> str:
        """获取格式化的上下文字符串"""
        lines = []
        for entry in sorted(self.entries, key=lambda e: e.timestamp):
            time_str = datetime.fromtimestamp(entry.timestamp).strftime("%m-%d %H:%M")
            lines.append(f"[{time_str}] {entry.memory_type.value}: {entry.content}")
        return "\n".join(lines)
    
    def clear(self):
        """清空上下文"""
        self.entries = []


class MemoryEnhancedAgent:
    """记忆增强的Agent基类"""
    
    def __init__(self, agent_id: str, storage_path: Optional[str] = None):
        self.agent_id = agent_id
        self.memory = MemoryStore(storage_path)
        self.context = ContextWindow()
    
    def remember(self, content: str, memory_type: str = "fact",
                 priority: str = "medium", **metadata) -> str:
        """
        记住信息
        
        Args:
            content: 要记忆的内容
            memory_type: 记忆类型 (fact/preference/decision/context/skill/conversation)
            priority: 优先级 (critical/high/medium/low/ephemeral)
            **metadata: 额外元数据
        """
        mtype = MemoryType(memory_type)
        mpriority = MemoryPriority[priority.upper()]
        
        memory_id = self.memory.store(
            content=content,
            memory_type=mtype,
            priority=mpriority,
            metadata={"agent_id": self.agent_id, **metadata}
        )
        
        return memory_id
    
    def recall(self, query: str, top_k: int = 5) -> List[Dict]:
        """回忆相关信息"""
        results = self.memory.search(query, top_k=top_k)
        return [
            {
                "content": entry.content,
                "type": entry.memory_type.value,
                "similarity": round(sim, 3),
                "timestamp": entry.timestamp
            }
            for entry, sim in results
        ]
    
    def get_preferences(self) -> Dict:
        """获取用户偏好"""
        return self.memory.get_user_preferences()
    
    def get_recent_context(self, hours: int = 24) -> List[Dict]:
        """获取近期上下文"""
        entries = self.memory.get_recent_context(hours)
        return [
            {
                "content": e.content,
                "type": e.memory_type.value,
                "timestamp": e.timestamp
            }
            for e in entries
        ]
    
    def forget(self, memory_id: str) -> bool:
        """遗忘特定记忆"""
        return self.memory.delete(memory_id)
    
    def stats(self) -> Dict:
        """获取记忆统计"""
        return self.memory.get_stats()


# 便捷函数
def create_memory_agent(agent_id: str, storage_path: Optional[str] = None) -> MemoryEnhancedAgent:
    """创建记忆增强Agent"""
    return MemoryEnhancedAgent(agent_id, storage_path)


if __name__ == "__main__":
    # 演示
    agent = create_memory_agent("demo-agent")
    
    # 存储记忆
    print("=== 存储记忆 ===")
    agent.remember("用户喜欢使用Python进行数据分析", "preference", "high", 
                   preferences={"language": "Python", "domain": "data_analysis"})
    agent.remember("当前正在开发股票分析系统", "context", "critical",
                   project="stock-analyzer", status="in_progress")
    agent.remember("用户要求每天早上8:30发送股票早报", "fact", "high")
    
    # 语义搜索
    print("\n=== 语义搜索 '编程语言' ===")
    results = agent.recall("编程语言", top_k=3)
    for r in results:
        print(f"  [{r['type']}] {r['content']} (相似度: {r['similarity']})")
    
    # 获取偏好
    print("\n=== 用户偏好 ===")
    prefs = agent.get_preferences()
    print(f"  {prefs}")
    
    # 统计
    print("\n=== 记忆统计 ===")
    stats = agent.stats()
    print(f"  总记忆数: {stats['total_memories']}")
    print(f"  按类型: {stats['by_type']}")
