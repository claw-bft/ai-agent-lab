"""
Agent Collaboration Protocol (ACP) - Workflow编排
"""
import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Union
from enum import Enum

from .agent import Agent
from .message import TaskResponse, TaskStatus, Priority


class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowStep:
    """工作流步骤"""
    step_id: str
    task_type: str
    agent_name: Optional[str] = None  # 指定Agent名称，None表示任意
    parameters: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    timeout: float = 30.0
    
    # 运行时状态
    status: WorkflowStatus = WorkflowStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None


@dataclass
class Workflow:
    """工作流定义"""
    workflow_id: str
    name: str
    steps: Dict[str, WorkflowStep]
    status: WorkflowStatus = WorkflowStatus.PENDING
    results: Dict[str, Any] = field(default_factory=dict)
    errors: Dict[str, str] = field(default_factory=dict)


class WorkflowEngine:
    """工作流引擎"""
    
    def __init__(self):
        self._agents: Dict[str, Agent] = {}
        self._workflows: Dict[str, Workflow] = {}
    
    def register_agent(self, agent: Agent) -> None:
        """注册Agent到引擎"""
        self._agents[agent.name] = agent
    
    def create_workflow(self, name: str, steps: List[WorkflowStep]) -> Workflow:
        """创建工作流"""
        workflow_id = f"wf_{name}_{asyncio.get_event_loop().time()}"
        steps_dict = {step.step_id: step for step in steps}
        
        workflow = Workflow(
            workflow_id=workflow_id,
            name=name,
            steps=steps_dict
        )
        self._workflows[workflow_id] = workflow
        return workflow
    
    async def execute_workflow(
        self,
        workflow: Workflow,
        context: Optional[Dict[str, Any]] = None
    ) -> Workflow:
        """
        执行工作流
        
        Args:
            workflow: 工作流实例
            context: 上下文数据，可用于参数模板
        
        Returns:
            完成的工作流
        """
        workflow.status = WorkflowStatus.RUNNING
        context = context or {}
        
        # 拓扑排序确定执行顺序
        execution_order = self._topological_sort(workflow.steps)
        
        for step_id in execution_order:
            step = workflow.steps[step_id]
            
            # 检查依赖是否完成
            if not self._check_dependencies(workflow, step):
                step.status = WorkflowStatus.CANCELLED
                step.error = "Dependencies not satisfied"
                workflow.errors[step_id] = step.error
                continue
            
            # 执行步骤
            try:
                step.status = WorkflowStatus.RUNNING
                step.start_time = asyncio.get_event_loop().time()
                
                # 解析参数模板
                parameters = self._resolve_parameters(step.parameters, context, workflow.results)
                
                # 查找Agent
                agent = self._find_agent(step.agent_name, step.task_type)
                if not agent:
                    raise RuntimeError(f"No agent found for task type: {step.task_type}")
                
                # 发送任务
                response = await agent.send_task(
                    to_agent=agent.agent_id,  # 发送给自己
                    task_type=step.task_type,
                    parameters=parameters,
                    timeout=step.timeout
                )
                
                step.end_time = asyncio.get_event_loop().time()
                
                if response.status == TaskStatus.COMPLETED:
                    step.status = WorkflowStatus.COMPLETED
                    step.result = response.result
                    workflow.results[step_id] = response.result
                else:
                    step.status = WorkflowStatus.FAILED
                    step.error = response.error or "Unknown error"
                    workflow.errors[step_id] = step.error
                    
            except Exception as e:
                step.status = WorkflowStatus.FAILED
                step.error = str(e)
                workflow.errors[step_id] = str(e)
        
        # 确定工作流整体状态
        if workflow.errors:
            workflow.status = WorkflowStatus.FAILED
        else:
            workflow.status = WorkflowStatus.COMPLETED
        
        return workflow
    
    def _topological_sort(self, steps: Dict[str, WorkflowStep]) -> List[str]:
        """拓扑排序步骤"""
        # 构建依赖图
        in_degree = {step_id: 0 for step_id in steps}
        graph = {step_id: [] for step_id in steps}
        
        for step_id, step in steps.items():
            for dep_id in step.depends_on:
                if dep_id in steps:
                    graph[dep_id].append(step_id)
                    in_degree[step_id] += 1
        
        # Kahn算法
        queue = [step_id for step_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            step_id = queue.pop(0)
            result.append(step_id)
            
            for next_id in graph[step_id]:
                in_degree[next_id] -= 1
                if in_degree[next_id] == 0:
                    queue.append(next_id)
        
        return result
    
    def _check_dependencies(self, workflow: Workflow, step: WorkflowStep) -> bool:
        """检查依赖是否满足"""
        for dep_id in step.depends_on:
            if dep_id not in workflow.steps:
                return False
            dep_step = workflow.steps[dep_id]
            if dep_step.status != WorkflowStatus.COMPLETED:
                return False
        return True
    
    def _resolve_parameters(
        self,
        parameters: Dict[str, Any],
        context: Dict[str, Any],
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """解析参数模板"""
        resolved = {}
        
        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith("$"):
                # 模板变量
                var_path = value[1:].split(".")
                var_source = var_path[0]
                var_keys = var_path[1:]
                
                if var_source == "context":
                    data = context
                elif var_source == "results":
                    data = results
                else:
                    data = {}
                
                # 导航到嵌套值
                for k in var_keys:
                    if isinstance(data, dict) and k in data:
                        data = data[k]
                    else:
                        data = None
                        break
                
                resolved[key] = data
            else:
                resolved[key] = value
        
        return resolved
    
    def _find_agent(self, agent_name: Optional[str], task_type: str) -> Optional[Agent]:
        """查找能处理任务的Agent"""
        if agent_name and agent_name in self._agents:
            agent = self._agents[agent_name]
            if task_type in agent.capabilities:
                return agent
        
        # 查找任意能处理该任务的Agent
        for agent in self._agents.values():
            if task_type in agent.capabilities:
                return agent
        
        return None
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Workflow]:
        """获取工作流状态"""
        return self._workflows.get(workflow_id)


class ParallelWorkflowEngine(WorkflowEngine):
    """支持并行执行的工作流引擎"""
    
    async def execute_workflow(
        self,
        workflow: Workflow,
        context: Optional[Dict[str, Any]] = None,
        max_parallel: int = 3
    ) -> Workflow:
        """
        并行执行工作流
        
        Args:
            workflow: 工作流实例
            context: 上下文数据
            max_parallel: 最大并行度
        """
        workflow.status = WorkflowStatus.RUNNING
        context = context or {}
        
        semaphore = asyncio.Semaphore(max_parallel)
        completed_steps: Set[str] = set()
        
        async def execute_step(step: WorkflowStep) -> None:
            """执行单个步骤"""
            async with semaphore:
                try:
                    step.status = WorkflowStatus.RUNNING
                    step.start_time = asyncio.get_event_loop().time()
                    
                    parameters = self._resolve_parameters(step.parameters, context, workflow.results)
                    
                    agent = self._find_agent(step.agent_name, step.task_type)
                    if not agent:
                        raise RuntimeError(f"No agent found for task type: {step.task_type}")
                    
                    response = await agent.send_task(
                        to_agent=agent.agent_id,
                        task_type=step.task_type,
                        parameters=parameters,
                        timeout=step.timeout
                    )
                    
                    step.end_time = asyncio.get_event_loop().time()
                    
                    if response.status == TaskStatus.COMPLETED:
                        step.status = WorkflowStatus.COMPLETED
                        step.result = response.result
                        workflow.results[step.step_id] = response.result
                    else:
                        step.status = WorkflowStatus.FAILED
                        step.error = response.error or "Unknown error"
                        workflow.errors[step.step_id] = step.error
                        
                except Exception as e:
                    step.status = WorkflowStatus.FAILED
                    step.error = str(e)
                    workflow.errors[step.step_id] = str(e)
                
                completed_steps.add(step.step_id)
        
        # 按层级并行执行
        remaining_steps = set(workflow.steps.keys())
        
        while remaining_steps:
            # 找出可以执行的步骤（依赖已满足）
            ready_steps = [
                workflow.steps[step_id]
                for step_id in remaining_steps
                if all(dep in completed_steps for dep in workflow.steps[step_id].depends_on)
            ]
            
            if not ready_steps:
                # 存在循环依赖或无法执行的步骤
                for step_id in remaining_steps:
                    workflow.steps[step_id].status = WorkflowStatus.CANCELLED
                    workflow.errors[step_id] = "Cannot satisfy dependencies"
                break
            
            # 并行执行就绪的步骤
            await asyncio.gather(*[execute_step(step) for step in ready_steps])
            
            # 更新剩余步骤
            for step in ready_steps:
                remaining_steps.discard(step.step_id)
        
        # 确定工作流整体状态
        if workflow.errors:
            workflow.status = WorkflowStatus.FAILED
        else:
            workflow.status = WorkflowStatus.COMPLETED
        
        return workflow
