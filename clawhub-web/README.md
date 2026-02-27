# ClawHub Web - 技能包市场Web界面

🐾 ClawHub 是 AI Agent Lab 的官方技能包市场 Web 界面。

## 功能特性

- 🔍 **智能搜索** - 快速查找所需技能包
- 🏷️ **分类浏览** - 按类别筛选技能包
- 📊 **排序功能** - 支持按下载量、评分、更新时间排序
- 🌙 **深色模式** - 支持深色/浅色主题切换
- 📱 **响应式设计** - 完美适配桌面和移动设备
- 🎯 **一键安装** - 复制安装命令，快速使用

## 技术栈

- **纯前端实现** - HTML5 + CSS3 + Vanilla JavaScript
- **无需构建** - 直接部署静态文件
- **GitHub Pages** - 免费托管

## 本地开发

```bash
# 克隆仓库
git clone https://github.com/claw-bft/ai-agent-lab.git
cd ai-agent-lab/clawhub-web

# 启动本地服务器
python -m http.server 8080

# 访问 http://localhost:8080
```

## 部署

### GitHub Pages (推荐)

1. 进入仓库 Settings > Pages
2. Source 选择 "Deploy from a branch"
3. Branch 选择 "master"，文件夹选择 "/clawhub-web"
4. 保存后等待部署完成

### Vercel

```bash
# 安装 Vercel CLI
npm i -g vercel

# 部署
vercel --prod
```

## 项目结构

```
clawhub-web/
├── index.html      # 主页面
├── styles.css      # 样式文件
├── app.js          # 交互逻辑
└── README.md       # 本文档
```

## 数据来源

当前使用模拟数据展示，后续将接入 ClawHub Registry API：

```javascript
// API 端点
const API_BASE = 'https://clawhub-registry.vercel.app';

// 获取技能列表
GET /skills

// 获取技能详情
GET /skills/:name

// 获取分类
GET /categories

// 获取统计
GET /stats
```

## 贡献

欢迎提交 Issue 和 PR！

## 许可证

MIT License - 详见 [LICENSE](../LICENSE)
