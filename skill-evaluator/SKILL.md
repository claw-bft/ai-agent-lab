# Skill Evaluator

技能包自动评测系统 - 全面评估技能包质量

## 功能特性

- **代码质量**: 圈复杂度、代码风格检查
- **测试覆盖**: 测试文件检测、通过率统计
- **文档评估**: README/SKILL.md完整性检查
- **安全扫描**: 依赖漏洞检测
- **性能测试**: 模块加载时间、大小评估

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

```bash
# 评测单个技能包
python skill_evaluator.py /path/to/skill

# 评测所有技能包
python skill_evaluator.py --all

# 生成报告
python skill_evaluator.py --all --output report.json
```

## Python API

```python
from skill_evaluator import SkillEvaluator

evaluator = SkillEvaluator()
result = evaluator.evaluate("/path/to/skill")
print(result.grade)  # S/A/B/C/D
print(result.score)  # 总分
```

## 评分维度

| 维度 | 权重 | 说明 |
|------|------|------|
| 代码质量 | 20% | 复杂度、风格 |
| 测试覆盖 | 30% | 测试数量、通过率 |
| 文档完整 | 25% | README/SKILL.md |
| 安全性 | 15% | 依赖漏洞 |
| 性能 | 10% | 加载时间 |

## 项目结构

```
skill-evaluator/
├── skill_evaluator.py  # 核心实现
├── tests/             # 测试目录
│   └── test_evaluator.py
└── README.md          # 本文档
```

## 测试

```bash
pytest tests/ -v
```

## License

MIT
