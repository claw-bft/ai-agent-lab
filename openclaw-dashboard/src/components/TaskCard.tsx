import { CheckCircle, Clock, AlertCircle, MoreHorizontal, Calendar, Tag } from 'lucide-react'

export interface Task {
  id: string
  title: string
  description: string
  status: 'completed' | 'in-progress' | 'pending' | 'cancelled'
  priority: 'high' | 'medium' | 'low'
  createdAt: string
  completedAt?: string
  tags: string[]
}

interface TaskCardProps {
  task: Task
}

const statusConfig = {
  completed: { icon: CheckCircle, color: 'text-success', bg: 'bg-success/10', label: '已完成' },
  'in-progress': { icon: Clock, color: 'text-accent', bg: 'bg-accent/10', label: '进行中' },
  pending: { icon: AlertCircle, color: 'text-warning', bg: 'bg-warning/10', label: '待处理' },
  cancelled: { icon: AlertCircle, color: 'text-error', bg: 'bg-error/10', label: '已取消' },
}

const priorityConfig = {
  high: { color: 'text-error border-error/30 bg-error/5', label: '高' },
  medium: { color: 'text-warning border-warning/30 bg-warning/5', label: '中' },
  low: { color: 'text-success border-success/30 bg-success/5', label: '低' },
}

export default function TaskCard({ task }: TaskCardProps) {
  const status = statusConfig[task.status]
  const priority = priorityConfig[task.priority]
  const StatusIcon = status.icon

  return (
    <div className="bg-surface border border-border rounded-xl p-5 card-hover">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className={`px-2 py-0.5 rounded text-xs font-medium border ${priority.color}`}>
            {priority.label}优先级
          </span>
          <span className={`flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${status.bg} ${status.color}`}>
            <StatusIcon className="w-3 h-3" />
            {status.label}
          </span>
        </div>
        <button className="p-1 rounded hover:bg-surface-hover text-muted hover:text-text-primary transition-colors">
          <MoreHorizontal className="w-4 h-4" />
        </button>
      </div>

      <h3 className="text-lg font-semibold text-text-primary mb-2">{task.title}</h3>
      <p className="text-sm text-text-secondary mb-4 line-clamp-2">{task.description}</p>

      <div className="flex items-center justify-between text-xs text-muted">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1">
            <Calendar className="w-3.5 h-3.5" />
            <span>{task.createdAt}</span>
          </div>
          
          {task.tags.length > 0 && (
            <div className="flex items-center gap-1">
              <Tag className="w-3.5 h-3.5" />
              <span>{task.tags.join(', ')}</span>
            </div>
          )}
        </div>

        {task.completedAt && (
          <span>完成于 {task.completedAt}</span>
        )}
      </div>
    </div>
  )
}
