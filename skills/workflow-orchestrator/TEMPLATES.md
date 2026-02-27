# 工作流模板生态

本文档介绍 workflow-orchestrator 提供的 6 个预定义工作流模板。

## 模板列表

| 模板ID | 名称 | 描述 | 复杂度 |
|--------|------|------|--------|
| `stock-research` | 股票研究 | 获取行情 → 公司研究 → 深度分析 | 简单 |
| `product-dev` | 产品开发 | 市场调研 → 竞品分析 → PRD → 原型代码 | 中等 |
| `content-marketing` | 内容营销 | 话题研究 → 深度研究 → 生成报告 | 简单 |
| `data-analysis` | 数据分析 | 数据采集 → 清洗 → 建模 → 可视化 | 中等 |
| `customer-service` | 客户服务 | 工单分类 → 智能回复 → 满意度分析 → 知识库更新 | 复杂 |
| `devops-monitoring` | 运维监控 | 指标采集 → 异常检测 → 告警 → 自动修复 → 报告 | 复杂 |

---

## 1. 股票研究 (stock-research)

**适用场景**: 股票基本面研究和技术分析

**流程**:
```
开始 → 获取行情(finance.quote) → 公司研究(research.search) → 深度分析(research.deep) → 完成
```

**输入参数**:
```json
{
  "symbol": "600519.SH"
}
```

**使用示例**:
```bash
./workflow-cli create --template stock-research --name "茅台研究"
./workflow-cli execute <workflow_id> --input '{"symbol": "600519.SH"}'
```

---

## 2. 产品开发 (product-dev)

**适用场景**: 从0到1的产品开发全流程

**流程**:
```
开始 → 市场调研 → 竞品分析 → 生成PRD → 原型代码 → 完成
```

**输入参数**:
```json
{
  "product_name": "智能客服系统"
}
```

**使用示例**:
```bash
./workflow-cli create --template product-dev --name "AI助手开发"
./workflow-cli execute <workflow_id> --input '{"product_name": "智能客服系统"}'
```

---

## 3. 内容营销 (content-marketing)

**适用场景**: 营销内容创作和研究报告生成

**流程**:
```
开始 → 话题研究 → 深度研究 → 生成报告 → 完成
```

**输入参数**:
```json
{
  "topic": "AI Agent发展趋势"
}
```

---

## 4. 数据分析 (data-analysis) ⭐ 新增

**适用场景**: 端到端的数据分析流程

**流程**:
```
开始 → 数据采集 → 数据清洗 → 分析建模 → 可视化报告 → 完成
```

**参与Agent**:
- `research-pro`: 数据采集、分析建模
- `coding-pro`: 数据清洗脚本、可视化代码

**输入参数**:
```json
{
  "data_source": "电商销售数据 2024年",
  "analysis_type": "趋势分析"
}
```

**输出**:
- 清洗后的数据
- 分析模型代码
- 可视化仪表板

**使用示例**:
```python
from workflow_engine import WorkflowTemplateLibrary

workflow = WorkflowTemplateLibrary.create_workflow_from_template(
    "data-analysis", "电商数据分析"
)
workflow_id = engine.register_workflow(workflow)
exec_id = engine.execute_workflow(workflow_id, {
    "data_source": "电商销售数据 2024年",
    "analysis_type": "趋势分析"
})
```

---

## 5. 客户服务 (customer-service) ⭐ 新增

**适用场景**: 自动化客服工单处理

**流程**:
```
开始 → 工单分类 → [是否技术问题?]
                    ├── 是 → 技术回复 ──┐
                    └── 否 → 一般回复 ──┤
                                      ↓
                              合并回复 → 满意度分析 → 更新知识库 → 完成
```

**参与Agent**:
- `research-pro`: 工单分类、一般回复、满意度分析
- `coding-pro`: 技术问题解决方案
- `product-pro`: 知识库更新

**特性**:
- 条件分支：根据问题类型自动分流
- 并行处理：技术问题和一般问题分别处理
- 知识沉淀：自动提取FAQ更新知识库

**输入参数**:
```json
{
  "ticket_content": "无法登录系统，提示密码错误但确认无误",
  "customer_id": "CUST-001"
}
```

**使用示例**:
```bash
# 从模板创建工作流
./workflow-cli create --template customer-service --name "智能客服"

# 执行工单处理
./workflow-cli execute <workflow_id> --input '{
  "ticket_content": "无法登录系统",
  "customer_id": "CUST-001"
}'
```

---

## 6. 运维监控 (devops-monitoring) ⭐ 新增

**适用场景**: 系统监控、异常检测和自动修复

**流程**:
```
开始 → 指标采集 → [异常检测?]
                  ├── 异常 → 告警通知 ──┐
                  │           自动修复 ──┤
                  │                     ↓
                  │            合并结果 → 等待验证 → 生成报告 → 完成
                  └── 正常 ───────────────────────────────┘
```

**参与Agent**:
- `research-pro`: 指标采集、告警通知、报告生成
- `coding-pro`: 自动修复脚本生成

**特性**:
- 条件分支：根据监控指标状态分流
- 并行处理：告警和修复同时进行
- 延迟验证：修复后等待验证效果
- 事件报告：生成完整的运维事件报告

**输入参数**:
```json
{
  "service_name": "订单服务",
  "metrics": ["CPU", "内存", "响应时间", "错误率"]
}
```

**使用示例**:
```python
# 创建运维监控工作流
workflow = WorkflowTemplateLibrary.create_workflow_from_template(
    "devops-monitoring", "订单服务监控"
)

# 执行监控
exec_id = engine.execute_workflow(workflow_id, {
    "service_name": "订单服务",
    "metrics": ["CPU", "内存", "响应时间"]
})
```

---

## 快速开始

### 查看所有模板
```bash
./workflow-cli templates
```

### 从模板创建工作流
```bash
# 数据分析
./workflow-cli create --template data-analysis --name "销售数据分析"

# 客户服务
./workflow-cli create --template customer-service --name "智能客服"

# 运维监控
./workflow-cli create --template devops-monitoring --name "系统监控"
```

### 执行工作流
```bash
./workflow-cli execute <workflow_id> --input '<JSON参数>'
```

### Web可视化编辑器
```bash
cd web-editor
python -m http.server 8080
# 访问 http://localhost:8080
```

---

## 扩展新模板

参考 `templates/` 目录下的 JSON 文件格式，创建自定义模板：

```json
{
  "id": "my-template",
  "name": "我的模板",
  "description": "模板描述",
  "nodes": [...],
  "edges": [...]
}
```

然后在 `workflow_engine.py` 的 `TEMPLATES` 字典中注册新模板。
