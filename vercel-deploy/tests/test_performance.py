"""
性能基准测试 - Vercel Deploy
"""

import time
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vercel_deploy import VercelClient, VercelDeploy, DeploymentInfo, EnvironmentVariable


class TestVercelDeployPerformance(unittest.TestCase):
    """性能基准测试"""

    def setUp(self):
        """测试准备"""
        with patch.dict(os.environ, {'VERCEL_TOKEN': 'test_token'}):
            self.client = VercelClient()
            self.deployer = VercelDeploy()

    def test_deployment_info_creation_performance(self):
        """测试DeploymentInfo对象创建性能"""
        iterations = 1000
        data = {
            'id': 'dpl_123456',
            'url': 'https://test.vercel.app',
            'state': 'READY',
            'createdAt': '2026-03-01T00:00:00Z',
            'target': 'production'
        }
        
        start_time = time.time()
        
        for _ in range(iterations):
            info = DeploymentInfo.from_api_response(data, "test-project")
        
        elapsed = time.time() - start_time
        avg_time = elapsed / iterations * 1000  # ms
        
        # 断言: 平均时间应小于0.1ms
        self.assertLess(avg_time, 0.1,
                       f"DeploymentInfo创建平均耗时 {avg_time:.4f}ms，超过0.1ms阈值")
        print(f"✓ DeploymentInfo创建平均耗时: {avg_time:.4f}ms ({iterations}次)")

    def test_env_var_creation_performance(self):
        """测试环境变量对象创建性能"""
        iterations = 2000
        
        start_time = time.time()
        
        for i in range(iterations):
            env_var = EnvironmentVariable(
                key=f"VAR_{i}",
                value=f"value_{i}",
                environment="production"
            )
        
        elapsed = time.time() - start_time
        avg_time = elapsed / iterations * 1000  # ms
        
        # 断言: 平均时间应小于0.05ms
        self.assertLess(avg_time, 0.05,
                       f"EnvironmentVariable创建平均耗时 {avg_time:.4f}ms，超过0.05ms阈值")
        print(f"✓ EnvironmentVariable创建平均耗时: {avg_time:.4f}ms ({iterations}次)")

    def test_api_payload_conversion_performance(self):
        """测试API载荷转换性能"""
        iterations = 1000
        env_var = EnvironmentVariable(
            key="API_KEY",
            value="secret_value_12345",
            environment="production"
        )
        
        start_time = time.time()
        
        for _ in range(iterations):
            payload = env_var.to_api_payload()
        
        elapsed = time.time() - start_time
        avg_time = elapsed / iterations * 1000  # ms
        
        # 断言: 平均时间应小于0.05ms
        self.assertLess(avg_time, 0.05,
                       f"API载荷转换平均耗时 {avg_time:.4f}ms，超过0.05ms阈值")
        print(f"✓ API载荷转换平均耗时: {avg_time:.4f}ms ({iterations}次)")

    def test_status_check_performance(self):
        """测试状态检查性能（模拟）"""
        iterations = 100
        
        mock_response = {
            'deployments': [{
                'id': 'dpl_latest',
                'url': 'https://demo.vercel.app',
                'state': 'READY',
                'createdAt': '2026-03-01T00:00:00Z',
                'target': 'production'
            }]
        }
        
        with patch.object(self.client, '_make_request', return_value=mock_response):
            with patch.object(self.deployer, 'client', self.client):
                start_time = time.time()
                
                for _ in range(iterations):
                    try:
                        status = self.deployer.get_status("demo-project")
                    except:
                        pass
                
                elapsed = time.time() - start_time
                avg_time = elapsed / iterations * 1000  # ms
                
                # 断言: 平均时间应小于5ms（模拟情况下）
                self.assertLess(avg_time, 5.0,
                               f"状态检查平均耗时 {avg_time:.2f}ms，超过5ms阈值")
                print(f"✓ 状态检查平均耗时: {avg_time:.2f}ms ({iterations}次)")

    def test_memory_usage(self):
        """测试内存使用"""
        import tracemalloc
        
        tracemalloc.start()
        
        # 创建大量对象
        deployments = []
        for i in range(1000):
            deployments.append(DeploymentInfo(
                id=f'dpl_{i}',
                url=f'https://project{i}.vercel.app',
                state='READY',
                created_at='2026-03-01T00:00:00Z',
                environment='production',
                project=f'project-{i}'
            ))
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # 断言: 峰值内存应小于5MB
        self.assertLess(peak / 1024 / 1024, 5.0,
                       f"峰值内存使用 {peak / 1024 / 1024:.2f}MB，超过5MB阈值")
        print(f"✓ 内存使用: 当前 {current / 1024:.2f}KB, 峰值 {peak / 1024:.2f}KB")


class TestBenchmarkSuite(unittest.TestCase):
    """基准测试套件"""

    @classmethod
    def setUpClass(cls):
        """类级别的准备"""
        print("\n" + "="*60)
        print("Vercel Deploy 性能基准测试")
        print("="*60)

    @classmethod
    def tearDownClass(cls):
        """类级别的清理"""
        print("\n" + "="*60)
        print("性能基准测试完成")
        print("="*60)


if __name__ == '__main__':
    unittest.main(verbosity=2)
