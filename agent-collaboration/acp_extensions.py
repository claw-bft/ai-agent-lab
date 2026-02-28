"""
ACP扩展 - 高级协作模式
Agent Collaboration Protocol Extensions

支持协商、投票、委托等高级多Agent协作模式
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Set
from datetime import datetime, timedelta
import json
import uuid
import asyncio
from collections import defaultdict
import heapq

from agent_protocol import (
    AgentMessage, MessageType, TaskStatus, AgentRole,
    AgentRegistry, MessageBus, TaskOrchestrator, Task
)


class CollaborationMode(Enum):
    """协作模式"""
    NEGOTIATION = "negotiation"     # 协商模式
    VOTING = "voting"               # 投票模式
    DELEGATION = "delegation"       # 委托模式
    AUCTION = "auction"             # 拍卖模式
    CONSENSUS = "consensus"         # 共识模式


class NegotiationStatus(Enum):
    """协商状态"""
    PROPOSING = auto()      # 提案中
    COUNTERING = auto()     # 反提案
    ACCEPTED = auto()       # 已接受
    REJECTED = auto()       # 已拒绝
    EXPIRED = auto()        # 已过期


class VoteType(Enum):
    """投票类型"""
    MAJORITY = "majority"           # 多数决
    UNANIMOUS = "unanimous"         # 全体一致
    WEIGHTED = "weighted"           # 加权投票
    RANKED = "ranked"               # 排序投票


@dataclass
class Proposal:
    """协商提案"""
    proposal_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    proposer: str = ""
    proposal_type: str = ""         # 提案类型
    content: Dict[str, Any] = field(default_factory=dict)
    conditions: Dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    status: NegotiationStatus = NegotiationStatus.PROPOSING
    responses: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "proposer": self.proposer,
            "proposal_type": self.proposal_type,
            "content": self.content,
            "conditions": self.conditions,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "status": self.status.name,
            "responses": self.responses,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class Vote:
    """投票记录"""
    vote_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    topic: str = ""
    vote_type: VoteType = VoteType.MAJORITY
    options: List[str] = field(default_factory=list)
    votes: Dict[str, Any] = field(default_factory=dict)  # agent_id -> vote
    weights: Dict[str, float] = field(default_factory=dict)  # agent_id -> weight
    deadline: Optional[datetime] = None
    min_participation: float = 0.5  # 最低参与率
    result: Optional[str] = None
    status: str = "open"  # open, closed, cancelled
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "vote_id": self.vote_id,
            "topic": self.topic,
            "vote_type": self.vote_type.value,
            "options": self.options,
            "votes": self.votes,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "min_participation": self.min_participation,
            "result": self.result,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class Delegation:
    """委托关系"""
    delegation_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    delegator: str = ""             # 委托方
    delegatee: str = ""             # 受托方
    scope: List[str] = field(default_factory=list)  # 委托范围
    permissions: List[str] = field(default_factory=list)
    expires_at: Optional[datetime] = None
    constraints: Dict[str, Any] = field(default_factory=dict)
    active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "delegation_id": self.delegation_id,
            "delegator": self.delegator,
            "delegatee": self.delegatee,
            "scope": self.scope,
            "permissions": self.permissions,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "constraints": self.constraints,
            "active": self.active,
            "created_at": self.created_at.isoformat()
        }


class NegotiationManager:
    """协商管理器"""
    
    def __init__(self, message_bus: MessageBus):
        self.message_bus = message_bus
        self._proposals: Dict[str, Proposal] = {}
        self._handlers: Dict[str, Callable] = {}
        self._default_timeout = timedelta(minutes=5)
    
    def create_proposal(self, proposer: str, proposal_type: str,
                       content: Dict[str, Any],
                       conditions: Dict[str, Any] = None,
                       timeout_seconds: int = 300) -> Proposal:
        """创建提案"""
        proposal = Proposal(
            proposer=proposer,
            proposal_type=proposal_type,
            content=content,
            conditions=conditions or {},
            expires_at=datetime.now() + timedelta(seconds=timeout_seconds)
        )
        self._proposals[proposal.proposal_id] = proposal
        
        # 广播提案
        message = AgentMessage(
            msg_type=MessageType.EVENT,
            sender=proposer,
            receiver="",  # 广播
            payload={
                "event_type": "proposal_created",
                "proposal": proposal.to_dict()
            }
        )
        self.message_bus.publish(message)
        
        return proposal
    
    def respond_to_proposal(self, proposal_id: str, responder: str,
                           accepted: bool,
                           counter_proposal: Dict[str, Any] = None,
                           reason: str = None) -> bool:
        """响应提案"""
        if proposal_id not in self._proposals:
            return False
        
        proposal = self._proposals[proposal_id]
        
        # 检查是否过期
        if proposal.expires_at and datetime.now() > proposal.expires_at:
            proposal.status = NegotiationStatus.EXPIRED
            return False
        
        response = {
            "accepted": accepted,
            "responded_at": datetime.now().isoformat(),
            "reason": reason
        }
        
        if counter_proposal:
            response["counter_proposal"] = counter_proposal
            proposal.status = NegotiationStatus.COUNTERING
        elif accepted:
            proposal.status = NegotiationStatus.ACCEPTED
        else:
            proposal.status = NegotiationStatus.REJECTED
        
        proposal.responses[responder] = response
        
        # 通知提案者
        message = AgentMessage(
            msg_type=MessageType.EVENT,
            sender=responder,
            receiver=proposal.proposer,
            payload={
                "event_type": "proposal_response",
                "proposal_id": proposal_id,
                "response": response
            },
            correlation_id=proposal_id
        )
        self.message_bus.publish(message)
        
        return True
    
    def get_proposal(self, proposal_id: str) -> Optional[Proposal]:
        """获取提案"""
        return self._proposals.get(proposal_id)
    
    def list_active_proposals(self) -> List[Proposal]:
        """列出活动提案"""
        now = datetime.now()
        return [
            p for p in self._proposals.values()
            if p.status in (NegotiationStatus.PROPOSING, NegotiationStatus.COUNTERING)
            and (not p.expires_at or p.expires_at > now)
        ]
    
    def check_consensus(self, proposal_id: str, 
                       required_agents: List[str]) -> Optional[bool]:
        """检查是否达成共识"""
        if proposal_id not in self._proposals:
            return None
        
        proposal = self._proposals[proposal_id]
        
        if proposal.status == NegotiationStatus.REJECTED:
            return False
        
        if proposal.status == NegotiationStatus.ACCEPTED:
            return True
        
        # 检查所有必需Agent是否都已响应并接受
        responses = proposal.responses
        
        # 首先检查是否所有必需Agent都已响应
        all_responded = all(agent in responses for agent in required_agents)
        if not all_responded:
            return None  # 还有Agent未响应
        
        # 所有Agent都已响应，检查是否全部接受
        all_accepted = all(
            responses.get(agent, {}).get("accepted", False)
            for agent in required_agents
        )
        
        if all_accepted:
            proposal.status = NegotiationStatus.ACCEPTED
            return True
        else:
            # 有人拒绝，标记为拒绝
            proposal.status = NegotiationStatus.REJECTED
            return False


class VotingManager:
    """投票管理器"""
    
    def __init__(self, message_bus: MessageBus):
        self.message_bus = message_bus
        self._votes: Dict[str, Vote] = {}
    
    def create_vote(self, topic: str, vote_type: VoteType,
                   options: List[str],
                   eligible_voters: List[str],
                   weights: Dict[str, float] = None,
                   duration_seconds: int = 300,
                   min_participation: float = 0.5) -> Vote:
        """创建投票"""
        vote = Vote(
            topic=topic,
            vote_type=vote_type,
            options=options,
            weights=weights or {voter: 1.0 for voter in eligible_voters},
            deadline=datetime.now() + timedelta(seconds=duration_seconds),
            min_participation=min_participation
        )
        
        # 只保留合格投票者的权重
        vote.weights = {k: v for k, v in vote.weights.items() 
                       if k in eligible_voters}
        
        self._votes[vote.vote_id] = vote
        
        # 广播投票开始
        message = AgentMessage(
            msg_type=MessageType.EVENT,
            sender="voting-manager",
            receiver="",  # 广播
            payload={
                "event_type": "vote_started",
                "vote": vote.to_dict()
            }
        )
        self.message_bus.publish(message)
        
        return vote
    
    def cast_vote(self, vote_id: str, voter: str, 
                 choice: Any) -> bool:
        """投票"""
        if vote_id not in self._votes:
            return False
        
        vote = self._votes[vote_id]
        
        # 检查投票是否还在进行
        if vote.status != "open":
            return False
        
        # 检查是否过期
        if vote.deadline and datetime.now() > vote.deadline:
            vote.status = "closed"
            return False
        
        # 检查投票者资格
        if voter not in vote.weights:
            return False
        
        vote.votes[voter] = choice
        
        # 检查是否达到最低参与率
        participation = len(vote.votes) / len(vote.weights)
        if participation >= vote.min_participation:
            self._tally_votes(vote_id)
        
        return True
    
    def _tally_votes(self, vote_id: str) -> Optional[str]:
        """计票"""
        if vote_id not in self._votes:
            return None
        
        vote = self._votes[vote_id]
        
        if not vote.votes:
            return None
        
        if vote.vote_type == VoteType.MAJORITY:
            # 简单多数
            counts = defaultdict(float)
            for voter, choice in vote.votes.items():
                weight = vote.weights.get(voter, 1.0)
                counts[choice] += weight
            
            total = sum(counts.values())
            winner = max(counts.items(), key=lambda x: x[1])
            
            if winner[1] > total / 2:
                vote.result = winner[0]
                vote.status = "closed"
        
        elif vote.vote_type == VoteType.UNANIMOUS:
            # 全体一致 - 必须所有合格投票者都投票且选择相同
            choices = set(vote.votes.values())
            all_voted = len(vote.votes) == len(vote.weights)
            if all_voted and len(choices) == 1:
                vote.result = list(choices)[0]
                vote.status = "closed"
        
        elif vote.vote_type == VoteType.WEIGHTED:
            # 加权投票
            scores = defaultdict(float)
            for voter, choice in vote.votes.items():
                weight = vote.weights.get(voter, 1.0)
                if isinstance(choice, dict):
                    for opt, score in choice.items():
                        scores[opt] += score * weight
                else:
                    scores[choice] += weight
            
            vote.result = max(scores.items(), key=lambda x: x[1])[0]
            vote.status = "closed"
        
        elif vote.vote_type == VoteType.RANKED:
            # 排序投票 (Instant Runoff)
            vote.result = self._instant_runoff(vote)
            vote.status = "closed"
        
        if vote.result:
            # 广播结果
            message = AgentMessage(
                msg_type=MessageType.EVENT,
                sender="voting-manager",
                receiver="",  # 广播
                payload={
                    "event_type": "vote_completed",
                    "vote_id": vote_id,
                    "result": vote.result,
                    "votes": vote.votes
                }
            )
            self.message_bus.publish(message)
        
        return vote.result
    
    def _instant_runoff(self, vote: Vote) -> str:
        """即时复选计票 (IRV)"""
        candidates = set(vote.options)
        
        while candidates:
            # 计算当前轮次每个候选人的第一选择票数
            first_choices = defaultdict(float)
            for voter, ranking in vote.votes.items():
                weight = vote.weights.get(voter, 1.0)
                if isinstance(ranking, list):
                    # 找到该选民在当前候选列表中的最高排名
                    for candidate in ranking:
                        if candidate in candidates:
                            first_choices[candidate] += weight
                            break
            
            if not first_choices:
                break
            
            total = sum(first_choices.values())
            
            # 检查是否有候选人获得多数 (>50%)
            for candidate, count in first_choices.items():
                if count > total / 2:
                    return candidate
            
            # 如果没有多数，淘汰得票最少的候选人
            min_votes = min(first_choices.values())
            losers = [c for c, v in first_choices.items() if v == min_votes]
            
            # 如果只剩一个候选人，返回它
            if len(candidates) == 1:
                return list(candidates)[0]
            
            # 淘汰得票最少的（按字母顺序打破平局）
            loser = sorted(losers)[0]
            candidates.remove(loser)
        
        return list(candidates)[0] if candidates else None
    
    def close_vote(self, vote_id: str) -> Optional[str]:
        """手动关闭投票"""
        if vote_id not in self._votes:
            return None
        
        vote = self._votes[vote_id]
        vote.status = "closed"
        return self._tally_votes(vote_id)
    
    def get_vote(self, vote_id: str) -> Optional[Vote]:
        """获取投票信息"""
        return self._votes.get(vote_id)


class DelegationManager:
    """委托管理器"""
    
    def __init__(self, message_bus: MessageBus):
        self.message_bus = message_bus
        self._delegations: Dict[str, Delegation] = {}
        self._agent_delegations: Dict[str, List[str]] = defaultdict(list)
    
    def create_delegation(self, delegator: str, delegatee: str,
                         scope: List[str],
                         permissions: List[str] = None,
                         duration_seconds: int = 3600,
                         constraints: Dict[str, Any] = None) -> Delegation:
        """创建委托"""
        delegation = Delegation(
            delegator=delegator,
            delegatee=delegatee,
            scope=scope,
            permissions=permissions or ["execute", "respond"],
            expires_at=datetime.now() + timedelta(seconds=duration_seconds),
            constraints=constraints or {}
        )
        
        self._delegations[delegation.delegation_id] = delegation
        self._agent_delegations[delegator].append(delegation.delegation_id)
        
        # 通知受托方
        message = AgentMessage(
            msg_type=MessageType.EVENT,
            sender=delegator,
            receiver=delegatee,
            payload={
                "event_type": "delegation_created",
                "delegation": delegation.to_dict()
            }
        )
        self.message_bus.publish(message)
        
        return delegation
    
    def revoke_delegation(self, delegation_id: str, 
                         revoked_by: str) -> bool:
        """撤销委托"""
        if delegation_id not in self._delegations:
            return False
        
        delegation = self._delegations[delegation_id]
        
        # 只有委托方可以撤销
        if delegation.delegator != revoked_by:
            return False
        
        delegation.active = False
        
        # 通知受托方
        message = AgentMessage(
            msg_type=MessageType.EVENT,
            sender=revoked_by,
            receiver=delegation.delegatee,
            payload={
                "event_type": "delegation_revoked",
                "delegation_id": delegation_id
            }
        )
        self.message_bus.publish(message)
        
        return True
    
    def check_permission(self, agent_id: str, action: str,
                        scope: str) -> Optional[str]:
        """检查Agent是否有权限执行操作"""
        now = datetime.now()
        
        for delegation_id in self._agent_delegations.get(agent_id, []):
            delegation = self._delegations.get(delegation_id)
            
            if not delegation or not delegation.active:
                continue
            
            # 检查是否过期
            if delegation.expires_at and now > delegation.expires_at:
                delegation.active = False
                continue
            
            # 检查权限和范围
            if action in delegation.permissions and scope in delegation.scope:
                return delegation.delegatee
        
        return None
    
    def get_active_delegations(self, agent_id: str) -> List[Delegation]:
        """获取Agent的活动委托"""
        now = datetime.now()
        result = []
        
        for delegation_id in self._agent_delegations.get(agent_id, []):
            delegation = self._delegations.get(delegation_id)
            if delegation and delegation.active:
                if not delegation.expires_at or delegation.expires_at > now:
                    result.append(delegation)
        
        return result
    
    def cleanup_expired(self):
        """清理过期委托"""
        now = datetime.now()
        for delegation in self._delegations.values():
            if delegation.expires_at and delegation.expires_at < now:
                delegation.active = False


class AdvancedOrchestrator(TaskOrchestrator):
    """高级编排器 - 支持复杂工作流"""
    
    def __init__(self, registry: AgentRegistry, message_bus: MessageBus):
        super().__init__(registry, message_bus)
        self.negotiation_manager = NegotiationManager(message_bus)
        self.voting_manager = VotingManager(message_bus)
        self.delegation_manager = DelegationManager(message_bus)
        
        # 工作流模板
        self._workflow_templates: Dict[str, Dict[str, Any]] = {}
        
        # 执行中的工作流
        self._active_workflows: Dict[str, Dict[str, Any]] = {}
    
    def register_workflow_template(self, template_id: str,
                                   name: str,
                                   description: str,
                                   steps: List[Dict[str, Any]],
                                   variables: Dict[str, Any] = None):
        """注册工作流模板"""
        self._workflow_templates[template_id] = {
            "template_id": template_id,
            "name": name,
            "description": description,
            "steps": steps,
            "variables": variables or {}
        }
    
    def create_workflow(self, template_id: str,
                       parameters: Dict[str, Any] = None) -> Optional[str]:
        """从模板创建工作流实例"""
        if template_id not in self._workflow_templates:
            return None
        
        template = self._workflow_templates[template_id]
        workflow_id = str(uuid.uuid4())[:8]
        
        workflow = {
            "workflow_id": workflow_id,
            "template_id": template_id,
            "name": template["name"],
            "status": "created",
            "steps": [],
            "current_step": 0,
            "parameters": parameters or {},
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "results": {}
        }
        
        # 实例化步骤
        for i, step_template in enumerate(template["steps"]):
            step = {
                "step_id": f"{workflow_id}_step_{i}",
                "name": step_template.get("name", f"Step {i}"),
                "type": step_template.get("type", "task"),
                "agent": step_template.get("agent"),
                "task_type": step_template.get("task_type"),
                "parameters": self._resolve_parameters(
                    step_template.get("parameters", {}),
                    parameters or {}
                ),
                "dependencies": step_template.get("dependencies", []),
                "status": "pending",
                "result": None
            }
            workflow["steps"].append(step)
        
        self._active_workflows[workflow_id] = workflow
        return workflow_id
    
    def _resolve_parameters(self, template_params: Dict[str, Any],
                           runtime_params: Dict[str, Any]) -> Dict[str, Any]:
        """解析参数模板"""
        resolved = {}
        for key, value in template_params.items():
            if isinstance(value, str) and value.startswith("$"):
                # 变量引用
                var_name = value[1:]
                resolved[key] = runtime_params.get(var_name, value)
            else:
                resolved[key] = value
        return resolved
    
    def start_workflow(self, workflow_id: str) -> bool:
        """启动工作流"""
        if workflow_id not in self._active_workflows:
            return False
        
        workflow = self._active_workflows[workflow_id]
        workflow["status"] = "running"
        workflow["started_at"] = datetime.now().isoformat()
        
        # 执行第一个就绪的步骤
        self._execute_ready_steps(workflow_id)
        return True
    
    def _execute_ready_steps(self, workflow_id: str):
        """执行就绪的步骤"""
        workflow = self._active_workflows[workflow_id]
        
        for step in workflow["steps"]:
            if step["status"] != "pending":
                continue
            
            # 检查依赖
            deps_satisfied = all(
                self._get_step_by_id(workflow_id, dep_id)["status"] == "completed"
                for dep_id in step["dependencies"]
            )
            
            if deps_satisfied:
                self._execute_step(workflow_id, step["step_id"])
    
    def _get_step_by_id(self, workflow_id: str, step_id: str) -> Optional[Dict]:
        """获取步骤"""
        workflow = self._active_workflows.get(workflow_id)
        if not workflow:
            return None
        
        for step in workflow["steps"]:
            if step["step_id"] == step_id:
                return step
        return None
    
    def _execute_step(self, workflow_id: str, step_id: str):
        """执行步骤"""
        step = self._get_step_by_id(workflow_id, step_id)
        if not step:
            return
        
        step["status"] = "running"
        
        if step["type"] == "task":
            # 创建任务
            task = self.create_task(
                task_type=step["task_type"],
                description=step["name"],
                parameters=step["parameters"]
            )
            
            # 分配任务
            if step["agent"]:
                self.assign_task(task.task_id, step["agent"])
            
            # 注册回调
            self.on_task_complete(task.task_id, 
                                 lambda t: self._on_step_complete(workflow_id, step_id, t))
        
        elif step["type"] == "negotiation":
            # 协商步骤
            proposal = self.negotiation_manager.create_proposal(
                proposer="orchestrator",
                proposal_type=step.get("proposal_type", "generic"),
                content=step["parameters"]
            )
            step["proposal_id"] = proposal.proposal_id
        
        elif step["type"] == "vote":
            # 投票步骤
            vote = self.voting_manager.create_vote(
                topic=step["parameters"].get("topic", "Vote"),
                vote_type=VoteType(step["parameters"].get("vote_type", "majority")),
                options=step["parameters"].get("options", []),
                eligible_voters=step["parameters"].get("voters", [])
            )
            step["vote_id"] = vote.vote_id
    
    def _on_step_complete(self, workflow_id: str, step_id: str, task: Task):
        """步骤完成回调"""
        step = self._get_step_by_id(workflow_id, step_id)
        if not step:
            return
        
        step["status"] = "completed" if task.status == TaskStatus.COMPLETED else "failed"
        step["result"] = task.result
        
        workflow = self._active_workflows[workflow_id]
        workflow["results"][step_id] = task.result
        
        # 检查工作流是否完成
        all_completed = all(s["status"] == "completed" for s in workflow["steps"])
        if all_completed:
            workflow["status"] = "completed"
            workflow["completed_at"] = datetime.now().isoformat()
        else:
            # 继续执行就绪步骤
            self._execute_ready_steps(workflow_id)
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """获取工作流状态"""
        if workflow_id not in self._active_workflows:
            return None
        
        workflow = self._active_workflows[workflow_id]
        return {
            "workflow_id": workflow_id,
            "status": workflow["status"],
            "progress": f"{sum(1 for s in workflow['steps'] if s['status'] == 'completed')}/{len(workflow['steps'])}",
            "current_step": workflow.get("current_step"),
            "started_at": workflow.get("started_at"),
            "completed_at": workflow.get("completed_at")
        }
    
    def execute_conditional(self, condition: Callable[[], bool],
                           true_tasks: List[Task],
                           false_tasks: List[Task]) -> List[str]:
        """条件执行"""
        if condition():
            return self.execute_parallel(true_tasks)
        else:
            return self.execute_parallel(false_tasks)
    
    def execute_map_reduce(self, items: List[Any],
                          map_task_factory: Callable[[Any], Task],
                          reduce_agent: str,
                          reduce_task_type: str) -> str:
        """Map-Reduce模式执行"""
        # Map阶段
        map_tasks = [map_task_factory(item) for item in items]
        map_task_ids = self.execute_parallel(map_tasks)
        
        # 创建Reduce任务，依赖于所有Map任务
        reduce_task = Task(
            task_type=reduce_task_type,
            description="Reduce results",
            parameters={"map_task_ids": map_task_ids},
            dependencies=map_task_ids
        )
        
        self._tasks[reduce_task.task_id] = reduce_task
        self.assign_task(reduce_task.task_id, reduce_agent)
        
        return reduce_task.task_id


def create_advanced_collaboration_system() -> tuple:
    """创建高级协作系统"""
    from agent_protocol import AgentRegistry, MessageBus
    
    registry = AgentRegistry()
    message_bus = MessageBus()
    orchestrator = AdvancedOrchestrator(registry, message_bus)
    
    # 监听结果消息
    def result_handler(msg: AgentMessage):
        if msg.msg_type == MessageType.RESULT:
            orchestrator.handle_result(msg)
    
    message_bus.subscribe("orchestrator", result_handler)
    
    return registry, message_bus, orchestrator


if __name__ == "__main__":
    # 测试高级协作功能
    registry, bus, orchestrator = create_advanced_collaboration_system()
    
    print("=== ACP扩展功能测试 ===\n")
    
    # 测试协商
    print("1. 测试协商功能")
    proposal = orchestrator.negotiation_manager.create_proposal(
        proposer="agent-a",
        proposal_type="resource_share",
        content={"resource": "gpu", "share_ratio": 0.5},
        timeout_seconds=60
    )
    print(f"   创建提案: {proposal.proposal_id}")
    
    orchestrator.negotiation_manager.respond_to_proposal(
        proposal_id=proposal.proposal_id,
        responder="agent-b",
        accepted=True
    )
    print(f"   Agent-B 接受提案")
    
    # 测试投票
    print("\n2. 测试投票功能")
    vote = orchestrator.voting_manager.create_vote(
        topic="选择项目方向",
        vote_type=VoteType.MAJORITY,
        options=["AI助手", "代码生成", "数据分析"],
        eligible_voters=["agent-a", "agent-b", "agent-c"],
        duration_seconds=60
    )
    print(f"   创建投票: {vote.vote_id}")
    
    orchestrator.voting_manager.cast_vote(vote.vote_id, "agent-a", "AI助手")
    orchestrator.voting_manager.cast_vote(vote.vote_id, "agent-b", "AI助手")
    print(f"   投票结果: {vote.result}")
    
    # 测试委托
    print("\n3. 测试委托功能")
    delegation = orchestrator.delegation_manager.create_delegation(
        delegator="agent-a",
        delegatee="agent-b",
        scope=["finance", "stock"],
        permissions=["execute", "query"],
        duration_seconds=3600
    )
    print(f"   创建委托: {delegation.delegation_id}")
    
    delegatee = orchestrator.delegation_manager.check_permission(
        "agent-a", "execute", "finance"
    )
    print(f"   权限检查: agent-a 可以委托给 {delegatee}")
    
    print("\n=== 所有测试完成 ===")
