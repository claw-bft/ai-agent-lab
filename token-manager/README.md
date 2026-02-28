# Token Manager

Token 管理器 - 安全存储和管理 API 密钥与访问令牌

## 功能特性

- **安全存储**: 本地 JSON 文件存储，敏感信息保护
- **多服务支持**: 管理多个服务的 API 密钥（GitHub、Vercel、AWS 等）
- **元数据支持**: 支持添加备注、用户名、过期时间等元数据
- **导入导出**: 支持凭证的导入和导出（可选包含敏感信息）
- **便捷函数**: 提供简单易用的全局函数快速访问

## 安装

```bash
# 复制到项目目录
cp -r token-manager /path/to/your/project/

# 使用
from token_manager import TokenManager, get_token, set_token
```

## 快速开始

### 基本使用

```python
from token_manager import TokenManager

# 创建管理器实例
tm = TokenManager()

# 设置凭证
tm.set_token('github', 'ghp_xxx123', username='myuser', note='个人访问令牌')

# 获取凭证
token = tm.get_token('github', 'token')
username = tm.get_token('github', 'username')

# 列出所有服务
services = tm.list_services()
print(services)  # ['github']
```

### 使用便捷函数

```python
from token_manager import get_token, set_token

# 快速设置
set_token('vercel', 'vc_token_xxx')

# 快速获取
token = get_token('vercel')
```

### 导入导出

```python
# 导出（不含敏感信息）
export_data = tm.export_tokens(include_secrets=False)

# 导出（包含敏感信息）
full_export = tm.export_tokens(include_secrets=True)

# 导入（合并模式）
tm.import_tokens(new_tokens, merge=True)

# 导入（覆盖模式）
tm.import_tokens(new_tokens, merge=False)
```

## API 参考

### TokenManager 类

| 方法 | 说明 |
|------|------|
| `set_token(service, token, **metadata)` | 设置服务凭证 |
| `get_token(service, field=None)` | 获取凭证信息 |
| `update_token(service, **kwargs)` | 更新凭证信息 |
| `delete_token(service)` | 删除凭证 |
| `has_token(service)` | 检查是否存在凭证 |
| `list_services()` | 列出所有服务 |
| `get_all_tokens()` | 获取所有凭证（隐藏敏感信息）|
| `export_tokens(include_secrets=False)` | 导出凭证 |
| `import_tokens(data, merge=True)` | 导入凭证 |
| `clear_all()` | 清除所有凭证 |

## 测试

```bash
cd token-manager
python3 -m pytest tests/ -v
```

## 文件结构

```
token-manager/
├── token_manager.py          # 主模块
├── SKILL.md                  # 技能文档
├── README.md                 # 本文件
└── tests/
    └── test_token_manager.py # 测试套件
```

## 许可证

MIT
