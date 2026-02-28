"""
资源隔离器 - 多租户数据隔离

确保各租户的数据相互隔离，防止跨租户数据泄露。
"""

import os
import hashlib
from typing import Optional, Dict, Any, List
from pathlib import Path


class ResourceIsolator:
    """
    资源隔离器

    提供：
    - 数据库表名隔离（租户前缀）
    - 文件存储路径隔离
    - 缓存键隔离
    - API限流键隔离
    """

    def __init__(self, base_path: str = "/tmp/ai-agent-lab/tenants"):
        """
        初始化隔离器

        Args:
            base_path: 租户文件存储基础路径
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def get_table_name(self, tenant_id: str, table_name: str) -> str:
        """
        获取带租户隔离的数据库表名

        Args:
            tenant_id: 租户ID
            table_name: 基础表名

        Returns:
            隔离后的表名，格式: tenant_{hash}_{table_name}
        """
        # 使用租户ID的哈希作为前缀，避免表名过长
        tenant_hash = hashlib.sha256(tenant_id.encode()).hexdigest()[:8]
        return f"t_{tenant_hash}_{table_name}"

    def get_schema_name(self, tenant_id: str) -> str:
        """
        获取租户专属schema名（PostgreSQL等支持schema的数据库）

        Args:
            tenant_id: 租户ID

        Returns:
            schema名称
        """
        tenant_hash = hashlib.sha256(tenant_id.encode()).hexdigest()[:12]
        return f"tenant_{tenant_hash}"

    def get_storage_path(self, tenant_id: str, *subpaths: str) -> Path:
        """
        获取租户专属存储路径

        Args:
            tenant_id: 租户ID
            *subpaths: 子路径

        Returns:
            完整路径对象
        """
        tenant_path = self.base_path / tenant_id
        if subpaths:
            tenant_path = tenant_path.joinpath(*subpaths)
        tenant_path.mkdir(parents=True, exist_ok=True)
        return tenant_path

    def get_cache_key(self, tenant_id: str, key: str) -> str:
        """
        获取带租户隔离的缓存键

        Args:
            tenant_id: 租户ID
            key: 原始缓存键

        Returns:
            隔离后的缓存键
        """
        return f"tenant:{tenant_id}:{key}"

    def get_rate_limit_key(self, tenant_id: str, user_id: Optional[str] = None) -> str:
        """
        获取API限流键

        Args:
            tenant_id: 租户ID
            user_id: 用户ID（可选）

        Returns:
            限流键
        """
        if user_id:
            return f"ratelimit:{tenant_id}:{user_id}"
        return f"ratelimit:{tenant_id}"

    def get_log_prefix(self, tenant_id: str) -> str:
        """
        获取日志前缀

        Args:
            tenant_id: 租户ID

        Returns:
            日志前缀字符串
        """
        return f"[Tenant:{tenant_id[:8]}...]"

    def ensure_tenant_directory(self, tenant_id: str) -> Path:
        """
        确保租户目录存在

        Args:
            tenant_id: 租户ID

        Returns:
            租户目录路径
        """
        tenant_dir = self.base_path / tenant_id
        tenant_dir.mkdir(parents=True, exist_ok=True)

        # 创建标准子目录
        (tenant_dir / "uploads").mkdir(exist_ok=True)
        (tenant_dir / "exports").mkdir(exist_ok=True)
        (tenant_dir / "temp").mkdir(exist_ok=True)
        (tenant_dir / "data").mkdir(exist_ok=True)

        return tenant_dir

    def cleanup_tenant_resources(self, tenant_id: str) -> bool:
        """
        清理租户资源（删除时调用）

        Args:
            tenant_id: 租户ID

        Returns:
            是否成功清理
        """
        import shutil

        tenant_dir = self.base_path / tenant_id
        if tenant_dir.exists():
            shutil.rmtree(tenant_dir)
            return True
        return False

    def list_tenant_resources(self, tenant_id: str) -> Dict[str, Any]:
        """
        列出租户资源使用情况

        Args:
            tenant_id: 租户ID

        Returns:
            资源使用统计
        """
        tenant_dir = self.base_path / tenant_id

        if not tenant_dir.exists():
            return {
                "tenant_id": tenant_id,
                "storage_used_bytes": 0,
                "storage_used_mb": 0,
                "file_count": 0,
            }

        total_size = 0
        file_count = 0

        for root, dirs, files in os.walk(tenant_dir):
            for file in files:
                file_path = Path(root) / file
                total_size += file_path.stat().st_size
                file_count += 1

        return {
            "tenant_id": tenant_id,
            "storage_used_bytes": total_size,
            "storage_used_mb": round(total_size / (1024 * 1024), 2),
            "file_count": file_count,
        }


class DatabaseRouter:
    """
    数据库路由（Django风格）

    根据租户ID路由到不同的数据库/schema。
    """

    def __init__(self, default_db: str = "default"):
        self.default_db = default_db
        self._tenant_db_map: Dict[str, str] = {}

    def db_for_read(self, tenant_id: str, model_name: str) -> str:
        """读取操作的数据库"""
        return self._tenant_db_map.get(tenant_id, self.default_db)

    def db_for_write(self, tenant_id: str, model_name: str) -> str:
        """写入操作的数据库"""
        return self._tenant_db_map.get(tenant_id, self.default_db)

    def allow_relation(self, obj1: Any, obj2: Any, **hints) -> bool:
        """是否允许跨表关联"""
        # 默认允许，实际应用中可能需要限制跨租户关联
        return True

    def allow_migrate(
        self,
        tenant_id: str,
        db: str,
        app_label: str,
        model_name: Optional[str] = None,
        **hints
    ) -> bool:
        """是否允许迁移"""
        # 只有默认数据库允许迁移，租户数据库在创建时自动设置
        return db == self.default_db
