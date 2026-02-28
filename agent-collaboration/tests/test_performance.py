"""
ACP扩展模块性能基准测试
Performance Benchmarks for Agent Collaboration Protocol Extensions
"""

import time
import pytest
from typing import List, Dict, Any
import asyncio

from acp_extensions import (
    NegotiationManager, VotingManager, DelegationManager,
    Proposal, Vote, DelegationTask, CollaborationMode, VoteType
)
from agent_protocol import AgentRegistry, MessageBus, Agent, AgentRole


class TestNegotiationPerformance:
    """协商管理器性能测试"""
    
    def test_proposal_creation_performance(self):
        """测试提案创建性能"""
        manager = NegotiationManager()
        
        start = time.perf_counter()
        for i in range(1000):
            manager.create_proposal(
                proposer=f"agent_{i}",
                proposal_type="test",
                content={"value": i},
                conditions={}
            )
        elapsed = time.perf_counter() - start
        
        # 1000个提案应在1秒内完成
        assert elapsed < 1.0, f"创建1000个提案耗时 {elapsed:.3f}s，超过1秒"
        assert len(manager.proposals) == 1000
    
    def test_proposal_response_performance(self):
        """测试提案响应性能"""
        manager = NegotiationManager()
        proposal = manager.create_proposal(
            proposer="agent_1",
            proposal_type="test",
            content={},
            conditions={}
        )
        
        start = time.perf_counter()
        for i in range(100):
            manager.respond_to_proposal(
                proposal.proposal_id,
                f"agent_{i}",
                "accept",
                {}
            )
        elapsed = time.perf_counter() - start
        
        # 100个响应应在0.5秒内完成
        assert elapsed < 0.5, f"100个响应耗时 {elapsed:.3f}s，超过0.5秒"
    
    def test_check_consensus_performance(self):
        """测试共识检查性能"""
        manager = NegotiationManager()
        
        # 创建大量提案
        proposals = []
        for i in range(100):
            p = manager.create_proposal(
                proposer="agent_1",
                proposal_type="test",
                content={},
                conditions={},
                required_participants=[f"agent_{j}" for j in range(10)]
            )
            proposals.append(p)
            # 添加响应
            for j in range(10):
                manager.respond_to_proposal(p.proposal_id, f"agent_{j}", "accept", {})
        
        start = time.perf_counter()
        for p in proposals:
            manager.check_consensus(p.proposal_id)
        elapsed = time.perf_counter() - start
        
        # 100个提案的共识检查应在0.5秒内完成
        assert elapsed < 0.5, f"100个提案共识检查耗时 {elapsed:.3f}s，超过0.5秒"


class TestVotingPerformance:
    """投票管理器性能测试"""
    
    def test_vote_creation_performance(self):
        """测试投票创建性能"""
        manager = VotingManager()
        
        start = time.perf_counter()
        for i in range(500):
            manager.create_vote(
                topic=f"topic_{i}",
                vote_type=VoteType.MAJORITY,
                options=["a", "b", "c"]
            )
        elapsed = time.perf_counter() - start
        
        # 500个投票应在0.5秒内完成
        assert elapsed < 0.5, f"创建500个投票耗时 {elapsed:.3f}s，超过0.5秒"
    
    def test_cast_vote_performance(self):
        """测试投票性能"""
        manager = VotingManager()
        vote = manager.create_vote(
            topic="test",
            vote_type=VoteType.MAJORITY,
            options=["a", "b", "c"]
        )
        
        start = time.perf_counter()
        for i in range(1000):
            manager.cast_vote(vote.vote_id, f"agent_{i}", "a")
        elapsed = time.perf_counter() - start
        
        # 1000个投票应在0.5秒内完成
        assert elapsed < 0.5, f"1000个投票耗时 {elapsed:.3f}s，超过0.5秒"
    
    def test_tally_votes_performance(self):
        """测试计票性能"""
        manager = VotingManager()
        
        # 创建多个投票并添加大量选票
        votes = []
        for i in range(50):
            v = manager.create_vote(
                topic=f"topic_{i}",
                vote_type=VoteType.MAJORITY,
                options=["a", "b", "c"]
            )
            votes.append(v)
            for j in range(100):
                manager.cast_vote(v.vote_id, f"agent_{j}", ["a", "b", "c"][j % 3])
        
        start = time.perf_counter()
        for v in votes:
            manager.tally_votes(v.vote_id)
        elapsed = time.perf_counter() - start
        
        # 50个投票的计票应在0.5秒内完成
        assert elapsed < 0.5, f"50个投票计票耗时 {elapsed:.3f}s，超过0.5秒"


class TestDelegationPerformance:
    """委托管理器性能测试"""
    
    def test_delegation_creation_performance(self):
        """测试委托创建性能"""
        manager = DelegationManager()
        
        start = time.perf_counter()
        for i in range(500):
            manager.delegate_task(
                delegator=f"agent_{i}",
                delegatee=f"delegatee_{i}",
                task_type="test",
                task_data={},
                permissions=["read", "write"]
            )
        elapsed = time.perf_counter() - start
        
        # 500个委托应在0.5秒内完成
        assert elapsed < 0.5, f"创建500个委托耗时 {elapsed:.3f}s，超过0.5秒"
    
    def test_check_permission_performance(self):
        """测试权限检查性能"""
        manager = DelegationManager()
        
        # 创建大量委托
        for i in range(100):
            manager.delegate_task(
                delegator="agent_1",
                delegatee=f"delegatee_{i}",
                task_type="test",
                task_data={},
                permissions=["read", "write", "execute"]
            )
        
        start = time.perf_counter()
        for i in range(1000):
            manager.check_permission(f"delegatee_{i % 100}", "read")
        elapsed = time.perf_counter() - start
        
        # 1000次权限检查应在0.3秒内完成
        assert elapsed < 0.3, f"1000次权限检查耗时 {elapsed:.3f}s，超过0.3秒"
    
    def test_revoke_delegation_performance(self):
        """测试撤销委托性能"""
        manager = DelegationManager()
        
        delegations = []
        for i in range(200):
            d = manager.delegate_task(
                delegator="agent_1",
                delegatee=f"delegatee_{i}",
                task_type="test",
                task_data={},
                permissions=["read"]
            )
            delegations.append(d)
        
        start = time.perf_counter()
        for d in delegations:
            manager.revoke_delegation(d.delegation_id, "agent_1")
        elapsed = time.perf_counter() - start
        
        # 200个委托撤销应在0.3秒内完成
        assert elapsed < 0.3, f"200个委托撤销耗时 {elapsed:.3f}s，超过0.3秒"


class TestMemoryEfficiency:
    """内存效率测试"""
    
    def test_proposal_memory_footprint(self):
        """测试提案内存占用"""
        import sys
        
        manager = NegotiationManager()
        proposals = []
        
        for i in range(100):
            p = manager.create_proposal(
                proposer=f"agent_{i}",
                proposal_type="test",
                content={"data": "x" * 100},
                conditions={}
            )
            proposals.append(p)
        
        # 估算内存占用（每个提案应小于2KB）
        total_size = sum(sys.getsizeof(p.__dict__) for p in proposals)
        avg_size = total_size / len(proposals)
        
        assert avg_size < 2048, f"平均提案内存占用 {avg_size:.0f} bytes，超过2KB"
    
    def test_vote_memory_footprint(self):
        """测试投票内存占用"""
        import sys
        
        manager = VotingManager()
        votes = []
        
        for i in range(100):
            v = manager.create_vote(
                topic=f"topic_{i}",
                vote_type=VoteType.MAJORITY,
                options=["a", "b", "c", "d", "e"]
            )
            votes.append(v)
        
        total_size = sum(sys.getsizeof(v.__dict__) for v in votes)
        avg_size = total_size / len(votes)
        
        assert avg_size < 1024, f"平均投票内存占用 {avg_size:.0f} bytes，超过1KB"


class TestScalability:
    """可扩展性测试"""
    
    def test_large_scale_negotiation(self):
        """测试大规模协商场景"""
        manager = NegotiationManager()
        
        # 模拟100个agent参与协商
        num_agents = 100
        num_proposals = 50
        
        start = time.perf_counter()
        
        for i in range(num_proposals):
            p = manager.create_proposal(
                proposer=f"agent_{i % num_agents}",
                proposal_type="resource_allocation",
                content={"resource": f"r{i}", "amount": i * 10},
                conditions={},
                required_participants=[f"agent_{j}" for j in range(num_agents)]
            )
            
            # 每个提案100个响应
            for j in range(num_agents):
                manager.respond_to_proposal(
                    p.proposal_id,
                    f"agent_{j}",
                    "accept" if j % 2 == 0 else "counter",
                    {"counter_offer": j * 5}
                )
        
        elapsed = time.perf_counter() - start
        
        # 5000次操作应在2秒内完成
        assert elapsed < 2.0, f"大规模协商耗时 {elapsed:.3f}s，超过2秒"
    
    def test_large_scale_voting(self):
        """测试大规模投票场景"""
        manager = VotingManager()
        
        # 创建投票，1000个agent参与
        vote = manager.create_vote(
            topic="major_decision",
            vote_type=VoteType.MAJORITY,
            options=["option_a", "option_b", "option_c"]
        )
        
        start = time.perf_counter()
        
        for i in range(1000):
            manager.cast_vote(vote.vote_id, f"agent_{i}", ["option_a", "option_b", "option_c"][i % 3])
        
        result = manager.tally_votes(vote.vote_id)
        
        elapsed = time.perf_counter() - start
        
        # 1000个投票应在1秒内完成
        assert elapsed < 1.0, f"大规模投票耗时 {elapsed:.3f}s，超过1秒"
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
