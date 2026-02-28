# Agent Collaboration

多智能体协作协议 (ACP) 扩展实现

## 功能特性

- **协商管理**: 支持提案、接受、拒绝、反提案等协商模式
- **投票系统**: 支持多数决、全体一致、加权投票、排序投票
- **委托机制**: 支持权限委托和撤销
- **工作流编排**: 高级工作流模板和执行管理
- **消息总线**: 基于事件的 Agent 间通信

## 核心组件

### 1. 协商管理器 (NegotiationManager)

支持多 Agent 之间的资源协商和任务分配。

```python
from acp_extensions import NegotiationManager
from agent_protocol import MessageBus

bus = MessageBus()
manager = NegotiationManager(bus)

# 创建提案
proposal = manager.create_proposal(
    proposer="agent-a",
    proposal_type="resource_share",
    content={"resource": "gpu", "share_ratio": 0.5},
    timeout_seconds=60
)

# 响应提案
manager.respond_to_proposal(
    proposal_id=proposal.proposal_id,
    responder="agent-b",
    accepted=True
)
```

### 2. 投票管理器 (VotingManager)

支持多种投票机制：

- **MAJORITY**: 多数决
- **UNANIMOUS**: 全体一致
- **WEIGHTED**: 加权投票
- **RANKED**: 排序投票 (IRV)

```python
from acp_extensions import VotingManager, VoteType

manager = VotingManager(bus)

# 创建投票
vote = manager.create_vote(
    topic="选择方向",
    vote_type=VoteType.MAJORITY,
    options=["A", "B", "C"],
    eligible_voters=["agent-a", "agent-b", "agent-c"]
)

# 投票
manager.cast_vote(vote.vote_id, "agent-a", "A")
```

### 3. 委托管理器 (DelegationManager)

支持权限的临时委托：

```python
from acp_extensions import DelegationManager

manager = DelegationManager(bus)

# 创建委托
delegation = manager.create_delegation(
    delegator="agent-a",
    delegatee="agent-b",
    scope=["finance", "stock"],
    permissions=["execute", "query"],
    duration_seconds=3600
)

# 检查权限
result = manager.check_permission("agent-a", "execute", "finance")
```

### 4. 高级编排器 (AdvancedOrchestrator)

工作流定义和执行：

```python
from acp_extensions import create_advanced_collaboration_system

registry, bus, orchestrator = create_advanced_collaboration_system()

# 注册工作流模板
orchestrator.register_workflow_template(
    template_id="data-pipeline",
    name="数据处理管道",
    steps=[
        {"name": "收集数据", "agent": "agent-a", "task_type": "collect"},
        {"name": "处理数据", "agent": "agent-b", "task_type": "process"},
    ]
)

# 执行工作流
workflow_id = orchestrator.create_workflow("data-pipeline")
orchestrator.start_workflow(workflow_id)
```

## 安装

```bash
# 复制到项目目录
cp -r agent-collaboration /path/to/your/project/

# 安装依赖
pip install -r requirements.txt  # 如有
```

## 测试

```bash
cd agent-collaboration
python3 -m pytest tests/ -v
```

## 文件结构

```
agent-collaboration/
├── agent_protocol.py         # 基础协议实现
├── acp_extensions.py         # ACP 扩展功能
├── skill_adapters.py         # 技能适配器
├── agent-collab              # CLI 工具
├── SKILL.md                  # 技能文档
├── README.md                 # 本文件
└── tests/
    └── test_acp_extensions.py # 测试套件
```

## 协议规范

### 消息类型

- `PROPOSAL`: 协商提案
- `VOTE`: 投票消息
- `DELEGATION`: 委托消息
- `TASK`: 任务分配
- `RESULT`: 结果返回

### 协商状态

- `PROPOSING`: 提案中
- `ACCEPTED`: 已接受
- `REJECTED`: 已拒绝
- `COUNTERING`: 反提案
- `EXPIRED`: 已过期

## 许可证

MIT
