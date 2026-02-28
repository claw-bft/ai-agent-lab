"""
用户模型 - 租户内用户管理
"""

import uuid
import hashlib
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum


class UserRole(Enum):
    """用户角色枚举"""
    OWNER = "owner"           # 租户所有者
    ADMIN = "admin"           # 管理员
    MEMBER = "member"         # 普通成员
    VIEWER = "viewer"         # 只读用户


class UserStatus(Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"


@dataclass
class User:
    """用户数据模型"""
    id: str
    tenant_id: str
    email: str
    username: str
    role: UserRole
    status: UserStatus
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    profile: Dict[str, Any] = field(default_factory=dict)
    permissions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "email": self.email,
            "username": self.username,
            "role": self.role.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "profile": self.profile,
            "permissions": self.permissions,
        }


class UserManager:
    """用户管理器"""
    
    def __init__(self):
        self._users: Dict[str, User] = {}
        self._email_index: Dict[str, str] = {}  # email -> user_id
        self._tenant_users: Dict[str, List[str]] = {}  # tenant_id -> [user_ids]
    
    def _generate_id(self) -> str:
        """生成用户ID"""
        return f"user_{uuid.uuid4().hex[:16]}"
    
    def create_user(
        self,
        tenant_id: str,
        email: str,
        username: str,
        role: UserRole = UserRole.MEMBER,
        profile: Optional[Dict[str, Any]] = None,
    ) -> User:
        """创建用户"""
        email = email.lower().strip()
        
        if email in self._email_index:
            raise ValueError(f"邮箱 {email} 已被使用")
        
        now = datetime.utcnow()
        user = User(
            id=self._generate_id(),
            tenant_id=tenant_id,
            email=email,
            username=username.strip(),
            role=role,
            status=UserStatus.ACTIVE,
            created_at=now,
            updated_at=now,
            profile=profile or {},
        )
        
        self._users[user.id] = user
        self._email_index[email] = user.id
        
        # 添加到租户用户列表
        if tenant_id not in self._tenant_users:
            self._tenant_users[tenant_id] = []
        self._tenant_users[tenant_id].append(user.id)
        
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """获取用户"""
        return self._users.get(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """通过邮箱获取用户"""
        email = email.lower().strip()
        user_id = self._email_index.get(email)
        if user_id:
            return self._users.get(user_id)
        return None
    
    def list_users(
        self,
        tenant_id: str,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
    ) -> List[User]:
        """列出租户内用户"""
        user_ids = self._tenant_users.get(tenant_id, [])
        users = [self._users[uid] for uid in user_ids if uid in self._users]
        
        if role:
            users = [u for u in users if u.role == role]
        if status:
            users = [u for u in users if u.status == status]
        
        return users
    
    def update_user(
        self,
        user_id: str,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
        profile: Optional[Dict[str, Any]] = None,
    ) -> Optional[User]:
        """更新用户"""
        user = self._users.get(user_id)
        if not user:
            return None
        
        if role is not None:
            user.role = role
        if status is not None:
            user.status = status
        if profile is not None:
            user.profile.update(profile)
        
        user.updated_at = datetime.utcnow()
        return user
    
    def delete_user(self, user_id: str) -> bool:
        """删除用户"""
        user = self._users.get(user_id)
        if not user:
            return False
        
        del self._users[user_id]
        del self._email_index[user.email]
        
        if user.tenant_id in self._tenant_users:
            self._tenant_users[user.tenant_id].remove(user_id)
        
        return True
    
    def has_permission(self, user_id: str, permission: str) -> bool:
        """检查用户是否有特定权限"""
        user = self._users.get(user_id)
        if not user:
            return False
        
        # 所有者拥有所有权限
        if user.role == UserRole.OWNER:
            return True
        
        # 管理员拥有大部分权限
        if user.role == UserRole.ADMIN:
            admin_permissions = [
                "user:read", "user:write",
                "skill:read", "skill:write",
                "workflow:read", "workflow:write",
                "setting:read", "setting:write",
            ]
            return permission in admin_permissions or permission in user.permissions
        
        # 普通成员
        if user.role == UserRole.MEMBER:
            member_permissions = [
                "user:read",
                "skill:read", "skill:write",
                "workflow:read", "workflow:write",
                "setting:read",
            ]
            return permission in member_permissions or permission in user.permissions
        
        # 只读用户
        if user.role == UserRole.VIEWER:
            viewer_permissions = ["user:read", "skill:read", "workflow:read"]
            return permission in viewer_permissions or permission in user.permissions
        
        return permission in user.permissions
