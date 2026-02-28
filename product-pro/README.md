# Product Pro

产品经理专业技能包 - 市场洞察、产品落地、数据驱动决策

## 功能特性

- **竞品分析**: SWOT分析、4P分析、用户旅程分析
- **PRD生成**: 标准/精简/详细三种PRD模板
- **PPT生成**: 自动生成产品规划PPT
- **市场研究**: 二手资料、用户访谈、问卷调查

## 安装

```bash
pip install python-pptx requests
```

## 快速开始

```bash
# 竞品分析
python product-pro.py competitor analyze --product "AI代码助手"

# 生成PRD
python product-pro.py prd create --feature "智能推荐系统" --template standard

# 生成PPT
python product-pro.py ppt create --topic "产品规划报告" --slides 10

# 市场研究
python product-pro.py research conduct --topic "AI助手市场" --method competitive
```

## Python API

```python
from product_pro import CompetitorAnalyzer, PRDGenerator

# 竞品分析
analyzer = CompetitorAnalyzer()
result = analyzer.analyze("AI代码助手")

# PRD生成
generator = PRDGenerator()
prd = generator.generate("智能推荐系统", template="standard")
```

## 项目结构

```
product-pro/
├── product-pro.py      # 核心实现
├── requirements.txt    # 依赖配置
├── tests/             # 测试目录
│   └── test_product.py
└── SKILL.md           # 技能文档
```

## 测试

```bash
pytest tests/ -v
```

## License

MIT
