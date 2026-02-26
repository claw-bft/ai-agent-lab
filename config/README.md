# 统一配置管理系统

集中管理所有凭证和配置，替代分散在 ~/.bashrc 中的环境变量。

## 目录结构

```
config/
├── credentials.yaml      # 加密存储的敏感凭证
├── settings.yaml         # 普通配置
├── config_manager.py     # 配置管理核心模块
├── security.py           # 加密/解密工具
├── migrate.py            # 从 ~/.bashrc 迁移配置
└── validate.py           # 配置验证脚本
```

## 使用方法

```python
from config.config_manager import ConfigManager

config = ConfigManager()
vercel_token = config.get_credential('vercel', 'token')
```

## 安全说明

- 敏感凭证使用 Fernet 对称加密存储
- 密钥存储在 ~/.openclaw/.config_key
- 首次使用时自动生成密钥
