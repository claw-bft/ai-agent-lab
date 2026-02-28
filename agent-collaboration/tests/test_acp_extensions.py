"""
ACP扩展功能测试套件
测试协商、投票、委托等高级协作模式
"""

import pytest
import sys
import os
from datetime import datetime, timedelta

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from acp_extensions import (
    CollaborationMode, NegotiationStatus, VoteType,
    Proposal, Vote, Delegation,
    NegotiationManager, VotingManager, DelegationManager,
    AdvancedOrchestrator, create_advanced_collaboration_system
)
from agent_protocol import (
    AgentMessage, MessageType, TaskStatus, AgentRole,
    AgentRegistry, MessageBus, TaskOrchestrator
)


class TestNegotiationManager:
    """协商管理器测试"""
    
    @pytest.fixture
    def setup(self):
        """测试设置"""
        bus = MessageBus()
        manager = NegotiationManager(bus)
        return bus, manager
    
    def test_create_proposal(self, setup):
        """测试创建提案"""
        bus, manager = setup
        
        proposal = manager.create_proposal(
            proposer="agent-a",
            proposal_type="resource_share",
            content={"resource": "gpu", "share_ratio": 0.5},
            timeout_seconds=60
        )
        
        assert proposal.proposer == "agent-a"
        assert proposal.proposal_type == "resource_share"
        assert proposal.content["resource"] == "gpu"
        assert proposal.status == NegotiationStatus.PROPOSING
        assert proposal.expires_at is not None
    
    def test_respond_to_proposal_accept(self, setup):
        """测试接受提案"""
        bus, manager = setup
        
        proposal = manager.create_proposal(
            proposer="agent-a",
            proposal_type="test",
            content={"data": "value"}
        )
        
        result = manager.respond_to_proposal(
            proposal_id=proposal.proposal_id,
            responder="agent-b",
            accepted=True
        )
        
        assert result is True
        assert proposal.status == NegotiationStatus.ACCEPTED
        assert "agent-b" in proposal.responses
        assert proposal.responses["agent-b"]["accepted"] is True
    
    def test_respond_to_proposal_reject(self, setup):
        """测试拒绝提案"""
        bus, manager = setup
        
        proposal = manager.create_proposal(
            proposer="agent-a",
            proposal_type="test",
            content={"data": "value"}
        )
        
        result = manager.respond_to_proposal(
            proposal_id=proposal.proposal_id,
            responder="agent-b",
            accepted=False,
            reason="资源不足"
        )
        
        assert result is True
        assert proposal.status == NegotiationStatus.REJECTED
        assert proposal.responses["agent-b"]["reason"] == "资源不足"
    
    def test_respond_to_proposal_counter(self, setup):
        """测试反提案"""
        bus, manager = setup
        
        proposal = manager.create_proposal(
            proposer="agent-a",
            proposal_type="test",
            content={"price": 100}
        )
        
        result = manager.respond_to_proposal(
            proposal_id=proposal.proposal_id,
            responder="agent-b",
            accepted=False,
            counter_proposal={"price": 80}
        )
        
        assert result is True
        assert proposal.status == NegotiationStatus.COUNTERING
        assert "counter_proposal" in proposal.responses["agent-b"]
    
    def test_respond_to_expired_proposal(self, setup):
        """测试响应过期提案"""
        bus, manager = setup
        
        proposal = manager.create_proposal(
            proposer="agent-a",
            proposal_type="test",
            content={"data": "value"},
            timeout_seconds=-1  # 已过期
        )
        
        result = manager.respond_to_proposal(
            proposal_id=proposal.proposal_id,
            responder="agent-b",
            accepted=True
        )
        
        assert result is False
        assert proposal.status == NegotiationStatus.EXPIRED
    
    def test_check_consensus(self, setup):
        """测试共识检查"""
        bus, manager = setup
        
        proposal = manager.create_proposal(
            proposer="agent-a",
            proposal_type="test",
            content={"data": "value"}
        )
        
        # 初始状态
        result = manager.check_consensus(proposal.proposal_id, ["agent-b", "agent-c"])
        assert result is None
        
        # agent-b 接受
        manager.respond_to_proposal(proposal.proposal_id, "agent-b", accepted=True)
        result = manager.check_consensus(proposal.proposal_id, ["agent-b", "agent-c"])
        assert result is None  # 还需要 agent-c
        
        # agent-c 接受
        manager.respond_to_proposal(proposal.proposal_id, "agent-c", accepted=True)
        result = manager.check_consensus(proposal.proposal_id, ["agent-b", "agent-c"])
        assert result is True
    
    def test_list_active_proposals(self, setup):
        """测试列出活动提案"""
        bus, manager = setup
        
        # 创建活动提案
        active = manager.create_proposal(
            proposer="agent-a",
            proposal_type="test",
            content={},
            timeout_seconds=3600
        )
        
        # 创建已过期提案
        expired = manager.create_proposal(
            proposer="agent-a",
            proposal_type="test",
            content={},
            timeout_seconds=-1
        )
        
        active_list = manager.list_active_proposals()
        assert len(active_list) == 1
        assert active_list[0].proposal_id == active.proposal_id


class TestVotingManager:
    """投票管理器测试"""
    
    @pytest.fixture
    def setup(self):
        """测试设置"""
        bus = MessageBus()
        manager = VotingManager(bus)
        return bus, manager
    
    def test_create_vote(self, setup):
        """测试创建投票"""
        bus, manager = setup
        
        vote = manager.create_vote(
            topic="选择方向",
            vote_type=VoteType.MAJORITY,
            options=["A", "B", "C"],
            eligible_voters=["agent-a", "agent-b", "agent-c"],
            duration_seconds=300
        )
        
        assert vote.topic == "选择方向"
        assert vote.vote_type == VoteType.MAJORITY
        assert len(vote.options) == 3
        assert vote.status == "open"
        assert vote.deadline is not None
    
    def test_cast_vote_majority(self, setup):
        """测试多数决投票"""
        bus, manager = setup
        
        vote = manager.create_vote(
            topic="选择方向",
            vote_type=VoteType.MAJORITY,
            options=["A", "B"],
            eligible_voters=["agent-a", "agent-b", "agent-c"],
            min_participation=0.5
        )
        
        # 投票
        manager.cast_vote(vote.vote_id, "agent-a", "A")
        assert vote.result is None  # 还没达到最低参与率
        
        manager.cast_vote(vote.vote_id, "agent-b", "A")
        # 现在应该出结果了
        assert vote.result == "A"
        assert vote.status == "closed"
    
    def test_cast_vote_unanimous(self, setup):
        """测试全体一致投票"""
        bus, manager = setup
        
        vote = manager.create_vote(
            topic="重要决策",
            vote_type=VoteType.UNANIMOUS,
            options=["yes", "no"],
            eligible_voters=["agent-a", "agent-b"]
        )
        
        manager.cast_vote(vote.vote_id, "agent-a", "yes")
        assert vote.result is None  # 还需要一个
        
        manager.cast_vote(vote.vote_id, "agent-b", "yes")
        assert vote.result == "yes"
    
    def test_cast_vote_weighted(self, setup):
        """测试加权投票"""
        bus, manager = setup
        
        vote = manager.create_vote(
            topic="加权选择",
            vote_type=VoteType.WEIGHTED,
            options=["A", "B"],
            eligible_voters=["agent-a", "agent-b", "agent-c"],
            weights={"agent-a": 3.0, "agent-b": 2.0, "agent-c": 1.0},
            min_participation=0.5
        )
        
        # agent-a 权重3，投A
        manager.cast_vote(vote.vote_id, "agent-a", {"A": 1.0, "B": 0.0})
        
        # agent-b 权重2，投B
        manager.cast_vote(vote.vote_id, "agent-b", {"A": 0.0, "B": 1.0})
        
        # A得分=3*1+2*0=3, B得分=3*0+2*1=2, A获胜
        assert vote.result == "A"
    
    def test_cast_vote_ranked(self, setup):
        """测试排序投票"""
        bus, manager = setup
        
        vote = manager.create_vote(
            topic="排序选择",
            vote_type=VoteType.RANKED,
            options=["A", "B", "C"],
            eligible_voters=["agent-a", "agent-b", "agent-c"],
            min_participation=0.5
        )
        
        # 投票
        manager.cast_vote(vote.vote_id, "agent-a", ["A", "B", "C"])
        manager.cast_vote(vote.vote_id, "agent-b", ["B", "A", "C"])
        
        # 第一轮: A=1, B=1, 无多数，淘汰C
        # 第二轮: A=1(原)+1(C的第二选择)=2, B=1, A获胜
        assert vote.result == "A"
    
    def test_cast_vote_ineligible(self, setup):
        """测试不合格投票者"""
        bus, manager = setup
        
        vote = manager.create_vote(
            topic="测试",
            vote_type=VoteType.MAJORITY,
            options=["A", "B"],
            eligible_voters=["agent-a"]
        )
        
        result = manager.cast_vote(vote.vote_id, "agent-b", "A")
        assert result is False
    
    def test_close_vote_manually(self, setup):
        """测试手动关闭投票"""
        bus, manager = setup
        
        vote = manager.create_vote(
            topic="测试",
            vote_type=VoteType.MAJORITY,
            options=["A", "B"],
            eligible_voters=["agent-a", "agent-b"]
        )
        
        manager.cast_vote(vote.vote_id, "agent-a", "A")
        result = manager.close_vote(vote.vote_id)
        
        assert result == "A"
        assert vote.status == "closed"


class TestDelegationManager:
    """委托管理器测试"""
    
    @pytest.fixture
    def setup(self):
        """测试设置"""
        bus = MessageBus()
        manager = DelegationManager(bus)
        return bus, manager
    
    def test_create_delegation(self, setup):
        """测试创建委托"""
        bus, manager = setup
        
        delegation = manager.create_delegation(
            delegator="agent-a",
            delegatee="agent-b",
            scope=["finance", "stock"],
            permissions=["execute", "query"],
            duration_seconds=3600
        )
        
        assert delegation.delegator == "agent-a"
        assert delegation.delegatee == "agent-b"
        assert "finance" in delegation.scope
        assert "execute" in delegation.permissions
        assert delegation.active is True
        assert delegation.expires_at is not None
    
    def test_check_permission(self, setup):
        """测试权限检查"""
        bus, manager = setup
        
        manager.create_delegation(
            delegator="agent-a",
            delegatee="agent-b",
            scope=["finance"],
            permissions=["execute"],
            duration_seconds=3600
        )
        
        # 有权限
        result = manager.check_permission("agent-a", "execute", "finance")
        assert result == "agent-b"
        
        # 无权限 - 范围不匹配
        result = manager.check_permission("agent-a", "execute", "coding")
        assert result is None
        
        # 无权限 - 操作不匹配
        result = manager.check_permission("agent-a", "delete", "finance")
        assert result is None
    
    def test_revoke_delegation(self, setup):
        """测试撤销委托"""
        bus, manager = setup
        
        delegation = manager.create_delegation(
            delegator="agent-a",
            delegatee="agent-b",
            scope=["finance"],
            permissions=["execute"]
        )
        
        # 非委托者不能撤销
        result = manager.revoke_delegation(delegation.delegation_id, "agent-c")
        assert result is False
        assert delegation.active is True
        
        # 委托者可以撤销
        result = manager.revoke_delegation(delegation.delegation_id, "agent-a")
        assert result is True
        assert delegation.active is False
        
        # 撤销后权限检查
        result = manager.check_permission("agent-a", "execute", "finance")
        assert result is None
    
    def test_expired_delegation(self, setup):
        """测试过期委托"""
        bus, manager = setup
        
        delegation = manager.create_delegation(
            delegator="agent-a",
            delegatee="agent-b",
            scope=["finance"],
            permissions=["execute"],
            duration_seconds=-1  # 已过期
        )
        
        result = manager.check_permission("agent-a", "execute", "finance")
        assert result is None
        assert delegation.active is False
    
    def test_get_active_delegations(self, setup):
        """测试获取活动委托"""
        bus, manager = setup
        
        # 创建活动委托
        active = manager.create_delegation(
            delegator="agent-a",
            delegatee="agent-b",
            scope=["finance"],
            duration_seconds=3600
        )
        
        # 创建过期委托
        expired = manager.create_delegation(
            delegator="agent-a",
            delegatee="agent-c",
            scope=["coding"],
            duration_seconds=-1
        )
        
        active_list = manager.get_active_delegations("agent-a")
        assert len(active_list) == 1
        assert active_list[0].delegation_id == active.delegation_id
    
    def test_cleanup_expired(self, setup):
        """测试清理过期委托"""
        bus, manager = setup
        
        delegation = manager.create_delegation(
            delegator="agent-a",
            delegatee="agent-b",
            scope=["finance"],
            duration_seconds=-1
        )
        
        assert delegation.active is True  # 清理前
        manager.cleanup_expired()
        assert delegation.active is False  # 清理后


class TestAdvancedOrchestrator:
    """高级编排器测试"""
    
    @pytest.fixture
    def setup(self):
        """测试设置"""
        registry, bus, orchestrator = create_advanced_collaboration_system()
        
        # 注册测试Agent
        registry.register("agent-a", AgentRole.WORKER, ["task-a"])
        registry.register("agent-b", AgentRole.WORKER, ["task-b"])
        
        return registry, bus, orchestrator
    
    def test_register_workflow_template(self, setup):
        """测试注册工作流模板"""
        registry, bus, orchestrator = setup
        
        orchestrator.register_workflow_template(
            template_id="test-workflow",
            name="测试工作流",
            description="用于测试的工作流",
            steps=[
                {
                    "name": "步骤1",
                    "type": "task",
                    "agent": "agent-a",
                    "task_type": "task-a",
                    "parameters": {"input": "$user_input"}
                }
            ],
            variables={"user_input": "default"}
        )
        
        assert "test-workflow" in orchestrator._workflow_templates
        template = orchestrator._workflow_templates["test-workflow"]
        assert template["name"] == "测试工作流"
        assert len(template["steps"]) == 1
    
    def test_create_workflow(self, setup):
        """测试创建工作流"""
        registry, bus, orchestrator = setup
        
        orchestrator.register_workflow_template(
            template_id="test-workflow",
            name="测试工作流",
            description="用于测试",
            steps=[
                {
                    "name": "步骤1",
                    "type": "task",
                    "agent": "agent-a",
                    "task_type": "task-a",
                    "parameters": {"input": "$user_input"}
                }
            ]
        )
        
        workflow_id = orchestrator.create_workflow(
            template_id="test-workflow",
            parameters={"user_input": "hello"}
        )
        
        assert workflow_id is not None
        assert workflow_id in orchestrator._active_workflows
        
        workflow = orchestrator._active_workflows[workflow_id]
        assert workflow["status"] == "created"
        assert len(workflow["steps"]) == 1
        assert workflow["steps"][0]["parameters"]["input"] == "hello"
    
    def test_resolve_parameters(self, setup):
        """测试参数解析"""
        registry, bus, orchestrator = setup
        
        result = orchestrator._resolve_parameters(
            template_params={"a": "$var_a", "b": "fixed", "c": "$var_c"},
            runtime_params={"var_a": "value_a", "var_c": "value_c"}
        )
        
        assert result["a"] == "value_a"
        assert result["b"] == "fixed"
        assert result["c"] == "value_c"
    
    def test_get_workflow_status(self, setup):
        """测试获取工作流状态"""
        registry, bus, orchestrator = setup
        
        orchestrator.register_workflow_template(
            template_id="test-workflow",
            name="测试",
            description="测试",
            steps=[{"name": "步骤1"}, {"name": "步骤2"}]
        )
        
        workflow_id = orchestrator.create_workflow("test-workflow")
        orchestrator.start_workflow(workflow_id)
        
        status = orchestrator.get_workflow_status(workflow_id)
        assert status is not None
        assert status["workflow_id"] == workflow_id
        assert status["status"] == "running"
        assert "progress" in status
    
    def test_integration_all_managers(self, setup):
        """集成测试 - 所有管理器"""
        registry, bus, orchestrator = setup
        
        # 验证协商管理器
        assert orchestrator.negotiation_manager is not None
        
        # 验证投票管理器
        assert orchestrator.voting_manager is not None
        
        # 验证委托管理器
        assert orchestrator.delegation_manager is not None
        
        # 创建提案
        proposal = orchestrator.negotiation_manager.create_proposal(
            proposer="agent-a",
            proposal_type="test",
            content={"data": "value"}
        )
        assert proposal is not None
        
        # 创建投票
        vote = orchestrator.voting_manager.create_vote(
            topic="测试",
            vote_type=VoteType.MAJORITY,
            options=["A", "B"],
            eligible_voters=["agent-a"]
        )
        assert vote is not None
        
        # 创建委托
        delegation = orchestrator.delegation_manager.create_delegation(
            delegator="agent-a",
            delegatee="agent-b",
            scope=["test"]
        )
        assert delegation is not None


class TestEdgeCases:
    """边界情况测试"""
    
    def test_invalid_proposal_id(self):
        """测试无效提案ID"""
        bus = MessageBus()
        manager = NegotiationManager(bus)
        
        result = manager.respond_to_proposal("invalid-id", "agent-a", True)
        assert result is False
        
        proposal = manager.get_proposal("invalid-id")
        assert proposal is None
    
    def test_empty_vote(self):
        """测试空投票"""
        bus = MessageBus()
        manager = VotingManager(bus)
        
        vote = manager.create_vote(
            topic="测试",
            vote_type=VoteType.MAJORITY,
            options=["A", "B"],
            eligible_voters=["agent-a"]
        )
        
        # 直接关闭，没有投票
        result = manager.close_vote(vote.vote_id)
        assert result is None
    
    def test_self_delegation(self):
        """测试自我委托"""
        bus = MessageBus()
        manager = DelegationManager(bus)
        
        # 虽然技术上允许，但应该检查
        delegation = manager.create_delegation(
            delegator="agent-a",
            delegatee="agent-a",  # 自己委托给自己
            scope=["test"]
        )
        
        assert delegation.delegator == delegation.delegatee
    
    def test_workflow_with_dependencies(self):
        """测试带依赖的工作流"""
        registry, bus, orchestrator = create_advanced_collaboration_system()
        
        orchestrator.register_workflow_template(
            template_id="dep-workflow",
            name="依赖工作流",
            description="有依赖步骤的工作流",
            steps=[
                {"name": "步骤1", "step_id": "step1"},
                {"name": "步骤2", "dependencies": ["step1"]},
                {"name": "步骤3", "dependencies": ["step1"]}
            ]
        )
        
        workflow_id = orchestrator.create_workflow("dep-workflow")
        workflow = orchestrator._active_workflows[workflow_id]
        
        # 检查依赖关系
        assert workflow["steps"][1]["dependencies"] == ["step1"]
        assert workflow["steps"][2]["dependencies"] == ["step1"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
