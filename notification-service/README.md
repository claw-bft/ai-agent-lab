# Notification Service

📬 为 AI Agent 任务提供主动通知能力，支持飞书、Webhook等多种渠道。

## 功能特性

- **飞书通知** - 支持飞书机器人消息推送
- **Webhook支持** - 通用HTTP回调通知
- **任务集成** - 轻松集成到spawn子任务
- **简洁API** - 一行命令发送通知
- **多平台** - 支持多种通知渠道扩展

## 安装

```bash
# 复制到您的项目
cp -r notification-service/ my-project/

# 确保有执行权限
chmod +x notification-service/notify-feishu.sh
```

## 快速开始

### 1. 飞书机器人配置

1. 在飞书群聊中添加自定义机器人
2. 获取 Webhook URL 中的 `key` 参数
3. 设置环境变量：

```bash
export FEISHU_WEBHOOK_KEY="your-webhook-key"
```

### 2. 发送通知

#### Shell 脚本方式

```bash
# 基础用法
./notify-feishu.sh "任务完成啦！"

# 带标题
./notify-feishu.sh "【构建成功】项目已部署到生产环境"
```

#### Python 方式

```python
from notify import NotificationService

# 初始化服务
service = NotificationService()

# 发送飞书通知
service.notify_feishu("任务执行完成", webhook_key="your-key")

# 发送富文本通知
service.notify_feishu(
    title="【成功】数据同步完成",
    content="已同步 1,234 条记录",
    url="https://dashboard.example.com"
)
```

#### Node.js 方式

```javascript
const { notifyFeishu } = require('./notify');

// 发送文本通知
await notifyFeishu('任务执行完成', process.env.FEISHU_WEBHOOK_KEY);

// 发送富文本通知
await notifyFeishu({
  title: '【成功】数据同步完成',
  content: '已同步 1,234 条记录',
  url: 'https://dashboard.example.com'
}, process.env.FEISHU_WEBHOOK_KEY);
```

## 项目结构

```
notification-service/
├── notify.py           # Python核心实现
├── notify.js           # Node.js实现
├── notify-feishu.sh    # Shell脚本入口
├── tests/              # 测试目录
│   └── test_notify.py
└── SKILL.md           # 技能文档
```

## 测试

```bash
pytest tests/ -v
```

## 许可证

MIT License
