"""
认证模块 - 多租户认证与授权
"""

import hashlib
import secrets
import hmac
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class AuthToken:
    """认证令牌"""
    access_token: str
    refresh_token: str
    expires_at: datetime
    token_type: str = "Bearer"
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        return datetime.utcnow() >= self.expires_at


class PasswordHasher:
    """密码哈希器"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """哈希密码"""
        salt = secrets.token_hex(16)
        pwdhash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return f"{salt}${pwdhash.hex()}"
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """验证密码"""
        try:
            salt, stored_hash = hashed.split('$')
            pwdhash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            return hmac.compare_digest(pwdhash.hex(), stored_hash)
        except ValueError:
            return False


class AuthManager:
    """
    认证管理器
    
    处理登录、令牌生成与验证。
    """
    
    def __init__(self, token_expiry_hours: int = 24):
        self.token_expiry_hours = token_expiry_hours
        self._passwords: Dict[str, str] = {}  # user_id -> hashed_password
        self._tokens: Dict[str, AuthToken] = {}  # token -> AuthToken
        self._refresh_tokens: Dict[str, str] = {}  # refresh_token -> user_id
        self._user_tokens: Dict[str, list] = {}  # user_id -> [tokens]
    
    def set_password(self, user_id: str, password: str) -> None:
        """设置用户密码"""
        self._passwords[user_id] = PasswordHasher.hash_password(password)
    
    def verify_user_password(self, user_id: str, password: str) -> bool:
        """验证用户密码"""
        hashed = self._passwords.get(user_id)
        if not hashed:
            return False
        return PasswordHasher.verify_password(password, hashed)
    
    def generate_token(self, user_id: str, tenant_id: str) -> AuthToken:
        """生成认证令牌"""
        access_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)
        
        expires_at = datetime.utcnow() + timedelta(hours=self.token_expiry_hours)
        
        token = AuthToken(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
        )
        
        self._tokens[access_token] = token
        self._refresh_tokens[refresh_token] = user_id
        
        if user_id not in self._user_tokens:
            self._user_tokens[user_id] = []
        self._user_tokens[user_id].append(access_token)
        
        return token
    
    def validate_token(self, access_token: str) -> Optional[Dict[str, str]]:
        """验证访问令牌"""
        token = self._tokens.get(access_token)
        if not token:
            return None
        
        if token.is_expired():
            return None
        
        # 查找用户ID
        user_id = None
        for uid, tokens in self._user_tokens.items():
            if access_token in tokens:
                user_id = uid
                break
        
        if not user_id:
            return None
        
        return {
            "user_id": user_id,
            "access_token": access_token,
        }
    
    def refresh_access_token(self, refresh_token: str) -> Optional[AuthToken]:
        """使用刷新令牌获取新访问令牌"""
        user_id = self._refresh_tokens.get(refresh_token)
        if not user_id:
            return None
        
        # 获取租户ID（简化处理）
        tenant_id = "unknown"
        
        # 生成新令牌
        return self.generate_token(user_id, tenant_id)
    
    def revoke_token(self, access_token: str) -> bool:
        """撤销令牌"""
        if access_token not in self._tokens:
            return False
        
        del self._tokens[access_token]
        
        # 从用户令牌列表中移除
        for user_id, tokens in self._user_tokens.items():
            if access_token in tokens:
                tokens.remove(access_token)
                break
        
        return True
    
    def revoke_all_user_tokens(self, user_id: str) -> int:
        """撤销用户的所有令牌"""
        tokens = self._user_tokens.get(user_id, [])
        count = 0
        
        for token in tokens:
            if token in self._tokens:
                del self._tokens[token]
                count += 1
        
        self._user_tokens[user_id] = []
        return count


class PermissionChecker:
    """权限检查器"""
    
    # 预定义权限集
    PERMISSIONS = {
        # 用户管理
        "user:read": "查看用户",
        "user:write": "创建/修改用户",
        "user:delete": "删除用户",
        
        # 技能管理
        "skill:read": "查看技能",
        "skill:write": "创建/修改技能",
        "skill:delete": "删除技能",
        "skill:publish": "发布技能",
        
        # 工作流管理
        "workflow:read": "查看工作流",
        "workflow:write": "创建/修改工作流",
        "workflow:delete": "删除工作流",
        "workflow:execute": "执行工作流",
        
        # 设置管理
        "setting:read": "查看设置",
        "setting:write": "修改设置",
        
        # 账单管理
        "billing:read": "查看账单",
        "billing:write": "管理账单",
        
        # 租户管理
        "tenant:admin": "租户管理员权限",
    }
    
    @classmethod
    def check(cls, user_permissions: list, required: str) -> bool:
        """检查是否有所需权限"""
        if "tenant:admin" in user_permissions:
            return True
        return required in user_permissions
    
    @classmethod
    def get_role_permissions(cls, role: str) -> list:
        """获取角色的默认权限"""
        role_perms = {
            "owner": list(cls.PERMISSIONS.keys()),
            "admin": [
                "user:read", "user:write",
                "skill:read", "skill:write", "skill:delete", "skill:publish",
                "workflow:read", "workflow:write", "workflow:delete", "workflow:execute",
                "setting:read", "setting:write",
                "billing:read",
            ],
            "member": [
                "user:read",
                "skill:read", "skill:write",
                "workflow:read", "workflow:write", "workflow:execute",
                "setting:read",
            ],
            "viewer": [
                "user:read",
                "skill:read",
                "workflow:read",
            ],
        }
        return role_perms.get(role, [])
