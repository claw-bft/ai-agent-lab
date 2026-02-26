"""
安全模块 - 提供加密/解密功能
使用 Fernet 对称加密
"""
import os
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class SecurityManager:
    """安全管理器"""
    
    def __init__(self, key_path: str = None):
        """
        初始化安全模块
        
        Args:
            key_path: 密钥文件路径，默认 ~/.openclaw/.config_key
        """
        if key_path:
            self.key_path = Path(key_path)
        else:
            self.key_path = Path.home() / '.openclaw' / '.config_key'
        
        self.key_path.parent.mkdir(parents=True, exist_ok=True)
        self._fernet = None
        self._init_key()
    
    def _init_key(self):
        """初始化或加载加密密钥"""
        if self.key_path.exists():
            # 加载现有密钥
            with open(self.key_path, 'rb') as f:
                key = f.read()
        else:
            # 生成新密钥
            key = Fernet.generate_key()
            with open(self.key_path, 'wb') as f:
                f.write(key)
            # 设置权限为仅所有者可读写
            os.chmod(self.key_path, 0o600)
        
        self._fernet = Fernet(key)
    
    def encrypt(self, plaintext: str) -> str:
        """
        加密字符串
        
        Args:
            plaintext: 明文
            
        Returns:
            加密后的字符串（base64编码）
        """
        if not plaintext:
            return ""
        encrypted = self._fernet.encrypt(plaintext.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')
    
    def decrypt(self, ciphertext: str) -> str:
        """
        解密字符串
        
        Args:
            ciphertext: 密文（base64编码）
            
        Returns:
            解密后的明文
        """
        if not ciphertext:
            return ""
        try:
            encrypted = base64.urlsafe_b64decode(ciphertext.encode('utf-8'))
            decrypted = self._fernet.decrypt(encrypted)
            return decrypted.decode('utf-8')
        except Exception as e:
            print(f"[Security] 解密失败: {e}")
            return ""
    
    def rotate_key(self) -> bool:
        """
        轮换加密密钥（重新加密所有凭证）
        
        Returns:
            是否成功
        """
        # 注意：密钥轮换需要重新加密所有凭证
        # 这里仅实现密钥生成，实际轮换需要在 ConfigManager 中配合完成
        try:
            new_key = Fernet.generate_key()
            with open(self.key_path, 'wb') as f:
                f.write(new_key)
            os.chmod(self.key_path, 0o600)
            self._fernet = Fernet(new_key)
            return True
        except Exception as e:
            print(f"[Security] 密钥轮换失败: {e}")
            return False
