# Workflow Orchestrator Test Suite

This directory contains comprehensive tests for the Workflow Orchestrator skill.

## Test Coverage

### Test Classes

1. **TestWorkflowNode** - 工作流节点测试
   - 默认节点创建
   - 完整字段节点创建
   - 序列化与反序列化
   - 所有节点类型验证

2. **TestWorkflowEdge** - 工作流边测试
   - 边创建
   - 条件边
   - 序列化

3. **TestWorkflow** - 工作流定义测试
   - 工作流创建
   - 添加节点和边
   - 获取节点
   - 工作流验证
   - 序列化

4. **TestWorkflowEngine** - 工作流引擎测试
   - 引擎初始化
   - 注册工作流
   - 获取工作流
   - 创建线性工作流

5. **TestWorkflowExecutor** - 工作流执行器测试
   - 执行器初始化
   - 上下文管理
   - 获取就绪节点
   - 节点状态转换

6. **TestWorkflowTemplates** - 工作流模板测试
   - 顺序执行模板
   - 并行执行模板
   - 条件分支模板

7. **TestIntegrationScenarios** - 集成场景测试
   - 数据处理工作流
   - 错误处理

## Running Tests

```bash
# Run all tests
pytest skills/workflow-orchestrator/tests/ -v

# Run with coverage
pytest skills/workflow-orchestrator/tests/ -v --cov=workflow_engine

# Run specific test class
pytest skills/workflow-orchestrator/tests/test_workflow_engine.py::TestWorkflowNode -v
```

## Test Status

- Total Test Cases: 20+
- Coverage Target: 80%+
- Status: ✅ Ready
