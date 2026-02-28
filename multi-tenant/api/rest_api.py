"""
多租户系统 REST API 接口

提供租户管理、用户管理、认证授权的 HTTP API。
"""

from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class APIResponse:
    """API 响应结构"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {"success": self.success}
        if self.data is not None:
            result["data"] = self.data
        if self.error is not None:
            result["error"] = self.error
        if self.meta is not None:
            result["meta"] = self.meta
        return result


class TenantAPI:
    """
    租户管理 API
    
    提供租户 CRUD 操作的 RESTful 接口。
    """
    
    def __init__(self, tenant_manager):
        """
        初始化 API
        
        Args:
            tenant_manager: TenantManager 实例
        """
        self.manager = tenant_manager
    
    def create_tenant(self, request: Dict[str, Any]) -> APIResponse:
        """
        创建租户
        
        POST /api/v1/tenants
        
        Request:
            {
                "name": "Acme Corp",
                "owner_id": "user_123",
                "tier": "starter",
                "settings": {}
            }
        """
        try:
            from core.tenant_manager import TenantTier
            
            name = request.get("name")
            owner_id = request.get("owner_id")
            tier_str = request.get("tier", "free")
            settings = request.get("settings", {})
            
            if not name or not owner_id:
                return APIResponse(success=False, error="name and owner_id are required")
            
            tier = TenantTier(tier_str.lower())
            tenant = self.manager.create_tenant(
                name=name,
                owner_id=owner_id,
                tier=tier,
                settings=settings,
            )
            
            return APIResponse(success=True, data=tenant.to_dict())
        except ValueError as e:
            return APIResponse(success=False, error=str(e))
        except Exception as e:
            return APIResponse(success=False, error=f"Internal error: {str(e)}")
    
    def get_tenant(self, tenant_id: str) -> APIResponse:
        """
        获取租户详情
        
        GET /api/v1/tenants/{tenant_id}
        """
        tenant = self.manager.get_tenant(tenant_id)
        if not tenant:
            return APIResponse(success=False, error="Tenant not found")
        
        return APIResponse(success=True, data=tenant.to_dict())
    
    def list_tenants(self, request: Dict[str, Any]) -> APIResponse:
        """
        列出租户
        
        GET /api/v1/tenants
        
        Query:
            - status: active, suspended, pending, deleted
            - tier: free, starter, professional, enterprise
            - limit: 默认 100
            - offset: 默认 0
        """
        try:
            from core.tenant_manager import TenantStatus, TenantTier
            
            status_str = request.get("status")
            tier_str = request.get("tier")
            limit = int(request.get("limit", 100))
            offset = int(request.get("offset", 0))
            
            status = TenantStatus(status_str) if status_str else None
            tier = TenantTier(tier_str) if tier_str else None
            
            tenants = self.manager.list_tenants(
                status=status,
                tier=tier,
                limit=limit,
                offset=offset,
            )
            
            return APIResponse(
                success=True,
                data=[t.to_dict() for t in tenants],
                meta={"total": len(tenants), "limit": limit, "offset": offset}
            )
        except Exception as e:
            return APIResponse(success=False, error=str(e))
    
    def update_tenant(self, tenant_id: str, request: Dict[str, Any]) -> APIResponse:
        """
        更新租户
        
        PATCH /api/v1/tenants/{tenant_id}
        
        Request:
            {
                "name": "New Name",
                "status": "suspended",
                "tier": "enterprise",
                "settings": {}
            }
        """
        try:
            from core.tenant_manager import TenantStatus, TenantTier
            
            kwargs = {}
            if "name" in request:
                kwargs["name"] = request["name"]
            if "status" in request:
                kwargs["status"] = TenantStatus(request["status"])
            if "tier" in request:
                kwargs["tier"] = TenantTier(request["tier"])
            if "settings" in request:
                kwargs["settings"] = request["settings"]
            
            tenant = self.manager.update_tenant(tenant_id, **kwargs)
            if not tenant:
                return APIResponse(success=False, error="Tenant not found")
            
            return APIResponse(success=True, data=tenant.to_dict())
        except Exception as e:
            return APIResponse(success=False, error=str(e))
    
    def delete_tenant(self, tenant_id: str, soft_delete: bool = True) -> APIResponse:
        """
        删除租户
        
        DELETE /api/v1/tenants/{tenant_id}
        
        Query:
            - hard: 是否硬删除（默认 false）
        """
        result = self.manager.delete_tenant(tenant_id, soft_delete=soft_delete)
        if not result:
            return APIResponse(success=False, error="Tenant not found")
        
        return APIResponse(success=True, data={"deleted": True})
    
    def get_quota(self, tenant_id: str) -> APIResponse:
        """
        获取租户配额
        
        GET /api/v1/tenants/{tenant_id}/quota
        """
        quotas = self.manager.get_quota_limits(tenant_id)
        if not quotas:
            return APIResponse(success=False, error="Tenant not found")
        
        return APIResponse(success=True, data=quotas)


class UserAPI:
    """
    用户管理 API
    
    提供租户内用户管理的 RESTful 接口。
    """
    
    def __init__(self, user_manager):
        """
        初始化 API
        
        Args:
            user_manager: UserManager 实例
        """
        self.manager = user_manager
    
    def create_user(self, tenant_id: str, request: Dict[str, Any]) -> APIResponse:
        """
        创建用户
        
        POST /api/v1/tenants/{tenant_id}/users
        
        Request:
            {
                "email": "user@example.com",
                "username": "username",
                "role": "member",
                "profile": {}
            }
        """
        try:
            from models.user import UserRole
            
            email = request.get("email")
            username = request.get("username")
            role_str = request.get("role", "member")
            profile = request.get("profile", {})
            
            if not email or not username:
                return APIResponse(success=False, error="email and username are required")
            
            role = UserRole(role_str.lower())
            user = self.manager.create_user(
                tenant_id=tenant_id,
                email=email,
                username=username,
                role=role,
                profile=profile,
            )
            
            return APIResponse(success=True, data=user.to_dict())
        except ValueError as e:
            return APIResponse(success=False, error=str(e))
        except Exception as e:
            return APIResponse(success=False, error=str(e))
    
    def list_users(self, tenant_id: str, request: Dict[str, Any]) -> APIResponse:
        """
        列出租户内用户
        
        GET /api/v1/tenants/{tenant_id}/users
        
        Query:
            - role: owner, admin, member, viewer
            - status: active, inactive, pending, suspended
        """
        try:
            from models.user import UserRole, UserStatus
            
            role_str = request.get("role")
            status_str = request.get("status")
            
            role = UserRole(role_str) if role_str else None
            status = UserStatus(status_str) if status_str else None
            
            users = self.manager.list_users(tenant_id, role=role, status=status)
            
            return APIResponse(
                success=True,
                data=[u.to_dict() for u in users],
                meta={"total": len(users)}
            )
        except Exception as e:
            return APIResponse(success=False, error=str(e))
    
    def get_user(self, user_id: str) -> APIResponse:
        """
        获取用户详情
        
        GET /api/v1/users/{user_id}
        """
        user = self.manager.get_user(user_id)
        if not user:
            return APIResponse(success=False, error="User not found")
        
        return APIResponse(success=True, data=user.to_dict())
    
    def update_user(self, user_id: str, request: Dict[str, Any]) -> APIResponse:
        """
        更新用户
        
        PATCH /api/v1/users/{user_id}
        """
        try:
            from models.user import UserRole, UserStatus
            
            kwargs = {}
            if "role" in request:
                kwargs["role"] = UserRole(request["role"])
            if "status" in request:
                kwargs["status"] = UserStatus(request["status"])
            if "profile" in request:
                kwargs["profile"] = request["profile"]
            
            user = self.manager.update_user(user_id, **kwargs)
            if not user:
                return APIResponse(success=False, error="User not found")
            
            return APIResponse(success=True, data=user.to_dict())
        except Exception as e:
            return APIResponse(success=False, error=str(e))
    
    def delete_user(self, user_id: str) -> APIResponse:
        """
        删除用户
        
        DELETE /api/v1/users/{user_id}
        """
        result = self.manager.delete_user(user_id)
        if not result:
            return APIResponse(success=False, error="User not found")
        
        return APIResponse(success=True, data={"deleted": True})
    
    def check_permission(self, user_id: str, permission: str) -> APIResponse:
        """
        检查用户权限
        
        GET /api/v1/users/{user_id}/permissions/{permission}
        """
        has_perm = self.manager.has_permission(user_id, permission)
        return APIResponse(success=True, data={"has_permission": has_perm})


class AuthAPI:
    """
    认证 API
    
    提供登录、令牌管理的 RESTful 接口。
    """
    
    def __init__(self, auth_manager):
        """
        初始化 API
        
        Args:
            auth_manager: AuthManager 实例
        """
        self.manager = auth_manager
    
    def login(self, request: Dict[str, Any]) -> APIResponse:
        """
        用户登录
        
        POST /api/v1/auth/login
        
        Request:
            {
                "user_id": "user_123",
                "password": "password",
                "tenant_id": "tenant_456"
            }
        """
        try:
            user_id = request.get("user_id")
            password = request.get("password")
            tenant_id = request.get("tenant_id")
            
            if not user_id or not password:
                return APIResponse(success=False, error="user_id and password are required")
            
            if not self.manager.verify_user_password(user_id, password):
                return APIResponse(success=False, error="Invalid credentials")
            
            token = self.manager.generate_token(user_id, tenant_id or "unknown")
            
            return APIResponse(success=True, data={
                "access_token": token.access_token,
                "refresh_token": token.refresh_token,
                "token_type": token.token_type,
                "expires_at": token.expires_at.isoformat(),
            })
        except Exception as e:
            return APIResponse(success=False, error=str(e))
    
    def refresh_token(self, request: Dict[str, Any]) -> APIResponse:
        """
        刷新访问令牌
        
        POST /api/v1/auth/refresh
        
        Request:
            {
                "refresh_token": "..."
            }
        """
        try:
            refresh_token = request.get("refresh_token")
            if not refresh_token:
                return APIResponse(success=False, error="refresh_token is required")
            
            new_token = self.manager.refresh_access_token(refresh_token)
            if not new_token:
                return APIResponse(success=False, error="Invalid refresh token")
            
            return APIResponse(success=True, data={
                "access_token": new_token.access_token,
                "refresh_token": new_token.refresh_token,
                "token_type": new_token.token_type,
                "expires_at": new_token.expires_at.isoformat(),
            })
        except Exception as e:
            return APIResponse(success=False, error=str(e))
    
    def logout(self, request: Dict[str, Any]) -> APIResponse:
        """
        用户登出
        
        POST /api/v1/auth/logout
        
        Request:
            {
                "access_token": "..."
            }
        """
        try:
            access_token = request.get("access_token")
            if not access_token:
                return APIResponse(success=False, error="access_token is required")
            
            self.manager.revoke_token(access_token)
            return APIResponse(success=True, data={"logged_out": True})
        except Exception as e:
            return APIResponse(success=False, error=str(e))
    
    def validate_token(self, request: Dict[str, Any]) -> APIResponse:
        """
        验证令牌
        
        POST /api/v1/auth/validate
        
        Request:
            {
                "access_token": "..."
            }
        """
        try:
            access_token = request.get("access_token")
            if not access_token:
                return APIResponse(success=False, error="access_token is required")
            
            user_info = self.manager.validate_token(access_token)
            if not user_info:
                return APIResponse(success=False, error="Invalid or expired token")
            
            return APIResponse(success=True, data=user_info)
        except Exception as e:
            return APIResponse(success=False, error=str(e))


# API 路由注册示例（FastAPI）
"""
from fastapi import FastAPI
from core.tenant_manager import TenantManager
from models.user import UserManager
from auth.auth import AuthManager

app = FastAPI()

# 初始化管理器
tenant_manager = TenantManager()
user_manager = UserManager()
auth_manager = AuthManager()

# 初始化 API
tenant_api = TenantAPI(tenant_manager)
user_api = UserAPI(user_manager)
auth_api = AuthAPI(auth_manager)

# 租户路由
@app.post("/api/v1/tenants")
def create_tenant(request: dict):
    return tenant_api.create_tenant(request).to_dict()

@app.get("/api/v1/tenants")
def list_tenants(status: str = None, tier: str = None, limit: int = 100, offset: int = 0):
    return tenant_api.list_tenants({
        "status": status,
        "tier": tier,
        "limit": limit,
        "offset": offset,
    }).to_dict()

@app.get("/api/v1/tenants/{tenant_id}")
def get_tenant(tenant_id: str):
    return tenant_api.get_tenant(tenant_id).to_dict()

@app.patch("/api/v1/tenants/{tenant_id}")
def update_tenant(tenant_id: str, request: dict):
    return tenant_api.update_tenant(tenant_id, request).to_dict()

@app.delete("/api/v1/tenants/{tenant_id}")
def delete_tenant(tenant_id: str, hard: bool = False):
    return tenant_api.delete_tenant(tenant_id, soft_delete=not hard).to_dict()

@app.get("/api/v1/tenants/{tenant_id}/quota")
def get_quota(tenant_id: str):
    return tenant_api.get_quota(tenant_id).to_dict()

# 用户路由
@app.post("/api/v1/tenants/{tenant_id}/users")
def create_user(tenant_id: str, request: dict):
    return user_api.create_user(tenant_id, request).to_dict()

@app.get("/api/v1/tenants/{tenant_id}/users")
def list_users(tenant_id: str, role: str = None, status: str = None):
    return user_api.list_users(tenant_id, {"role": role, "status": status}).to_dict()

@app.get("/api/v1/users/{user_id}")
def get_user(user_id: str):
    return user_api.get_user(user_id).to_dict()

@app.patch("/api/v1/users/{user_id}")
def update_user(user_id: str, request: dict):
    return user_api.update_user(user_id, request).to_dict()

@app.delete("/api/v1/users/{user_id}")
def delete_user(user_id: str):
    return user_api.delete_user(user_id).to_dict()

# 认证路由
@app.post("/api/v1/auth/login")
def login(request: dict):
    return auth_api.login(request).to_dict()

@app.post("/api/v1/auth/refresh")
def refresh_token(request: dict):
    return auth_api.refresh_token(request).to_dict()

@app.post("/api/v1/auth/logout")
def logout(request: dict):
    return auth_api.logout(request).to_dict()

@app.post("/api/v1/auth/validate")
def validate_token(request: dict):
    return auth_api.validate_token(request).to_dict()
"""
