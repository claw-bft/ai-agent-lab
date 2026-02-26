# 飞书图片处理配置方案

## 现状分析

**好消息**: OpenClaw 的 Feishu 插件已经原生支持图片处理！

**已有功能**:
- `downloadImageFeishu()` - 下载图片
- `downloadMessageResourceFeishu()` - 下载消息资源（图片/文件）
- `uploadImageFeishu()` - 上传图片
- `sendImageFeishu()` - 发送图片消息

## 配置步骤

### 1. 确认 Feishu 应用权限

需要确保飞书应用有以下权限：
- `im:chat:readonly` - 读取群组信息
- `im:message:send` - 发送消息
- `im:message.group_msg` - 接收群消息
- `im:message.p2p_msg` - 接收单聊消息
- `im:image:readonly` - 读取图片（关键权限）
- `im:file:readonly` - 读取文件

**检查方式**:
1. 登录飞书开放平台: https://open.feishu.cn/app
2. 找到你的应用 `cli_a90c4cdf8d78dcc8`
3. 进入「权限管理」
4. 确认上述权限已开通

### 2. 配置 OpenClaw 接收图片消息

当前 OpenClaw 配置已经启用了飞书频道，但需要确保能处理图片类型消息。

**消息类型处理**:
飞书图片消息格式:
```json
{
  "msg_type": "image",
  "content": {
    "image_key": "img_xxxxxx"
  }
}
```

### 3. 图片处理流程

```
用户发送图片 → OpenClaw 接收消息 → 提取 image_key 
    → 调用 downloadImageFeishu() 下载
    → 使用多模态模型分析
    → 返回分析结果
```

## 实施方案

### 方案 A: 使用现有工具（推荐）

OpenClaw 已经有 `feishu_doc` 等工具，可以扩展添加图片处理工具。

**需要添加的工具**:
1. `feishu_download_image` - 下载图片
2. `feishu_analyze_image` - 分析图片内容

### 方案 B: 自动处理（更智能）

在消息处理流程中自动检测图片并分析：

```typescript
// 伪代码
if (message.msg_type === 'image') {
  const imageBuffer = await downloadImageFeishu({
    cfg,
    imageKey: message.content.image_key
  });
  
  // 使用多模态模型分析
  const analysis = await analyzeImage(imageBuffer);
  
  // 将分析结果加入对话上下文
  context.addImageAnalysis(analysis);
}
```

## 测试步骤

1. 在飞书群聊中发送一张图片
2. 检查 OpenClaw 是否接收到消息
3. 验证图片是否能被正确下载和分析

## 注意事项

1. **图片大小限制**: 飞书图片最大 20MB
2. **格式支持**: JPG, PNG, WEBP, GIF, TIFF, BMP, ICO
3. **引用消息**: 需要额外处理 `parent_id` 获取原消息内容
4. **话题消息**: 需要处理 `thread_id` 字段

## 下一步

需要我:
1. 检查当前 Feishu 应用的权限配置？
2. 创建一个图片处理测试脚本？
3. 扩展 feishu 工具添加图片分析功能？
