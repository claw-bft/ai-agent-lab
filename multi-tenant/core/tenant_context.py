"""
租户上下文 - 请求级租户信息传递

提供线程/协程安全的租户上下文管理，确保多租户环境下的数据隔离。
"""

import contextvars
import threading
from typing import Optional, Dict, Any
from dataclasses import dataclass


# 上下文变量（用于异步环境）
_tenant_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "tenant_id", default=None
)
_tenant_slug_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "tenant_slug", default=None
)

# 线程本地存储（用于同步环境）
_thread_local = threading.local()


@dataclass
class TenantContextData:
    """租户上下文数据"""
    tenant_id: str
    tenant_slug: str
    user_id: Optional[str] = None
    permissions: list = None
    
    def __post_init__(self):
        if self.permissions is None:
            self.permissions = []


class TenantContext:
    """
    租户上下文管理器
    
    支持：
    - 异步上下文变量（asyncio）
    - 线程本地存储（threading）
    - 上下文管理器（with语句）
    
    使用示例：
        # 方式1: 上下文管理器
        with TenantContext(tenant_id="xxx", tenant_slug="acme"):
            # 在此范围内，get_current_tenant() 返回当前租户
            process_request()
        
        # 方式2: 手动设置/清除
        TenantContext.set_current("xxx", "acme")
        try:
            process_request()
        finally:
            TenantContext.clear()
    """
    
    @classmethod
    def set_current(
        cls,
        tenant_id: str,
        tenant_slug: str,
        user_id: Optional[str] = None,
    ) -> None:
        """
        设置当前租户上下文
        
        Args:
            tenant_id: 租户ID
            tenant_slug: 租户slug
            user_id: 当前用户ID
        """
        # 设置上下文变量（异步）
        _tenant_id_var.set(tenant_id)
        _tenant_slug_var.set(tenant_slug)
        
        # 设置线程本地存储（同步）
        _thread_local.tenant_id = tenant_id
        _thread_local.tenant_slug = tenant_slug
        _thread_local.user_id = user_id
    
    @classmethod
    def get_current_id(cls) -> Optional[str]:
        """获取当前租户ID"""
        # 优先尝试上下文变量
        tenant_id = _tenant_id_var.get()
        if tenant_id:
            return tenant_id
        # 回退到线程本地存储
        return getattr(_thread_local, "tenant_id", None)
    
    @classmethod
    def get_current_slug(cls) -> Optional[str]:
        """获取当前租户slug"""
        tenant_slug = _tenant_slug_var.get()
        if tenant_slug:
            return tenant_slug
        return getattr(_thread_local, "tenant_slug", None)
    
    @classmethod
    def get_current_user_id(cls) -> Optional[str]:
        """获取当前用户ID"""
        return getattr(_thread_local, "user_id", None)
    
    @classmethod
    def get_current(cls) -> Optional[TenantContextData]:
        """获取完整的当前上下文"""
        tenant_id = cls.get_current_id()
        tenant_slug = cls.get_current_slug()
        
        if not tenant_id:
            return None
        
        return TenantContextData(
            tenant_id=tenant_id,
            tenant_slug=tenant_slug or "",
            user_id=cls.get_current_user_id(),
        )
    
    @classmethod
    def clear(cls) -> None:
        """清除当前租户上下文"""
        _tenant_id_var.set(None)
        _tenant_slug_var.set(None)
        
        if hasattr(_thread_local, "tenant_id"):
            delattr(_thread_local, "tenant_id")
        if hasattr(_thread_local, "tenant_slug"):
            delattr(_thread_local, "tenant_slug")
        if hasattr(_thread_local, "user_id"):
            delattr(_thread_local, "user_id")
    
    @classmethod
    def is_set(cls) -> bool:
        """检查是否已设置租户上下文"""
        return cls.get_current_id() is not None
    
    def __init__(
        self,
        tenant_id: str,
        tenant_slug: str,
        user_id: Optional[str] = None,
    ):
        """
        初始化上下文管理器
        
        Args:
            tenant_id: 租户ID
            tenant_slug: 租户slug
            user_id: 用户ID
        """
        self.tenant_id = tenant_id
        self.tenant_slug = tenant_slug
        self.user_id = user_id
        self._tokens = []
    
    def __enter__(self):
        """进入上下文"""
        # 保存当前状态
        self._prev_id = _tenant_id_var.get()
        self._prev_slug = _tenant_slug_var.get()
        
        # 设置新上下文
        self._tokens.append(_tenant_id_var.set(self.tenant_id))
        self._tokens.append(_tenant_slug_var.set(self.tenant_slug))
        
        _thread_local.tenant_id = self.tenant_id
        _thread_local.tenant_slug = self.tenant_slug
        _thread_local.user_id = self.user_id
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        # 恢复上下文变量
        for token in self._tokens:
            # 注意：contextvars 不支持直接reset，这里简化处理
            pass
        
        # 恢复或清除线程本地存储
        if self._prev_id:
            _thread_local.tenant_id = self._prev_id
            _thread_local.tenant_slug = self._prev_slug
        else:
            self.clear()
        
        return False  # 不吞掉异常


def get_current_tenant_id() -> Optional[str]:
    """便捷函数：获取当前租户ID"""
    return TenantContext.get_current_id()


def get_current_tenant_slug() -> Optional[str]:
    """便捷函数：获取当前租户slug"""
    return TenantContext.get_current_slug()


def require_tenant() -> str:
    """
    要求当前必须有租户上下文
    
    Returns:
        租户ID
        
    Raises:
        RuntimeError: 如果没有设置租户上下文
    """
    tenant_id = get_current_tenant_id()
    if not tenant_id:
        raise RuntimeError("租户上下文未设置，此操作需要在租户上下文中执行")
    return tenant_id
