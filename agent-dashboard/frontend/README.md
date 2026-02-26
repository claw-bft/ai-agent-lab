# Agent Dashboard Frontend

Agent团队可视化Dashboard的React前端项目。

## 技术栈

- React 18 + TypeScript
- Tailwind CSS
- Chart.js (react-chartjs-2)
- Vite
- React Router DOM
- Lucide React (图标)
- clsx (类名管理)

## 项目结构

```
src/
├── components/
│   └── Layout.tsx          # 侧边栏布局组件
├── pages/
│   ├── Dashboard.tsx       # Dashboard首页
│   ├── Tasks.tsx           # 任务列表页面
│   └── Agents.tsx          # Agent管理页面
├── App.tsx                 # 主应用组件
├── main.tsx               # 入口文件
└── index.css              # 全局样式
```

## 页面功能

### 1. Dashboard首页
- 统计卡片展示（总Agent数、活跃任务、待处理任务、失败任务）
- 任务活动趋势图（Chart.js折线图）
- 任务摘要面板（完成/待处理/失败任务统计）
- 成功率进度条

### 2. Tasks页面
- 任务列表表格
- 搜索和状态筛选
- 任务进度条显示
- 详情抽屉（点击任务行打开）
  - 任务详情
  - 进度展示
  - 执行日志
  - 操作按钮（暂停/恢复、重启、删除）

### 3. Agents页面
- Agent统计概览
- Agent卡片网格
- CPU和内存使用率可视化
- 任务完成数统计
- Agent状态标识

## 设计特点

- **深色主题**: slate-950背景，slate-900卡片
- **响应式布局**: 支持桌面和移动端
- **实时数据**: 通过props传入数据，UI纯展示
- **交互体验**: 侧边栏可折叠、抽屉动画、悬停效果

## 安装和运行

```bash
# 安装依赖
npm install

# 开发模式
npm run dev

# 构建
npm run build

# 预览
npm run preview
```

## 数据接口

### Dashboard Props
```typescript
interface DashboardProps {
  stats: {
    totalAgents: number
    activeAgents: number
    totalTasks: number
    pendingTasks: number
    completedTasks: number
    failedTasks: number
  }
  chartData: ChartData
}
```

### Tasks Props
```typescript
interface TasksProps {
  tasks: Array<{
    id: string
    title: string
    status: 'running' | 'pending' | 'completed' | 'failed'
    agent: string
    priority: 'high' | 'medium' | 'low'
    progress: number
    createdAt: string
  }>
}
```

### Agents Props
```typescript
interface AgentsProps {
  agents: Array<{
    id: string
    name: string
    status: 'busy' | 'idle' | 'offline'
    type: string
    cpu: number
    memory: number
    tasksCompleted: number
  }>
}
```