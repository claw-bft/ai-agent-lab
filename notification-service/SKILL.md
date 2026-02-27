# Notification Service - 任务完成主动通知 (简化版)

## 使用方式

在spawn子任务时，在prompt末尾添加：

```
任务完成后，你必须：
1. 总结任务结果（1-2句话）
2. 使用 message 工具发送飞书消息通知用户
3. 消息格式："【任务完成】任务名称：结果摘要"

示例：
message action=send target="user:ou_a3b690a5560dafe48a8c244c42c76bf0" text="【任务完成】早报生成：第057期早报已部署 https://xxx.vercel.app"
```

## 集成到现有任务

修改后的spawn示例：

```javascript
sessions_spawn({
  task: `执行股市早报任务...

任务完成后，你必须：
1. 总结任务结果（1-2句话）
2. 使用 message 工具发送飞书消息通知用户
3. 消息格式："【任务完成】早报生成：结果摘要 + 链接"`
});
```

## 效果
- 子任务完成后，用户会收到飞书消息
- 不需要用户主动查看
- 真正实现"异步执行 + 主动推送"
