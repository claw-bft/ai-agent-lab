"""
Vercel Deploy - Python API
Vercel项目部署和管理工具，提供Python接口调用Vercel API。
"""

import os
import json
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, asdict
from enum import Enum


class DeploymentEnvironment(Enum):
    """部署环境"""
    PRODUCTION = "production"
    PREVIEW = "preview"
    DEVELOPMENT = "development"


@dataclass
class DeploymentInfo:
    """部署信息"""
    id: str
    url: str
    state: str
    created_at: str
    environment: str
    project: str

    @classmethod
    def from_api_response(cls, data: Dict[str, Any], project: str) -> "DeploymentInfo":
        """从API响应创建对象"""
        return cls(
            id=data.get('id', ''),
            url=data.get('url', ''),
            state=data.get('state', 'unknown'),
            created_at=data.get('createdAt', ''),
            environment=data.get('target', 'preview'),
            project=project
        )


@dataclass
class EnvironmentVariable:
    """环境变量"""
    key: str
    value: str
    environment: str = "production"  # production, preview, development

    def to_api_payload(self) -> Dict[str, Any]:
        """转换为API请求体"""
        return {
            "key": self.key,
            "value": self.value,
            "target": [self.environment] if isinstance(self.environment, str) else self.environment
        }


class VercelClient:
    """Vercel API客户端"""

    API_BASE = "https://api.vercel.com"
    API_VERSION = "v13"

    def __init__(self, token: Optional[str] = None):
        """
        初始化Vercel客户端

        Args:
            token: Vercel API Token，默认从环境变量读取
        """
        self.token = token or os.environ.get("VERCEL_TOKEN")
        if not self.token:
            raise ValueError("必须提供Vercel API Token，可通过参数或环境变量VERCEL_TOKEN设置")

    def _make_request(self, method: str, endpoint: str,
                     data: Optional[Dict] = None,
                     params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        发起API请求

        Args:
            method: HTTP方法
            endpoint: API端点(不含base URL)
            data: 请求体数据
            params: URL参数

        Returns:
            API响应数据
        """
        url = f"{self.API_BASE}/{endpoint}"
        if params:
            query_string = &quot;&quot;.join([f"{k}={v}" for k, v in params.items()])
            url = f"{url}?{query_string}"

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        req_data = json.dumps(data).encode('utf-8') if data else None
        req = urllib.request.Request(
            url,
            data=req_data,
            headers=headers,
            method=method
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise VercelAPIError(f"API错误 {e.code}: {error_body}")
        except Exception as e:
            raise VercelAPIError(f"请求失败: {e}")

    # ========== 项目管理 ==========

    def list_projects(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取项目列表"""
        result = self._make_request("GET", f"{self.API_VERSION}/projects", params={"limit": limit})
        return result.get('projects', [])

    def get_project(self, project_name: str) -> Dict[str, Any]:
        """获取项目详情"""
        return self._make_request("GET", f"{self.API_VERSION}/projects/{project_name}")

    # ========== 部署管理 ==========

    def list_deployments(self, project_name: str, limit: int = 10) -> List[DeploymentInfo]:
        """
        获取部署列表

        Args:
            project_name: 项目名称
            limit: 返回数量限制

        Returns:
            部署信息列表
        """
        result = self._make_request(
            "GET",
            f"{self.API_VERSION}/projects/{project_name}/deployments",
            params={"limit": limit}
        )

        deployments = result.get('deployments', [])
        return [DeploymentInfo.from_api_response(d, project_name) for d in deployments]

    def get_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """获取部署详情"""
        return self._make_request("GET", f"{self.API_VERSION}/deployments/{deployment_id}")

    def deploy_project(self, project_name: str,
                      environment: DeploymentEnvironment = DeploymentEnvironment.PREVIEW) -> DeploymentInfo:
        """
        部署项目

        Args:
            project_name: 项目名称
            environment: 部署环境

        Returns:
            部署信息
        """
        # 注意：实际部署需要git提交触发或使用不同API
        # 这里返回最新部署信息作为示例
        deployments = self.list_deployments(project_name, limit=1)
        if deployments:
            return deployments[0]
        raise VercelAPIError(f"项目 {project_name} 没有部署记录")

    def get_deployment_logs(self, deployment_id: str,
                           limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取部署日志

        Args:
            deployment_id: 部署ID
            limit: 日志条数限制

        Returns:
            日志列表
        """
        result = self._make_request(
            "GET",
            f"{self.API_VERSION}/deployments/{deployment_id}/events",
            params={"limit": limit}
        )
        return result.get('events', [])

    # ========== 环境变量管理 ==========

    def list_env_vars(self, project_name: str) -> List[Dict[str, Any]]:
        """获取项目环境变量列表"""
        result = self._make_request(
            "GET",
            f"{self.API_VERSION}/projects/{project_name}/env"
        )
        return result.get('envs', [])

    def set_env_var(self, project_name: str, env_var: EnvironmentVariable) -> bool:
        """
        设置环境变量

        Args:
            project_name: 项目名称
            env_var: 环境变量对象

        Returns:
            是否设置成功
        """
        try:
            self._make_request(
                "POST",
                f"{self.API_VERSION}/projects/{project_name}/env",
                data=env_var.to_api_payload()
            )
            return True
        except VercelAPIError:
            return False

    def delete_env_var(self, project_name: str, key: str) -> bool:
        """
        删除环境变量

        Args:
            project_name: 项目名称
            key: 变量名

        Returns:
            是否删除成功
        """
        try:
            self._make_request(
                "DELETE",
                f"{self.API_VERSION}/projects/{project_name}/env/{key}"
            )
            return True
        except VercelAPIError:
            return False


class VercelAPIError(Exception):
    """Vercel API错误"""
    pass


class VercelDeploy:
    """Vercel部署工具类 - 简化常用操作"""

    def __init__(self, token: Optional[str] = None):
        """
        初始化部署工具

        Args:
            token: Vercel API Token
        """
        self.client = VercelClient(token)

    def deploy(self, project_name: str, production: bool = False) -> str:
        """
        部署项目

        Args:
            project_name: 项目名称
            production: 是否部署到生产环境

        Returns:
            部署URL
        """
        env = DeploymentEnvironment.PRODUCTION if production else DeploymentEnvironment.PREVIEW
        deployment = self.client.deploy_project(project_name, env)
        return deployment.url

    def get_status(self, project_name: str) -> Dict[str, Any]:
        """
        获取项目部署状态

        Args:
            project_name: 项目名称

        Returns:
            状态信息
        """
        deployments = self.client.list_deployments(project_name, limit=1)
        if not deployments:
            return {"status": "no_deployments", "message": "没有部署记录"}

        latest = deployments[0]
        return {
            "status": latest.state,
            "url": latest.url,
            "created_at": latest.created_at,
            "environment": latest.environment
        }

    def set_env(self, project_name: str, key: str, value: str,
                environment: str = "production") -> bool:
        """
        设置环境变量

        Args:
            project_name: 项目名称
            key: 变量名
            value: 变量值
            environment: 环境 (production/preview/development)

        Returns:
            是否设置成功
        """
        env_var = EnvironmentVariable(key=key, value=value, environment=environment)
        return self.client.set_env_var(project_name, env_var)

    def get_logs(self, deployment_id: str, limit: int = 50) -> List[str]:
        """
        获取部署日志

        Args:
            deployment_id: 部署ID
            limit: 日志条数

        Returns:
            日志文本列表
        """
        events = self.client.get_deployment_logs(deployment_id, limit)
        return [f"[{e.get('createdAt', '')}] {e.get('text', '')}" for e in events]


def quick_deploy(project_name: str, token: Optional[str] = None) -> str:
    """
    快速部署项目

    Args:
        project_name: 项目名称
        token: Vercel API Token

    Returns:
        部署URL
    """
    deployer = VercelDeploy(token)
    return deployer.deploy(project_name)


def quick_status(project_name: str, token: Optional[str] = None) -> Dict[str, Any]:
    """
    快速获取部署状态

    Args:
        project_name: 项目名称
        token: Vercel API Token

    Returns:
        状态信息
    """
    deployer = VercelDeploy(token)
    return deployer.get_status(project_name)


if __name__ == "__main__":
    # 简单测试
    import sys

    if len(sys.argv) < 2:
        print("用法: python vercel_deploy.py <project_name> [status|deploy]")
        sys.exit(1)

    project = sys.argv[1]
    action = sys.argv[2] if len(sys.argv) > 2 else "status"

    try:
        deployer = VercelDeploy()

        if action == "status":
            status = deployer.get_status(project)
            print(f"项目 {project} 状态:")
            print(json.dumps(status, indent=2, ensure_ascii=False))
        elif action == "deploy":
            url = deployer.deploy(project)
            print(f"部署完成: {url}")
        else:
            print(f"未知操作: {action}")

    except Exception as e:
        print(f"错误: {e}")
