# 新闻情报仪表板 (News Intelligence Hub)

实时热点新闻抓取、关联分析与可视化仪表板。

## 功能特性

- ✅ 实时热点新闻抓取（每30分钟更新）
- ✅ 新闻关联网络图（D3.js力导向图）
- ✅ 影响维度雷达图（社会/经济/政治/科技）
- ✅ 分类分布与情绪分析
- ✅ 热度时间线与关键词云
- ✅ 移动端响应式设计

## 部署

### Vercel部署

```bash
# 安装Vercel CLI
npm i -g vercel

# 登录
vercel login

# 部署
vercel --prod
```

### 本地预览

```bash
npx serve .
```

## 数据来源

- 新浪财经
- 央视网
- 中国新闻网
- 其他公开新闻API

## 技术栈

- HTML5 + Tailwind CSS
- D3.js（网络图）
- Chart.js（图表）
- 纯前端静态部署
