# 飞书图片识别方案

## 需求分析
需要识别飞书聊天中的:
1. 话题消息中的图片
2. 引用消息中的图片

## 方案

### 方案 1: 使用 Feishu API 获取图片内容

**流程:**
```
用户发送带图片的消息
    ↓
OpenClaw 接收消息事件
    ↓
提取消息中的 image_key
    ↓
调用 Feishu API 下载图片
    ↓
使用多模态模型分析图片
    ↓
返回分析结果
```

**API 调用:**
```bash
# 获取图片内容
GET https://open.feishu.cn/open-apis/im/v1/images/{image_key}
Authorization: Bearer ${tenant_access_token}
```

**代码示例:**
```javascript
// 处理飞书消息中的图片
async function processFeishuImage(message) {
  // 1. 检查消息类型
  if (message.msg_type === 'image') {
    const imageKey = message.content.image_key;
    
    // 2. 下载图片
    const imageBuffer = await downloadImage(imageKey);
    
    // 3. 分析图片
    const analysis = await analyzeImage(imageBuffer);
    
    return analysis;
  }
  
  // 处理引用消息中的图片
  if (message.content?.mentions?.length > 0) {
    for (const mention of message.content.mentions) {
      if (mention.type === 'image') {
        const imageKey = mention.image_key;
        // ... 同样处理
      }
    }
  }
}
```

### 方案 2: 使用 OpenClaw 内置的图片处理能力

**配置:**
在 OpenClaw 配置中启用飞书图片处理:
```yaml
channels:
  feishu:
    handler:
      image:
        enabled: true
        download: true
        max_size: 10MB
```

### 方案 3: 使用外部 OCR 服务

**流程:**
```
飞书图片消息
    ↓
下载图片
    ↓
调用 OCR API (如 Azure Vision, Google Vision)
    ↓
提取文字/内容
    ↓
结合 LLM 分析
```

## 推荐实现

### 短期方案 (快速实现)
使用 OpenClaw 现有的图片处理能力，配置 feishu 连接器自动下载图片内容。

### 长期方案 (完整功能)
1. 扩展 feishu 连接器支持图片消息类型
2. 添加图片缓存机制
3. 集成多模态模型分析
4. 支持引用消息解析

## 技术要点

1. **图片下载**: 使用 Feishu API 需要 tenant_access_token
2. **格式支持**: 支持 JPG, PNG, GIF, WEBP
3. **大小限制**: 建议限制 10MB 以内
4. **引用消息**: 需要解析 message 的 parent_id 获取原消息
