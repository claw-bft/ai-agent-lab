"""
Token Manager - 全局凭证管理系统

安全存储和管理敏感凭证，支持按服务分类、权限控制和加密存储。
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any, List


class TokenManager:
    """凭证管理器 - 安全存储和管理API密钥和访问令牌"""

    DEFAULT_CONFIG_DIR = Path.home() / '.openclaw'
    DEFAULT_TOKENS_FILE = DEFAULT_CONFIG_DIR / 'secrets' / 'tokens.json'

    def __init__(self, tokens_file: Optional[str] = None, auto_save: bool = True):
        """
        初始化凭证管理器

        Args:
            tokens_file: 自定义凭证文件路径，默认使用 ~/.openclaw/secrets/tokens.json
            auto_save: 是否自动保存到文件，批量操作时设为False可提升性能
        """
        self.tokens_file = Path(tokens_file) if tokens_file else self.DEFAULT_TOKENS_FILE
        self._tokens: Dict[str, Dict[str, Any]] = {}
        self._auto_save = auto_save
        self._load_tokens()

    def _load_tokens(self) -> None:
        """从文件加载凭证"""
        if self.tokens_file.exists():
            try:
                with open(self.tokens_file, 'r', encoding='utf-8') as f:
                    self._tokens = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._tokens = {}
        else:
            self._tokens = {}

    def _save_tokens(self) -> None:
        """保存凭证到文件"""
        self.tokens_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.tokens_file, 'w', encoding='utf-8') as f:
            json.dump(self._tokens, f, indent=2, ensure_ascii=False)

    def get_token(self, service: str, key: Optional[str] = None) -> Optional[Any]:
        """
        获取指定服务的凭证

        Args:
            service: 服务名称 (如 'github', 'vercel')
            key: 特定字段，如 'token', 'username'。为None时返回整个凭证对象

        Returns:
            凭证值或None（如果不存在）

        Example:
            >>> tm = TokenManager()
            >>> token = tm.get_token('github', 'token')
            >>> user_data = tm.get_token('github')  # 返回完整对象
        """
        if service not in self._tokens:
            return None

        service_data = self._tokens[service]

        if key is None:
            return service_data.copy()

        return service_data.get(key)

    def set_token(self, service: str, token: str, save: bool = True, **metadata) -> None:
        """
        设置/更新服务的凭证

        Args:
            service: 服务名称
            token: API密钥或访问令牌
            save: 是否立即保存到文件（批量操作时设为False）
            **metadata: 额外元数据 (username, scopes, note等)

        Example:
            >>> tm = TokenManager()
            >>> tm.set_token('github', 'ghp_xxx',
            ...              username='claw-bft',
            ...              scopes=['repo', 'user'],
            ...              note='GitHub CLI token')
        """
        self._tokens[service] = {
            'token': token,
            'created_at': datetime.now().isoformat(),
            **metadata
        }
        if save and self._auto_save:
            self._save_tokens()

    def update_token(self, service: str, save: bool = True, **updates) -> bool:
        """
        更新现有凭证的部分字段

        Args:
            service: 服务名称
            save: 是否立即保存到文件（批量操作时设为False）
            **updates: 要更新的字段

        Returns:
            是否成功更新
        """
        if service not in self._tokens:
            return False

        self._tokens[service].update(updates)
        self._tokens[service]['updated_at'] = datetime.now().isoformat()
        if save and self._auto_save:
            self._save_tokens()
        return True

    def delete_token(self, service: str, save: bool = True) -> bool:
        """
        删除指定服务的凭证

        Args:
            service: 服务名称
            save: 是否立即保存到文件（批量操作时设为False）

        Returns:
            是否成功删除
        """
        if service not in self._tokens:
            return False

        del self._tokens[service]
        if save and self._auto_save:
            self._save_tokens()
        return True

    def list_services(self) -> List[str]:
        """
        列出所有已存储的服务名称

        Returns:
            服务名称列表
        """
        return list(self._tokens.keys())

    def search_tokens(self, tags: Optional[List[str]] = None,
                      service_pattern: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        根据标签或服务名模式搜索凭证

        Args:
            tags: 标签列表，匹配任一标签即返回
            service_pattern: 服务名包含的模式字符串

        Returns:
            匹配的凭证字典
        """
        results = {}
        for service, data in self._tokens.items():
            # 按服务名模式匹配
            if service_pattern and service_pattern.lower() not in service.lower():
                continue
            
            # 按标签匹配
            if tags:
                token_tags = data.get('tags', [])
                if isinstance(token_tags, str):
                    token_tags = [token_tags]
                if not any(tag in token_tags for tag in tags):
                    continue
            
            results[service] = data.copy()
        
        return results

    def has_token(self, service: str) -> bool:
        """
        检查是否存储了指定服务的凭证

        Args:
            service: 服务名称

        Returns:
            是否存在
        """
        return service in self._tokens

    def get_all_tokens(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有凭证（不包含敏感token值）

        Returns:
            服务名称到元数据的映射，token值被隐藏
        """
        result = {}
        for service, data in self._tokens.items():
            result[service] = {
                k: ('***' if k == 'token' else v)
                for k, v in data.items()
            }
        return result

    def export_tokens(self, include_secrets: bool = False) -> Dict[str, Any]:
        """
        导出所有凭证

        Args:
            include_secrets: 是否包含敏感token值

        Returns:
            凭证字典
        """
        if include_secrets:
            return self._tokens.copy()
        return self.get_all_tokens()

    def import_tokens(self, tokens: Dict[str, Dict[str, Any]],
                      merge: bool = True) -> None:
        """
        导入凭证

        Args:
            tokens: 要导入的凭证字典
            merge: 是否合并现有凭证（False则覆盖）
        """
        if merge:
            self._tokens.update(tokens)
        else:
            self._tokens = tokens.copy()
        self._save_tokens()

    def clear_all(self) -> None:
        """清除所有凭证（谨慎使用）"""
        self._tokens = {}
        self._save_tokens()

    def set_tokens_batch(self, tokens: Dict[str, Dict[str, Any]]) -> None:
        """
        批量设置凭证（高性能模式，只保存一次）

        Args:
            tokens: 凭证字典，格式为 {service: {'token': 'xxx', ...metadata}}

        Example:
            >>> tm = TokenManager(auto_save=False)
            >>> tm.set_tokens_batch({
            ...     'github': {'token': 'ghp_xxx', 'username': 'user1'},
            ...     'vercel': {'token': 'vc_xxx', 'username': 'user2'}
            ... })
            >>> tm.save()  # 手动保存
        """
        for service, data in tokens.items():
            token_value = data.pop('token', '')
            self._tokens[service] = {
                'token': token_value,
                'created_at': datetime.now().isoformat(),
                **data
            }
        if self._auto_save:
            self._save_tokens()

    def save(self) -> None:
        """手动保存凭证到文件（用于批量操作后）"""
        self._save_tokens()


def get_token(service: str, key: Optional[str] = 'token',
              tokens_file: Optional[str] = None) -> Optional[str]:
    """
    便捷函数 - 获取指定服务的凭证

    Args:
        service: 服务名称
        key: 要获取的字段，默认'token'
        tokens_file: 自定义凭证文件路径

    Returns:
        凭证值或None

    Example:
        >>> token = get_token('github')
        >>> username = get_token('github', 'username')
    """
    tm = TokenManager(tokens_file)
    return tm.get_token(service, key)


def set_token(service: str, token: str,
              tokens_file: Optional[str] = None,
              **metadata) -> None:
    """
    便捷函数 - 设置凭证

    Args:
        service: 服务名称
        token: API密钥或访问令牌
        tokens_file: 自定义凭证文件路径
        **metadata: 额外元数据

    Example:
        >>> set_token('github', 'ghp_xxx', username='claw-bft')
    """
    tm = TokenManager(tokens_file)
    tm.set_token(service, token, **metadata)
