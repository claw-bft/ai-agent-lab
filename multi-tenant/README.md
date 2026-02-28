# 企业级多租户支持系统

AI Agent Lab 的企业级多租户支持系统，为SaaS部署提供完整的租户隔离、用户管理和权限控制功能。

## 功能特性

### 核心功能
- **租户管理**: 创建、查询、更新、删除租户，支持软删除
- **用户管理**: 租户内用户管理，支持多种角色
- **权限控制**: 基于角色的权限系统 (RBAC)
- **数据隔离**: 数据库表名隔离、文件存储隔离、缓存键隔离
- **资源配额**: 按服务等级限制资源使用

### 服务等级
| 等级 | 用户数 | 技能数 | 工作流数 | API调用/天 | 存储空间 |
|------|--------|--------|----------|------------|----------|
| FREE | 3 | 5 | 10 | 1,000 | 100MB |
| STARTER | 10 | 20 | 50 | 10,000 | 1GB |
| PROFESSIONAL | 50 | 100 | 500 | 100,000 | 10GB |
| ENTERPRISE | 无限制 | 无限制 | 无限制 | 无限制 | 无限制 |

## 快速开始

### 安装

```python
# 多租户模块已包含在项目中
from multi_tenant.core import TenantManager, TenantContext
from multi_tenant.auth import AuthManager
```

### 创建租户

```python
from multi_tenant.core import TenantManager, TenantTier

manager = TenantManager()

# 创建新租户
tenant = manager.create_tenant(
    name="Acme Corporation",
    owner_id="user_123",
    tier=TenantTier.PROFESSIONAL,
)

print(f"租户ID: {tenant.id}")
print(f"租户Slug: {tenant.slug}")
```

### 管理租户用户

```python
from multi_tenant.models import UserManager, UserRole

user_manager = UserManager()

# 创建用户
user = user_manager.create_user(
    tenant_id=tenant.id,
    email="admin@acme.com",
    username="admin",
    role=UserRole.ADMIN,
)

# 检查权限
if user_manager.has_permission(user.id, "skill:write"):
    print("用户有权限创建技能")
```

### 使用租户上下文

```python
from multi_tenant.core import TenantContext, get_current_tenant_id

# 方式1: 使用上下文管理器
with TenantContext(tenant_id="tenant_123", tenant_slug="acme"):
    # 在此范围内，get_current_tenant_id() 返回当前租户
    current_tenant = get_current_tenant_id()
    process_request()

# 方式2: 手动设置/清除
TenantContext.set_current("tenant_123", "acme", user_id="user_456")
try:
    process_request()
finally:
    TenantContext.clear()
```

### 资源隔离

```python
from multi_tenant.core import ResourceIsolator

isolator = ResourceIsolator(base_path="/data/tenants")

# 获取隔离的数据库表名
table_name = isolator.get_table_name("tenant_123", "users")
# 结果: t_a1b2c3d4_users

# 获取租户专属存储路径
storage_path = isolator.get_storage_path("tenant_123", "uploads")
# 结果: Path("/data/tenants/tenant_123/uploads")

# 获取隔离的缓存键
cache_key = isolator.get_cache_key("tenant_123", "user:profile:456")
# 结果: "tenant:tenant_123:user:profile:456"
```

### 认证与授权

```python
from multi_tenant.auth import AuthManager, PermissionChecker

auth = AuthManager(token_expiry_hours=24)

# 设置密码
auth.set_password("user_123", "secure_password")

# 验证密码
if auth.verify_user_password("user_123", "secure_password"):
    # 生成令牌
    token = auth.generate_token("user_123", "tenant_456")
    print(f"访问令牌: {token.access_token}")

# 验证令牌
user_info = auth.validate_token(token.access_token)
if user_info:
    print(f"用户ID: {user_info['user_id']}")

# 检查权限
if PermissionChecker.check(user.permissions, "workflow:execute"):
    print("有权限执行工作流")
```

## 项目结构

```
multi-tenant/
├── core/                   # 核心模块
│   ├── __init__.py        # 模块导出
│   ├── tenant_manager.py  # 租户管理器
│   ├── tenant_context.py  # 租户上下文
│   └── isolation.py       # 资源隔离器
├── models/                # 数据模型
│   └── user.py           # 用户模型和管理器
├── auth/                  # 认证模块
│   └── auth.py           # 认证管理器、权限检查
└── tests/                 # 测试套件
    ├── test_tenant_manager.py
    ├── test_tenant_context.py
    ├── test_isolation.py
    └── test_auth.py
```

## 运行测试

```bash
cd /root/.openclaw/workspace/ai-agent-lab/multi-tenant
python3 -m pytest tests/ -v
```

## API 参考

### TenantManager

```python
class TenantManager:
    def create_tenant(name, owner_id, tier, settings) -> Tenant
    def get_tenant(tenant_id) -> Optional[Tenant]
    def get_tenant_by_slug(slug) -> Optional[Tenant]
    def list_tenants(status, tier, limit, offset) -> List[Tenant]
    def update_tenant(tenant_id, **kwargs) -> Optional[Tenant]
    def delete_tenant(tenant_id, soft_delete=True) -> bool
    def get_quota_limits(tenant_id) -> Dict[str, int]
```

### TenantContext

```python
class TenantContext:
    @classmethod
    def set_current(tenant_id, tenant_slug, user_id)
    @classmethod
    def get_current_id() -> Optional[str]
    @classmethod
    def clear()
    @classmethod
    def is_set() -> bool
```

### ResourceIsolator

```python
class ResourceIsolator:
    def get_table_name(tenant_id, table_name) -> str
    def get_schema_name(tenant_id) -> str
    def get_storage_path(tenant_id, *subpaths) -> Path
    def get_cache_key(tenant_id, key) -> str
    def get_rate_limit_key(tenant_id, user_id) -> str
    def ensure_tenant_directory(tenant_id) -> Path
    def cleanup_tenant_resources(tenant_id) -> bool
```

## 集成指南

### 与 FastAPI 集成

```python
from fastapi import FastAPI, Request, Depends
from multi_tenant.core import TenantContext

app = FastAPI()

async def get_current_tenant(request: Request):
    # 从请求头或子域名获取租户
    tenant_slug = request.headers.get("X-Tenant-Slug")
    tenant_id = resolve_tenant_id(tenant_slug)
    
    TenantContext.set_current(tenant_id, tenant_slug)
    try:
        yield tenant_id
    finally:
        TenantContext.clear()

@app.get("/api/skills")
async def list_skills(tenant_id: str = Depends(get_current_tenant)):
    # 自动在租户上下文中执行
    return {"tenant_id": tenant_id, "skills": []}
```

### 与 Django 集成

```python
# middleware.py
from multi_tenant.core import TenantContext

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant_id = request.headers.get("X-Tenant-ID")
        tenant_slug = request.headers.get("X-Tenant-Slug")
        
        TenantContext.set_current(tenant_id, tenant_slug)
        try:
            response = self.get_response(request)
        finally:
            TenantContext.clear()
        
        return response
```

## 注意事项

1. **线程安全**: TenantContext 使用线程本地存储和上下文变量，支持同步和异步环境
2. **嵌套上下文**: 当前实现中嵌套上下文退出后不会自动恢复外层，建议使用上下文管理器
3. **存储后端**: 默认使用内存存储，生产环境应替换为数据库存储后端
4. **密码安全**: 使用 PBKDF2 哈希算法，生产环境建议使用更强的算法如 Argon2

## 许可证

MIT License
