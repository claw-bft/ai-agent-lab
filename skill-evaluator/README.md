# Skill Evaluator - 技能包自动评测系统

自动化测试和质量评估系统，用于评估技能包的代码质量、测试覆盖率、文档完整性等。

## 功能特性

- **代码质量评估**: 检查代码规范、复杂度、潜在问题
- **测试覆盖率分析**: 统计测试覆盖率，识别未覆盖代码
- **文档完整性检查**: 验证README、SKILL.md等文档存在性和完整性
- **依赖安全性扫描**: 检查依赖包已知漏洞
- **性能基准测试**: 测量关键操作执行时间
- **综合评分系统**: 生成0-100的综合质量评分

## 使用方法

```python
from skill_evaluator import SkillEvaluator

# 初始化评测器
evaluator = SkillEvaluator()

# 评测单个技能包
result = evaluator.evaluate_skill("/path/to/skill-package")
print(f"评分: {result['overall_score']}/100")
print(f"等级: {result['grade']}")

# 批量评测所有技能包
results = evaluator.evaluate_all_skills("/path/to/skills/dir")
for name, result in results.items():
    print(f"{name}: {result['overall_score']}/100 ({result['grade']})")
```

## 评测维度

| 维度 | 权重 | 说明 |
|------|------|------|
| 代码质量 | 25% | 代码规范、复杂度、lint问题 |
| 测试覆盖率 | 25% | 单元测试覆盖率和通过率 |
| 文档完整性 | 20% | README、SKILL.md、API文档 |
| 依赖安全 | 15% | 依赖包漏洞扫描 |
| 性能基准 | 15% | 关键操作执行时间 |

## 评分等级

- **S (90-100)**: 优秀，生产就绪
- **A (80-89)**: 良好，推荐使用
- **B (70-79)**: 合格，基本可用
- **C (60-69)**: 待改进，存在问题
- **D (0-59)**: 不合格，需要重构

## CLI 使用

```bash
# 评测当前目录技能包
python skill_evaluator.py

# 评测指定技能包
python skill_evaluator.py --skill /path/to/skill

# 批量评测
python skill_evaluator.py --all --dir /path/to/skills

# 生成报告
python skill_evaluator.py --all --report eval_report.json

# 详细输出
python skill_evaluator.py --skill /path/to/skill --verbose
```

## 测试

```bash
python -m pytest tests/ -v
```
