#!/usr/bin/env python3
"""
Skill Evaluator 测试套件
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from skill_evaluator import SkillEvaluator, EvaluationResult, Grade


class TestSkillEvaluator:
    """测试技能包评测器"""
    
    def setup_method(self):
        """每个测试方法前执行"""
        self.evaluator = SkillEvaluator(verbose=False)
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """每个测试方法后执行"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_grade_from_score(self):
        """测试评分等级转换"""
        assert Grade.from_score(95) == Grade.S
        assert Grade.from_score(85) == Grade.A
        assert Grade.from_score(75) == Grade.B
        assert Grade.from_score(65) == Grade.C
        assert Grade.from_score(55) == Grade.D
        assert Grade.from_score(100) == Grade.S
        assert Grade.from_score(0) == Grade.D
    
    def test_is_skill_package(self):
        """测试技能包识别"""
        # 创建临时技能包结构
        skill_dir = Path(self.temp_dir) / "test-skill"
        skill_dir.mkdir()
        
        # 空目录不是技能包
        assert not self.evaluator._is_skill_package(skill_dir)
        
        # 有Python文件是技能包
        (skill_dir / "main.py").write_text("print('hello')")
        assert self.evaluator._is_skill_package(skill_dir)
        
        # 有SKILL.md是技能包
        skill_dir2 = Path(self.temp_dir) / "test-skill2"
        skill_dir2.mkdir()
        (skill_dir2 / "SKILL.md").write_text("# Skill")
        assert self.evaluator._is_skill_package(skill_dir2)
    
    def test_evaluate_empty_skill(self):
        """测试空技能包评测"""
        skill_dir = Path(self.temp_dir) / "empty-skill"
        skill_dir.mkdir()
        
        # 添加一个空Python文件使其被识别为技能包
        (skill_dir / "empty.py").write_text("")
        
        result = self.evaluator.evaluate_skill(str(skill_dir))
        
        assert result.skill_name == "empty-skill"
        assert result.overall_score >= 0.0
        assert result.grade == "D"
        assert len(result.issues) > 0
    
    def test_evaluate_good_skill(self):
        """测试良好技能包评测"""
        skill_dir = Path(self.temp_dir) / "good-skill"
        skill_dir.mkdir()
        
        # 创建README
        (skill_dir / "README.md").write_text("""# Good Skill

## 功能
这是一个测试技能包

## 使用
```python
import good_skill
```

## 示例
见文档
""")
        
        # 创建SKILL.md
        (skill_dir / "SKILL.md").write_text("""---
name: good-skill
description: 测试技能包
---

# Good Skill

## 使用示例
```python
from good_skill import main
main()
```
""")
        
        # 创建Python模块
        (skill_dir / "good_skill.py").write_text('''
"""Good Skill 模块"""

def main():
    """主函数"""
    return "Hello World"

def helper():
    """辅助函数"""
    return 42
''')
        
        # 创建测试目录和测试文件
        tests_dir = skill_dir / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_good_skill.py").write_text('''
import pytest
from good_skill import main, helper

def test_main():
    assert main() == "Hello World"

def test_helper():
    assert helper() == 42

def test_another():
    assert True
''')
        
        result = self.evaluator.evaluate_skill(str(skill_dir))
        
        assert result.skill_name == "good-skill"
        assert result.overall_score > 50  # 应该有不错的分数
        assert result.documentation_score >= 60  # 文档应该不错
    
    def test_code_quality_evaluation(self):
        """测试代码质量评估"""
        skill_dir = Path(self.temp_dir) / "code-skill"
        skill_dir.mkdir()
        
        # 创建有问题的代码
        (skill_dir / "bad_code.py").write_text('''
def complex_function(x):
    if x > 0:
        if x > 10:
            if x > 100:
                return "big"
            else:
                return "medium"
        else:
            return "small"
    else:
        return "negative"
    
# 很长的行，超过120字符限制，这是一个很长的注释，用来测试行长度检查功能是否正常工作
''')
        
        score, details = self.evaluator._evaluate_code_quality(skill_dir)
        
        assert details["total_files"] == 1
        assert details["total_lines"] > 0
        assert len(details["style_issues"]) > 0  # 应该有风格问题
    
    def test_documentation_evaluation(self):
        """测试文档完整性评估"""
        skill_dir = Path(self.temp_dir) / "doc-skill"
        skill_dir.mkdir()
        
        # 初始没有文档
        score1, details1 = self.evaluator._evaluate_documentation(skill_dir)
        assert score1 == 0
        assert not details1["has_readme"]
        assert not details1["has_skill_md"]
        
        # 添加README
        (skill_dir / "README.md").write_text("# Doc Skill\n\n## 功能\n测试\n\n## 使用\n使用说明")
        
        score2, details2 = self.evaluator._evaluate_documentation(skill_dir)
        assert score2 > 0
        assert details2["has_readme"]
    
    def test_security_evaluation(self):
        """测试安全性评估"""
        skill_dir = Path(self.temp_dir) / "sec-skill"
        skill_dir.mkdir()
        
        # 创建有安全问题的代码
        (skill_dir / "unsafe.py").write_text('''
import os

def run_command(user_input):
    # 安全问题: 使用eval
    result = eval(user_input)
    return result

def get_password():
    # 硬编码密码
    password = "secret123"
    return password
''')
        
        score, details = self.evaluator._evaluate_security(skill_dir)
        
        assert len(details["security_issues"]) > 0
        assert score < 100  # 应该有扣分
    
    def test_calculate_complexity(self):
        """测试复杂度计算"""
        code1 = "def simple(): return 1"
        code2 = """
def complex(x):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                while True:
                    break
    elif x < 0:
        try:
            result = 1 / x
        except:
            pass
    else:
        return None
"""
        
        c1 = self.evaluator._calculate_complexity(code1)
        c2 = self.evaluator._calculate_complexity(code2)
        
        assert c2 > c1  # 复杂代码应该有更高的复杂度
    
    def test_generate_report(self):
        """测试报告生成"""
        results = {
            "skill1": EvaluationResult(
                skill_name="skill1",
                skill_path="/path/skill1",
                overall_score=85.0,
                grade="A"
            ),
            "skill2": EvaluationResult(
                skill_name="skill2",
                skill_path="/path/skill2",
                overall_score=65.0,
                grade="C"
            )
        }
        
        report_path = Path(self.temp_dir) / "report.json"
        report = self.evaluator.generate_report(results, str(report_path))
        
        assert report["total_skills"] == 2
        assert report["summary"]["average_score"] == 75.0
        assert report_path.exists()


def run_tests():
    """运行测试"""
    import traceback
    
    test_class = TestSkillEvaluator()
    methods = [m for m in dir(test_class) if m.startswith("test_")]
    
    passed = 0
    failed = 0
    
    print(f"运行 {len(methods)} 个测试...\n")
    
    for method_name in methods:
        try:
            test_class.setup_method()
            getattr(test_class, method_name)()
            test_class.teardown_method()
            print(f"✅ {method_name}")
            passed += 1
        except Exception as e:
            print(f"❌ {method_name}")
            print(f"   错误: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"测试结果: {passed} 通过, {failed} 失败")
    
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
