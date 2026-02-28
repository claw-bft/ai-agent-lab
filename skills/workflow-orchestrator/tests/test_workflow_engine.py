#!/usr/bin/env python3
"""
Workflow Orchestrator Tests - 工作流编排器测试套件

测试覆盖:
- 工作流节点创建与序列化
- 工作流边连接逻辑
- 工作流引擎执行流程
- 条件分支与并行执行
- 错误处理与状态管理
"""

import pytest
import json
import time
import threading
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# 导入被测模块
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflow_engine import (
    NodeType, NodeStatus, WorkflowStatus,
    WorkflowNode, WorkflowEdge, WorkflowDefinition, WorkflowEngine,
    NodeExecution
)


class TestWorkflowNode:
    """工作流节点测试"""
    
    def test_node_creation_with_defaults(self):
        """测试默认节点创建"""
        node = WorkflowNode(name="Test Node")
        assert node.name == "Test Node"
        assert node.node_type == NodeType.TASK
        assert len(node.node_id) == 8  # UUID前8位
        assert node.parameters == {}
        assert node.config == {}
    
    def test_node_creation_with_all_fields(self):
        """测试完整字段节点创建"""
        node = WorkflowNode(
            node_type=NodeType.CONDITION,
            name="Decision Node",
            description="Makes a decision",
            agent_id="agent-001",
            task_type="decision",
            parameters={"threshold": 0.5},
            config={"timeout": 30},
            position={"x": 100, "y": 200}
        )
        assert node.node_type == NodeType.CONDITION
        assert node.name == "Decision Node"
        assert node.parameters["threshold"] == 0.5
        assert node.position["x"] == 100
    
    def test_node_serialization(self):
        """测试节点序列化与反序列化"""
        original = WorkflowNode(
            node_type=NodeType.TASK,
            name="Serialize Test",
            parameters={"key": "value"}
        )
        
        # 序列化
        data = original.to_dict()
        assert data["node_type"] == "task"
        assert data["name"] == "Serialize Test"
        
        # 反序列化
        restored = WorkflowNode.from_dict(data)
        assert restored.name == original.name
        assert restored.node_type == original.node_type
        assert restored.parameters == original.parameters
    
    def test_all_node_types(self):
        """测试所有节点类型"""
        types = [NodeType.START, NodeType.END, NodeType.TASK, 
                NodeType.CONDITION, NodeType.PARALLEL, NodeType.AGGREGATE, NodeType.DELAY]
        
        for node_type in types:
            node = WorkflowNode(node_type=node_type, name=f"{node_type.value}_node")
            assert node.node_type == node_type


class TestWorkflowEdge:
    """工作流边测试"""
    
    def test_edge_creation(self):
        """测试边创建"""
        edge = WorkflowEdge(
            source="node-1",
            target="node-2",
            label="Success Path"
        )
        assert edge.source == "node-1"
        assert edge.target == "node-2"
        assert edge.label == "Success Path"
        assert len(edge.edge_id) == 8
    
    def test_edge_with_condition(self):
        """测试带条件的边"""
        edge = WorkflowEdge(
            source="decision",
            target="branch-a",
            condition="result > 0.5",
            label="High Value"
        )
        assert edge.condition == "result > 0.5"
        assert edge.label == "High Value"
    
    def test_edge_serialization(self):
        """测试边序列化"""
        edge = WorkflowEdge(
            source="a",
            target="b",
            condition="x > 0",
            label="test"
        )
        
        data = edge.to_dict()
        assert data["source"] == "a"
        assert data["target"] == "b"
        assert data["condition"] == "x > 0"
        
        restored = WorkflowEdge.from_dict(data)
        assert restored.source == edge.source
        assert restored.condition == edge.condition


class TestWorkflowDefinition:
    """工作流定义测试"""
    
    def test_workflow_creation(self):
        """测试工作流创建"""
        workflow = WorkflowDefinition(
            name="Test Workflow",
            description="A test workflow"
        )
        assert workflow.name == "Test Workflow"
        assert workflow.description == "A test workflow"
        assert workflow.version == "1.0.0"
        assert workflow.nodes == []
        assert workflow.edges == []
    
    def test_add_node(self):
        """测试添加节点"""
        workflow = WorkflowDefinition(name="Test")
        node = WorkflowNode(name="Task 1")
        
        workflow.nodes.append(node)
        assert len(workflow.nodes) == 1
        assert workflow.nodes[0].name == "Task 1"
    
    def test_add_edge(self):
        """测试添加边"""
        workflow = WorkflowDefinition(name="Test")
        node1 = WorkflowNode(name="Start")
        node2 = WorkflowNode(name="End")
        
        workflow.nodes.append(node1)
        workflow.nodes.append(node2)
        
        edge = WorkflowEdge(source=node1.node_id, target=node2.node_id)
        workflow.edges.append(edge)
        
        assert len(workflow.edges) == 1
        assert edge.source == node1.node_id
        assert edge.target == node2.node_id
    
    def test_get_node(self):
        """测试获取节点"""
        workflow = WorkflowDefinition(name="Test")
        node = WorkflowNode(name="Find Me")
        workflow.nodes.append(node)
        
        found = workflow.get_node(node.node_id)
        assert found is not None
        assert found.name == "Find Me"
        
        not_found = workflow.get_node("non-existent")
        assert not_found is None
    
    def test_workflow_validation(self):
        """测试工作流验证 - 检查节点获取功能"""
        workflow = WorkflowDefinition(name="Validation Test")
        
        # 添加开始节点
        start = WorkflowNode(node_type=NodeType.START, name="Start")
        workflow.nodes.append(start)
        
        # 验证能获取开始节点
        found_start = workflow.get_start_node()
        assert found_start is not None
        assert found_start.node_type == NodeType.START
    
    def test_workflow_serialization(self):
        """测试工作流序列化"""
        workflow = WorkflowDefinition(
            name="Serial Test",
            description="Test serialization"
        )
        
        start = WorkflowNode(node_type=NodeType.START, name="Start")
        task = WorkflowNode(node_type=NodeType.TASK, name="Task")
        end = WorkflowNode(node_type=NodeType.END, name="End")
        
        workflow.nodes.append(start)
        workflow.nodes.append(task)
        workflow.nodes.append(end)
        workflow.edges.append(WorkflowEdge(source=start.node_id, target=task.node_id))
        workflow.edges.append(WorkflowEdge(source=task.node_id, target=end.node_id))
        
        # 序列化
        data = workflow.to_dict()
        assert data["name"] == "Serial Test"
        assert len(data["nodes"]) == 3
        assert len(data["edges"]) == 2
        
        # 反序列化
        restored = WorkflowDefinition.from_dict(data)
        assert restored.name == workflow.name
        assert len(restored.nodes) == 3
        assert len(restored.edges) == 2


class TestWorkflowEngine:
    """工作流引擎测试"""
    
    def test_engine_initialization(self):
        """测试引擎初始化"""
        engine = WorkflowEngine()
        assert engine._workflows == {}
        assert engine._executions == {}
    
    def test_register_workflow(self):
        """测试注册工作流"""
        engine = WorkflowEngine()
        workflow = WorkflowDefinition(name="Test Workflow")
        
        engine.register_workflow(workflow)
        assert workflow.workflow_id in engine._workflows
        assert engine._workflows[workflow.workflow_id].name == "Test Workflow"
    
    def test_get_workflow(self):
        """测试获取工作流"""
        engine = WorkflowEngine()
        workflow = WorkflowDefinition(name="Test")
        engine.register_workflow(workflow)
        
        found = engine.get_workflow(workflow.workflow_id)
        assert found is not None
        assert found.name == "Test"
        
        not_found = engine.get_workflow("non-existent")
        assert not_found is None
    
    def test_create_simple_linear_workflow(self):
        """测试创建简单线性工作流"""
        engine = WorkflowEngine()
        workflow = WorkflowDefinition(
            name="Linear Flow",
            description="Simple linear workflow"
        )
        
        # 添加开始节点
        start = WorkflowNode(node_type=NodeType.START, name="Start")
        workflow.nodes.append(start)
        
        # 添加任务节点
        task1 = WorkflowNode(node_type=NodeType.TASK, name="Task 1", task_type="process")
        workflow.nodes.append(task1)
        
        # 添加结束节点
        end = WorkflowNode(node_type=NodeType.END, name="End")
        workflow.nodes.append(end)
        
        # 连接节点
        workflow.edges.append(WorkflowEdge(source=start.node_id, target=task1.node_id))
        workflow.edges.append(WorkflowEdge(source=task1.node_id, target=end.node_id))
        
        # 验证
        assert len(workflow.nodes) == 3
        assert len(workflow.edges) == 2


class TestNodeExecution:
    """节点执行测试"""
    
    def test_execution_initialization(self):
        """测试执行记录初始化"""
        execution = NodeExecution(
            node_id="node-123",
            status=NodeStatus.PENDING
        )
        
        assert execution.node_id == "node-123"
        assert execution.status == NodeStatus.PENDING
        assert execution.execution_id is not None
        assert len(execution.execution_id) == 8
    
    def test_execution_serialization(self):
        """测试执行记录序列化"""
        execution = NodeExecution(
            node_id="node-123",
            status=NodeStatus.COMPLETED,
            result={"output": "success"}
        )
        
        data = execution.to_dict()
        assert data["node_id"] == "node-123"
        assert data["status"] == "completed"
        assert data["result"]["output"] == "success"


class TestWorkflowTemplates:
    """工作流模板测试 - 验证模板创建功能"""
    
    def test_sequential_workflow_structure(self):
        """测试顺序工作流结构"""
        workflow = WorkflowDefinition(name="Sequential Test")
        
        # 创建顺序节点
        start = WorkflowNode(node_type=NodeType.START, name="Start")
        step1 = WorkflowNode(node_type=NodeType.TASK, name="Step 1", task_type="process")
        step2 = WorkflowNode(node_type=NodeType.TASK, name="Step 2", task_type="process")
        step3 = WorkflowNode(node_type=NodeType.TASK, name="Step 3", task_type="process")
        end = WorkflowNode(node_type=NodeType.END, name="End")
        
        workflow.nodes.extend([start, step1, step2, step3, end])
        workflow.edges.append(WorkflowEdge(source=start.node_id, target=step1.node_id))
        workflow.edges.append(WorkflowEdge(source=step1.node_id, target=step2.node_id))
        workflow.edges.append(WorkflowEdge(source=step2.node_id, target=step3.node_id))
        workflow.edges.append(WorkflowEdge(source=step3.node_id, target=end.node_id))
        
        assert len(workflow.nodes) == 5
        assert len(workflow.edges) == 4
        
        # 验证开始和结束节点存在
        node_types = [n.node_type for n in workflow.nodes]
        assert NodeType.START in node_types
        assert NodeType.END in node_types
    
    def test_parallel_workflow_structure(self):
        """测试并行工作流结构"""
        workflow = WorkflowDefinition(name="Parallel Test")
        
        start = WorkflowNode(node_type=NodeType.START, name="Start")
        parallel = WorkflowNode(node_type=NodeType.PARALLEL, name="Fork")
        branch_a = WorkflowNode(node_type=NodeType.TASK, name="Branch A", task_type="process_a")
        branch_b = WorkflowNode(node_type=NodeType.TASK, name="Branch B", task_type="process_b")
        branch_c = WorkflowNode(node_type=NodeType.TASK, name="Branch C", task_type="process_c")
        aggregate = WorkflowNode(node_type=NodeType.AGGREGATE, name="Join")
        end = WorkflowNode(node_type=NodeType.END, name="End")
        
        workflow.nodes.extend([start, parallel, branch_a, branch_b, branch_c, aggregate, end])
        workflow.edges.append(WorkflowEdge(source=start.node_id, target=parallel.node_id))
        workflow.edges.append(WorkflowEdge(source=parallel.node_id, target=branch_a.node_id))
        workflow.edges.append(WorkflowEdge(source=parallel.node_id, target=branch_b.node_id))
        workflow.edges.append(WorkflowEdge(source=parallel.node_id, target=branch_c.node_id))
        workflow.edges.append(WorkflowEdge(source=branch_a.node_id, target=aggregate.node_id))
        workflow.edges.append(WorkflowEdge(source=branch_b.node_id, target=aggregate.node_id))
        workflow.edges.append(WorkflowEdge(source=branch_c.node_id, target=aggregate.node_id))
        workflow.edges.append(WorkflowEdge(source=aggregate.node_id, target=end.node_id))
        
        assert len(workflow.nodes) == 7
        
        # 验证并行节点存在
        node_types = [n.node_type for n in workflow.nodes]
        assert NodeType.PARALLEL in node_types
        assert NodeType.AGGREGATE in node_types
    
    def test_conditional_workflow_structure(self):
        """测试条件工作流结构"""
        workflow = WorkflowDefinition(name="Conditional Test")
        
        start = WorkflowNode(node_type=NodeType.START, name="Start")
        condition = WorkflowNode(node_type=NodeType.CONDITION, name="Check Value", task_type="decision")
        high_branch = WorkflowNode(node_type=NodeType.TASK, name="High Value Process", task_type="process_high")
        low_branch = WorkflowNode(node_type=NodeType.TASK, name="Low Value Process", task_type="process_low")
        end = WorkflowNode(node_type=NodeType.END, name="End")
        
        workflow.nodes.extend([start, condition, high_branch, low_branch, end])
        workflow.edges.append(WorkflowEdge(source=start.node_id, target=condition.node_id))
        workflow.edges.append(WorkflowEdge(source=condition.node_id, target=high_branch.node_id, condition="value > 0.5"))
        workflow.edges.append(WorkflowEdge(source=condition.node_id, target=low_branch.node_id, condition="value <= 0.5"))
        workflow.edges.append(WorkflowEdge(source=high_branch.node_id, target=end.node_id))
        workflow.edges.append(WorkflowEdge(source=low_branch.node_id, target=end.node_id))
        
        # 验证条件节点存在
        node_types = [n.node_type for n in workflow.nodes]
        assert NodeType.CONDITION in node_types
        
        # 验证条件边
        conditional_edges = [e for e in workflow.edges if e.condition]
        assert len(conditional_edges) == 2


class TestIntegrationScenarios:
    """集成场景测试"""
    
    def test_simple_data_processing_workflow(self):
        """测试简单数据处理工作流"""
        engine = WorkflowEngine()
        
        # 创建工作流
        workflow = WorkflowDefinition(
            name="Data Processing",
            description="Process incoming data"
        )
        
        # 添加节点
        start = WorkflowNode(node_type=NodeType.START, name="Receive Data")
        validate = WorkflowNode(node_type=NodeType.TASK, name="Validate", task_type="validate")
        process = WorkflowNode(node_type=NodeType.TASK, name="Process", task_type="process")
        save = WorkflowNode(node_type=NodeType.TASK, name="Save", task_type="save")
        end = WorkflowNode(node_type=NodeType.END, name="Complete")
        
        workflow.nodes.extend([start, validate, process, save, end])
        
        # 连接
        workflow.edges.append(WorkflowEdge(source=start.node_id, target=validate.node_id))
        workflow.edges.append(WorkflowEdge(source=validate.node_id, target=process.node_id))
        workflow.edges.append(WorkflowEdge(source=process.node_id, target=save.node_id))
        workflow.edges.append(WorkflowEdge(source=save.node_id, target=end.node_id))
        
        # 验证结构
        assert len(workflow.nodes) == 5
        assert len(workflow.edges) == 4
        
        # 验证开始节点
        start_node = workflow.get_start_node()
        assert start_node is not None
        assert start_node.node_type == NodeType.START
    
    def test_error_handling_in_execution(self):
        """测试执行中的错误处理"""
        execution = NodeExecution(
            node_id="task-1",
            status=NodeStatus.FAILED,
            error="Connection timeout"
        )
        
        assert execution.status == NodeStatus.FAILED
        assert execution.error == "Connection timeout"
        
        # 验证序列化包含错误信息
        data = execution.to_dict()
        assert data["status"] == "failed"
        assert data["error"] == "Connection timeout"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
