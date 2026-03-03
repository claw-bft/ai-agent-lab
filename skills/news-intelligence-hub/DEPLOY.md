# 新闻情报仪表板 - 部署包

## 📦 部署包内容

- `index.html` - 主仪表板页面（自包含，内嵌数据）
- `dashboard.html` - 备用仪表板页面
- `data.json` - 新闻数据文件
- `vercel.json` - Vercel 部署配置
- `package.json` - NPM 配置
- `README.md` - 项目说明

## 🚀 部署方式

### 方式一：Surge.sh 部署（当前使用）

**访问链接**: https://news-intelligence-hub.surge.sh

```bash
cd /root/.openclaw/workspace/ai-agent-lab/skills/news-intelligence-hub/deploy
surge --project . --domain news-intelligence-hub.surge.sh
```

### 方式二：Vercel 部署

1. 安装 Vercel CLI:
```bash
npm i -g vercel
```

2. 登录 Vercel:
```bash
vercel login
```

3. 部署:
```bash
cd /root/.openclaw/workspace/ai-agent-lab/skills/news-intelligence-hub
vercel --prod
```

### 方式三：Netlify 部署

```bash
npm i -g netlify-cli
netlify deploy --prod --dir=.
```

## 📊 数据概览

- **新闻总数**: 30 条
- **高影响事件**: 18 条
- **平均热度**: 81.2
- **部署时间**: 2026-03-04 03:47 (Asia/Shanghai)
- **访问链接**: https://news-intelligence-hub.surge.sh

### 分类分布
- 科技: 15 条
- 经济金融: 6 条
- 国际政治: 5 条
- 国内政治: 4 条

### TOP 5 热点新闻

1. **美以袭击伊朗致中东局势升级 霍尔木兹海峡关闭** (热度: 99)
2. **全国政协十四届四次会议开幕 2026全国两会时间开启** (热度: 95)
3. **卡塔尔能源设施遭袭停产 欧洲天然气飙涨40%** (热度: 92)
4. **高盛：中国AI走出独立行情 潜在价值低估50%至100%** (热度: 91)
5. **具身智能开年狂揽超200亿融资 银河通用完成25亿元融资** (热度: 88)

## 🔧 技术栈

- **前端框架**: 原生 HTML5 + CSS3
- **可视化**: D3.js (网络图), Chart.js (雷达图)
- **响应式设计**: 支持移动端和桌面端
- **部署平台**: Vercel / Surge.sh / Netlify

## 📱 功能特性

- ✅ 实时热点新闻展示
- ✅ 新闻关联网络图（力导向图）
- ✅ 影响维度雷达图（社会/经济/政治/科技）
- ✅ 热度时间线
- ✅ 移动端响应式设计
- ✅ 交互式筛选

## 📝 更新日志

### 2026-03-04 03:47 (最新)
- ✅ 成功部署到 Surge.sh: https://news-intelligence-hub.surge.sh
- 更新 30 条最新热点新闻（新增6条）
- 新增：阿里巴巴AI品牌统一为千问、我国生成式AI用户超6亿、北京海淀AI产业布局、Anthropic Claude服务中断、十四五重大工程进展、特朗普指定英语为美国官方语言
- 数据时间戳更新至当前时间 (2026-03-04 03:47)
- 优化新闻关联网络，新增10条关联关系
- 统计：科技15条、经济金融6条、国际政治5条、国内政治4条

### 2026-03-04 02:17
- ✅ 成功部署到 Surge.sh: https://news-intelligence-hub.surge.sh
- 更新 24 条最新热点新闻（新增4条）
- 新增：高盛中国AI研报、荣耀MagicAgent开源、华为超节点海外亮相、世界经济论坛风险报告
- 数据时间戳更新至当前时间
- 优化新闻关联网络，新增7条关联关系

### 2026-03-04 01:48
- ✅ 成功部署到 Surge.sh: https://news-intelligence-hub.surge.sh
- 更新 20 条最新热点新闻
- 新增：美以袭击伊朗、全国两会、具身智能融资热潮等
- 数据时间戳更新至当前时间
- 生成部署包: news-intelligence-hub-deploy-20260304-0117.tar.gz

### 2026-03-04 01:17
- 更新 20 条最新热点新闻
- 新增：美以袭击伊朗、全国两会、具身智能融资热潮等
- 数据时间戳更新至当前时间
- 生成部署包: news-intelligence-hub-deploy-20260304-0117.tar.gz

---

*新闻情报仪表板 © 2026*