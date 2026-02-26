"""
配置管理核心模块
提供统一的配置读取、写入和管理接口
"""
import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from .security import SecurityManager


class ConfigManager:
    """统一配置管理器"""
    
    def __init__(self, base_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            base_path: 配置目录路径，默认 ~/.openclaw/config
        """
        if base_path:
            self.base_path = Path(base_path)
        else:
            self.base_path = Path.home() / '.openclaw' / 'config'
        
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # 配置文件路径
        self.credentials_file = self.base_path / 'credentials.yaml'
        self.settings_file = self.base_path / 'settings.yaml'
        
        # 安全模块
        self.security = SecurityManager()
        
        # 缓存
        self._credentials_cache: Dict[str, Any] = {}
        self._settings_cache: Dict[str, Any] = {}
        
        # 加载配置
        self._load_all()
    
    def _load_all(self):
        """加载所有配置文件"""
        self._credentials_cache = self._load_yaml(self.credentials_file)
        self._settings_cache = self._load_yaml(self.settings_file)
    
    def _load_yaml(self, filepath: Path) -> Dict[str, Any]:
        """加载 YAML 文件"""
        if not filepath.exists():
            return {}
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"[Config] 加载 {filepath} 失败: {e}")
            return {}
    
    def _save_yaml(self, filepath: Path, data: Dict[str, Any]):
        """保存 YAML 文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    
    def get_credential(self, service: str, key: str) -> Optional[str]:
        """
        获取加密的凭证
        
        Args:
            service: 服务名称 (e.g., 'vercel', 'github')
            key: 凭证键名 (e.g., 'token', 'api_key')
            
        Returns:
            解密后的凭证值，如果不存在返回 None
        """
        encrypted_value = self._credentials_cache.get(service, {}).get(key)
        if encrypted_value:
            return self.security.decrypt(encrypted_value)
        return None
    
    def set_credential(self, service: str, key: str, value: str):
        """
        设置并加密存储凭证
        
        Args:
            service: 服务名称
            key: 凭证键名
            value: 凭证值（明文）
        """
        encrypted_value = self.security.encrypt(value)
        
        if service not in self._credentials_cache:
            self._credentials_cache[service] = {}
        
        self._credentials_cache[service][key] = encrypted_value
        self._save_yaml(self.credentials_file, self._credentials_cache)
    
    def get_setting(self, section: str, key: str, default: Any = None) -> Any:
        """
        获取普通配置项
        
        Args:
            section: 配置分区
            key: 配置键名
            default: 默认值
            
        Returns:
            配置值
        """
        return self._settings_cache.get(section, {}).get(key, default)
    
    def set_setting(self, section: str, key: str, value: Any):
        """
        设置普通配置项
        
        Args:
            section: 配置分区
            key: 配置键名
            value: 配置值
        """
        if section not in self._settings_cache:
            self._settings_cache[section] = {}
        
        self._settings_cache[section][key] = value
        self._save_yaml(self.settings_file, self._settings_cache)
    
    def get_all_credentials(self) -> Dict[str, list]:
        """
        获取所有已配置的服务列表（不包含实际凭证值）
        
        Returns:
            {服务名: [凭证键列表]}
        """
        return {service: list(keys.keys()) 
                for service, keys in self._credentials_cache.items()}
    
    def get_all_settings(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有普通配置
        
        Returns:
            完整的配置字典
        """
        return self._settings_cache.copy()
    
    def delete_credential(self, service: str, key: str) -> bool:
        """
        删除凭证
        
        Args:
            service: 服务名称
            key: 凭证键名
            
        Returns:
            是否成功删除
        """
        if service in self._credentials_cache and key in self._credentials_cache[service]:
            del self._credentials_cache[service][key]
            if not self._credentials_cache[service]:
                del self._credentials_cache[service]
            self._save_yaml(self.credentials_file, self._credentials_cache)
            return True
        return False
    
    def delete_setting(self, section: str, key: str) -> bool:
        """
        删除配置项
        
        Args:
            section: 配置分区
            key: 配置键名
            
        Returns:
            是否成功删除
        """
        if section in self._settings_cache and key in self._settings_cache[section]:
            del self._settings_cache[section][key]
            if not self._settings_cache[section]:
                del self._settings_cache[section]
            self._save_yaml(self.settings_file, self._settings_cache)
            return True
        return False
    
    def validate(self) -> Dict[str, list]:
        """
        验证配置完整性
        
        Returns:
            {'valid': [], 'invalid': [], 'missing': []}
        """
        result = {'valid': [], 'invalid': [], 'missing': []}
        
        # 检查关键凭证
        required_services = [
            ('vercel', 'token'),
        ]
        
        for service, key in required_services:
            value = self.get_credential(service, key)
            if value:
                result['valid'].append(f"{service}.{key}")
            else:
                result['missing'].append(f"{service}.{key}")
        
        return result
