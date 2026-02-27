# Legal Assistant - 法律助手

## 描述
专业法律文档分析和咨询服务，支持合同审查、法规查询、文档解析。

## 功能

### 1. 合同审查 (contract_analyzer.py)
- 风险条款识别（不公平条款、模糊条款、缺失条款、责任限制）
- 合同类型自动检测（劳动/买卖/租赁/服务等）
- 权利义务分析
- 修改建议生成

### 2. 法规查询 (legal_query.py)
- 基础法律知识库（劳动法、合同法、消费者权益等）
- 智能问答匹配
- 相关法条检索
- 维权建议生成

### 3. 文档解析 (document_parser.py)
- 多格式文档解析
- 当事人/日期/金额提取
- 章节结构分析
- 关键条款提取

## 使用示例

### 命令行工具

```bash
# 审查合同
cd /root/.openclaw/workspace/skills/legal-assistant
python cli.py review --file contract.txt --type employment

# 法规查询
python cli.py search --question "试用期最长多久"
python cli.py search --keyword "劳动合同法"

# 解析文档
python cli.py parse --file document.txt
```

### Python API

```python
from contract_analyzer import ContractAnalyzer
from legal_query import LegalKnowledgeBase
from document_parser import DocumentParser

# 合同审查
analyzer = ContractAnalyzer()
result = analyzer.analyze(contract_text)
for finding in result.risk_findings:
    print(f"[{finding.level.value}] {finding.description}")

# 法律咨询
kb = LegalKnowledgeBase()
advice = kb.query("加班费怎么算？")
print(advice.analysis)

# 文档解析
parser = DocumentParser()
doc = parser.parse(text)
print(f"当事人: {doc.parties}")
```

## 风险检测能力

### 不公平条款检测
- 最终解释权归属
- 单方修改权
- 过度免责条款
- 过高违约金

### 模糊条款检测
- "合理期限"
- "适当补偿"
- "必要时"
- "根据实际情况"

### 缺失条款检测
- 劳动合同：工作内容、工资、社保、试用期等
- 买卖合同：标的物、质量、价款、验收等
- 租赁合同：租期、租金、维修责任、押金等

## 依赖
- Python 3.8+
- 无第三方依赖（纯标准库）

## 免责声明
本工具提供的法律建议仅供参考，不构成正式法律意见。重要法律事务请咨询专业律师。

## 状态
✅ 已实现核心功能
- contract_analyzer.py - 合同风险分析
- legal_query.py - 法律咨询查询
- document_parser.py - 文档解析
- cli.py - 命令行接口
