"""
ACP单元测试
"""
import asyncio
import pytest
from datetime import datetime

from acp import (
    Agent, MessageBusFactory, WorkflowEngine, WorkflowStep, WorkflowStatus,
    Message, MessageType, TaskRequest, TaskResponse, TaskStatus, Priority,
    create_task_request_message, create_task_response_message
)


class TestMessageTypes:
    """测试消息类型"""
    
    def test_task_request_creation(self):
        request = TaskRequest(
            task_id="test-123",
            task_type="test_task",
            parameters={"key": "value"},
            priority=Priority.HIGH
        )
        assert request.task_id == "test-123"
        assert request.task_type == "test_task"
        assert request.priority == Priority.HIGH
    
    def test_task_request_serialization(self):
        request = TaskRequest(
            task_id="test-123",
            task_type="test_task",
            parameters={"key": "value"}
        )
        data = request.to_dict()
        restored = TaskRequest.from_dict(data)
        assert restored.task_id == request.task_id
        assert restored.task_type == request.task_type
    
    def test_message_creation(self):
        message = create_task_request_message(
            from_agent="agent-a",
            to_agent="agent-b",
            task_type="test_task",
            parameters={"key": "value"}
        )
        assert message.msg_type == MessageType.TASK_REQUEST
        assert message.from_agent == "agent-a"
        assert message.to_agent == "agent-b"
    
    def test_message_serialization(self):
        message = create_task_request_message(
            from_agent="agent-a",
            to_agent="agent-b",
            task_type="test_task",
            parameters={"key": "value"}
        )
        data = message.to_dict()
        restored = Message.from_dict(data)
        assert restored.msg_type == message.msg_type
        assert restored.from_agent == message.from_agent


class TestInMemoryMessageBus:
    """测试内存消息总线"""
    
    @pytest.mark.asyncio
    async def test_publish_and_subscribe(self):
        bus = MessageBusFactory.create("memory")
        received_messages = []
        
        async def callback(message):
            received_messages.append(message)
        
        await bus.subscribe("agent-1", callback)
        
        message = create_task_request_message(
            from_agent="agent-2",
            to_agent="agent-1",
            task_type="test",
            parameters={}
        )
        await bus.publish(message)
        
        await asyncio.sleep(0.1)
        assert len(received_messages) == 1
        assert received_messages[0].message_id == message.message_id
        
        await bus.close()
    
    @pytest.mark.asyncio
    async def test_broadcast(self):
        bus = MessageBusFactory.create("memory")
        agent1_messages = []
        agent2_messages = []
        
        async def callback1(message):
            agent1_messages.append(message)
        
        async def callback2(message):
            agent2_messages.append(message)
        
        await bus.subscribe("agent-1", callback1)
        await bus.subscribe("agent-2", callback2)
        
        message = create_task_request_message(
            from_agent="agent-3",
            to_agent="broadcast",
            task_type="test",
            parameters={}
        )
        await bus.publish(message)
        
        await asyncio.sleep(0.1)
        assert len(agent1_messages) == 1
        assert len(agent2_messages) == 1
        
        await bus.close()
    
    @pytest.mark.asyncio
    async def test_unsubscribe(self):
        bus = MessageBusFactory.create("memory")
        received_messages = []
        
        async def callback(message):
            received_messages.append(message)
        
        await bus.subscribe("agent-1", callback)
        await bus.unsubscribe("agent-1")
        
        message = create_task_request_message(
            from_agent="agent-2",
            to_agent="agent-1",
            task_type="test",
            parameters={}
        )
        await bus.publish(message)
        
        await asyncio.sleep(0.1)
        assert len(received_messages) == 0
        
        await bus.close()


class TestAgent:
    """测试Agent"""
    
    @pytest.mark.asyncio
    async def test_agent_creation(self):
        agent = Agent(
            name="test-agent",
            capabilities=["task1", "task2"]
        )
        assert agent.name == "test-agent"
        assert agent.capabilities == ["task1", "task2"]
        assert agent.info.version == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_handler_registration(self):
        agent = Agent(name="test-agent", capabilities=["test_task"])
        
        @agent.handler("test_task")
        async def handle_test(request):
            return {"result": "success"}
        
        assert "test_task" in agent._handlers
    
    @pytest.mark.asyncio
    async def test_task_execution(self):
        bus = MessageBusFactory.create("memory")
        
        agent1 = Agent(name="agent1", capabilities=["test_task"], message_bus=bus)
        agent2 = Agent(name="agent2", capabilities=[], message_bus=bus)
        
        @agent1.handler("test_task")
        async def handle_test(request):
            return {"result": "success", "data": request.parameters.get("data")}
        
        await agent1.start()
        await agent2.start()
        
        # 发送任务
        response = await agent2.send_task(
            to_agent=agent1.agent_id,
            task_type="test_task",
            parameters={"data": "hello"},
            timeout=5.0
        )
        
        assert response.status == TaskStatus.COMPLETED
        assert response.result["result"] == "success"
        assert response.result["data"] == "hello"
        
        await agent1.stop()
        await agent2.stop()
        await bus.close()
    
    @pytest.mark.asyncio
    async def test_task_timeout(self):
        bus = MessageBusFactory.create("memory")
        
        agent1 = Agent(name="agent1", capabilities=["slow_task"], message_bus=bus)
        agent2 = Agent(name="agent2", capabilities=[], message_bus=bus)
        
        @agent1.handler("slow_task")
        async def handle_slow(request):
            await asyncio.sleep(10)  # 很慢的任务
            return {"result": "done"}
        
        await agent1.start()
        await agent2.start()
        
        # 发送任务，设置短超时
        response = await agent2.send_task(
            to_agent=agent1.agent_id,
            task_type="slow_task",
            parameters={},
            timeout=0.1
        )
        
        assert response.status == TaskStatus.FAILED
        assert "Timeout" in response.error
        
        await agent1.stop()
        await agent2.stop()
        await bus.close()


class TestWorkflowEngine:
    """测试工作流引擎"""
    
    @pytest.mark.asyncio
    async def test_workflow_creation(self):
        engine = WorkflowEngine()
        
        steps = [
            WorkflowStep(step_id="step1", task_type="task1"),
            WorkflowStep(step_id="step2", task_type="task2", depends_on=["step1"])
        ]
        
        workflow = engine.create_workflow("test_workflow", steps)
        
        assert workflow.name == "test_workflow"
        assert len(workflow.steps) == 2
        assert "step1" in workflow.steps
        assert "step2" in workflow.steps
    
    @pytest.mark.asyncio
    async def test_simple_workflow(self):
        bus = MessageBusFactory.create("memory")
        engine = WorkflowEngine()
        
        agent = Agent(name="test-agent", capabilities=["task1", "task2"], message_bus=bus)
        
        @agent.handler("task1")
        async def handle_task1(request):
            return {"output": "task1_result"}
        
        @agent.handler("task2")
        async def handle_task2(request):
            return {"output": "task2_result"}
        
        await agent.start()
        engine.register_agent(agent)
        
        steps = [
            WorkflowStep(step_id="step1", task_type="task1", agent_name="test-agent"),
            WorkflowStep(step_id="step2", task_type="task2", agent_name="test-agent", depends_on=["step1"])
        ]
        
        workflow = engine.create_workflow("test_workflow", steps)
        result = await engine.execute_workflow(workflow)
        
        assert result.status == WorkflowStatus.COMPLETED
        assert "step1" in result.results
        assert "step2" in result.results
        
        await agent.stop()
        await bus.close()
    
    @pytest.mark.asyncio
    async def test_workflow_with_parameters(self):
        bus = MessageBusFactory.create("memory")
        engine = WorkflowEngine()
        
        agent = Agent(name="test-agent", capabilities=["process"], message_bus=bus)
        
        @agent.handler("process")
        async def handle_process(request):
            value = request.parameters.get("value", 0)
            return {"result": value * 2}
        
        await agent.start()
        engine.register_agent(agent)
        
        steps = [
            WorkflowStep(
                step_id="step1",
                task_type="process",
                agent_name="test-agent",
                parameters={"value": 5}
            )
        ]
        
        workflow = engine.create_workflow("param_test", steps)
        result = await engine.execute_workflow(workflow)
        
        assert result.status == WorkflowStatus.COMPLETED
        assert result.results["step1"]["result"] == 10
        
        await agent.stop()
        await bus.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
