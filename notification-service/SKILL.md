# Notification Service - 任务完成主动通知

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

### 3. 集成到子任务

```javascript
// 在spawn任务中集成通知
sessions_spawn({
  task: `执行数据备份任务...

任务完成后，你必须：
1. 总结任务结果（1-2句话）
2. 使用 message 工具发送飞书消息通知用户
3. 消息格式："【任务完成】备份任务：结果摘要"`
});
```

## API 参考

### Shell 脚本

#### `notify-feishu.sh <message>`

发送飞书文本消息

**参数：**
- `message`: 要发送的消息内容

**环境变量：**
- `FEISHU_WEBHOOK_KEY`: 飞书机器人Webhook密钥

**示例：**
```bash
./notify-feishu.sh "【成功】构建完成"
./notify-feishu.sh "【警告】磁盘空间不足"
./notify-feishu.sh "【错误】数据库连接失败"
```

### Node.js 模块

#### `notifyFeishu(message, webhookKey)`

发送飞书通知

**参数：**
- `message`: 字符串或对象
  - 字符串: 直接发送文本
  - 对象: `{ title, content, url }` 发送富文本卡片
- `webhookKey`: 飞书机器人Webhook密钥

**返回：**
- Promise<void>

**示例：**
```javascript
// 简单文本
await notifyFeishu('Hello from AI Agent', 'your-key');

// 富文本卡片
await notifyFeishu({
  title: '【日报生成】第100期',
  content: '已生成并部署到: https://...',
  url: 'https://example.com/report'
}, 'your-key');
```

## 使用场景

### 场景1: 定时任务通知

```bash
#!/bin/bash
# daily-report.sh

# 生成日报
python3 generate_report.py

# 发送通知
./notification-service/notify-feishu.sh "【日报生成】$(date +%Y-%m-%d) 日报已完成"
```

### 场景2: CI/CD 流水线

```javascript
// deploy.js
const { notifyFeishu } = require('./notification-service/notify');

async function deploy() {
  try {
    await build();
    await deployToServer();
    await notifyFeishu('【部署成功】生产环境已更新', process.env.FEISHU_KEY);
  } catch (error) {
    await notifyFeishu(`【部署失败】${error.message}`, process.env.FEISHU_KEY);
    process.exit(1);
  }
}
```

### 场景3: 数据监控告警

```python
import subprocess
import os

def check_disk_space():
    usage = get_disk_usage()
    if usage > 90:
        subprocess.run([
            './notification-service/notify-feishu.sh',
            f'【告警】磁盘使用率 {usage}%，请及时清理'
        ])
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `FEISHU_WEBHOOK_KEY` | 飞书机器人Webhook密钥 | 是 |

### 获取飞书Webhook密钥

1. 打开飞书群聊设置
2. 点击 "群机器人" → "添加机器人"
3. 选择 "自定义机器人"
4. 复制Webhook URL中的 `key` 参数
   - URL格式: `https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxx`
   - key 为 `xxxxxx` 部分

## 扩展其他通知渠道

### 添加钉钉支持

```javascript
// notify-dingtalk.js
async function notifyDingtalk(message, webhookUrl) {
  const payload = {
    msgtype: 'text',
    text: { content: message }
  };
  
  await fetch(webhookUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
}

module.exports = { notifyDingtalk };
```

### 添加 Slack 支持

```javascript
// notify-slack.js
async function notifySlack(message, webhookUrl) {
  await fetch(webhookUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: message })
  });
}
```

## 最佳实践

1. **消息格式**: 使用统一的标签前缀
   - `【成功】` - 任务完成
   - `【警告】` - 需要注意
   - `【错误】` - 任务失败
   - `【信息】` - 一般通知

2. **敏感信息**: 不要在消息中包含API密钥、密码等敏感信息

3. **消息长度**: 保持消息简洁，重要信息放在前面

4. **错误处理**: 通知失败不应影响主流程

```javascript
// 好的做法
try {
  await notifyFeishu('任务完成', key);
} catch (e) {
  console.error('通知发送失败:', e);
  // 继续执行，不中断主流程
}
```

## 故障排查

### 消息发送失败

1. 检查 `FEISHU_WEBHOOK_KEY` 是否正确设置
2. 确认网络可以访问 `open.feishu.cn`
3. 查看飞书机器人是否被禁言或删除

### 权限问题

```bash
# 添加执行权限
chmod +x notify-feishu.sh
```

## 许可证

MIT License
