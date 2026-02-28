"""
性能基准测试 - ClawHub Web
"""

import time
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clawhub_web import ClawHubWeb, ClawHubAPI, SkillPackage


class TestClawHubPerformance(unittest.TestCase):
    """性能基准测试"""

    def setUp(self):
        """测试准备"""
        self.hub = ClawHubWeb()

    def test_skill_search_performance(self):
        """测试技能搜索性能"""
        iterations = 100
        start_time = time.time()
        
        for _ in range(iterations):
            results = self.hub.search_skills("finance")
        
        elapsed = time.time() - start_time
        avg_time = elapsed / iterations * 1000  # ms
        
        # 断言: 平均搜索时间应小于10ms
        self.assertLess(avg_time, 10.0, 
                       f"搜索平均耗时 {avg_time:.2f}ms，超过10ms阈值")
        print(f"✓ 技能搜索平均耗时: {avg_time:.2f}ms ({iterations}次)")

    def test_skill_list_performance(self):
        """测试技能列表获取性能"""
        iterations = 50
        start_time = time.time()
        
        for _ in range(iterations):
            skills = self.hub.api.list_skills()
        
        elapsed = time.time() - start_time
        avg_time = elapsed / iterations * 1000  # ms
        
        # 断言: 平均列表获取时间应小于5ms
        self.assertLess(avg_time, 5.0,
                       f"列表获取平均耗时 {avg_time:.2f}ms，超过5ms阈值")
        print(f"✓ 技能列表获取平均耗时: {avg_time:.2f}ms ({iterations}次)")

    def test_top_skills_performance(self):
        """测试热门技能获取性能"""
        iterations = 100
        start_time = time.time()
        
        for _ in range(iterations):
            top_skills = self.hub.get_top_skills(5)
        
        elapsed = time.time() - start_time
        avg_time = elapsed / iterations * 1000  # ms
        
        # 断言: 平均时间应小于5ms
        self.assertLess(avg_time, 5.0,
                       f"热门技能获取平均耗时 {avg_time:.2f}ms，超过5ms阈值")
        print(f"✓ 热门技能获取平均耗时: {avg_time:.2f}ms ({iterations}次)")

    def test_generate_readme_performance(self):
        """测试README生成性能"""
        iterations = 200
        start_time = time.time()
        
        for _ in range(iterations):
            readme = self.hub.generate_readme("coding-pro")
        
        elapsed = time.time() - start_time
        avg_time = elapsed / iterations * 1000  # ms
        
        # 断言: 平均时间应小于2ms
        self.assertLess(avg_time, 2.0,
                       f"README生成平均耗时 {avg_time:.2f}ms，超过2ms阈值")
        print(f"✓ README生成平均耗时: {avg_time:.2f}ms ({iterations}次)")

    def test_skill_package_creation_performance(self):
        """测试SkillPackage对象创建性能"""
        iterations = 1000
        data = {
            'name': 'test-skill',
            'display_name': 'Test Skill',
            'description': 'A test skill package',
            'category': 'test',
            'tags': ['test', 'demo'],
            'rating': 4.5,
            'downloads': 1000,
            'install_command': 'claw install test-skill'
        }
        
        start_time = time.time()
        
        for _ in range(iterations):
            skill = SkillPackage.from_dict(data)
        
        elapsed = time.time() - start_time
        avg_time = elapsed / iterations * 1000  # ms
        
        # 断言: 平均时间应小于0.1ms
        self.assertLess(avg_time, 0.1,
                       f"SkillPackage创建平均耗时 {avg_time:.4f}ms，超过0.1ms阈值")
        print(f"✓ SkillPackage创建平均耗时: {avg_time:.4f}ms ({iterations}次)")

    def test_memory_usage(self):
        """测试内存使用"""
        import tracemalloc
        
        tracemalloc.start()
        
        # 创建大量对象
        skills = []
        for i in range(1000):
            skills.append(SkillPackage(
                name=f"skill-{i}",
                display_name=f"Skill {i}",
                description=f"Description for skill {i}",
                category="test",
                tags=["test", "demo"],
                rating=4.0,
                downloads=i * 100
            ))
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # 断言: 峰值内存应小于10MB
        self.assertLess(peak / 1024 / 1024, 10.0,
                       f"峰值内存使用 {peak / 1024 / 1024:.2f}MB，超过10MB阈值")
        print(f"✓ 内存使用: 当前 {current / 1024:.2f}KB, 峰值 {peak / 1024:.2f}KB")


class TestBenchmarkSuite(unittest.TestCase):
    """基准测试套件"""

    @classmethod
    def setUpClass(cls):
        """类级别的准备"""
        print("\n" + "="*60)
        print("ClawHub Web 性能基准测试")
        print("="*60)

    @classmethod
    def tearDownClass(cls):
        """类级别的清理"""
        print("\n" + "="*60)
        print("性能基准测试完成")
        print("="*60)


if __name__ == '__main__':
    unittest.main(verbosity=2)
