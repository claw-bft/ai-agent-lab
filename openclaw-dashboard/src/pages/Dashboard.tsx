import { useEffect, useState } from 'react'
import {
  Activity,
  CheckCircle,
  Clock,
  AlertCircle,
  Zap,
  Terminal,
  Cpu,
  HardDrive,
  MemoryStick,
  ArrowUpRight,
  TrendingUp,
  Server
} from 'lucide-react'
import type { Task } from '../components/TaskCard'
import type { Skill } from '../components/SkillCard'

interface SystemStatus {
  gateway: 'online' | 'offline'
  memory: number
  disk: number
  cpu: number
  activeSessions: number
  uptime: string
}

export default function Dashboard() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [skills, setSkills] = useState<Skill[]>([])
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    gateway: 'online',
    memory: 45,
    disk: 72,
    cpu: 23,
    activeSessions: 1,
    uptime: '3d 12h 45m',
  })

  useEffect(() => {
    // Parse tasks from TASKS.md content
    const mockTasks: Task[] = [
      {
        id: 'Task-001',
        title: 'LLM Coding能力对比网站',
        description: '创建交互式LLM Coding能力对比网站并部署到 Vercel',
        status: 'completed',
        priority: 'high',
        createdAt: '2026-02-25',
        completedAt: '2026-02-25',
        tags: ['web', 'vercel', 'llm'],
      },
    ]
    setTasks(mockTasks)

    // Mock skills data
    const mockSkills: Skill[] = [
      { name: 'discord', description: 'Discord integration', version: '1.0.0', author: 'OpenClaw', category: 'communication', tags: ['chat', 'bot'], global: true },
      { name: 'github', description: 'GitHub operations', version: '1.2.0', author: 'OpenClaw', category: 'productivity', tags: ['git', 'api'], global: true },
      { name: 'feishu', description: 'Feishu/Lark integration', version: '1.0.5', author: 'OpenClaw', category: 'communication', tags: ['docs', 'chat'], global: true },
      { name: 'weather', description: 'Weather queries', version: '0.9.0', author: 'Community', category: 'utility', tags: ['api', 'data'], global: true },
    ]
    setSkills(mockSkills)
  }, [])

  const stats = [
    { label: '总任务', value: tasks.length, icon: CheckCircle, color: 'text-success', bg: 'bg-success/10' },
    { label: '进行中', value: tasks.filter(t => t.status === 'in-progress').length, icon: Clock, color: 'text-accent', bg: 'bg-accent/10' },
    { label: '技能数', value: skills.length + 50, icon: Zap, color: 'text-warning', bg: 'bg-warning/10' },
    { label: '活跃会话', value: systemStatus.activeSessions, icon: Terminal, color: 'text-primary', bg: 'bg-primary/10' },
  ]

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">仪表板</h1>
          <p className="text-text-secondary mt-1">欢迎回来！这里是您的 OpenClaw 系统概览。</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-success/10 border border-success/30">
          <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
          <span className="text-sm text-success font-medium">系统正常</span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <div
            key={stat.label}
            className="bg-surface border border-border rounded-xl p-5 card-hover"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-muted text-sm">{stat.label}</p>
                <p className="text-2xl font-bold text-text-primary mt-1">{stat.value}</p>
              </div>
              <div className={`w-12 h-12 rounded-xl ${stat.bg} flex items-center justify-center`}>
                <stat.icon className={`w-6 h-6 ${stat.color}`} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* System Status */}
        <div className="lg:col-span-2 bg-surface border border-border rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                <Activity className="w-5 h-5 text-primary" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-text-primary">系统状态</h2>
                <p className="text-sm text-muted">实时监控</p>
              </div>
            </div>
            <span className="text-sm text-muted">运行时间: {systemStatus.uptime}</span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 rounded-lg bg-background border border-border">
              <div className="flex items-center gap-2 mb-2">
                <Server className="w-4 h-4 text-primary" />
                <span className="text-sm text-muted">Gateway</span>
              </div>
              <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium bg-success/10 text-success">
                <div className="w-1.5 h-1.5 rounded-full bg-success" />
                在线
              </span>
            </div>

            <div className="p-4 rounded-lg bg-background border border-border">
              <div className="flex items-center gap-2 mb-2">
                <Cpu className="w-4 h-4 text-accent" />
                <span className="text-sm text-muted">CPU</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-semibold text-text-primary">{systemStatus.cpu}%</span>
                <div className="flex-1 h-1.5 bg-surface rounded-full overflow-hidden">
                  <div
                    className="h-full bg-accent rounded-full transition-all duration-500"
                    style={{ width: `${systemStatus.cpu}%` }}
                  />
                </div>
              </div>
            </div>

            <div className="p-4 rounded-lg bg-background border border-border">
              <div className="flex items-center gap-2 mb-2">
                <MemoryStick className="w-4 h-4 text-warning" />
                <span className="text-sm text-muted">内存</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-semibold text-text-primary">{systemStatus.memory}%</span>
                <div className="flex-1 h-1.5 bg-surface rounded-full overflow-hidden">
                  <div
                    className="h-full bg-warning rounded-full transition-all duration-500"
                    style={{ width: `${systemStatus.memory}%` }}
                  />
                </div>
              </div>
            </div>

            <div className="p-4 rounded-lg bg-background border border-border">
              <div className="flex items-center gap-2 mb-2">
                <HardDrive className="w-4 h-4 text-secondary" />
                <span className="text-sm text-muted">磁盘</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-semibold text-text-primary">{systemStatus.disk}%</span>
                <div className="flex-1 h-1.5 bg-surface rounded-full overflow-hidden">
                  <div
                    className="h-full bg-secondary rounded-full transition-all duration-500"
                    style={{ width: `${systemStatus.disk}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-surface border border-border rounded-xl p-6">
          <h2 className="text-lg font-semibold text-text-primary mb-4">快捷操作</h2>
          <div className="space-y-3">
            {[
              { label: '新建任务', icon: CheckCircle, color: 'text-success', action: () => {} },
              { label: '查看技能', icon: Zap, color: 'text-warning', action: () => {} },
              { label: '打开终端', icon: Terminal, color: 'text-primary', action: () => {} },
              { label: '系统设置', icon: Activity, color: 'text-accent', action: () => {} },
            ].map((item) => (
              <button
                key={item.label}
                onClick={item.action}
                className="w-full flex items-center justify-between p-3 rounded-lg bg-background border border-border hover:border-border-hover hover:bg-surface-hover transition-all duration-200"
              >
                <div className="flex items-center gap-3">
                  <item.icon className={`w-5 h-5 ${item.color}`} />
                  <span className="text-text-primary">{item.label}</span>
                </div>
                <ArrowUpRight className="w-4 h-4 text-muted" />
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Tasks */}
      <div className="bg-surface border border-border rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-text-primary">最近任务</h2>
          <button className="text-sm text-primary hover:text-primary-hover transition-colors">
            查看全部
          </button>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-3 px-4 text-sm font-medium text-muted">任务</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-muted">状态</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-muted">优先级</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-muted">创建时间</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((task) => (
                <tr key={task.id} className="border-b border-border/50 hover:bg-surface-hover/50 transition-colors">
                  <td className="py-3 px-4">
                    <div className="font-medium text-text-primary">{task.title}</div>
                    <div className="text-sm text-muted truncate max-w-xs">{task.description}</div>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium ${
                      task.status === 'completed' ? 'bg-success/10 text-success' :
                      task.status === 'in-progress' ? 'bg-accent/10 text-accent' :
                      'bg-warning/10 text-warning'
                    }`}>
                      <div className={`w-1.5 h-1.5 rounded-full ${
                        task.status === 'completed' ? 'bg-success' :
                        task.status === 'in-progress' ? 'bg-accent' :
                        'bg-warning'
                      }`} />
                      {task.status === 'completed' ? '已完成' :
                       task.status === 'in-progress' ? '进行中' : '待处理'}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`text-xs ${
                      task.priority === 'high' ? 'text-error' :
                      task.priority === 'medium' ? 'text-warning' :
                      'text-success'
                    }`}>
                      {task.priority === 'high' ? '高' :
                       task.priority === 'medium' ? '中' : '低'}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-sm text-muted">{task.createdAt}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
