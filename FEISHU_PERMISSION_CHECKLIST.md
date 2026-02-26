# 飞书应用权限配置清单

## 应用信息
- **应用 ID**: cli_a90c4cdf8d78dcc8
- **配置地址**: https://open.feishu.cn/app/cli_a90c4cdf8d78dcc8/permission

---

## 必需权限清单

### 1. 消息权限 (IM)
| 权限名称 | 权限 Key | 用途 | 状态 |
|---------|---------|------|------|
| 读取用户发给机器人的单聊消息 | `im:message.p2p_msg` | 接收单聊消息 | ☐ |
| 读取用户发给机器人的群聊消息 | `im:message.group_msg` | 接收群聊消息 | ☐ |
| 读取群信息 | `im:chat:readonly` | 获取群信息 | ☐ |
| 读取图片 | `im:image:readonly` | 下载图片 | ☐ |
| 读取文件 | `im:file:readonly` | 下载文件 | ☐ |
| 发送消息 | `im:message:send` | 发送消息 | ☐ |
| 发送图片 | `im:image` | 发送图片 | ☐ |
| 发送文件 | `im:file` | 发送文件 | ☐ |

### 2. 用户权限
| 权限名称 | 权限 Key | 用途 | 状态 |
|---------|---------|------|------|
| 获取用户基本信息 | `contact:user.base:readonly` | 获取用户信息 | ☐ |
| 获取部门基础信息 | `contact:department.base:readonly` | 获取部门信息 | ☐ |

### 3. 云文档权限 (可选)
| 权限名称 | 权限 Key | 用途 | 状态 |
|---------|---------|------|------|
| 查看云文档 | `docs:doc:readonly` | 读取文档 | ☐ |
| 查看电子表格 | `sheets:spreadsheet:readonly` | 读取表格 | ☐ |
| 查看多维表格 | `bitable:app:readonly` | 读取多维表格 | ☐ |

### 4. 知识库权限 (可选)
| 权限名称 | 权限 Key | 用途 | 状态 |
|---------|---------|------|------|
| 查看知识库 | `wiki:wiki:readonly` | 读取知识库 | ☐ |
| 查看云文档 | `wiki:page:readonly` | 读取知识库页面 | ☐ |

---

## 配置步骤

### Step 1: 登录飞书开放平台
1. 访问 https://open.feishu.cn/
2. 使用管理员账号登录

### Step 2: 进入应用管理
1. 点击「开发者后台」
2. 找到应用 `cli_a90c4cdf8d78dcc8`
3. 点击进入应用详情

### Step 3: 配置权限
1. 左侧菜单点击「权限管理」
2. 在搜索框中搜索上述权限 Key
3. 逐个勾选所需权限
4. 点击「批量申请」

### Step 4: 发布版本 (重要!)
1. 左侧菜单点击「版本管理与发布」
2. 点击「创建版本」
3. 填写版本信息
4. 提交审核或直接发布（内部应用可直接发布）

---

## 验证配置

配置完成后，在飞书群聊中:
1. 发送一张图片
2. @机器人
3. 检查机器人是否能识别并分析图片

---

## 常见问题

### Q: 权限已开通但无法下载图片?
A: 需要重新发布应用版本，权限变更需要发布后才生效。

### Q: 图片下载失败?
A: 检查 `im:image:readonly` 权限是否已申请并通过。

### Q: 引用消息中的图片无法识别?
A: 需要额外处理 `parent_id` 获取原消息，当前需要自定义代码实现。

---

## 当前状态检查

运行以下命令检查当前配置:
```bash
# 检查 OpenClaw 配置
cat /root/.openclaw/openclaw.json | grep -A 5 feishu

# 检查 Feishu 插件版本
ls -la /root/.openclaw/extensions/feishu/
```
