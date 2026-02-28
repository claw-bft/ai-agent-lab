# Product Pro

产品经理专业技能包 - 市场洞察、产品落地、数据驱动决策

## 功能特性

### 1. 竞品分析 (Competitor Analysis)
全面分析竞争对手产品，输出专业分析报告：
- **SWOT分析**: 优势、劣势、机会、威胁四维度评估
- **4P分析**: 产品、价格、渠道、促销策略分析
- **用户旅程分析**: 从认知到留存的全流程体验分析
- **功能对比矩阵**: 核心功能逐项对比

### 2. PRD生成 (Product Requirements Document)
自动生成标准化产品需求文档：
- **标准模板**: 完整PRD结构，适合大型项目
- **精简模板**: 核心要素，适合敏捷开发
- **详细模板**: 包含UI/UX说明，适合设计驱动项目
- **自定义字段**: 支持根据产品类型调整章节

### 3. PPT生成 (Presentation Generator)
一键生成产品规划演示文稿：
- **自动排版**: 智能布局，专业美观
- **数据可视化**: 自动插入图表和图形
- **多主题支持**: 商务、科技、简约多种风格
- **导出格式**: 支持PPTX、PDF导出

### 4. 市场研究 (Market Research)
系统化市场研究方法工具：
- **二手资料研究**: 行业报告、新闻、论文分析
- **用户访谈**: 访谈提纲生成、结果分析
- **问卷调查**: 问卷设计、数据分析
- **市场规模估算**: TAM/SAM/SOM计算

## 安装

### 环境要求
- Python 3.8+
- 依赖包: python-pptx, requests

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/claw-bft/ai-agent-lab.git
cd ai-agent-lab/product-pro

# 安装依赖
pip install -r requirements.txt

# 验证安装
python product-pro.py --help
```

## 快速开始

### 命令行使用

```bash
# 竞品分析 - 分析AI代码助手市场
python product-pro.py competitor analyze --product "AI代码助手" --output report.md

# 生成PRD - 标准模板
python product-pro.py prd create --feature "智能推荐系统" --template standard

# 生成PRD - 精简模板
python product-pro.py prd create --feature "登录功能优化" --template minimal

# 生成PPT - 10页产品规划
python product-pro.py ppt create --topic "Q3产品规划报告" --slides 10 --output plan.pptx

# 市场研究 - 竞争分析
python product-pro.py research conduct --topic "AI助手市场" --method competitive

# 市场研究 - 用户访谈
python product-pro.py research conduct --topic "用户付费意愿" --method interview
```

### Python API 使用

```python
from product_pro import CompetitorAnalyzer, PRDGenerator, PPTGenerator

# ===== 竞品分析 =====
analyzer = CompetitorAnalyzer()

# 基础分析
result = analyzer.analyze("AI代码助手")
print(result['swot'])

# 带输出文件
analyzer.analyze("视频会议软件", output_file="competitor_report.md")


# ===== PRD生成 =====
generator = PRDGenerator()

# 标准模板
prd = generator.generate(
    feature="智能推荐系统",
    template="standard",
    author="产品经理",
    priority="高"
)

# 精简模板
prd_minimal = generator.generate(
    feature="暗黑模式支持",
    template="minimal"
)


# ===== PPT生成 =====
ppt_gen = PPTGenerator()

# 生成演示文稿
ppt_gen.create(
    topic="产品年度规划",
    slides=15,
    style="business",
    output_file="annual_plan.pptx"
)
```

## 使用示例

### 示例1: 完整的竞品分析流程

```python
from product_pro import CompetitorAnalyzer

# 1. 定义分析目标
product = "在线文档协作工具"
competitors = ["Notion", "飞书文档", "腾讯文档"]

# 2. 执行分析
analyzer = CompetitorAnalyzer()
for comp in competitors:
    result = analyzer.analyze(comp, context=product)
    print(f"\n=== {comp} 分析结果 ===")
    print(f"优势: {result['strengths']}")
    print(f"劣势: {result['weaknesses']}")

# 3. 生成对比报告
analyzer.generate_comparison_matrix(competitors, output="comparison.md")
```

### 示例2: 敏捷PRD生成

```python
from product_pro import PRDGenerator

generator = PRDGenerator()

# 快速生成用户故事
stories = [
    "作为用户，我想通过微信一键登录，减少注册流程",
    "作为用户，我想保存搜索历史，方便再次查找",
    "作为管理员，我想导出用户数据，用于数据分析"
]

for story in stories:
    prd = generator.from_user_story(story, template="minimal")
    print(f"\n用户故事: {story}")
    print(f"PRD: {prd[:200]}...")
```

## 项目结构

```
product-pro/
├── product-pro.py          # 核心实现 (908行)
├── requirements.txt        # 依赖配置
├── README.md              # 项目文档
├── SKILL.md               # 技能使用说明
├── tests/                 # 测试目录
│   ├── test_product_pro.py    # 功能测试 (26个)
│   └── test_performance.py    # 性能测试
└── examples/              # 示例输出
    ├── prd_example.md
    ├── competitor_report.md
    └── presentation.pptx
```

## 核心类说明

| 类名 | 功能 | 主要方法 |
|------|------|----------|
| `CompetitorAnalyzer` | 竞品分析 | `analyze()`, `swot_analysis()`, `journey_map()` |
| `PRDGenerator` | PRD生成 | `generate()`, `from_user_story()` |
| `PPTGenerator` | PPT生成 | `create()`, `add_slide()`, `export()` |
| `MarketResearch` | 市场研究 | `conduct()`, `survey_design()`, `data_analysis()` |

## 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_product_pro.py::TestPRDGenerator -v

# 带覆盖率报告
pytest tests/ --cov=product_pro --cov-report=html
```

### 测试结果

- **总测试数**: 26个
- **通过率**: 100%
- **测试覆盖**: 核心功能全覆盖

## 最佳实践

1. **竞品分析**: 建议每季度更新一次，跟踪市场变化
2. **PRD编写**: 根据项目规模选择合适模板，避免过度文档化
3. **PPT制作**: 善用数据可视化，一页一个核心观点
4. **市场研究**: 多方法交叉验证，提高结论可信度

## 常见问题

**Q: 生成的PRD可以直接用于开发吗？**  
A: 生成的PRD是结构化模板，需要根据实际产品填充具体内容。

**Q: PPT生成支持自定义模板吗？**  
A: 当前版本支持内置主题，自定义模板功能正在开发中。

**Q: 竞品分析的数据来源是什么？**  
A: 基于公开信息和AI生成，建议结合实际调研数据使用。

## 更新日志

### v1.0.0 (2026-02-24)
- 初始版本发布
- 支持竞品分析、PRD生成、PPT生成、市场研究四大功能
- 26个单元测试全覆盖

## 贡献指南

欢迎提交Issue和PR！请确保：
- 代码通过所有测试
- 新增功能包含测试用例
- 更新相关文档

## License

MIT License - 详见 [LICENSE](../LICENSE) 文件
