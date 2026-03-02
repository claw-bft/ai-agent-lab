# 新闻情报仪表板 - 部署包

## 📦 部署包内容

- `index.html` - 主仪表板页面（自包含，内嵌数据）
- `dashboard.html` - 备用仪表板页面
- `data.json` - 新闻数据文件
- `vercel.json` - Vercel 部署配置
- `package.json` - NPM 配置
- `README.md` - 项目说明

## 🚀 部署方式

### 当前部署（推荐）

**访问链接**: https://news-intelligence-2026-03-02.surge.sh

### 方式二：Vercel 手动部署

1. 访问 https://vercel.com/new
2. 选择 "Import Git Repository" 或 "Upload"
3. 上传 `news-intelligence-hub-deploy-20260302-2220.tar.gz` 文件
4. 点击 "Deploy"

### 方式三：Netlify 部署

1. 访问 https://app.netlify.com/drop
2. 拖拽 `index.html` 文件到上传区域
3. 获得访问链接

### 方式四：Cloudflare Pages

1. 访问 https://dash.cloudflare.com/
2. 创建新 Pages 项目
3. 上传 `index.html` 文件

### 方式五：GitHub Pages

1. 创建新 GitHub 仓库
2. 上传 `index.html` 文件
3. 启用 GitHub Pages

## 📊 当前数据概览

- **更新时间**: 2026-03-02 22:17 (Asia/Shanghai)
- **新闻总数**: 12 条
- **高影响事件**: 6 条
- **平均热度**: 85.3

### 分类分布
- 国际政治: 3 条
- 财经: 3 条
- 科技: 3 条
- 科技政策: 2 条
- 国内政治: 1 条

### 情绪分布
- 政治/地缘紧张: 4 条
- 科技创新: 5 条
- 经济政策: 3 条

### TOP 5 热点新闻

1. **伊朗最高领袖哈梅内伊在美以袭击中遇害** (热度: 98)
2. **霍尔木兹海峡关闭：全球能源大动脉陷入停滞** (热度: 94)
3. **全国政协十四届四次会议将于3月4日在京召开** (热度: 92)
4. **四部门发布20项举措推动科技保险高质量发展** (热度: 88)
5. **我国生成式人工智能用户规模超6亿人** (热度: 86)

## 🔧 技术栈

- **前端框架**: 原生 HTML5 + CSS3
- **可视化**: D3.js (网络图), Chart.js (雷达图)
- **响应式设计**: 支持移动端和桌面端
- **部署平台**: Surge.sh

## 📱 功能特性

- ✅ 实时热点新闻展示
- ✅ 新闻关联网络图（力导向图）
- ✅ 影响维度雷达图（社会/经济/政治/科技）
- ✅ 热度时间线
- ✅ 移动端响应式设计
- ✅ 交互式筛选

## 📝 更新日志

### 2026-03-02 22:17
- 更新 12 条最新热点新闻
- 数据时间戳更新至当前时间
- 生成新的部署包 news-intelligence-hub-deploy-20260302-2220.tar.gz
- **已部署至**: https://news-intelligence-2026-03-02.surge.sh

### 2026-03-02 16:47
- 更新 38 条最新热点新闻
- 数据时间戳更新至当前时间
- 生成新的部署包 news-intelligence-hub-deploy-20260302-1650.tar.gz
- **已部署至**: https://news-intelligence-hub-1772441402.surge.sh

---

*新闻情报仪表板 © 2026*