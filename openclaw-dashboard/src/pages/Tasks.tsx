import { useState, useEffect } from 'react'
import {
  Search,
  Filter,
  Plus,
  MoreHorizontal,
  CheckCircle,
  Clock,
  AlertCircle,
  Calendar,
  Tag,
  ArrowUpDown,
  Download,
  Trash2,
  Edit
} from 'lucide-react'
import TaskCard, { type Task } from '../components/TaskCard'

export default function Tasks() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [priorityFilter, setPriorityFilter] = useState<string>('all')
  const [sortBy, setSortBy] = useState<'date' | 'priority' | 'status'>('date')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')

  useEffect(() => {
    // Parse tasks from TASKS.md content
    const mockTasks: Task[] = [
      {
        id: 'Task-001',
        title: 'LLM Coding能力对比网站',
        description: '创建交互式LLM Coding能力对比网站并部署到 Vercel。需要实现交互式图表、模型筛选器、成本计算器和推荐系统。',
        status: 'completed',
        priority: 'high',
        createdAt: '2026-02-25',
        completedAt: '2026-02-25',
        tags: ['web', 'vercel', 'llm', 'dashboard'],
      },
      {
        id: 'Task-002',
        title: 'OpenClaw 控制面板',
        description: '创建 OpenClaw 可视化控制面板网站，包含 Dashboard、任务管理、技能管理、交互终端和系统设置页面。',
        status: 'in-progress',
        priority: 'high',
        createdAt: '2026-02-25',
        tags: ['web', 'react', 'dashboard', 'openclaw'],
      },
      {
        id: 'Task-003',
        title: '飞书消息集成优化',
        description: '优化飞书消息的发送和接收逻辑，支持更多消息类型和格式。',
        status: 'pending',
        priority: 'medium',
        createdAt: '2026-02-24',
        tags: ['feishu', 'integration', 'messaging'],
      },
      {
        id: 'Task-004',
        title: '技能市场开发',
        description: '开发技能市场功能，允许用户浏览、安装和管理第三方技能。',
        status: 'pending',
        priority: 'low',
        createdAt: '2026-02-20',
        tags: ['skills', 'marketplace', 'feature'],
      },
    ]
    setTasks(mockTasks)
  }, [])

  const filteredTasks = tasks.filter((task) => {
    const matchesSearch = task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         task.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         task.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    const matchesStatus = statusFilter === 'all' || task.status === statusFilter
    const matchesPriority = priorityFilter === 'all' || task.priority === priorityFilter
    return matchesSearch && matchesStatus && matchesPriority
  })

  const sortedTasks = [...filteredTasks].sort((a, b) => {
    if (sortBy === 'date') {
      return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    }
    if (sortBy === 'priority') {
      const priorityOrder = { high: 3, medium: 2, low: 1 }
      return priorityOrder[b.priority] - priorityOrder[a.priority]
    }
    if (sortBy === 'status') {
      const statusOrder = { 'in-progress': 4, pending: 3, completed: 2, cancelled: 1 }
      return statusOrder[b.status] - statusOrder[a.status]
    }
    return 0
  })

  const stats = {
    total: tasks.length,
    completed: tasks.filter(t => t.status === 'completed').length,
    inProgress: tasks.filter(t => t.status === 'in-progress').length,
    pending: tasks.filter(t => t.status === 'pending').length,
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">任务管理</h1>
          <p className="text-text-secondary mt-1">管理和跟踪您的所有任务</p>
        </div>
        <button className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          新建任务
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: '总任务', value: stats.total, color: 'text-primary', bg: 'bg-primary/10' },
          { label: '已完成', value: stats.completed, color: 'text-success', bg: 'bg-success/10' },
          { label: '进行中', value: stats.inProgress, color: 'text-accent', bg: 'bg-accent/10' },
          { label: '待处理', value: stats.pending, color: 'text-warning', bg: 'bg-warning/10' },
        ].map((stat) => (
          <div key={stat.label} className="bg-surface border border-border rounded-xl p-4">
            <p className="text-muted text-sm">{stat.label}</p>
            <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="bg-surface border border-border rounded-xl p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
            <input
              type="text"
              placeholder="搜索任务..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input-dark pl-10 w-full"
            />
          </div>
          
          <div className="flex gap-2">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input-dark"
            >
              <option value="all">所有状态</option>
              <option value="completed">已完成</option>
              <option value="in-progress">进行中</option>
              <option value="pending">待处理</option>
              <option value="cancelled">已取消</option>
            </select>
            
            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="input-dark"
            >
              <option value="all">所有优先级</option>
              <option value="high">高</option>
              <option value="medium">中</option>
              <option value="low">低</option>
            </select>
            
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'date' | 'priority' | 'status')}
              className="input-dark"
            >
              <option value="date">按日期</option>
              <option value="priority">按优先级</option>
              <option value="status">按状态</option>
            </select>
          </div>
        </div>
      </div>

      {/* Task List */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <p className="text-muted text-sm">
            显示 {sortedTasks.length} 个任务
          </p>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-lg transition-colors ${viewMode === 'grid' ? 'bg-primary text-white' : 'text-muted hover:text-text-primary'}`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
              </svg>
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-lg transition-colors ${viewMode === 'list' ? 'bg-primary text-white' : 'text-muted hover:text-text-primary'}`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>

        {viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {sortedTasks.map((task) => (
              <TaskCard key={task.id} task={task} />
            ))}
          </div>
        ) : (
          <div className="bg-surface border border-border rounded-xl overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-surface-hover">
                  <th className="text-left py-3 px-4 text-sm font-medium text-muted">任务</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-muted">状态</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-muted">优先级</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-muted">标签</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-muted">创建时间</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-muted">操作</th>
                </tr>
              </thead>
              <tbody>
                {sortedTasks.map((task) => (
                  <tr key={task.id} className="border-b border-border/50 hover:bg-surface-hover/50 transition-colors">
                    <td className="py-3 px-4">
                      <div className="font-medium text-text-primary">{task.title}</div>
                      <div className="text-sm text-muted truncate max-w-xs">{task.description}</div>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium ${
                        task.status === 'completed' ? 'bg-success/10 text-success' :
                        task.status === 'in-progress' ? 'bg-accent/10 text-accent' :
                        task.status === 'cancelled' ? 'bg-error/10 text-error' :
                        'bg-warning/10 text-warning'
                      }`}>
                        <div className={`w-1.5 h-1.5 rounded-full ${
                          task.status === 'completed' ? 'bg-success' :
                          task.status === 'in-progress' ? 'bg-accent' :
                          task.status === 'cancelled' ? 'bg-error' :
                          'bg-warning'
                        }`} />
                        {task.status === 'completed' ? '已完成' :
                         task.status === 'in-progress' ? '进行中' :
                         task.status === 'cancelled' ? '已取消' : '待处理'}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`text-xs font-medium ${
                        task.priority === 'high' ? 'text-error' :
                        task.priority === 'medium' ? 'text-warning' :
                        'text-success'
                      }`}>
                        {task.priority === 'high' ? '高' :
                         task.priority === 'medium' ? '中' : '低'}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex gap-1">
                        {task.tags.slice(0, 2).map((tag) => (
                          <span key={tag} className="px-1.5 py-0.5 rounded text-xs bg-surface-hover text-muted border border-border">
                            {tag}
                          </span>
                        ))}
                        {task.tags.length > 2 && (
                          <span className="text-xs text-muted">+{task.tags.length - 2}</span>
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-4 text-sm text-muted">{task.createdAt}</td>
                    <td className="py-3 px-4">
                      <div className="flex items-center justify-end gap-1">
                        <button className="p-1.5 rounded hover:bg-surface-hover text-muted hover:text-text-primary transition-colors">
                          <Edit className="w-4 h-4" />
                        </button>
                        <button className="p-1.5 rounded hover:bg-error/10 text-muted hover:text-error transition-colors">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {sortedTasks.length === 0 && (
          <div className="text-center py-12">
            <div className="w-16 h-16 rounded-full bg-surface border border-border flex items-center justify-center mx-auto mb-4">
              <Search className="w-8 h-8 text-muted" />
            </div>
            <p className="text-text-secondary">没有找到匹配的任务</p>
            <button
              onClick={() => {
                setSearchQuery('')
                setStatusFilter('all')
                setPriorityFilter('all')
              }}
              className="mt-2 text-primary hover:text-primary-hover"
            >
              清除筛选
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
