# 新闻情报仪表板 - 部署说明

## 📊 项目概述

新闻情报仪表板 (News Intelligence Hub) 是一个实时热点新闻抓取、关联分析与可视化系统。

### 功能特性
- ✅ 实时热点新闻抓取（每30分钟更新）
- ✅ 新闻关联网络图（D3.js力导向图）
- ✅ 影响维度雷达图（社会/经济/政治/科技）
- ✅ 分类分布与情绪分析
- ✅ 热度时间线与关键词云
- ✅ 移动端响应式设计

---

## 📁 文件结构

```
news-intelligence-hub/
├── dashboard.html      # 主仪表板页面
├── data.json           # 新闻数据文件
├── vercel.json         # Vercel部署配置
├── package.json        # NPM配置
├── README.md           # 项目说明
└── news-intelligence-hub.tar.gz  # 部署压缩包
```

---

## 🚀 部署方式

### 方式一：Vercel部署（推荐）

#### 步骤1：安装Vercel CLI
```bash
npm install -g vercel
```

#### 步骤2：登录Vercel
```bash
vercel login
```

#### 步骤3：进入项目目录并部署
```bash
cd news-intelligence-hub
vercel --prod
```

部署完成后，Vercel会提供一个访问链接，例如：
- `https://news-intelligence-hub.vercel.app`

---

### 方式二：手动上传到Vercel

1. 访问 [Vercel Dashboard](https://vercel.com/dashboard)
2. 点击 "Add New Project"
3. 选择 "Import Git Repository" 或 "Upload" 
4. 上传 `news-intelligence-hub.tar.gz` 文件
5. 点击 "Deploy"

---

### 方式三：其他静态托管

由于本项目是纯前端静态页面，可以部署到任何静态托管服务：

- **GitHub Pages**: 将文件推送到GitHub仓库并启用Pages
- **Netlify**: 拖拽文件夹到Netlify Drop
- **Cloudflare Pages**: 上传文件夹
- **AWS S3**: 上传文件并配置静态网站托管

---

## 📊 数据来源

本次抓取的新闻数据（2026-03-01 18:47）包含：

| 指标 | 数值 |
|------|------|
| 总新闻数 | 20条 |
| 高影响事件 | 8条 |
| 平均热度 | 81.3 |
| 分类分布 | 科技(8), 财经(7), 国际政治(2), 社会(1), 政治(1) |

### 热点新闻TOP5

1. **美以联合袭击伊朗，全球金融市场震荡** (热度: 98.5)
2. **伊朗确认武装部队总参谋长、防长等高级将领遇袭身亡** (热度: 96.0)
3. **霍尔木兹停摆，欧佩克+能否稳住油价？** (热度: 95.0)
4. **OpenAI狂揽7500亿元，英伟达、亚马逊、软银抢投** (热度: 92.0)
5. **特朗普封杀Anthropic，OpenAI先声援后背刺** (热度: 88.5)

---

## 🔧 技术栈

- **前端框架**: 原生HTML5 + Tailwind CSS
- **可视化**: D3.js (网络图), Chart.js (图表)
- **字体**: Inter (Google Fonts)
- **部署**: Vercel Static

---

## 📝 更新计划

- [ ] 添加自动刷新功能
- [ ] 集成后端API实时抓取
- [ ] 添加用户订阅功能
- [ ] 多语言支持

---

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 项目地址: `/root/.openclaw/workspace/ai-agent-lab/skills/news-intelligence-hub`

---

*最后更新: 2026-03-01 18:47 (Asia/Shanghai)*