#!/usr/bin/env python3
"""
Skill Evaluator - 技能包自动评测系统

自动化测试和质量评估系统，用于评估技能包的：
- 代码质量（规范、复杂度）
- 测试覆盖率
- 文档完整性
- 依赖安全性
- 性能基准

Author: AI Agent Lab
Version: 1.0.0
"""

import os
import sys
import json
import ast
import re
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import argparse


class Grade(Enum):
    """评分等级"""
    S = "S"  # 90-100 优秀
    A = "A"  # 80-89 良好
    B = "B"  # 70-79 合格
    C = "C"  # 60-69 待改进
    D = "D"  # 0-59 不合格

    @classmethod
    def from_score(cls, score: float) -> "Grade":
        if score >= 90:
            return cls.S
        elif score >= 80:
            return cls.A
        elif score >= 70:
            return cls.B
        elif score >= 60:
            return cls.C
        else:
            return cls.D


@dataclass
class EvaluationResult:
    """评测结果"""
    skill_name: str
    skill_path: str
    overall_score: float = 0.0
    grade: str = "D"

    # 各维度得分
    code_quality_score: float = 0.0
    test_coverage_score: float = 0.0
    documentation_score: float = 0.0
    security_score: float = 0.0
    performance_score: float = 0.0

    # 详细信息
    code_quality_details: Dict[str, Any] = field(default_factory=dict)
    test_coverage_details: Dict[str, Any] = field(default_factory=dict)
    documentation_details: Dict[str, Any] = field(default_factory=dict)
    security_details: Dict[str, Any] = field(default_factory=dict)
    performance_details: Dict[str, Any] = field(default_factory=dict)

    # 问题和建议
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    # 元数据
    evaluated_at: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%S"))
    duration_ms: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SkillEvaluator:
    """技能包评测器"""

    # 权重配置
    WEIGHTS = {
        "code_quality": 0.25,
        "test_coverage": 0.25,
        "documentation": 0.20,
        "security": 0.15,
        "performance": 0.15
    }

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.issues: List[str] = []
        self.suggestions: List[str] = []

    def log(self, message: str):
        """输出日志"""
        if self.verbose:
            print(f"[SkillEvaluator] {message}")

    def evaluate_skill(self, skill_path: str) -> EvaluationResult:
        """评测单个技能包"""
        start_time = time.time()
        skill_path = Path(skill_path).resolve()
        skill_name = skill_path.name

        self.log(f"开始评测技能包: {skill_name}")
        self.issues = []
        self.suggestions = []

        result = EvaluationResult(
            skill_name=skill_name,
            skill_path=str(skill_path)
        )

        # 1. 代码质量评估
        self.log("评估代码质量...")
        result.code_quality_score, result.code_quality_details = self._evaluate_code_quality(skill_path)

        # 2. 测试覆盖率评估
        self.log("评估测试覆盖率...")
        result.test_coverage_score, result.test_coverage_details = self._evaluate_test_coverage(skill_path)

        # 3. 文档完整性评估
        self.log("评估文档完整性...")
        result.documentation_score, result.documentation_details = self._evaluate_documentation(skill_path)

        # 4. 依赖安全性评估
        self.log("评估依赖安全性...")
        result.security_score, result.security_details = self._evaluate_security(skill_path)

        # 5. 性能基准评估
        self.log("评估性能基准...")
        result.performance_score, result.performance_details = self._evaluate_performance(skill_path)

        # 计算综合得分
        result.overall_score = self._calculate_overall_score(result)
        result.grade = Grade.from_score(result.overall_score).value
        result.issues = self.issues.copy()
        result.suggestions = self.suggestions.copy()
        result.duration_ms = int((time.time() - start_time) * 1000)

        self.log(f"评测完成: {skill_name} - {result.overall_score:.1f}/100 ({result.grade})")

        return result

    def evaluate_all_skills(self, skills_dir: str) -> Dict[str, EvaluationResult]:
        """批量评测所有技能包"""
        skills_dir = Path(skills_dir).resolve()
        results = {}

        self.log(f"扫描技能包目录: {skills_dir}")

        # 查找所有可能的技能包目录
        for item in skills_dir.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                # 检查是否是技能包（包含Python文件或SKILL.md）
                if self._is_skill_package(item):
                    result = self.evaluate_skill(str(item))
                    results[item.name] = result

        return results

    def _is_skill_package(self, path: Path) -> bool:
        """检查是否是技能包目录"""
        has_python = any(path.glob("*.py"))
        has_skill_md = (path / "SKILL.md").exists()
        has_readme = (path / "README.md").exists()
        return has_python or has_skill_md or has_readme

    def _evaluate_code_quality(self, skill_path: Path) -> Tuple[float, Dict[str, Any]]:
        """评估代码质量"""
        details = {
            "total_files": 0,
            "total_lines": 0,
            "avg_complexity": 0.0,
            "lint_issues": 0,
            "style_issues": []
        }

        python_files = list(skill_path.rglob("*.py"))
        python_files = [f for f in python_files if "test_" not in f.name and "__pycache__" not in str(f)]

        if not python_files:
            self.issues.append("未找到Python源代码文件")
            self.suggestions.append("添加核心功能Python模块")
            return 0.0, details

        details["total_files"] = len(python_files)

        total_lines = 0
        total_complexity = 0
        style_issues = []

        for py_file in python_files:
            try:
                content = py_file.read_text(encoding="utf-8")
                lines = content.split("\n")
                total_lines += len(lines)

                # 计算圈复杂度（简化版）
                complexity = self._calculate_complexity(content)
                total_complexity += complexity

                # 检查代码风格问题
                issues = self._check_style_issues(content, py_file.name)
                style_issues.extend(issues)

            except Exception as e:
                self.log(f"分析文件失败 {py_file}: {e}")

        details["total_lines"] = total_lines
        details["avg_complexity"] = total_complexity / len(python_files) if python_files else 0
        details["style_issues"] = style_issues[:10]  # 只保留前10个问题
        details["lint_issues"] = len(style_issues)

        # 计算得分
        score = 100.0

        # 根据代码行数扣分（文件太小可能功能不完整）
        if total_lines < 50:
            score -= 10
            self.suggestions.append("代码量较少，建议增加更多功能")

        # 根据复杂度扣分
        if details["avg_complexity"] > 15:
            score -= 15
            self.issues.append(f"平均圈复杂度过高: {details['avg_complexity']:.1f}")
            self.suggestions.append("重构复杂函数，降低圈复杂度")
        elif details["avg_complexity"] > 10:
            score -= 8
            self.suggestions.append("部分函数复杂度偏高，建议优化")

        # 根据风格问题扣分
        lint_penalty = min(len(style_issues) * 2, 20)
        score -= lint_penalty

        if style_issues:
            self.suggestions.append(f"修复 {len(style_issues)} 个代码风格问题")

        return max(0, score), details

    def _calculate_complexity(self, content: str) -> int:
        """计算代码圈复杂度（简化版）"""
        complexity = 1  # 基础复杂度

        # 计算分支语句
        patterns = [
            r"\bif\b", r"\belif\b", r"\belse\b",
            r"\bfor\b", r"\bwhile\b",
            r"\bexcept\b", r"\bfinally\b",
            r"\bwith\b",
            r"\band\b", r"\bor\b",
            r"\blambda\b",
            r"\bcomprehension\b"
        ]

        for pattern in patterns:
            complexity += len(re.findall(pattern, content))

        return complexity

    def _check_style_issues(self, content: str, filename: str) -> List[str]:
        """检查代码风格问题"""
        issues = []
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # 检查行长度
            if len(line) > 120:
                issues.append(f"{filename}:{i}: 行长度超过120字符")

            # 检查尾随空格
            if line.rstrip() != line:
                issues.append(f"{filename}:{i}: 存在尾随空格")

            # 检查未使用的导入（简化检查）
            if line.strip().startswith("import ") or line.strip().startswith("from "):
                import_name = line.strip().split()[1].split(".")[0]
                if import_name not in ["sys", "os", "json", "time"]:
                    # 检查是否在代码中使用
                    usage_count = content.count(import_name) - 1  # 减去导入本身
                    if usage_count == 0:
                        issues.append(f"{filename}:{i}: 可能的未使用导入 '{import_name}'")

        # 检查函数文档字符串
        if "def " in content and '"""' not in content and "'''" not in content:
            issues.append(f"{filename}: 缺少模块/函数文档字符串")

        return issues

    def _evaluate_test_coverage(self, skill_path: Path) -> Tuple[float, Dict[str, Any]]:
        """评估测试覆盖率"""
        details = {
            "has_tests": False,
            "test_files": 0,
            "test_count": 0,
            "coverage_percent": 0.0,
            "tests_passed": 0,
            "tests_failed": 0
        }

        # 查找测试目录和文件
        test_dirs = [skill_path / "tests", skill_path / "test"]
        test_files = []

        for test_dir in test_dirs:
            if test_dir.exists():
                test_files.extend(list(test_dir.rglob("test_*.py")))
                test_files.extend(list(test_dir.rglob("*_test.py")))

        # 也检查根目录下的测试文件
        test_files.extend(list(skill_path.glob("test_*.py")))
        test_files.extend(list(skill_path.glob("*_test.py")))

        if not test_files:
            self.issues.append("未找到测试文件")
            self.suggestions.append("添加单元测试，建议测试覆盖率至少达到70%")
            return 0.0, details

        details["has_tests"] = True
        details["test_files"] = len(test_files)

        # 统计测试函数数量
        total_tests = 0
        for test_file in test_files:
            try:
                content = test_file.read_text(encoding="utf-8")
                # 简单统计 def test_ 开头的函数
                total_tests += len(re.findall(r"def test_", content))
            except Exception:
                pass

        details["test_count"] = total_tests

        # 尝试运行测试
        try:
            # 检测可用的 Python 命令
            python_cmd = "python3" if subprocess.run(
                ["which", "python3"], capture_output=True
            ).returncode == 0 else "python"

            # 在技能包目录下运行测试，并添加PYTHONPATH
            env = os.environ.copy()
            env["PYTHONPATH"] = str(skill_path) + ":" + env.get("PYTHONPATH", "")

            # 排除性能测试文件（避免超时）
            result = subprocess.run(
                [python_cmd, "-m", "pytest", "tests/", "-v", "--tb=no", "-q",
                 "--ignore=tests/test_performance.py", "--ignore=tests/performance"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(skill_path),
                env=env
            )

            output = result.stdout + result.stderr

            # 解析测试结果
            passed_match = re.search(r"(\d+) passed", output)
            failed_match = re.search(r"(\d+) failed", output)
            error_match = re.search(r"(\d+) error", output)

            details["tests_passed"] = int(passed_match.group(1)) if passed_match else 0
            details["tests_failed"] = int(failed_match.group(1)) if failed_match else 0
            details["tests_failed"] += int(error_match.group(1)) if error_match else 0

        except Exception as e:
            self.log(f"运行测试失败: {e}")
            details["tests_passed"] = 0
            details["tests_failed"] = total_tests

        # 计算覆盖率得分
        if total_tests == 0:
            return 0.0, details

        # 基于测试数量和通过率的得分
        test_score = min(total_tests * 5, 50)  # 最多50分基于测试数量
        pass_rate = (
            details["tests_passed"] / (details["tests_passed"] + details["tests_failed"])
            if (details["tests_passed"] + details["tests_failed"]) > 0 else 0
        )
        pass_score = pass_rate * 50  # 通过率占50分

        score = test_score + pass_score

        if details["tests_failed"] > 0:
            self.issues.append(f"有 {details['tests_failed']} 个测试失败")
            self.suggestions.append("修复失败的测试用例")

        if total_tests < 5:
            self.suggestions.append("增加更多测试用例，建议至少5个")

        return min(100, score), details

    def _evaluate_documentation(self, skill_path: Path) -> Tuple[float, Dict[str, Any]]:
        """评估文档完整性"""
        details = {
            "has_readme": False,
            "has_skill_md": False,
            "has_api_docs": False,
            "readme_length": 0,
            "skill_md_length": 0,
            "doc_completeness": 0.0
        }

        score = 0.0

        # 检查 README.md
        readme_path = skill_path / "README.md"
        if readme_path.exists():
            details["has_readme"] = True
            content = readme_path.read_text(encoding="utf-8")
            details["readme_length"] = len(content)
            score += 30

            # 检查README内容完整性
            required_sections = ["##", "###", "功能", "使用", "示例"]
            has_sections = sum(1 for s in required_sections if s in content)
            if has_sections >= 3:
                score += 10
            else:
                self.suggestions.append("README.md 内容可以更完整，建议添加功能介绍和使用示例")
        else:
            self.issues.append("缺少 README.md 文件")
            self.suggestions.append("添加 README.md 文档")

        # 检查 SKILL.md
        skill_md_path = skill_path / "SKILL.md"
        if skill_md_path.exists():
            details["has_skill_md"] = True
            content = skill_md_path.read_text(encoding="utf-8")
            details["skill_md_length"] = len(content)
            score += 30

            # 检查SKILL.md内容
            if "```" in content:  # 包含代码示例
                score += 10
            else:
                self.suggestions.append("SKILL.md 建议添加代码使用示例")
        else:
            self.issues.append("缺少 SKILL.md 文件")
            self.suggestions.append("添加 SKILL.md 文档，描述技能包功能和使用方法")

        # 检查 API 文档
        api_doc_paths = [
            skill_path / "docs" / "api.md",
            skill_path / "API.md",
            skill_path / "docs" / "API.md"
        ]
        for path in api_doc_paths:
            if path.exists():
                details["has_api_docs"] = True
                score += 20
                break

        # 检查代码注释
        python_files = list(skill_path.rglob("*.py"))
        python_files = [f for f in python_files if "test_" not in f.name and "__pycache__" not in str(f)]

        if python_files:
            total_docstrings = 0
            for py_file in python_files:
                try:
                    content = py_file.read_text(encoding="utf-8")
                    if '"""' in content or "'''" in content:
                        total_docstrings += 1
                except Exception:
                    pass

            doc_ratio = total_docstrings / len(python_files) if python_files else 0
            details["doc_completeness"] = doc_ratio * 100
            score += doc_ratio * 20

        if not details["has_readme"] and not details["has_skill_md"]:
            self.issues.append("缺少主要文档文件")

        return min(100, score), details

    def _evaluate_security(self, skill_path: Path) -> Tuple[float, Dict[str, Any]]:
        """评估依赖安全性"""
        details = {
            "has_requirements": False,
            "dependencies": [],
            "vulnerabilities": [],
            "security_issues": []
        }

        score = 100.0

        # 检查 requirements.txt
        req_path = skill_path / "requirements.txt"
        if req_path.exists():
            details["has_requirements"] = True
            content = req_path.read_text(encoding="utf-8")

            # 解析依赖
            deps = []
            for line in content.split("\n"):
                line = line.strip()
                if line and not line.startswith("#"):
                    dep_name = line.split("==")[0].split(">=")[0].split("<")[0].strip()
                    if dep_name:
                        deps.append(dep_name)

            details["dependencies"] = deps

            # 检查已知有问题的依赖（简化版）
            risky_packages = {
                "requests": ["<2.20.0"],
                "urllib3": ["<1.24.0"],
                "django": ["<2.0.0"],
                "flask": ["<1.0.0"],
            }

            for dep in deps:
                dep_lower = dep.lower()
                if dep_lower in risky_packages:
                    details["security_issues"].append(f"依赖 {dep} 可能需要版本检查")
                    score -= 10

        # 检查代码中的安全问题
        python_files = list(skill_path.rglob("*.py"))
        security_patterns = [
            (r"eval\s*\(", "使用 eval() 存在安全风险"),
            (r"exec\s*\(", "使用 exec() 存在安全风险"),
            (r"subprocess\.call.*shell\s*=\s*True", "subprocess 使用 shell=True 存在注入风险"),
            (r"input\s*\(", "使用 input() 可能导致注入问题"),
            (r"password\s*=\s*['\"][^'\"]+['\"]", "硬编码密码"),
            (r"api_key\s*=\s*['\"][^'\"]+['\"]", "硬编码API密钥"),
        ]

        for py_file in python_files:
            if "test_" in py_file.name:
                continue
            try:
                content = py_file.read_text(encoding="utf-8")
                for pattern, message in security_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        issue = f"{py_file.name}: {message}"
                        details["security_issues"].append(issue)
                        score -= 5
            except Exception:
                pass

        if details["security_issues"]:
            self.issues.extend(details["security_issues"][:3])
            self.suggestions.append("修复代码中的安全问题")

        return max(0, score), details

    def _evaluate_performance(self, skill_path: Path) -> Tuple[float, Dict[str, Any]]:
        """评估性能基准"""
        details = {
            "import_time_ms": 0,
            "module_size_kb": 0,
            "has_performance_tests": False
        }

        score = 80.0  # 基础分

        # 计算模块大小
        python_files = list(skill_path.rglob("*.py"))
        total_size = 0
        for py_file in python_files:
            if "__pycache__" not in str(py_file):
                try:
                    total_size += py_file.stat().st_size
                except Exception:
                    pass

        details["module_size_kb"] = total_size / 1024

        # 检查性能测试
        perf_test_files = list(skill_path.rglob("*bench*.py")) + list(skill_path.rglob("*perf*.py"))
        if perf_test_files:
            details["has_performance_tests"] = True
            score += 10
        else:
            self.suggestions.append("考虑添加性能基准测试")

        # 根据模块大小评分
        if details["module_size_kb"] > 500:
            score -= 10
            self.suggestions.append("模块较大，考虑优化代码结构")

        # 尝试测量导入时间
        main_module = None
        for py_file in python_files:
            if py_file.name == "__init__.py":
                continue
            if "test_" not in py_file.name and py_file.stem == skill_path.name:
                main_module = py_file
                break

        if main_module:
            try:
                start = time.time()
                # 尝试导入模块
                spec = __import__("importlib.util").util.spec_from_file_location(
                    main_module.stem, str(main_module)
                )
                if spec and spec.loader:
                    module = __import__("importlib.util").util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                details["import_time_ms"] = int((time.time() - start) * 1000)

                if details["import_time_ms"] > 1000:
                    score -= 10
                    self.suggestions.append("模块导入时间较长，考虑优化初始化逻辑")
            except Exception as e:
                self.log(f"测量导入时间失败: {e}")

        return min(100, score), details

    def _calculate_overall_score(self, result: EvaluationResult) -> float:
        """计算综合得分"""
        score = (
            result.code_quality_score * self.WEIGHTS["code_quality"] +
            result.test_coverage_score * self.WEIGHTS["test_coverage"] +
            result.documentation_score * self.WEIGHTS["documentation"] +
            result.security_score * self.WEIGHTS["security"] +
            result.performance_score * self.WEIGHTS["performance"]
        )
        return round(score, 1)

    def generate_report(self, results: Dict[str, EvaluationResult], output_path: str):
        """生成评测报告"""
        report = {
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "total_skills": len(results),
            "summary": {
                "average_score": 0.0,
                "grade_distribution": {"S": 0, "A": 0, "B": 0, "C": 0, "D": 0},
                "top_skills": [],
                "needs_improvement": []
            },
            "results": {name: r.to_dict() for name, r in results.items()}
        }

        if results:
            scores = [r.overall_score for r in results.values()]
            report["summary"]["average_score"] = round(sum(scores) / len(scores), 1)

            for r in results.values():
                report["summary"]["grade_distribution"][r.grade] += 1

            # 排序获取最佳和待改进
            sorted_results = sorted(results.items(), key=lambda x: x[1].overall_score, reverse=True)
            report["summary"]["top_skills"] = [name for name, _ in sorted_results[:3]]
            report["summary"]["needs_improvement"] = [
                {"name": name, "score": r.overall_score, "grade": r.grade}
                for name, r in sorted_results[-3:] if r.overall_score < 70
            ]

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return report


def main():
    """CLI入口"""
    parser = argparse.ArgumentParser(description="技能包自动评测系统")
    parser.add_argument("--skill", "-s", help="评测指定技能包路径")
    parser.add_argument("--all", "-a", action="store_true", help="批量评测所有技能包")
    parser.add_argument("--dir", "-d", default=".", help="技能包目录（用于--all）")
    parser.add_argument("--report", "-r", help="生成报告文件路径")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    args = parser.parse_args()

    evaluator = SkillEvaluator(verbose=args.verbose)

    if args.skill:
        # 评测单个技能包
        result = evaluator.evaluate_skill(args.skill)

        print(f"\n{'='*60}")
        print(f"技能包评测结果: {result.skill_name}")
        print(f"{'='*60}")
        print(f"综合评分: {result.overall_score}/100")
        print(f"质量等级: {result.grade}")
        print(f"评测耗时: {result.duration_ms}ms")
        print(f"\n各维度得分:")
        print(f"  代码质量:   {result.code_quality_score:.1f}/100")
        print(f"  测试覆盖:   {result.test_coverage_score:.1f}/100")
        print(f"  文档完整:   {result.documentation_score:.1f}/100")
        print(f"  依赖安全:   {result.security_score:.1f}/100")
        print(f"  性能基准:   {result.performance_score:.1f}/100")

        if result.issues:
            print(f"\n发现问题 ({len(result.issues)}):")
            for issue in result.issues[:5]:
                print(f"  ⚠️  {issue}")

        if result.suggestions:
            print(f"\n改进建议 ({len(result.suggestions)}):")
            for suggestion in result.suggestions[:5]:
                print(f"  💡 {suggestion}")

        if args.report:
            evaluator.generate_report({result.skill_name: result}, args.report)
            print(f"\n报告已保存: {args.report}")

    elif args.all:
        # 批量评测
        print(f"扫描技能包目录: {args.dir}")
        results = evaluator.evaluate_all_skills(args.dir)

        print(f"\n{'='*70}")
        print(f"批量评测结果 ({len(results)} 个技能包)")
        print(f"{'='*70}")

        for name, result in sorted(results.items(), key=lambda x: x[1].overall_score, reverse=True):
            status = "✅" if result.grade in ["S", "A"] else "⚠️" if result.grade in ["B"] else "❌"
            print(f"{status} {name:30s} {result.overall_score:5.1f}/100 ({result.grade})")

        if results:
            avg_score = sum(r.overall_score for r in results.values()) / len(results)
            print(f"\n平均评分: {avg_score:.1f}/100")

        if args.report:
            evaluator.generate_report(results, args.report)
            print(f"\n报告已保存: {args.report}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
