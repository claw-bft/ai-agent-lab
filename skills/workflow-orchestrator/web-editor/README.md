# Workflow Orchestrator Web Editor

可视化工作流编辑器 - 基于浏览器的拖拽式工作流设计工具。

## 功能特性

### 节点系统
- **基础节点**: 开始、结束
- **任务节点**: 任务执行、条件判断
- **流程控制**: 并行执行、结果聚合、延迟等待

### 可视化编辑
- 拖拽式节点添加和布局
- 可视化连线编辑
- 实时属性面板
- 网格对齐辅助

### 模板库
- 📈 股票研究: 获取行情 → 公司研究 → 深度分析
- 🚀 产品开发: 调研 → 竞品分析 → PRD → 原型
- ✍️ 内容营销: 话题研究 → 深度分析 → 报告
- 📊 数据分析: 采集 → 清洗 → 可视化

### 导入导出
- JSON 格式工作流定义
- 本地存储自动保存
- 一键导出分享

### 执行监控
- 实时执行状态显示
- 节点执行动画
- 执行日志面板

## 使用方法

### 本地打开
```bash
cd /root/.openclaw/workspace/skills/workflow-orchestrator/web-editor
python -m http.server 8080
# 然后访问 http://localhost:8080
```

或直接双击 `index.html` 在浏览器中打开。

### 创建工作流
1. 从左侧拖拽节点到画布
2. 点击节点编辑属性
3. 拖拽节点端口创建连接
4. 点击执行按钮运行工作流

### 快捷键
- `Delete`: 删除选中节点
- `拖拽`: 移动节点
- `点击端口拖拽`: 创建连接

## 技术栈

- 纯 HTML/CSS/JavaScript
- 无需构建工具
- 无需后端依赖
- 支持现代浏览器

## 与后端集成

编辑器生成的 JSON 工作流定义可直接被 `workflow_engine.py` 执行：

```python
from workflow_engine import WorkflowEngine, WorkflowDefinition

# 从 JSON 加载
with open('workflow.json') as f:
    data = json.load(f)

workflow = WorkflowDefinition.from_dict(data)
engine = WorkflowEngine()
engine.register_workflow(workflow)
engine.execute_workflow(workflow.workflow_id)
```

## 更新日志

### 2026-02-27
- ✅ 实现完整的可视化编辑器
- ✅ 支持7种节点类型
- ✅ 实现拖拽式节点编辑
- ✅ 实现可视化连线
- ✅ 添加4个预定义模板
- ✅ 实现执行监控面板
- ✅ 支持导入导出 JSON
