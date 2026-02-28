# Research Pro

研究分析专业技能包 - 深度调研、竞品分析、趋势洞察

## 功能特性

- **深度研究**: 多源信息整合，结构化输出
- **竞品分析**: 产品对比、功能矩阵
- **趋势洞察**: 行业趋势、技术演进
- **报告生成**: 自动生成研究报告

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

```bash
# 深度研究
python research-pro.py deep --topic "AI发展趋势"

# 竞品分析
python research-pro.py competitor --product "AI助手"

# 趋势洞察
python research-pro.py trend --industry "人工智能"
```

## Python API

```python
from research_pro import ResearchPro

rp = ResearchPro()

# 深度研究
result = rp.deep_research("AI发展趋势")

# 竞品分析
analysis = rp.competitor_analysis("AI助手")
```

## 项目结构

```
research-pro/
├── research-pro.py     # 核心实现
├── requirements.txt    # 依赖配置
├── tests/             # 测试目录
│   └── test_research.py
└── SKILL.md           # 技能文档
```

## 测试

```bash
pytest tests/ -v
```

## License

MIT
