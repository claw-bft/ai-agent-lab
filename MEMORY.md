# 长期记忆

## 部署规则
- **默认部署平台**: Vercel
- **部署技能路径**: `/root/.openclaw/workspace/.claude/skills/vercel-deploy/`
- **部署脚本**: `bash /root/.openclaw/workspace/.claude/skills/vercel-deploy/scripts/deploy.sh <项目路径>`
- **特点**: 无需认证，自动检测框架，返回预览URL和认领URL

## 关键配置 (每次会话必须检查)

### VERCEL_TOKEN
- **状态**: ✅ 已配置
- **位置**: ~/.bashrc 第103行
- **值**: vcp_8CnZxMGVDbcYde49qIp77UmmDu7Df67MPf9dhGSsZfWWAH7SKX1Ag5GK
- **验证**: `grep "VERCEL" ~/.bashrc`
- **CLI**: vercel --version 可用
- **警告**: 用户极度厌恶重复询问此配置

### 其他环境变量
- 检查命令: `grep -E "export|TOKEN|KEY|SECRET" ~/.bashrc ~/.profile 2>/dev/null`

## 待办事项
- [x] 配置 VERCEL_TOKEN 以支持自动部署
- [x] 完成 Task-001 的 Vercel 部署
- [ ] 优化记忆系统 - 建立会话启动检查清单

## 项目记录

### LLM Coding 对比网站
- **创建时间**: 2026-02-25
- **Vercel链接**: https://skill-deploy-obqn9kyl4e-agent-skill-vercel.vercel.app
- **代码位置**: /root/.openclaw/workspace/llm-coding-comparison/
- **状态**: ✅ 已完成
