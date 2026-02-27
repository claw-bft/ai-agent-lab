#!/usr/bin/env python3
"""
Workflow Orchestrator - 智能工作流编排系统
可视化工作流编排器的核心引擎
"""

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from collections import defaultdict
import threading


class NodeType(Enum):
    """工作流节点类型"""
    START = "start"
    END = "end"
    TASK = "task"
    CONDITION = "condition"
    PARALLEL = "parallel"
    AGGREGATE = "aggregate"
    DELAY = "delay"


class NodeStatus(Enum):
    """节点状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStatus(Enum):
    """工作流状态"""
    DRAFT = "draft"
    ACTIVE = "active"
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class WorkflowNode:
    """工作流节点"""
    node_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    node_type: NodeType = NodeType.TASK
    name: str = ""
    description: str = ""
    agent_id: str = ""  # 执行任务的Agent
    task_type: str = ""  # 任务类型
    parameters: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    position: Dict[str, float] = field(default_factory=lambda: {"x": 0, "y": 0})
    
    def to_dict(self) -> Dict:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "name": self.name,
            "description": self.description,
            "agent_id": self.agent_id,
            "task_type": self.task_type,
            "parameters": self.parameters,
            "config": self.config,
            "position": self.position
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'WorkflowNode':
        return cls(
            node_id=data.get("node_id", str(uuid.uuid4())[:8]),
            node_type=NodeType(data.get("node_type", "task")),
            name=data.get("name", ""),
            description=data.get("description", ""),
            agent_id=data.get("agent_id", ""),
            task_type=data.get("task_type", ""),
            parameters=data.get("parameters", {}),
            config=data.get("config", {}),
            position=data.get("position", {"x": 0, "y": 0})
        )


@dataclass
class WorkflowEdge:
    """工作流边（连接）"""
    edge_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    source: str = ""  # 源节点ID
    target: str = ""  # 目标节点ID
    condition: Optional[str] = None  # 条件表达式
    label: str = ""  # 边标签
    
    def to_dict(self) -> Dict:
        return {
            "edge_id": self.edge_id,
            "source": self.source,
            "target": self.target,
            "condition": self.condition,
            "label": self.label
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'WorkflowEdge':
        return cls(
            edge_id=data.get("edge_id", str(uuid.uuid4())[:8]),
            source=data.get("source", ""),
            target=data.get("target", ""),
            condition=data.get("condition"),
            label=data.get("label", "")
        )


@dataclass
class NodeExecution:
    """节点执行记录"""
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    node_id: str = ""
    status: NodeStatus = NodeStatus.PENDING
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict] = None
    error: Optional[str] = None
    logs: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "execution_id": self.execution_id,
            "node_id": self.node_id,
            "status": self.status.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "result": self.result,
            "error": self.error,
            "logs": self.logs
        }


@dataclass
class WorkflowDefinition:
    """工作流定义"""
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    nodes: List[WorkflowNode] = field(default_factory=list)
    edges: List[WorkflowEdge] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "variables": self.variables,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'WorkflowDefinition':
        return cls(
            workflow_id=data.get("workflow_id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            nodes=[WorkflowNode.from_dict(n) for n in data.get("nodes", [])],
            edges=[WorkflowEdge.from_dict(e) for e in data.get("edges", [])],
            variables=data.get("variables", {}),
            tags=data.get("tags", [])
        )
    
    def get_node(self, node_id: str) -> Optional[WorkflowNode]:
        """获取节点"""
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None
    
    def get_start_node(self) -> Optional[WorkflowNode]:
        """获取开始节点"""
        for node in self.nodes:
            if node.node_type == NodeType.START:
                return node
        return None
    
    def get_next_nodes(self, node_id: str) -> List[WorkflowNode]:
        """获取下一个节点"""
        next_nodes = []
        for edge in self.edges:
            if edge.source == node_id:
                node = self.get_node(edge.target)
                if node:
                    next_nodes.append(node)
        return next_nodes
    
    def get_prev_nodes(self, node_id: str) -> List[WorkflowNode]:
        """获取上一个节点"""
        prev_nodes = []
        for edge in self.edges:
            if edge.target == node_id:
                node = self.get_node(edge.source)
                if node:
                    prev_nodes.append(node)
        return prev_nodes


@dataclass
class WorkflowExecution:
    """工作流执行实例"""
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str = ""
    status: WorkflowStatus = WorkflowStatus.PENDING
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    node_executions: Dict[str, NodeExecution] = field(default_factory=dict)
    current_nodes: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "status": self.status.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "node_executions": {k: v.to_dict() for k, v in self.node_executions.items()},
            "current_nodes": self.current_nodes,
            "context": self.context
        }


class WorkflowEngine:
    """工作流引擎 - 执行工作流定义"""
    
    def __init__(self):
        self._workflows: Dict[str, WorkflowDefinition] = {}
        self._executions: Dict[str, WorkflowExecution] = {}
        self._lock = threading.Lock()
        self._task_handlers: Dict[str, Callable] = {}
    
    def register_workflow(self, workflow: WorkflowDefinition) -> str:
        """注册工作流"""
        with self._lock:
            self._workflows[workflow.workflow_id] = workflow
            return workflow.workflow_id
    
    def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """获取工作流定义"""
        with self._lock:
            return self._workflows.get(workflow_id)
    
    def list_workflows(self) -> List[WorkflowDefinition]:
        """列出所有工作流"""
        with self._lock:
            return list(self._workflows.values())
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """删除工作流"""
        with self._lock:
            if workflow_id in self._workflows:
                del self._workflows[workflow_id]
                return True
            return False
    
    def register_task_handler(self, task_type: str, handler: Callable):
        """注册任务处理器"""
        self._task_handlers[task_type] = handler
    
    def execute_workflow(self, workflow_id: str, input_data: Dict[str, Any] = None) -> str:
        """执行工作流"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            input_data=input_data or {},
            status=WorkflowStatus.RUNNING,
            started_at=datetime.now().isoformat(),
            context={"input": input_data or {}}
        )
        
        with self._lock:
            self._executions[execution.execution_id] = execution
        
        # 找到开始节点
        start_node = workflow.get_start_node()
        if start_node:
            execution.current_nodes = [start_node.node_id]
            self._execute_nodes(execution, workflow)
        
        return execution.execution_id
    
    def _execute_nodes(self, execution: WorkflowExecution, workflow: WorkflowDefinition):
        """执行当前节点"""
        for node_id in execution.current_nodes[:]:
            node = workflow.get_node(node_id)
            if not node:
                continue
            
            # 创建节点执行记录
            node_exec = NodeExecution(
                node_id=node_id,
                status=NodeStatus.RUNNING,
                started_at=datetime.now().isoformat()
            )
            execution.node_executions[node_id] = node_exec
            
            try:
                # 执行节点
                result = self._execute_node(node, execution)
                
                node_exec.status = NodeStatus.COMPLETED
                node_exec.completed_at = datetime.now().isoformat()
                node_exec.result = result
                
                # 更新上下文
                execution.context[f"node_{node_id}_result"] = result
                
                # 获取下一个节点
                next_nodes = workflow.get_next_nodes(node_id)
                execution.current_nodes.remove(node_id)
                
                for next_node in next_nodes:
                    if next_node.node_id not in execution.current_nodes:
                        execution.current_nodes.append(next_node.node_id)
                
            except Exception as e:
                node_exec.status = NodeStatus.FAILED
                node_exec.error = str(e)
                execution.status = WorkflowStatus.FAILED
        
        # 检查是否完成
        if not execution.current_nodes:
            execution.status = WorkflowStatus.COMPLETED
            execution.completed_at = datetime.now().isoformat()
    
    def _execute_node(self, node: WorkflowNode, execution: WorkflowExecution) -> Dict:
        """执行单个节点"""
        if node.node_type == NodeType.START:
            return {"status": "started"}
        
        elif node.node_type == NodeType.END:
            return {"status": "ended", "output": execution.context}
        
        elif node.node_type == NodeType.TASK:
            handler = self._task_handlers.get(node.task_type)
            if handler:
                # 替换参数中的变量
                params = self._resolve_parameters(node.parameters, execution.context)
                return handler(params)
            else:
                # 模拟执行
                return {
                    "task_type": node.task_type,
                    "agent_id": node.agent_id,
                    "parameters": node.parameters,
                    "status": "completed"
                }
        
        elif node.node_type == NodeType.DELAY:
            delay_ms = node.config.get("delay_ms", 1000)
            import time
            time.sleep(delay_ms / 1000)
            return {"status": "delayed", "delay_ms": delay_ms}
        
        return {"status": "unknown_node_type"}
    
    def _resolve_parameters(self, params: Dict, context: Dict) -> Dict:
        """解析参数中的变量引用"""
        resolved = {}
        for key, value in params.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                var_path = value[2:-1]
                resolved[key] = self._get_context_value(context, var_path)
            else:
                resolved[key] = value
        return resolved
    
    def _get_context_value(self, context: Dict, path: str) -> Any:
        """从上下文中获取值"""
        parts = path.split(".")
        value = context
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None
        return value
    
    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """获取执行状态"""
        with self._lock:
            return self._executions.get(execution_id)
    
    def list_executions(self, workflow_id: str = None) -> List[WorkflowExecution]:
        """列出执行记录"""
        with self._lock:
            executions = list(self._executions.values())
            if workflow_id:
                executions = [e for e in executions if e.workflow_id == workflow_id]
            return executions


class WorkflowTemplateLibrary:
    """工作流模板库"""
    
    TEMPLATES = {
        "stock-research": {
            "name": "股票研究",
            "description": "获取股票行情 -> 研究公司背景 -> 深度分析",
            "nodes": [
                {"node_type": "start", "name": "开始", "position": {"x": 100, "y": 100}},
                {"node_type": "task", "name": "获取行情", "agent_id": "finance-pro", "task_type": "finance.quote", "position": {"x": 300, "y": 100}},
                {"node_type": "task", "name": "公司研究", "agent_id": "research-pro", "task_type": "research.search", "position": {"x": 500, "y": 100}},
                {"node_type": "task", "name": "深度分析", "agent_id": "research-pro", "task_type": "research.deep", "position": {"x": 700, "y": 100}},
                {"node_type": "end", "name": "完成", "position": {"x": 900, "y": 100}}
            ],
            "edges": [
                {"source": "node_0", "target": "node_1"},
                {"source": "node_1", "target": "node_2"},
                {"source": "node_2", "target": "node_3"},
                {"source": "node_3", "target": "node_4"}
            ]
        },
        "product-dev": {
            "name": "产品开发",
            "description": "市场调研 -> 竞品分析 -> 生成PRD -> 原型代码",
            "nodes": [
                {"node_type": "start", "name": "开始", "position": {"x": 100, "y": 100}},
                {"node_type": "task", "name": "市场调研", "agent_id": "research-pro", "task_type": "research.search", "position": {"x": 300, "y": 100}},
                {"node_type": "task", "name": "竞品分析", "agent_id": "product-pro", "task_type": "product.competitor", "position": {"x": 500, "y": 100}},
                {"node_type": "task", "name": "生成PRD", "agent_id": "product-pro", "task_type": "product.prd", "position": {"x": 700, "y": 100}},
                {"node_type": "task", "name": "原型代码", "agent_id": "coding-pro", "task_type": "coding.generate", "position": {"x": 900, "y": 100}},
                {"node_type": "end", "name": "完成", "position": {"x": 1100, "y": 100}}
            ],
            "edges": [
                {"source": "node_0", "target": "node_1"},
                {"source": "node_1", "target": "node_2"},
                {"source": "node_2", "target": "node_3"},
                {"source": "node_3", "target": "node_4"},
                {"source": "node_4", "target": "node_5"}
            ]
        },
        "content-marketing": {
            "name": "内容营销",
            "description": "研究话题 -> 生成内容 -> 优化SEO -> 发布",
            "nodes": [
                {"node_type": "start", "name": "开始", "position": {"x": 100, "y": 100}},
                {"node_type": "task", "name": "话题研究", "agent_id": "research-pro", "task_type": "research.search", "position": {"x": 300, "y": 100}},
                {"node_type": "task", "name": "深度研究", "agent_id": "research-pro", "task_type": "research.deep", "position": {"x": 500, "y": 100}},
                {"node_type": "task", "name": "生成报告", "agent_id": "research-pro", "task_type": "research.report", "position": {"x": 700, "y": 100}},
                {"node_type": "end", "name": "完成", "position": {"x": 900, "y": 100}}
            ],
            "edges": [
                {"source": "node_0", "target": "node_1"},
                {"source": "node_1", "target": "node_2"},
                {"source": "node_2", "target": "node_3"},
                {"source": "node_3", "target": "node_4"}
            ]
        },
        "data-analysis": {
            "name": "数据分析",
            "description": "数据采集 -> 清洗处理 -> 分析建模 -> 可视化报告",
            "nodes": [
                {"node_type": "start", "name": "开始", "position": {"x": 100, "y": 200}},
                {"node_type": "task", "name": "数据采集", "agent_id": "research-pro", "task_type": "research.search", "position": {"x": 300, "y": 200}},
                {"node_type": "task", "name": "数据清洗", "agent_id": "coding-pro", "task_type": "coding.generate", "position": {"x": 500, "y": 200}},
                {"node_type": "task", "name": "分析建模", "agent_id": "research-pro", "task_type": "research.deep", "position": {"x": 700, "y": 200}},
                {"node_type": "task", "name": "可视化报告", "agent_id": "coding-pro", "task_type": "coding.generate", "position": {"x": 900, "y": 200}},
                {"node_type": "end", "name": "完成", "position": {"x": 1100, "y": 200}}
            ],
            "edges": [
                {"source": "node_0", "target": "node_1"},
                {"source": "node_1", "target": "node_2"},
                {"source": "node_2", "target": "node_3"},
                {"source": "node_3", "target": "node_4"},
                {"source": "node_4", "target": "node_5"}
            ]
        },
        "customer-service": {
            "name": "客户服务",
            "description": "工单分类 -> 智能回复 -> 满意度分析 -> 知识库更新",
            "nodes": [
                {"node_type": "start", "name": "开始", "position": {"x": 100, "y": 200}},
                {"node_type": "task", "name": "工单分类", "agent_id": "research-pro", "task_type": "research.search", "position": {"x": 300, "y": 200}},
                {"node_type": "condition", "name": "是否技术问题", "position": {"x": 500, "y": 200}},
                {"node_type": "task", "name": "技术回复", "agent_id": "coding-pro", "task_type": "coding.generate", "position": {"x": 700, "y": 100}},
                {"node_type": "task", "name": "一般回复", "agent_id": "research-pro", "task_type": "research.report", "position": {"x": 700, "y": 300}},
                {"node_type": "aggregate", "name": "合并回复", "position": {"x": 900, "y": 200}},
                {"node_type": "task", "name": "满意度分析", "agent_id": "research-pro", "task_type": "research.deep", "position": {"x": 1100, "y": 200}},
                {"node_type": "task", "name": "更新知识库", "agent_id": "product-pro", "task_type": "product.prd", "position": {"x": 1300, "y": 200}},
                {"node_type": "end", "name": "完成", "position": {"x": 1500, "y": 200}}
            ],
            "edges": [
                {"source": "node_0", "target": "node_1"},
                {"source": "node_1", "target": "node_2"},
                {"source": "node_2", "target": "node_3", "label": "是"},
                {"source": "node_2", "target": "node_4", "label": "否"},
                {"source": "node_3", "target": "node_5"},
                {"source": "node_4", "target": "node_5"},
                {"source": "node_5", "target": "node_6"},
                {"source": "node_6", "target": "node_7"},
                {"source": "node_7", "target": "node_8"}
            ]
        },
        "devops-monitoring": {
            "name": "运维监控",
            "description": "指标采集 -> 异常检测 -> 告警通知 -> 自动修复 -> 报告生成",
            "nodes": [
                {"node_type": "start", "name": "开始", "position": {"x": 100, "y": 200}},
                {"node_type": "task", "name": "指标采集", "agent_id": "research-pro", "task_type": "research.search", "position": {"x": 300, "y": 200}},
                {"node_type": "condition", "name": "异常检测", "position": {"x": 500, "y": 200}},
                {"node_type": "task", "name": "告警通知", "agent_id": "research-pro", "task_type": "research.report", "position": {"x": 700, "y": 100}},
                {"node_type": "task", "name": "自动修复", "agent_id": "coding-pro", "task_type": "coding.generate", "position": {"x": 700, "y": 300}},
                {"node_type": "aggregate", "name": "合并结果", "position": {"x": 900, "y": 200}},
                {"node_type": "delay", "name": "等待验证", "position": {"x": 1100, "y": 200}},
                {"node_type": "task", "name": "生成报告", "agent_id": "research-pro", "task_type": "research.report", "position": {"x": 1300, "y": 200}},
                {"node_type": "end", "name": "完成", "position": {"x": 1500, "y": 200}}
            ],
            "edges": [
                {"source": "node_0", "target": "node_1"},
                {"source": "node_1", "target": "node_2"},
                {"source": "node_2", "target": "node_3", "label": "异常"},
                {"source": "node_2", "target": "node_7", "label": "正常"},
                {"source": "node_3", "target": "node_5"},
                {"source": "node_4", "target": "node_5"},
                {"source": "node_5", "target": "node_6"},
                {"source": "node_6", "target": "node_7"},
                {"source": "node_7", "target": "node_8"}
            ]
        }
    }
    
    @classmethod
    def get_template(cls, template_id: str) -> Optional[Dict]:
        """获取模板"""
        return cls.TEMPLATES.get(template_id)
    
    @classmethod
    def list_templates(cls) -> List[Dict]:
        """列出所有模板"""
        return [
            {"id": k, "name": v["name"], "description": v["description"]}
            for k, v in cls.TEMPLATES.items()
        ]
    
    @classmethod
    def create_workflow_from_template(cls, template_id: str, name: str = None) -> WorkflowDefinition:
        """从模板创建工作流"""
        template = cls.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        workflow = WorkflowDefinition(
            name=name or template["name"],
            description=template["description"],
            tags=["template", template_id]
        )
        
        # 创建节点
        node_map = {}  # 旧ID -> 新ID
        for i, node_data in enumerate(template["nodes"]):
            node = WorkflowNode(
                node_type=NodeType(node_data["node_type"]),
                name=node_data["name"],
                agent_id=node_data.get("agent_id", ""),
                task_type=node_data.get("task_type", ""),
                position=node_data.get("position", {"x": 0, "y": 0})
            )
            workflow.nodes.append(node)
            node_map[f"node_{i}"] = node.node_id
        
        # 创建边
        for edge_data in template["edges"]:
            edge = WorkflowEdge(
                source=node_map.get(edge_data["source"], ""),
                target=node_map.get(edge_data["target"], ""),
                label=edge_data.get("label", "")
            )
            workflow.edges.append(edge)
        
        return workflow


def create_stock_research_workflow(symbol: str) -> WorkflowDefinition:
    """创建股票研究工作流"""
    workflow = WorkflowDefinition(
        name=f"股票研究 - {symbol}",
        description=f"对 {symbol} 进行全面的股票研究分析",
        tags=["stock", "research", "finance"]
    )
    
    # 开始节点
    start = WorkflowNode(node_type=NodeType.START, name="开始", position={"x": 100, "y": 200})
    workflow.nodes.append(start)
    
    # 获取行情
    quote = WorkflowNode(
        node_type=NodeType.TASK,
        name="获取股票行情",
        agent_id="finance-pro",
        task_type="finance.quote",
        parameters={"symbol": symbol},
        position={"x": 300, "y": 200}
    )
    workflow.nodes.append(quote)
    
    # 公司研究
    research = WorkflowNode(
        node_type=NodeType.TASK,
        name="研究公司背景",
        agent_id="research-pro",
        task_type="research.search",
        parameters={"query": f"{symbol} 公司简介 主营业务"},
        position={"x": 550, "y": 200}
    )
    workflow.nodes.append(research)
    
    # 深度分析
    deep = WorkflowNode(
        node_type=NodeType.TASK,
        name="深度分析",
        agent_id="research-pro",
        task_type="research.deep",
        parameters={"topic": f"{symbol} 投资价值分析"},
        position={"x": 800, "y": 200}
    )
    workflow.nodes.append(deep)
    
    # 结束节点
    end = WorkflowNode(node_type=NodeType.END, name="完成", position={"x": 1000, "y": 200})
    workflow.nodes.append(end)
    
    # 连接边
    workflow.edges.append(WorkflowEdge(source=start.node_id, target=quote.node_id))
    workflow.edges.append(WorkflowEdge(source=quote.node_id, target=research.node_id))
    workflow.edges.append(WorkflowEdge(source=research.node_id, target=deep.node_id))
    workflow.edges.append(WorkflowEdge(source=deep.node_id, target=end.node_id))
    
    return workflow


def create_product_dev_workflow(product_name: str) -> WorkflowDefinition:
    """创建产品开发工作流"""
    workflow = WorkflowDefinition(
        name=f"产品开发 - {product_name}",
        description=f"从调研到原型的完整产品开发流程",
        tags=["product", "development"]
    )
    
    # 节点
    start = WorkflowNode(node_type=NodeType.START, name="开始", position={"x": 50, "y": 200})
    workflow.nodes.append(start)
    
    market = WorkflowNode(
        node_type=NodeType.TASK,
        name="市场调研",
        agent_id="research-pro",
        task_type="research.search",
        parameters={"query": f"{product_name} 市场规模 竞品分析"},
        position={"x": 250, "y": 200}
    )
    workflow.nodes.append(market)
    
    competitor = WorkflowNode(
        node_type=NodeType.TASK,
        name="竞品分析",
        agent_id="product-pro",
        task_type="product.competitor",
        parameters={"product": product_name},
        position={"x": 450, "y": 200}
    )
    workflow.nodes.append(competitor)
    
    prd = WorkflowNode(
        node_type=NodeType.TASK,
        name="生成PRD",
        agent_id="product-pro",
        task_type="product.prd",
        parameters={"feature": product_name},
        position={"x": 650, "y": 200}
    )
    workflow.nodes.append(prd)
    
    code = WorkflowNode(
        node_type=NodeType.TASK,
        name="生成原型代码",
        agent_id="coding-pro",
        task_type="coding.generate",
        parameters={"prompt": f"创建 {product_name} 的MVP原型", "language": "python"},
        position={"x": 850, "y": 200}
    )
    workflow.nodes.append(code)
    
    end = WorkflowNode(node_type=NodeType.END, name="完成", position={"x": 1050, "y": 200})
    workflow.nodes.append(end)
    
    # 边
    workflow.edges.append(WorkflowEdge(source=start.node_id, target=market.node_id))
    workflow.edges.append(WorkflowEdge(source=market.node_id, target=competitor.node_id))
    workflow.edges.append(WorkflowEdge(source=competitor.node_id, target=prd.node_id))
    workflow.edges.append(WorkflowEdge(source=prd.node_id, target=code.node_id))
    workflow.edges.append(WorkflowEdge(source=code.node_id, target=end.node_id))
    
    return workflow


# 全局引擎实例
_engine = None

def get_workflow_engine() -> WorkflowEngine:
    """获取全局工作流引擎"""
    global _engine
    if _engine is None:
        _engine = WorkflowEngine()
    return _engine


if __name__ == "__main__":
    print("=== Workflow Orchestrator Test ===")
    
    # 测试模板库
    print("\n1. Available Templates:")
    for t in WorkflowTemplateLibrary.list_templates():
        print(f"   - {t['id']}: {t['name']}")
    
    # 创建工作流
    print("\n2. Creating Stock Research Workflow:")
    workflow = create_stock_research_workflow("600519.SH")
    print(f"   Workflow ID: {workflow.workflow_id}")
    print(f"   Name: {workflow.name}")
    print(f"   Nodes: {len(workflow.nodes)}")
    print(f"   Edges: {len(workflow.edges)}")
    
    # 注册到引擎
    engine = get_workflow_engine()
    engine.register_workflow(workflow)
    
    # 执行工作流
    print("\n3. Executing Workflow:")
    exec_id = engine.execute_workflow(workflow.workflow_id, {"symbol": "600519.SH"})
    print(f"   Execution ID: {exec_id}")
    
    # 检查状态
    execution = engine.get_execution(exec_id)
    print(f"   Status: {execution.status.value}")
    print(f"   Node Executions: {len(execution.node_executions)}")
    
    print("\n=== Test Complete ===")
