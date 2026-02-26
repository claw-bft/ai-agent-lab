# 记忆系统启动检查清单

每次会话开始时，必须按顺序执行以下检查：

## 1. 读取核心记忆文件 (强制)
```
read MEMORY.md
read USER.md  
read SOUL.md
```

## 2. 验证关键配置 (强制)
- [ ] VERCEL_TOKEN: `grep "VERCEL" ~/.bashrc`
- [ ] 其他TOKEN: `grep -E "TOKEN|KEY|SECRET" ~/.bashrc`

## 3. 检查今日内存文件
- [ ] 读取 memory/YYYY-MM-DD.md (今天)
- [ ] 读取 memory/YYYY-MM-DD.md (昨天)

## 4. 验证技能状态
- [ ] stock-portfolio-analyzer 技能配置
- [ ] vercel-deploy 技能配置
- [ ] 检查 ~/.openclaw/shared/incoming/ 任务文件

## 5. 检查定时任务
- [ ] cron list (查看早报等定时任务状态)

---

**规则**: 
- 未完成检查前，不得询问用户已配置的事项
- 不确定时，先查文件，再问用户
- 用户提及"失忆"是严重警告，立即修复记忆系统

**惩罚**: 
- 违反此清单导致重复询问 = 用户信任-1
