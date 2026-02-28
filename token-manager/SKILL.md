# Token Manager - 全局凭证管理

🔐 安全存储和管理敏感凭证，支持按服务分类、权限控制和加密存储。

## 功能特性

- **安全存储** - 敏感信息存储在用户主目录下
- **服务分类** - 按服务类型组织凭证（GitHub、Vercel等）
- **元数据支持** - 记录创建时间、权限范围、备注等
- **便捷函数** - 提供快速读取/写入的全局函数
- **完整测试** - 21个单元测试覆盖所有功能

## 安装

```bash
# 复制到您的项目
cp -r token-manager/ my-project/

# 使用
from token_manager import TokenManager, get_token, set_token
```

## 快速开始

### 1. 基础使用

```python
from token_manager import TokenManager

# 初始化管理器
tm = TokenManager()

# 设置凭证
tm.set_token('github', 'ghp_xxx', 
             username='claw-bft',
             scopes=['repo', 'user'],
             note='GitHub CLI token')

# 获取凭证
token = tm.get_token('github', 'token')
username = tm.get_token('github', 'username')
```

### 2. 便捷函数

```python
from token_manager import get_token, set_token

# 快速设置
set_token('vercel', 'vcp_xxx', note='Deployment token')

# 快速获取
token = get_token('github')
```

### 3. 管理多个凭证

```python
# 列出所有服务
services = tm.list_services()
# ['github', 'vercel', 'aws']

# 检查是否存在
if tm.has_token('github'):
    print('GitHub token exists')

# 更新部分字段
tm.update_token('github', note='Updated note')

# 删除凭证
tm.delete_token('old_service')
```

## 存储位置

默认存储路径：`~/.openclaw/secrets/tokens.json`

```json
{
  "github": {
    "token": "ghp_xxx",
    "created_at": "2026-02-28T12:00:00",
    "username": "claw-bft",
    "scopes": ["repo", "user"],
    "note": "GitHub CLI token"
  },
  "vercel": {
    "token": "vcp_xxx",
    "created_at": "2026-02-28T12:00:00",
    "note": "Vercel deployment"
  }
}
```

## API 参考

### TokenManager 类

#### `__init__(tokens_file=None)`
初始化凭证管理器
- `tokens_file`: 自定义凭证文件路径（可选）

#### `get_token(service, key=None)`
获取凭证
- `service`: 服务名称
- `key`: 特定字段，为None返回整个对象
- 返回: 凭证值或None

#### `set_token(service, token, **metadata)`
设置凭证
- `service`: 服务名称
- `token`: API密钥或令牌
- `**metadata`: 额外元数据

#### `update_token(service, **updates)`
更新现有凭证
- 返回: 是否成功更新

#### `delete_token(service)`
删除凭证
- 返回: 是否成功删除

#### `list_services()`
列出所有服务名称
- 返回: 服务名称列表

#### `has_token(service)`
检查是否存在
- 返回: bool

#### `get_all_tokens()`
获取所有凭证（token值被隐藏为***）
- 返回: 凭证字典

#### `export_tokens(include_secrets=False)`
导出凭证
- `include_secrets`: 是否包含敏感值
- 返回: 凭证字典

#### `import_tokens(tokens, merge=True)`
导入凭证
- `tokens`: 要导入的字典
- `merge`: True合并，False覆盖

#### `clear_all()`
清除所有凭证（谨慎使用）

### 便捷函数

#### `get_token(service, key='token', tokens_file=None)`
快速获取凭证

#### `set_token(service, token, tokens_file=None, **metadata)`
快速设置凭证

## 测试

```bash
cd token-manager
python3 -m pytest tests/ -v
```

测试结果：21个测试全部通过 ✅

## 安全提示

1. **文件权限**: 凭证文件存储在用户主目录，确保目录权限正确
2. **敏感信息**: 使用 `get_all_tokens()` 时token值会被隐藏
3. **备份**: 定期备份 `~/.openclaw/secrets/tokens.json`
4. **版本控制**: 切勿将凭证文件提交到Git仓库

## 使用示例

### CI/CD 集成

```python
from token_manager import get_token
import os

# 在CI环境中使用
github_token = get_token('github')
os.environ['GITHUB_TOKEN'] = github_token
```

### 多环境配置

```python
from token_manager import TokenManager

# 开发环境
dev_tm = TokenManager('~/.tokens/dev.json')

# 生产环境
prod_tm = TokenManager('~/.tokens/prod.json')
```

## 许可证

MIT License
