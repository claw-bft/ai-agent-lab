"""
技能评测器性能基准测试
Performance Benchmarks for Skill Evaluator
"""

import time
import pytest
import tempfile
import os
from pathlib import Path

from skill_evaluator import SkillEvaluator, Grade


class TestSkillEvaluatorPerformance:
    """技能评测器性能测试"""
    
    def test_evaluate_small_skill_performance(self, tmp_path):
        """测试评估小型技能包性能"""
        evaluator = SkillEvaluator()
        
        # 创建一个小型测试技能包
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "__init__.py").write_text("")
        (skill_dir / "main.py").write_text("""
def hello():
    return "Hello World"
""")
        (skill_dir / "README.md").write_text("# Test Skill\n\nA test skill.")
        
        tests_dir = skill_dir / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_main.py").write_text("""
def test_hello():
    assert hello() == "Hello World"
""")
        
        start = time.perf_counter()
        result = evaluator.evaluate_skill(str(skill_dir))
        elapsed = time.perf_counter() - start
        
        # 小型技能评估应在2秒内完成
        assert elapsed < 2.0, f"小型技能评估耗时 {elapsed:.3f}s，超过2秒"
        assert "overall_score" in result
    
    def test_evaluate_code_quality_performance(self):
        """测试代码质量评估性能"""
        evaluator = SkillEvaluator()
        
        # 创建测试代码
        test_code = "\n".join([f"def func_{i}(): pass" for i in range(100)])
        
        start = time.perf_counter()
        complexity = evaluator._calculate_complexity(test_code)
        elapsed = time.perf_counter() - start
        
        # 100个函数的复杂度分析应在0.5秒内完成
        assert elapsed < 0.5, f"复杂度分析耗时 {elapsed:.3f}s，超过0.5秒"
    
    def test_check_style_performance(self):
        """测试代码风格检查性能"""
        evaluator = SkillEvaluator()
        
        # 创建包含多种风格问题的代码
        test_code = "\n".join([
            f"import unused_module_{i}  # 未使用导入" for i in range(50)
        ] + [
            f"x = '{ 'a' * 150 }'  # 长行" for i in range(50)
        ])
        
        start = time.perf_counter()
        issues = evaluator._check_style_issues(test_code, "test.py")
        elapsed = time.perf_counter() - start
        
        # 风格检查应在0.5秒内完成
        assert elapsed < 0.5, f"风格检查耗时 {elapsed:.3f}s，超过0.5秒"
    
    def test_grade_calculation_performance(self):
        """测试评分等级计算性能"""
        start = time.perf_counter()
        
        for score in range(0, 101):
            grade = Grade.from_score(score)
        
        elapsed = time.perf_counter() - start
        
        # 101次评分计算应在0.01秒内完成
        assert elapsed < 0.01, f"评分计算耗时 {elapsed:.3f}s，超过0.01秒"


class TestReportGenerationPerformance:
    """报告生成性能测试"""
    
    def test_generate_report_performance(self, tmp_path):
        """测试报告生成性能"""
        evaluator = SkillEvaluator()
        
        # 创建模拟评测结果
        results = {
            f"skill-{i}": {
                "skill_name": f"skill-{i}",
                "overall_score": 85.0 + i,
                "grade": "A",
                "code_quality_score": 80.0,
                "test_coverage_score": 90.0,
                "documentation_score": 85.0,
                "security_score": 95.0,
                "performance_score": 80.0,
            }
            for i in range(20)
        }
        
        report_path = tmp_path / "benchmark_report.json"
        
        start = time.perf_counter()
        evaluator.generate_report(results, str(report_path))
        elapsed = time.perf_counter() - start
        
        # 20个技能包的报告生成应在0.5秒内完成
        assert elapsed < 0.5, f"报告生成耗时 {elapsed:.3f}s，超过0.5秒"
        assert report_path.exists()
    
    def test_batch_evaluation_performance(self, tmp_path):
        """测试批量评估性能"""
        evaluator = SkillEvaluator()
        
        # 创建多个测试技能包
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        
        for i in range(5):
            skill_dir = skills_dir / f"test-skill-{i}"
            skill_dir.mkdir()
            (skill_dir / "__init__.py").write_text("")
            (skill_dir / "main.py").write_text(f"""
def skill_{i}():
    return "Skill {i}"
""")
            (skill_dir / "README.md").write_text(f"# Skill {i}")
        
        start = time.perf_counter()
        results = evaluator.evaluate_all(str(skills_dir))
        elapsed = time.perf_counter() - start
        
        # 5个技能包批量评估应在10秒内完成
        assert elapsed < 10.0, f"批量评估耗时 {elapsed:.3f}s，超过10秒"
        assert len(results) == 5
