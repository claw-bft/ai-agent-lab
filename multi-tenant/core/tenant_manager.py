"""
租户管理器 - 核心管理类

负责租户的CRUD操作、状态管理和生命周期控制。
"""

import uuid
import hashlib
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum


class TenantStatus(Enum):
    """租户状态枚举"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"
    DELETED = "deleted"


class TenantTier(Enum):
    """租户服务等级"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


@dataclass
class Tenant:
    """租户数据模型"""
    id: str
    name: str
    slug: str
    status: TenantStatus
    tier: TenantTier
    owner_id: str
    created_at: datetime
    updated_at: datetime
    settings: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "status": self.status.value,
            "tier": self.tier.value,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "settings": self.settings,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Tenant":
        """从字典创建"""
        return cls(
            id=data["id"],
            name=data["name"],
            slug=data["slug"],
            status=TenantStatus(data["status"]),
            tier=TenantTier(data["tier"]),
            owner_id=data["owner_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            settings=data.get("settings", {}),
            metadata=data.get("metadata", {}),
        )


class TenantManager:
    """
    租户管理器

    负责：
    - 租户创建、查询、更新、删除
    - 租户状态管理
    - 资源配额检查
    """

    def __init__(self, storage_backend: Optional[Any] = None):
        """
        初始化租户管理器

        Args:
            storage_backend: 存储后端，默认使用内存存储（仅用于开发）
        """
        self._storage = storage_backend or {}
        self._tenants: Dict[str, Tenant] = {}
        self._slug_index: Dict[str, str] = {}  # slug -> tenant_id

    def _generate_slug(self, name: str) -> str:
        """从名称生成唯一的slug"""
        base_slug = name.lower().replace(" ", "-").replace("_", "-")
        base_slug = "".join(c for c in base_slug if c.isalnum() or c == "-")

        slug = base_slug
        counter = 1
        while slug in self._slug_index:
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    def _generate_id(self) -> str:
        """生成唯一租户ID"""
        return f"tenant_{uuid.uuid4().hex[:16]}"

    def create_tenant(
        self,
        name: str,
        owner_id: str,
        tier: TenantTier = TenantTier.FREE,
        settings: Optional[Dict[str, Any]] = None,
    ) -> Tenant:
        """
        创建新租户

        Args:
            name: 租户名称
            owner_id: 所有者用户ID
            tier: 服务等级
            settings: 租户设置

        Returns:
            创建的租户对象

        Raises:
            ValueError: 名称无效
        """
        if not name or len(name.strip()) < 2:
            raise ValueError("租户名称至少需要2个字符")

        now = datetime.utcnow()
        tenant = Tenant(
            id=self._generate_id(),
            name=name.strip(),
            slug=self._generate_slug(name),
            status=TenantStatus.ACTIVE,
            tier=tier,
            owner_id=owner_id,
            created_at=now,
            updated_at=now,
            settings=settings or {},
        )

        self._tenants[tenant.id] = tenant
        self._slug_index[tenant.slug] = tenant.id

        return tenant

    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """通过ID获取租户"""
        return self._tenants.get(tenant_id)

    def get_tenant_by_slug(self, slug: str) -> Optional[Tenant]:
        """通过slug获取租户"""
        tenant_id = self._slug_index.get(slug)
        if tenant_id:
            return self._tenants.get(tenant_id)
        return None

    def list_tenants(
        self,
        status: Optional[TenantStatus] = None,
        tier: Optional[TenantTier] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Tenant]:
        """
        列出租户

        Args:
            status: 按状态筛选
            tier: 按等级筛选
            limit: 返回数量限制
            offset: 分页偏移

        Returns:
            租户列表
        """
        tenants = list(self._tenants.values())

        if status:
            tenants = [t for t in tenants if t.status == status]
        if tier:
            tenants = [t for t in tenants if t.tier == tier]

        # 按创建时间倒序
        tenants.sort(key=lambda t: t.created_at, reverse=True)

        return tenants[offset:offset + limit]

    def update_tenant(
        self,
        tenant_id: str,
        name: Optional[str] = None,
        status: Optional[TenantStatus] = None,
        tier: Optional[TenantTier] = None,
        settings: Optional[Dict[str, Any]] = None,
    ) -> Optional[Tenant]:
        """
        更新租户信息

        Args:
            tenant_id: 租户ID
            name: 新名称
            status: 新状态
            tier: 新等级
            settings: 更新的设置（会合并）

        Returns:
            更新后的租户，不存在则返回None
        """
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return None

        if name is not None:
            tenant.name = name.strip()
        if status is not None:
            tenant.status = status
        if tier is not None:
            tenant.tier = tier
        if settings is not None:
            tenant.settings.update(settings)

        tenant.updated_at = datetime.utcnow()
        return tenant

    def delete_tenant(self, tenant_id: str, soft_delete: bool = True) -> bool:
        """
        删除租户

        Args:
            tenant_id: 租户ID
            soft_delete: 是否软删除（默认True）

        Returns:
            是否成功删除
        """
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return False

        if soft_delete:
            tenant.status = TenantStatus.DELETED
            tenant.updated_at = datetime.utcnow()
        else:
            del self._tenants[tenant_id]
            del self._slug_index[tenant.slug]

        return True

    def get_quota_limits(self, tenant_id: str) -> Dict[str, int]:
        """
        获取租户的资源配额限制

        Args:
            tenant_id: 租户ID

        Returns:
            资源配额字典
        """
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return {}

        # 各等级的默认配额
        quotas = {
            TenantTier.FREE: {
                "max_users": 3,
                "max_skills": 5,
                "max_workflows": 10,
                "api_calls_per_day": 1000,
                "storage_mb": 100,
            },
            TenantTier.STARTER: {
                "max_users": 10,
                "max_skills": 20,
                "max_workflows": 50,
                "api_calls_per_day": 10000,
                "storage_mb": 1000,
            },
            TenantTier.PROFESSIONAL: {
                "max_users": 50,
                "max_skills": 100,
                "max_workflows": 500,
                "api_calls_per_day": 100000,
                "storage_mb": 10000,
            },
            TenantTier.ENTERPRISE: {
                "max_users": -1,  # 无限制
                "max_skills": -1,
                "max_workflows": -1,
                "api_calls_per_day": -1,
                "storage_mb": -1,
            },
        }

        return quotas.get(tenant.tier, quotas[TenantTier.FREE])
